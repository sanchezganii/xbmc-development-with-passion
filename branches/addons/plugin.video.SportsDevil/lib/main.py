# -*- coding: latin-1 -*-

# Merge xSopcast and SportsDevil
#http://forum.xbmc.org/showthread.php?tid=100031&pid=1101338#pid1101338

#Freedocast fix
#http://forum.xbmc.org/showthread.php?tid=100597&pid=1094333#pid1094333

import os
from string import capitalize
import xbmcplugin
import sys
import xbmc, xbmcgui
import traceback
import urllib
import urllib2
import common

from entities.CList import CList
from entities.CListItem import CListItem


from downloader import Downloader
from favouritesManager import FavouritesManager

from dialogs.dialogProgress import DialogProgress

import utils.encodingUtils as enc
from utils import fileUtils as fu
from utils.regexUtils import parseText
from utils.xbmcUtils import getKeyboard, setSortMethodsForCurrentXBMCList


from parser import Parser

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


def codeUrl(item):
    params = ''

    for info_name in item.infos_names:
        if info_name != 'url' and info_name.find('.tmp') == -1:
            info_value = item[info_name]
            try:
                value = urllib.quote(enc.smart_unicode(info_value).encode('utf-8'))
            except:
                value = enc.smart_unicode(info_value)
            keyValPair = enc.smart_unicode(info_name) + ':' + value
            params += '&' + keyValPair
    try:
        url = enc.smart_unicode(urllib.quote_plus(item['url']))
    except:
        url = item['url']
    params += '&url:' + url

    return params.lstrip('&')


def decodeUrl(url):
    item = CListItem()
    if url.find('&') == -1:
        item['url'] = enc.clean_safe(url)
        return item

    keyValPairs = url.split('&')
    for keyValPair in keyValPairs:
        if keyValPair.find(':') > -1:
            key, val = keyValPair.split(':',1)
            item[key] = urllib.unquote_plus(val)
    return item



class Main:

    MAIN_MENU_FILE = 'mainMenu.cfg'



    def __init__(self):
        common.log('Initializing SportsDevil')

        if not os.path.exists(common.Paths.pluginDataDir):
            os.makedirs(common.Paths.pluginDataDir)

        self.curr_file = ''
        self.urlList = []
        self.extensionList = []
        self.selectionList = []
        self.currentlist = None
        self.favouritesManager = FavouritesManager(common.Paths.favouritesFolder)

        self.parser = Parser()

        self.handle = int(sys.argv[1])

        common.log('SportsDevil initialized')

        paramstring = sys.argv[2]
        self.run(paramstring)


    def playVideo(self, videoItem, isAutoplay = False):
        if not videoItem:
            return

        url = urllib.unquote_plus(videoItem['url'])

        title = videoItem['videoTitle']
        if not title:
            title = videoItem['title']
            if not title:
                title = 'unknown'

        try:
            icon = videoItem['icon']
        except:
            icon = common.Paths.defaultVideoIcon

        listitem = xbmcgui.ListItem(title, title, icon, icon)
        listitem.setInfo('video', {'Title':title})

        for video_info_name in videoItem.infos_names:
            try:
                listitem.setInfo(type = 'Video', infoLabels = {video_info_name: videoItem[video_info_name]})
            except:
                pass

        listitem.setPath(url)

        if not isAutoplay:
            xbmcplugin.setResolvedUrl(self.handle, True, listitem)
        else:
            xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(url, listitem)


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
            common.log('Video ' + url + ' downloaded to ' + downloaded_file)

        return downloaded_file


    def getVideos(self, lItem, dia = None, percent = 0, percentSpan = 100):
        allitems = []
        currentName = lItem['title']

        if lItem['type'].find('video') != -1:
            if dia:
                dia.update(percent + percentSpan, thirdline=currentName)
            allitems.append(lItem)
        else:
            tmpList = self.parser.parse(lItem)
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
        try:
            curr_phrase = fu.getFileContent(searchCache)
        except:
            curr_phrase = ''
        search_phrase = getKeyboard(default = curr_phrase, heading = common.translate(30102))
        if search_phrase == '':
            return None
        xbmc.sleep(10)
        fu.setFileContent(searchCache, search_phrase)

        return search_phrase

    def __endOfDirectory(self, succeeded=True):
        xbmcplugin.endOfDirectory(handle=self.handle, succeeded=succeeded, cacheToDisc=True)


    def parseView(self, url):

        lItem = decodeUrl(url)
        if lItem['type'] == 'search':
            search_phrase = self.getSearchPhrase()
            if not search_phrase:
                common.log("search canceled")
                self.__endOfDirectory(False)
                return None
            lItem['type'] = 'rss'
            lItem['url'] =  lItem['url'] % (urllib.quote_plus(search_phrase))

        url = lItem['url']

        tmpList = self.parser.parse(lItem)
        if not tmpList:
            common.showError("Parsing failed")
            self.__endOfDirectory(False)
            return None

        # Remove duplicates
        urls = []
        for i in range(len(tmpList.items)-1,-1,-1):
            item = tmpList.items[i]
            tmpUrl = item['url']
            tmpCfg = item['cfg']
            if not tmpCfg:
                tmpCfg = ''
            if not urls.__contains__(tmpUrl + '|' + tmpCfg):
                urls.append(tmpUrl + '|' + tmpCfg)
            else:
                tmpList.items.remove(item)

        # SHOW ITEMS IN GUI
        # if it's the main menu, add folder 'Favourites'
        if url == self.MAIN_MENU_FILE:
            # Add Favourites
            tmp = CListItem()
            tmp['title'] = 'Favourites'
            tmp['type'] = 'rss'
            tmp['url'] = str(common.Paths.favouritesFile)
            tmpList.items.insert(0,tmp)

        # if it's the favourites menu, add item 'Add item'
        elif url == common.Paths.favouritesFile:
            tmp = CListItem()
            tmp['title'] = 'Add item...'
            tmp['type'] = 'command'
            action = 'RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(Mode.ADDITEM) + '&url=')
            tmp['url'] = action
            tmpList.items.append(tmp)

        count = len(tmpList.items)
        if count > 0 and not (common.getSetting('autoplay') == 'true' and count == 1 and len(tmpList.getVideos()) == 1):
            # sort methods
            sortKeys = tmpList.sort.split('|')
            setSortMethodsForCurrentXBMCList(self.handle, sortKeys)

            # Add items to XBMC list
            for m in tmpList.items:
                self.addListItem(m, len(tmpList.items))

            self.__endOfDirectory()
            common.log('End of directory')
        else:
            self.__endOfDirectory(False)
        return tmpList


    def createXBMCListItem(self, item):
        liz = None
        title = enc.clean_safe(item['title'])

        icon = item['icon']
        if icon:
            liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
        else:
            liz = xbmcgui.ListItem(title)

        fanart = item['fanart']
        if not fanart:
            fanart = common.Paths.pluginFanart
        liz.setProperty('fanart_image', fanart)

        for video_info_name in item.infos_names:
            if video_info_name.find('context.') != -1:
                try:
                    cItem = item
                    cItem['type'] = 'rss'
                    cItem['url'] = item[video_info_name]
                    action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?url=' + codeUrl(cItem))
                    liz.addContextMenuItems([(video_info_name[video_info_name.find('.') + 1:], action)])
                except:
                    pass
            if video_info_name not in ['url', 'title', 'icon', 'type', 'extension'] and video_info_name.find('.tmp') == -1 and video_info_name.find('.append') == -1 and video_info_name.find('context.') == -1:
                try:
                    info_value = item[video_info_name]
                    infoLabels = {}
                    if video_info_name.find('.int') != -1:
                        infoLabels = {capitalize(video_info_name[:video_info_name.find('.int')]): int(info_value)}
                    elif video_info_name.find('.tmp') != -1:
                        infoLabels = {capitalize(video_info_name[:video_info_name.find('.tmp')]): info_value}
                    else:
                        infoLabels = {capitalize(video_info_name): info_value}
                    liz.setInfo(type = 'Video', infoLabels = infoLabels)
                except:
                    pass
        return liz





    def addListItem(self, lItem, totalItems):
        def createContextMenuItem(label, mode, codedItem):
            action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(mode) + '&url=' + codedItem)
            return (label, action)

        contextMenuItems = []
        definedIn = lItem['definedIn']

        codedItem = codeUrl(lItem)

        # Jump to MainMenu
