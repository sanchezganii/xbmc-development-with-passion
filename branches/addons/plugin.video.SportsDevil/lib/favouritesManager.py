# -*- coding: latin-1 -*-

from string import *
from helpers import *

import sys, os.path
import string

import xbmc, xbmcgui

from CListItem import CListItem
from xml.dom.minidom import parseString

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
            setFileContent(self._favouritesFile, '\n'.join(data))

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

        if targetFileForFavourite and os.path.exists(targetFileForFavourite):
            fav = self._createFavourite(item, label)
            appendFileContent(targetFileForFavourite, fav)


    def _removeVirtualFolder(self, item):
        url = item.getInfo('url')
        fullPath = os.path.join(self._favouritesFoldersFolder, url.split('/')[1])
        if os.path.exists(fullPath) and os.path.isfile(fullPath):
            os.remove(fullPath)


    def removeItem(self, item):
        cfgFile = self._favouritesFile
        definedIn = item.getInfo('definedIn')
        if definedIn and definedIn.startswith('favfolders/'):
            cfgFile = os.path.join(self._favouritesFoldersFolder, definedIn.split('/')[1])

        if os.path.exists(cfgFile):
            fav = self._createFavourite(item)
            old = getFileContent(cfgFile)
            new = old.replace(smart_unicode(fav).encode('utf-8'),'')
            setFileContent(cfgFile, new)

            # delete virtual folder
            if self._isVirtualFolder(item):
                self._removeVirtualFolder(item)


    def changeLabel(self, cfgFile, item, newLabel):
        if os.path.exists(cfgFile):
            oldfav = self._createFavourite(item)
            old = getFileContent(cfgFile)

            # if it's a virtual folder, change target url too; check if target already exists; rename target
            # (helpful, if you want to edit files manually)

            if self._isVirtualFolder(item):
                url = item.getInfo('url')
                oldTargetFile = os.path.join(self._favouritesFoldersFolder, url.split('/')[1])
                # check if new target is valid
                newTargetFile = os.path.join(self._favouritesFoldersFolder, urllib.quote_plus(newLabel) + '.cfg')
                if os.path.exists(newTargetFile):
                    showDialog('Folder already exists')
                    return
                # rename target
                os.rename(oldTargetFile, newTargetFile)
                # update target url
                item.setInfo('url', 'favfolders/' + urllib.quote_plus(newLabel) + '.cfg')

            newfav = self._createFavourite(item, title=newLabel)
            new = old.replace(smart_unicode(oldfav).encode('utf-8'), smart_unicode(newfav).encode('utf-8'))
            setFileContent(cfgFile, new)


    def changeIcon(self, cfgFile, item, newIcon):
        if os.path.exists(cfgFile):
            fav = self._createFavourite(item)
            newfav = self._createFavourite(item, icon=newIcon)
            old = getFileContent(cfgFile)
            new = old.replace(smart_unicode(fav).encode('utf-8'), smart_unicode(newfav).encode('utf-8'))
            setFileContent(cfgFile, new)

    def changeFanart(self, cfgFile, item, newFanart):
        if os.path.exists(cfgFile):
            fav = self._createFavourite(item)
            newfav = self._createFavourite(item, fanart=newFanart)
            old = getFileContent(cfgFile)
            new = old.replace(smart_unicode(fav).encode('utf-8'), smart_unicode(newfav).encode('utf-8'))
            setFileContent(cfgFile, new)


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
            self.changeLabel(cfgFile, item, newLabel)
        elif select == 1:
            newIcon = self._getImage('Change icon')
            if not newIcon:
                return False
            self.changeIcon(cfgFile, item, newIcon)
        elif select == 2:
            newFanart = self._getImage('Change fanart')
            if not newFanart:
                return False
            self.changeFanart(cfgFile, item, newFanart)
        elif select == 3:
            newCfgFile = self._virtualFolderSelection(virtualFolders)
            if not newCfgFile or cfgFile == newCfgFile:
                return False
            self.moveToFolder(cfgFile, item, newCfgFile)

        return True


    def moveToFolder(self, cfgFile, item, newCfgFile):
        if os.path.exists(cfgFile) and os.path.exists(newCfgFile):
            fav = self._createFavourite(item)
            old = getFileContent(cfgFile)
            new = old.replace(smart_unicode(fav).encode('utf-8'),'')
            setFileContent(cfgFile, new)
            appendFileContent(newCfgFile, fav)


    def addItem(self):
        menuItems = ["Add folder", "Add SportsDevil item", "Add xbmc favourite"]
        select = xbmcgui.Dialog().select('Choose', menuItems)
        if select == -1:
            return False
        elif select == 0:
            self.addFolder()
        elif select == 1:
            showDialog('Please browse through SportsDevil and use \ncontext menu entry "Add to SportsDevil favourites"')
            xbmc.executebuiltin('Action(ParentFolder)')
        elif select == 2:
            self.addXbmcFavourite()
        return True


    def addXbmcFavourite(self):
        fav_dir = xbmc.translatePath( 'special://profile/favourites.xml' )

        # Check if file exists
        if os.path.exists(fav_dir):
            favourites_xml = getFileContent(fav_dir)
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

        showDialog('No favourites found')
        return False

    def addFolder(self):
        if os.path.exists(self._favouritesFile) and os.path.exists(self._favouritesFoldersFolder):
            # get name
            name = getKeyboard(default = '', heading = 'Set name')
            if not name or name == "":
                return False

            # create cfg
            virtualFolderFile = urllib.quote_plus(name) + '.cfg'
            physicalFolder = self._favouritesFoldersFolder
            virtualFolderPath = os.path.join(physicalFolder, virtualFolderFile)
            if os.path.exists(virtualFolderPath):
                showDialog('Folder already exists')
                return
            data = [\
                '\n',
                '########################################################',
                '# ' + name.upper(),
                '########################################################'
                ]
            setFileContent(virtualFolderPath, '\n'.join(data))

            # create link
            linkToFolder = self._createItem(name, 'rss', '', '', None, 'favfolders/' + virtualFolderFile)
            appendFileContent(self._favouritesFile, linkToFolder)


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

