# -*- coding: latin-1 -*-

import os.path
import re
import xbmc, xbmcgui
import urllib
import common

from entities.CListItem import CListItem
from xml.dom.minidom import parseString


from utils import fileUtils as fu

from utils.xbmcUtils import getKeyboard
import utils.encodingUtils as enc
from utils import regexUtils

class FavouritesManager:

    def __init__(self, favouritesFolder):
        self._favouritesFolder = favouritesFolder
        if not os.path.exists(self._favouritesFolder):
            os.makedirs(self._favouritesFolder, 0777)

        self._favouritesFile = os.path.join(self._favouritesFolder, 'favourites.cfg')
        if not os.path.exists(self._favouritesFile):
            data = [\
                '########################################################',
                '#                    Favourites                        #',
                '########################################################'
                ]
            fu.setFileContent(self._favouritesFile, '\n'.join(data))

        self._favouritesFoldersFolder = os.path.join(self._favouritesFolder, 'favfolders')
        if not os.path.exists(self._favouritesFoldersFolder):
            os.mkdir(self._favouritesFoldersFolder)


    def _createItem(self, title, m_type, icon, fanart, cfg, url):
        data = [\
            '\n',
            '########################################################',
            '# ' + title.upper(),
            '########################################################',
            'title=' + title,
            'type=' + m_type
            ]
        if icon:
            data.append('icon=' + icon)
        if fanart:
            data.append('fanart=' + fanart)
        if cfg:
            data.append('cfg=' + cfg)
        data.append('url=' + url)
        datastr = '\n'.join(data)
        return datastr

    
    def _createFavourite(self, item, title=None, icon=None, fanart=None):
        if not title:
            title = item.getInfo('title')

        m_type = item.getInfo('type')

        if not icon:
            icon = item.getInfo('icon')

        if not fanart:
            fanart = item.getInfo('fanart')

        cfg = item.getInfo('cfg')
        url = item.getInfo('url')

        return self._createItem(title, m_type, icon, fanart, cfg, url)


    def _getImage(self, heading):
        dialog = xbmcgui.Dialog()
        image = dialog.browse(1, heading, 'pictures', '.jpg|.png', True)
        return image


    def _getVirtualFoldersList(self):
        virtualFolders = os.listdir(self._favouritesFoldersFolder)
        return virtualFolders


    def _virtualFolderSelection(self, virtualFolders):
        menuItems = ['Favourites (root)']
        for vf in virtualFolders:
            name, ext = vf.split('.')
            menuItems.append(urllib.unquote_plus(name))

        select = xbmcgui.Dialog().select('Select destination', menuItems)
        if select == -1:
            return None
        elif select == 0:
            return self._favouritesFile
        else:
            return os.path.join(self._favouritesFoldersFolder, virtualFolders[select-1])


    def _isVirtualFolder(self, item):
        url = item.getInfo('url')
        return url and url.startswith("favfolders/")


    def addToFavourites(self, item, label=''):
        # if virtual folders exist
        virtualFolders = self._getVirtualFoldersList()
        targetFileForFavourite = None

        if len(virtualFolders) > 0:
            targetFileForFavourite = self._virtualFolderSelection(virtualFolders)
        else:
            targetFileForFavourite = self._favouritesFile

        if targetFileForFavourite and os.path.exists(targetFileForFavourite):
            fav = self._createFavourite(item, label)
            fu.appendFileContent(targetFileForFavourite, fav)


    def _removeVirtualFolder(self, item):
        url = item.getInfo('url')
        fullPath = os.path.join(self._favouritesFoldersFolder, url.split('/')[1])
        if os.path.exists(fullPath) and os.path.isfile(fullPath):
            os.remove(fullPath)


    def _findItem(self, item):
        title = re.escape(item.getInfo('title'))    
        cfg = item.getInfo('cfg')
        if cfg:
            cfg = re.escape(cfg)
        url = re.escape(item.getInfo('url'))
    
        regex = [\
            '',
            '########################################################',
            '# ' + title.upper(),
            '########################################################',
            'title=' + title,
            '.*?'
            ]
        
        if cfg:
            regex.append('cfg=' + cfg)
        regex.append('url=' + url)
        regex = '(' + '\s*'.join(regex) + ')'
        
        cfgFile = self._favouritesFile
        definedIn = item.getInfo('definedIn')
        if definedIn and definedIn.startswith('favfolders/'):
            cfgFile = os.path.join(self._favouritesFoldersFolder, definedIn.split('/')[1])

        if os.path.exists(cfgFile):
            data = fu.getFileContent(cfgFile)            
            matches = regexUtils.findall(data, regex)
            if matches and len(matches) > 0:
                fav = matches[0]
                return (cfgFile, data, fav)
        return None
    



    def changeLabel(self, item, newLabel):
        found = self._findItem(item)
        if found:
            [cfgFile, data, fav] = found
        
            # if it's a virtual folder, change target url too; check if target already exists; rename target
            # (helpful, if you want to edit files manually)

            if self._isVirtualFolder(item):
                url = item.getInfo('url')
                oldTargetFile = os.path.join(self._favouritesFoldersFolder, url.split('/')[1])
                # check if new target is valid
                newTargetFile = os.path.join(self._favouritesFoldersFolder, urllib.quote_plus(newLabel) + '.cfg')
                if os.path.exists(newTargetFile):
                    common.showInfo('Folder already exists')
                    return
                # rename target
                os.rename(oldTargetFile, newTargetFile)
                # update target url
                item.setInfo('url', 'favfolders/' + urllib.quote_plus(newLabel) + '.cfg')

            newfav = self._createFavourite(item, title=newLabel)
            new = data.replace(fav, enc.smart_unicode(newfav).encode('utf-8'))
            fu.setFileContent(cfgFile, new)


    def changeIcon(self, item, newIcon):
        found = self._findItem(item)
        if found:
            [cfgFile, data, fav] = found
            newfav = self._createFavourite(item, icon=newIcon)
            new = data.replace(fav, enc.smart_unicode(newfav).encode('utf-8'))
            fu.setFileContent(cfgFile, new)

    def changeFanart(self, item, newFanart):
        found = self._findItem(item)
        if found:
            [cfgFile, data, fav] = found
            newfav = self._createFavourite(item, fanart=newFanart)
            new = data.replace(fav, enc.smart_unicode(newfav).encode('utf-8'))
            fu.setFileContent(cfgFile, new)

    def moveToFolder(self, cfgFile, item, newCfgFile):
        found = self._findItem(item)
        if found:
            [cfgFile, data, fav] = found
            if os.path.exists(newCfgFile):
                new = data.replace(fav,'')
                fu.setFileContent(cfgFile, new)
                fu.appendFileContent(newCfgFile, fav)


    def editItem(self, item):
        menuItems = ["Change label", "Change icon", "Change fanart"]
        virtualFolders = self._getVirtualFoldersList()
        if len(virtualFolders) > 0 and not item.getInfo('url').startswith('favfolders/'):
            menuItems.append("Move to folder")
        select = xbmcgui.Dialog().select('Choose' , menuItems)
        if select == -1:
            return False

        cfgFile = self._favouritesFile
        definedIn = item.getInfo('definedIn')
        if definedIn and definedIn.startswith('favfolders/'):
            cfgFile = os.path.join(self._favouritesFoldersFolder, definedIn.split('/')[1])

        if select == 0:
            newLabel = getKeyboard(default = item.getInfo('title'), heading = 'Change label')
            if not newLabel or newLabel == "":
                return False
            self.changeLabel(item, newLabel)
        elif select == 1:
            newIcon = self._getImage('Change icon')
            if not newIcon:
                return False
            self.changeIcon(item, newIcon)
        elif select == 2:
            newFanart = self._getImage('Change fanart')
            if not newFanart:
                return False
            self.changeFanart(item, newFanart)
        elif select == 3:
            newCfgFile = self._virtualFolderSelection(virtualFolders)
            if not newCfgFile or cfgFile == newCfgFile:
                return False
            self.moveToFolder(cfgFile, item, newCfgFile)

        return True




    def addItem(self):
        menuItems = ["Add folder", "Add SportsDevil item", "Add xbmc favourite"]
        select = xbmcgui.Dialog().select('Choose', menuItems)
        if select == -1:
            return False
        elif select == 0:
            return self.addFolder()
        elif select == 1:
            common.showInfo('Please browse through SportsDevil and use \ncontext menu entry "Add to SportsDevil favourites"')
            xbmc.executebuiltin('Action(ParentFolder)')
            return False
        elif select == 2:
            return self.addXbmcFavourite()
        return True

    def removeItem(self, item):
        found = self._findItem(item)
        if found:
            [cfgFile, data, fav] = found
            new = data.replace(fav,'')
            fu.setFileContent(cfgFile, new)

            # delete virtual folder
            if self._isVirtualFolder(item):
                self._removeVirtualFolder(item)


    def addXbmcFavourite(self):
        fav_dir = xbmc.translatePath( 'special://profile/favourites.xml' )

        # Check if file exists
        if os.path.exists(fav_dir):
            favourites_xml = fu.getFileContent(fav_dir)
            doc = parseString(favourites_xml)
            xbmcFavs = doc.documentElement.getElementsByTagName('favourite')
            menuItems = []
            favItems = []
            for doc in xbmcFavs:
                title = doc.attributes['name'].nodeValue
                menuItems.append(title)
                try:
                    icon = doc.attributes ['thumb'].nodeValue
                except:
                    icon = ''
                url = doc.childNodes[0].nodeValue
                favItem = XbmcFavouriteItem(title, icon, url)
                favItems.append(favItem)

            select = xbmcgui.Dialog().select('Choose' , menuItems)
            if select == -1:
                return False
            else:
                item = favItems[select].convertToCListItem()
                self.addToFavourites(item)
                return True

        common.showInfo('No favourites found')
        return False

    def addFolder(self):
        if not (os.path.exists(self._favouritesFile) and os.path.exists(self._favouritesFoldersFolder)):
            return False
        
        # get name
        name = getKeyboard(default = '', heading = 'Set name')
        if not name or name == "":
            return False

        # create cfg
        virtualFolderFile = urllib.quote_plus(name) + '.cfg'
        physicalFolder = self._favouritesFoldersFolder
        virtualFolderPath = os.path.join(physicalFolder, virtualFolderFile)
        if os.path.exists(virtualFolderPath):
            common.showInfo('Folder already exists')
            return False
        data = [\
            '\n',
            '########################################################',
            '# ' + name.upper(),
            '########################################################'
            ]
        fu.setFileContent(virtualFolderPath, '\n'.join(data))

        # create link
        linkToFolder = self._createItem(name, 'rss', '', '', None, 'favfolders/' + virtualFolderFile)
        fu.appendFileContent(self._favouritesFile, linkToFolder)
        return True    

class XbmcFavouriteItem:
    def __init__(self, title, icon, url):
        self.title = title
        self.icon = icon
        self.url = url

    def convertToCListItem(self):
        item = CListItem()
        item.setInfo('title', self.title)
        item.setInfo('type', 'command')
        item.setInfo('icon', self.icon)
        item.setInfo('url', self.url)
        return item