#        if definedIn and definedIn != self.MAIN_MENU_FILE:
#            action = 'Container.Update(%s, replace)' % (sys.argv[0])
#            contextMenuItem = ('Jump to Mainmenu', action)
#            contextMenuItems.append(contextMenuItem)



        # Queue
        if definedIn:
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
        if m_type == 'video':
            u = sys.argv[0] + '?mode=' + str(Mode.PLAY) + '&url=' + codedItem
            if lItem['IsDownloadable']:
                contextMenuItem = createContextMenuItem('Download', Mode.DOWNLOAD, codedItem)
                contextMenuItems.append(contextMenuItem)
            liz.setProperty('IsPlayable','true')
            isFolder = False
        elif m_type.find('command') > -1:
            u = sys.argv[0] + '?mode=' + str(Mode.EXECUTE) + '&url=' + codedItem
            isFolder = False
        else:
            u = sys.argv[0] + '?mode=' + str(Mode.VIEW) + '&url=' + codedItem
            isFolder = True

        liz.addContextMenuItems(contextMenuItems)
        xbmcplugin.addDirectoryItem(handle = self.handle, url = u, listitem = liz, isFolder = isFolder, totalItems = totalItems)


    def clearCache(self):
        cacheDir = common.Paths.cacheDir
        if not os.path.exists(cacheDir):
            common.log('Creating cache directory ' + str(cacheDir))
            os.mkdir(cacheDir)
            common.log('Cache directory created')
        else:
            common.log('Purging cache directory')
            for root, dirs, files in os.walk(cacheDir , topdown = False):
                for name in files:
                    if not name == 'cookies.lwp':
                        os.remove(os.path.join(root, name))
            common.log('Cache directory purged')


    def run(self, paramstring):
        common.log('SportsDevil running')
        try:
            # Main Menu
            if len(paramstring) <= 2:
                # Set fanart
                xbmcplugin.setPluginFanart(self.handle, common.Paths.pluginFanart)

                # Clear cache
                self.clearCache()

                # Show Main Menu
                tmpList = self.parseView(self.MAIN_MENU_FILE)
                if tmpList:
                    self.currentlist = tmpList
                    self.curr_file = tmpList.cfg

            else:
                params = paramstring
                mode, codedItem = params.split('&',1)
                mode = int(mode.split('=')[1])

                codedItem = codedItem[4:]
                item = decodeUrl(codedItem)

                # switch(mode)
                if mode == Mode.VIEW:
                    tmpList = self.parseView(codedItem)
                    if tmpList:
                        self.currentlist = tmpList
                        self.curr_file = tmpList.cfg
                        count = len(self.currentlist.items)
                        if count == 0:
                            common.showInfo('No stream available')
                        elif count == 1:
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
                            uc = sys.argv[0] + '?mode=' + str(Mode.PLAY) + '&url=' + codeUrl(it)
                            item.setProperty('IsPlayable', 'true')
                            item.setProperty('IsFolder','false')
                            xbmc.PlayList(1).add(uc, item)
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





