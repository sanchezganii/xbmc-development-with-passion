# -*- coding: latin-1 -*-

# Merge xSopcast and SportsDevil
#http://forum.xbmc.org/showthread.php?tid=100031&pid=1101338#pid1101338

#Freedocast fix
#http://forum.xbmc.org/showthread.php?tid=100597&pid=1094333#pid1094333

import os
import xbmcplugin
import sys
import xbmc, xbmcgui
import traceback
import urllib

import common

import utils.encodingUtils as enc
from utils import fileUtils as fu
from utils.regexUtils import parseText
from utils.xbmcUtils import getKeyboard, setSortMethodsForCurrentXBMCList
from dialogs.dialogProgress import DialogProgress

from parser import Parser, ParsingResult
from downloader import Downloader
from favouritesManager import FavouritesManager

import entities.CListItem as ListItem
from utils.fileUtils import getFileContent, setFileContent


class Mode:
    VIEW = 1
    PLAY = 2
    QUEUE = 3
    DOWNLOAD = 4
    EXECUTE = 5
    ADDTOFAVOURITES = 6
    REMOVEFROMFAVOURITES = 7
    EDITITEM = 8
    ADDITEM = 9





class Main:

    MAIN_MENU_FILE = 'mainMenu.cfg'


    def __init__(self):
        self.base = sys.argv[0]
        self.handle = int(sys.argv[1])

        if not os.path.exists(common.Paths.pluginDataDir):
            os.makedirs(common.Paths.pluginDataDir, 0777)

        self.favouritesManager = FavouritesManager(common.Paths.favouritesFolder)

        if not os.path.exists(common.Paths.customModulesDir):
            os.makedirs(common.Paths.customModulesDir, 0777)

        self.parser = Parser()
        self.currentlist = None

        common.log('SportsDevil initialized')

        paramstring = urllib.unquote_plus(sys.argv[2])
        self.run(paramstring)

    def getPlayerType(self):
        sPlayerType = common.getSetting('playerType')

        if (sPlayerType == '0'):
            return xbmc.PLAYER_CORE_AUTO

        if (sPlayerType == '1'):
            return xbmc.PLAYER_CORE_MPLAYER

        if (sPlayerType == '2'):
            return xbmc.PLAYER_CORE_DVDPLAYER        
        
        # PLAYER_CORE_AMLPLAYER
        if (sPlayerType == '3'):
            return 5

    def playVideo(self, videoItem, isAutoplay = False):
        if not videoItem:
            return

        listitem = self.createXBMCListItem(videoItem)

        title = videoItem['videoTitle']
        if title:
            listitem.setInfo('video', {'title': enc.clean_safe(title)})

        if not isAutoplay:
            xbmcplugin.setResolvedUrl(self.handle, True, listitem)
        else:
            url = urllib.unquote_plus(videoItem['url'])
            xbmc.Player(self.getPlayerType()).play(url, listitem)


    def downloadVideo(self, url, title):
        common.log('Trying to download video ' + str(url))

        # check url
        if url.startswith('plugin'):
            common.log('Video is not downloadable')
            return None

        path = common.getSetting('download_path')
        if not path:
            path = common.browseFolders(common.translate(30017))
            common.setSetting('download_path', path)

        title = getKeyboard(default = fu.cleanFilename(title),heading='SportsDevil')
        if title == None or title == '':
            return None

        downloader = Downloader()
        downloaded_file = downloader.downloadMovie(url, path,  fu.cleanFilename(title), '.flv')

        if downloaded_file == None:
            common.log ('Download cancelled')
        else:
            common.log('Video ' + url + " downloaded to '" + downloaded_file + "'")

        return downloaded_file


    def getVideos(self, lItem, dia = None, percent = 0, percentSpan = 100):
        allitems = []
        currentName = lItem['title']

        if lItem['type'].find('video') != -1:
            if dia:
                dia.update(percent + percentSpan, thirdline=currentName)
            allitems.append(lItem)
        else:
            tmpList = self.parser.parse(lItem).list
            if tmpList and len(tmpList.items) > 0:
                inc = percentSpan/len(tmpList.items)
                dia.update(percent, secondline=currentName, thirdline=' ')
                for item in tmpList.items:
                    if dia.isCanceled():
                        break
                    children = self.getVideos(item, dia, percent, inc)
                    if children:
                        allitems.extend(children)
                    percent += inc

        return allitems


    def getSearchPhrase(self):
        searchCache = os.path.join(common.Paths.cacheDir, 'search')
        default_phrase = fu.getFileContent(searchCache)
        if not default_phrase:
            default_phrase = ''

        search_phrase = common.showOSK(default_phrase, common.translate(30102))
        if search_phrase == '':
            return None
        xbmc.sleep(10)
        fu.setFileContent(searchCache, search_phrase)

        return search_phrase


    def parseView(self, url):

        def endOfDirectory(succeeded=True):
            xbmcplugin.endOfDirectory(handle=self.handle, succeeded=succeeded, cacheToDisc=True)

        lItem = ListItem.fromUrl(url)

        if lItem['type'] == 'search':
            search_phrase = self.getSearchPhrase()
            if not search_phrase:
                common.log("search canceled")
                endOfDirectory(False)
                return None
            else:
                lItem['type'] = 'rss'
                lItem['url'] =  lItem['url'] % (urllib.quote_plus(search_phrase))

        url = lItem['url']

        result = self.parser.parse(lItem)
        if result.code == ParsingResult.Code.SUCCESS:
            tmpList = result.list
        else:
            if result.code == ParsingResult.Code.CFGFILE_NOT_FOUND:
                common.showError("Cfg file not found")
            elif result.code == ParsingResult.Code.CFGSYNTAX_INVALID:
                common.showError("Cfg syntax invalid")
            elif result.code == ParsingResult.Code.WEBREQUEST_FAILED:
                common.showError("Web request failed")

            endOfDirectory(False)
            return None

        # if it's the main menu, add folder 'Favourites'
        if url == self.MAIN_MENU_FILE:
            # Add Favourites
            tmp = ListItem.create()
            tmp['title'] = 'Favourites'
            tmp['type'] = 'rss'
            tmp['icon'] = os.path.join(common.Paths.imgDir, 'bookmark.png')
            tmp['url'] = str(common.Paths.favouritesFile)
            tmpList.items.insert(0, tmp)
            
            customModules = self.getCustomModules()
            if customModules:
                tmp = ListItem.create()
                tmp['title'] = 'Custom Modules'
                tmp['type'] = 'rss'
                tmp['url'] = os.path.join(common.Paths.customModulesDir, 'custom.cfg')
                tmpList.items.insert(0, tmp)

        # if it's the favourites menu, add item 'Add item'
        elif url == common.Paths.favouritesFile:
            tmp = ListItem.create()
            tmp['title'] = 'Add item...'
            tmp['type'] = 'command'
            tmp['icon'] = os.path.join(common.Paths.imgDir, 'bookmark_add.png')
            action = 'RunPlugin(%s)' % (self.base + '?mode=' + str(Mode.ADDITEM) + '&url=')
            tmp['url'] = action
            tmpList.items.append(tmp)


        # Create menu or play, if it's a single video and autoplay is enabled
        proceed = False

        count = len(tmpList.items)
        if count == 0:
            common.showInfo('No stream available')
        elif count > 0 and not (common.getSetting('autoplay') == 'true' and count == 1 and len(tmpList.getVideos()) == 1):
            # sort methods
            sortKeys = tmpList.sort.split('|')
            setSortMethodsForCurrentXBMCList(self.handle, sortKeys)

            # Add items to XBMC list
            for m in tmpList.items:
                self.addListItem(m, len(tmpList.items))

            proceed = True

        endOfDirectory(proceed)
        common.log('End of directory')
        return tmpList


    def getCustomModules(self):
        customDir = common.Paths.customModulesDir
        txt = ''
        for root, dirs, files in os.walk(customDir , topdown = False):
            for name in files:
                if name.endswith('.module'):
                    txt += getFileContent(os.path.join(root, name)) + '\n'
        if txt != '':
            setFileContent(os.path.join(common.Paths.customModulesDir, 'custom.cfg'), txt)
            return True
        else:
            return False

    def createXBMCListItem(self, item):
        title = enc.clean_safe(item['title'])

        m_type = item['type']

        icon = item['icon']
        if not icon:
            if m_type == 'video':
                icon = common.Paths.defaultVideoIcon
            else:
                icon = common.Paths.defaultCategoryIcon

        liz = xbmcgui.ListItem(title, title, iconImage=icon, thumbnailImage=icon)

        fanart = item['fanart']
        if not fanart:
            fanart = common.Paths.pluginFanart
        liz.setProperty('fanart_image', fanart)

        """
        General Values that apply to all types:
            count         : integer (12) - can be used to store an id for later, or for sorting purposes
            size          : long (1024) - size in bytes
            date          : string (%d.%m.%Y / 01.01.2009) - file date

        Video Values:
            genre         : string (Comedy)
            year          : integer (2009)
            episode       : integer (4)
            season        : integer (1)
            top250        : integer (192)
            tracknumber   : integer (3)
            rating        : float (6.4) - range is 0..10
            watched       : depreciated - use playcount instead
            playcount     : integer (2) - number of times this item has been played
            overlay       : integer (2) - range is 0..8.  See GUIListItem.h for values
            cast          : list (Michal C. Hall)
            castandrole   : list (Michael C. Hall|Dexter)
            director      : string (Dagur Kari)
            mpaa          : string (PG-13)
            plot          : string (Long Description)
            plotoutline   : string (Short Description)
            title         : string (Big Fan)
            originaltitle : string (Big Fan)
            duration      : string (3:18)
            studio        : string (Warner Bros.)
            tagline       : string (An awesome movie) - short description of movie
            writer        : string (Robert D. Siegel)
            tvshowtitle   : string (Heroes)
            premiered     : string (2005-03-04)
            status        : string (Continuing) - status of a TVshow
            code          : string (tt0110293) - IMDb code
            aired         : string (2008-12-07)
            credits       : string (Andy Kaufman) - writing credits
            lastplayed    : string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)
            album         : string (The Joshua Tree)
            votes         : string (12345 votes)
            trailer       : string (/home/user/trailer.avi)
        """

        infoLabels = {}
        for video_info_name in item.infos_names:
            infoLabels[video_info_name] = enc.clean_safe(item[video_info_name])
        infoLabels['title'] = title

        liz.setInfo('video', infoLabels)

        url = urllib.unquote_plus(item['url'])
        liz.setPath(url)

        if m_type == 'video':
            liz.setProperty('IsPlayable','true')

        return liz


    def addListItem(self, lItem, totalItems):
        def createContextMenuItem(label, mode, codedItem):
            action = 'XBMC.RunPlugin(%s)' % (self.base + '?mode=' + str(mode) + '&url=' + codedItem)
            return (label, action)

        contextMenuItems = []
        definedIn = lItem['definedIn']

        codedItem = urllib.quote_plus(ListItem.toUrl(lItem))

        # Jump to MainMenu
#        if definedIn and definedIn != self.MAIN_MENU_FILE:
#            action = 'Container.Update(%s, replace)' % (self.base)
#            contextMenuItem = ('Jump to Mainmenu', action)
#            contextMenuItems.append(contextMenuItem)

        if definedIn:
            # Queue
            contextMenuItem = createContextMenuItem('Queue', Mode.QUEUE, codedItem)
            contextMenuItems.append(contextMenuItem)

            if definedIn.endswith('favourites.cfg') or definedIn.startswith("favfolders/"):
                # Remove from favourites
                contextMenuItem = createContextMenuItem('Remove', Mode.REMOVEFROMFAVOURITES, codedItem)
                contextMenuItems.append(contextMenuItem)

                # Edit label
                contextMenuItem = createContextMenuItem('Edit', Mode.EDITITEM, codedItem)
                contextMenuItems.append(contextMenuItem)

            elif lItem['title'] != "Favourites":
                    # Add to favourites
                    contextMenuItem = createContextMenuItem('Add to SportsDevil favourites', Mode.ADDTOFAVOURITES, codedItem)
                    contextMenuItems.append(contextMenuItem)

        liz = self.createXBMCListItem(lItem)

        m_type = lItem['type']
        if not m_type:
            m_type = 'rss'
        
        if m_type == 'video':
            u = self.base + '?mode=' + str(Mode.PLAY) + '&url=' + codedItem
            if lItem['IsDownloadable']:
                contextMenuItem = createContextMenuItem('Download', Mode.DOWNLOAD, codedItem)
                contextMenuItems.append(contextMenuItem)
            isFolder = False
        elif m_type.find('command') > -1:
            u = self.base + '?mode=' + str(Mode.EXECUTE) + '&url=' + codedItem
            isFolder = False
        else:
            u = self.base + '?mode=' + str(Mode.VIEW) + '&url=' + codedItem
            isFolder = True

        liz.addContextMenuItems(contextMenuItems)
        xbmcplugin.addDirectoryItem(handle = self.handle, url = u, listitem = liz, isFolder = isFolder, totalItems = totalItems)


    def clearCache(self):
        cacheDir = common.Paths.cacheDir
        if not os.path.exists(cacheDir):
            os.mkdir(cacheDir, 0777)
            common.log('Cache directory created' + str(cacheDir))
        else:
            for root, dirs, files in os.walk(cacheDir , topdown = False):
                for name in files:
                    os.remove(os.path.join(root, name))
            common.log('Cache directory purged')


    def run(self, paramstring):
        common.log('SportsDevil running')
        try:
            # Main Menu
            if len(paramstring) <= 2:
                xbmcplugin.setPluginFanart(self.handle, common.Paths.pluginFanart)
                self.clearCache()
                tmpList = self.parseView(self.MAIN_MENU_FILE)
                if tmpList:
                    self.currentlist = tmpList

            else:
                params = paramstring
                mode, codedItem = params.split('&',1)
                mode = int(mode.split('=')[1])

                codedItem = codedItem[4:]
                item = ListItem.fromUrl(codedItem)

                # switch(mode)
                if mode == Mode.VIEW:
                    tmpList = self.parseView(codedItem)
                    if tmpList:
                        self.currentlist = tmpList
                        count = len(self.currentlist.items)
                        if count == 1:
                            # Autoplay single video
                            autoplayEnabled = common.getSetting('autoplay') == 'true'
                            if autoplayEnabled:
                                videos = self.currentlist.getVideos()
                                if len(videos) == 1:
                                    self.playVideo(videos[0], True)


                elif mode == Mode.ADDITEM:
                    if self.favouritesManager.addItem():
                        xbmc.executebuiltin('Container.Refresh()')

                elif mode in [Mode.ADDTOFAVOURITES, Mode.REMOVEFROMFAVOURITES, Mode.EDITITEM]:

                    if mode == Mode.ADDTOFAVOURITES:
                        self.favouritesManager.addToFavourites(item)
                    elif mode == Mode.REMOVEFROMFAVOURITES:
                        self.favouritesManager.removeItem(item)
                        xbmc.executebuiltin('Container.Refresh()')
                    elif mode == Mode.EDITITEM:
                        if self.favouritesManager.editItem(item):
                            xbmc.executebuiltin('Container.Refresh()')

                elif mode == Mode.EXECUTE:
                    url = item['url']
                    if url.find('(') > -1:
                        xbmcCommand = parseText(url,'([^\(]*).*')
                        if xbmcCommand.lower() in ['activatewindow', 'runscript', 'runplugin', 'playmedia']:
                            if xbmcCommand.lower() == 'activatewindow':
                                params = parseText(url, '.*\(\s*(.+?)\s*\).*').split(',')
                                for i in range(len(params)-1,-1,-1):
                                    p = params[i]
                                    if p == 'return':
                                        params.remove(p)
                                path = enc.unescape(params[len(params)-1])
                                xbmc.executebuiltin('Container.Update(' + path + ')')
                                return
                            xbmc.executebuiltin(enc.unescape(url))

                elif mode == Mode.PLAY:
                    self.playVideo(item)

                elif mode == Mode.QUEUE:
                    dia = DialogProgress()
                    dia.create('SportsDevil', 'Get videos...' + item['title'])
                    dia.update(0)

                    items = self.getVideos(item, dia)
                    if items:
                        for it in items:
                            item = self.createXBMCListItem(it)
                            uc = self.base + '?mode=' + str(Mode.PLAY) + '&url=' + ListItem.toUrl(it)
                            xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(uc, item)
                        resultLen = len(items)
                        msg = 'Queued ' + str(resultLen) + ' video'
                        if resultLen > 1:
                            msg += 's'
                        dia.update(100, msg)
                        xbmc.sleep(500)
                        dia.update(100, msg,' ',' ')
                    else:
                        dia.update(0, 'No items found',' ')

                    xbmc.sleep(700)
                    dia.close()

                elif mode == Mode.DOWNLOAD:
                    url = urllib.unquote(item['url'])
                    title = item['title']
                    self.downloadVideo(url, title)

        except Exception, e:
            if common.enable_debug:
                traceback.print_exc(file = sys.stdout)
            common.showError('Error running SportsDevil.\n\nReason:\n' + str(e))


