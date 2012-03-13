# -*- coding: latin-1 -*-

from string import *
import xbmcplugin, xbmcaddon
import sys, os.path
import urllib,urllib2, filecmp
import re, random, string, shutil
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import cookielib, htmlentitydefs

from globals import *
from CListItem import CListItem
from sportsdevil import *
from helpers import *
from downloader import Downloader
from favouritesManager import FavouritesManager
from dialogProgress import DialogProgress

enable_debug = True
__settings__ = xbmcaddon.Addon(id='plugin.video.SportsDevil')
__language__ = __settings__.getLocalizedString



class Main:

    def __init__(self):
        log('Initializing SportsDevil')
        if not os.path.exists(pluginDataDir):
            os.makedirs(pluginDataDir)
        self.pDialog = None
        self.curr_file = ''
        self.urlList = []
        self.extensionList = []
        self.selectionList = []
        self.videoExtension = '.flv'
        self.currentlist = CItemsList()
        self.favouritesManager = FavouritesManager(favouritesFolder)
        log('SportsDevil initialized')
        self.run()


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
            icon = os.path.join(imgDir, 'video.png')

##        try:
##            urllib.urlretrieve(icon, os.path.join(cacheDir, 'thumb.tbn'))
##            icon = os.path.join(cacheDir, 'thumb.tbn')
##        except:
##            if enable_debug:
##                traceback.print_exc(file = sys.stdout)
##            icon = os.path.join(imgDir, 'video.png')

        listitem = xbmcgui.ListItem(title, title, icon, icon)
        listitem.setInfo('video', {'Title':title})

        for video_info_name in videoItem.infos_names:
            try:
                listitem.setInfo(type = 'Video', infoLabels = {video_info_name: videoItem[video_info_name]})
            except:
                pass

        # download video and take this file for playback
        if self.currentlist.skill.find('nodownload') == -1:
            downloaded_file = None
            if __settings__.getSetting('download') == 'true':
                downloaded_file = self.downloadVideo(urllib.unquote(url), title)
            elif __settings__.getSetting('download') == 'false' and __settings__.getSetting('download_ask') == 'true':
                dia = xbmcgui.Dialog()
                if dia.yesno('', __language__(30052)):
                    downloaded_file = self.downloadVideo(urllib.unquote(url), title)
            if downloaded_file:
                url = downloaded_file

        listitem.setPath(url)
        if not isAutoplay:
            xbmcplugin.setResolvedUrl(self.handle, True, listitem)
        else:
            xbmc.Player(0).play(url,listitem)


    def downloadVideo(self, url, title):
        log('Trying to download video ' + str(url))

        # check url
        if url.startswith('plugin'):
            log('Video is not downloadable')
            return None

        path = __settings__.getSetting('download_path')
        if not path:
            path = xbmcgui.Dialog().browse(0, __language__(30017),'files', '', False, False)
            __settings__.setSetting(id='download_path', value=path)

        title = getKeyboard(default=first_clean_filename(title),heading='SportsDevil')
        if title == None or title == '':
            return None

        downloader = Downloader(__language__)
        file = downloader.downloadMovie(url, path, first_clean_filename(title), self.videoExtension)

        if file == None:
            log ('Download cancelled')
        else:
            log('Video ' + url + ' downloaded to ' + file)

        return file


    def getVideos(self, lItem, dia = None, percent = 0, percentSpan = 100):
        allitems = []
        currentName = lItem['title']

        if lItem['type'].find('video') != -1:
            if dia:
                dia.update(percent + percentSpan, thirdline=currentName)
            allitems.append(lItem)
        else:
            url = lItem['url']
            tmpList = CItemsList()

            # Load cfg file
            cfg = lItem['cfg']
            if cfg:
                result = tmpList.loadLocal(cfg, lItem = lItem)

            # Load url and parse
            if url.endswith('.cfg') or url.endswith('.list'):
                result = tmpList.loadLocal(url, lItem = lItem)
            else:
                result = tmpList.loadRemote(url, False, lItem = lItem)

            if len(tmpList.items) == 0:
                # try to find redirect
                red = findRedirect(url)
                if red != url:
                    setCurrentUrl(red)
                    lItem['url'] = red
                    children = self.getVideos(lItem, dia, percent, percentSpan)
                    if children:
                        allitems.extend(children)
            else:
                inc = percentSpan/len(tmpList.items)
                dia.update(percent, secondline=currentName, thirdline=' ')
                for item in tmpList.items:
                    children = self.getVideos(item, dia, percent, inc)
                    if children:
                        allitems.extend(children)
                    percent += inc

        return allitems


    def parseView(self, url):
        lItem = self.currentlist.decodeUrl(url)
        url = lItem['url']
        ext = getFileExtension(url)

        if ext == 'cfg' or ext == 'list':
            result = self.currentlist.loadLocal(url, lItem = lItem)
            self.curr_file = url
        else:
            result = self.currentlist.loadRemote(url, lItem = lItem)

        if result == -1:
            return result

        # if there is something to scrape at all
        if not (ext in ['cfg', 'list'] and self.currentlist.start == ''):
            i = 0
            maxIt = 3
            condition = True
            startUrl = getLastUrl()
            while condition:
                # Find Redirect automatically
                if len(self.currentlist.items) == 0:
                    red = findRedirect(startUrl)
                    if startUrl == red:
                        log('No redirect found')
                        condition = False
                    else:
                        log('Redirect: ' + red)
                        try:
                            tmpCfg = lItem['cfg']
                            if tmpCfg:
                                result = self.currentlist.loadLocal(tmpCfg, lItem = lItem)
                            else:
                                tmpCfg = getCurrentCfg()
                            self.currentlist.rules = []
                        except:
                            traceback.print_exc(file = sys.stdout)
                        result = self.currentlist.loadRemote(red,lItem = lItem)
                        if result == -1:
                            break
                        log(str(len(self.currentlist.items)) + ' items ' + tmpCfg + ' -> ' + red)
                        startUrl = red

                # Autoselect single folder
                tmpItem = self.autoselect(self.currentlist)
                if tmpItem:
                    lItem = tmpItem
                    startUrl = lItem['url']

                condition = condition and (len(self.currentlist.items) == 0 and i < maxIt)
                i += 1


            # Remove double entries
            urls = []
            for i in range(len(self.currentlist.items)-1,-1,-1):
                item = self.currentlist.items[i]
                tmpUrl = item['url']
                tmpCfg = item['cfg']
                if not tmpCfg:
                    tmpCfg = ''
                if not urls.__contains__(tmpUrl + '|' + tmpCfg):
                    urls.append(tmpUrl + '|' + tmpCfg)
                else:
                    self.currentlist.items.remove(item)

            # Autoplay single Video
            if __settings__.getSetting('autoplay') == 'true' and len(self.currentlist.items) == 1 and self.currentlist.videoCount() == 1:
                videoItem = self.currentlist.getVideo()
                #u = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(Mode.PLAY) + '&url=' + self.currentlist.codeUrl(videoItem))
                #xbmc.executebuiltin(u)
                result = self.playVideo(videoItem, True)
                return -2

            elif __settings__.getSetting('autoplay') == 'true' and len(self.currentlist.items) == 0:
                dialog = xbmcgui.Dialog()
                dialog.ok('SportsDevil Info', 'No stream available')
                return

        # Add items to XBMC list

        # sort methods
        if self.currentlist.sort == '':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_LABEL)
        elif self.currentlist.sort in ['name','label']:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_LABEL)

        if self.currentlist.sort.find('none') != -1:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_NONE)
        else:
            if self.currentlist.sort.find('size') != -1:
                xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_SIZE)
            if self.currentlist.sort.find('duration') != -1:
                xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_DURATION)
            if self.currentlist.sort.find('genre') != -1:
                xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_GENRE)
            if self.currentlist.sort.find('rating') != -1:
                xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_VIDEO_RATING)
            if self.currentlist.sort.find('date') != -1:
                xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_DATE)
            if self.currentlist.sort.find('file') != -1:
                xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_FILE)


        for m in self.currentlist.items:
            definedIn = self.curr_file
            if not definedIn:
                definedIn = m['cfg'].split('@',1)[0]
            m['definedIn'] = definedIn
            self.addListItem(m, len(self.currentlist.items))

        return result


    def autoselect(self, list):
        item = None
        while list.skill.find('autoselect') != -1 and len(list.items) == 1:
            m = list.items[0]
            m_type = m['type']

            if m_type == 'rss':
                try:
                    log('Autoselect - ' + m['title'])
                    tmpCfg = m['cfg']
                    tmpUrl = m['url']
                    if not tmpUrl.endswith('.cfg'):
                        setCurrentUrl(tmpUrl)
                    list.rules = []
                    list.section = ''
                    result = list.loadLocal(tmpCfg, lItem = m)
                    result = list.loadRemote(tmpUrl, False, lItem = m)
                    item = m

                    log(str(len(list.items)) + ' items ' + tmpCfg + ' -> ' + tmpUrl)
                except:
                    log('Couldn\'t autoselect')
            else:
                break
        return item

    def createListItem(self, item):
        liz = None
        title = clean_safe(item['title'])

        icon = item['icon']
        if icon:
            liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
        else:
            liz = xbmcgui.ListItem(title)

        fanart = item['fanart']
        if not fanart:
            fanart = pluginFanart
        liz.setProperty('fanart_image', fanart)

        for video_info_name in item.infos_names:
            if video_info_name.find('context.') != -1:
                try:
                    cItem = item
                    cItem['type'] = 'rss'
                    cItem['url'] = item[video_info_name]
                    action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?url=' + self.currentlist.codeUrl(cItem))
                    liz.addContextMenuItems([(video_info_name[video_info_name.find('.') + 1:], action)])
                except:
                    pass
            if video_info_name not in ['url', 'title', 'icon', 'type', 'extension'] and video_info_name.find('.tmp') == -1 and video_info_name.find('.append') == -1 and video_info_name.find('context.') == -1:
                try:
                    info_value = item[video_info_name]
                    if video_info_name.find('.int') != -1:
                        liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name[:video_info_name.find('.int')]): int(info_value)})
                    elif video_info_name.find('.tmp') != -1:
                        liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name[:video_info_name.find('.tmp')]): info_value})
                    else:
                        liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name): info_value})
                except:
                    pass
        return liz

    def _createContextMenuItem(self, label, mode, codedItem):
        action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(mode) + '&url=' + codedItem)
        return (label, action)

    def addListItem(self, lItem, totalItems):
        contextMenuItems = []

        codedItem = self.currentlist.codeUrl(lItem)

        # Queue
        contextMenuItem = self._createContextMenuItem('Queue', Mode.QUEUE, codedItem)
        contextMenuItems.append(contextMenuItem)

        if self.curr_file.endswith('favourites.cfg') or self.curr_file.startswith("favfolders/"):
            # Remove from favourites
            contextMenuItem = self._createContextMenuItem('Remove', Mode.REMOVEFROMFAVOURITES, codedItem)
            contextMenuItems.append(contextMenuItem)

            # Edit label
            contextMenuItem = self._createContextMenuItem('Edit', Mode.EDITITEM, codedItem)
            contextMenuItems.append(contextMenuItem)

        else:
            if lItem['title'] != "Favourites":
                # Add to favourites
                contextMenuItem = self._createContextMenuItem('Add to SportsDevil favourites', Mode.ADDTOFAVOURITES, codedItem)
                contextMenuItems.append(contextMenuItem)


        liz = self.createListItem(lItem)

        m_type = lItem['type']
        if m_type.__contains__('video'):
            u = sys.argv[0] + '?mode=' + str(Mode.PLAY) + '&url=' + codedItem
            contextMenuItem = self._createContextMenuItem('Download', Mode.DOWNLOAD, codedItem)
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


    def purgeCache(self):
        for root, dirs, files in os.walk(cacheDir , topdown = False):
            for name in files:
                if not name == 'cookies.lwp':
                    os.remove(os.path.join(root, name))


    def run(self):
        log('SportsDevil running')
        try:
            self.handle = int(sys.argv[1])
            xbmcplugin.setPluginFanart(self.handle, pluginFanart)
            paramstring = sys.argv[2]
            if len(paramstring) <= 2:
                if __settings__.getSetting('hide_warning') == 'false':
                    dialog = xbmcgui.Dialog()
                    if not dialog.yesno(__language__(30061), __language__(30062), __language__(30063), __language__(30064), __language__(30065), __language__(30066)):
                        return
                log('Cache directory: ' + str(cacheDir))
                log('Resource directory: ' + str(resDir))
                log('Image directory: ' + str(imgDir))

                if not os.path.exists(cacheDir):
                    log('Creating cache directory ' + str(cacheDir))
                    os.mkdir(cacheDir)
                    log('Cache directory created')
                else:
                    log('Purging cache directory')
                    self.purgeCache()
                    log('Cache directory purged')


                # Show Main Menu
                self.parseView('sites.list')
                log('End of directory')
                xbmcplugin.endOfDirectory(self.handle)
            else:
                params = sys.argv[2]
                mode, codedItem = params.split('&',1)
                mode = int(mode.split('=')[1])
                codedItem = codedItem[4:]
                if mode == Mode.VIEW:
                    result = self.parseView(codedItem)
                    if result == -2:
                        return

                if mode == Mode.ADDITEM:
                    self.favouritesManager.addItem()
                    xbmc.executebuiltin('Container.Refresh()')

                elif mode in [Mode.ADDTOFAVOURITES, Mode.REMOVEFROMFAVOURITES, Mode.EDITITEM]:
                    item = self.currentlist.decodeUrl(codedItem)
                    if mode == Mode.ADDTOFAVOURITES:
                        self.favouritesManager.addToFavourites(item)
                    elif mode == Mode.REMOVEFROMFAVOURITES:
                        self.favouritesManager.removeItem(item)
                        xbmc.executebuiltin('Container.Refresh()')
                    elif mode == Mode.EDITITEM:
                        if self.favouritesManager.editItem(item):
                            xbmc.executebuiltin('Container.Refresh()')
                    return


                if mode == Mode.EXECUTE:
                    item = self.currentlist.decodeUrl(codedItem)
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
                                path = unescape(params[len(params)-1])
                                xbmc.executebuiltin('Container.Update(' + path + ')')
                                return
                            xbmc.executebuiltin(unescape(url))
                            return

                if mode == Mode.PLAY:
                    videoItem = self.currentlist.decodeUrl(codedItem)
                    self.playVideo(videoItem)

                elif mode == Mode.QUEUE:
                    #xbmc.executebuiltin('XBMC.Action(Queue)')
                    #return
                    it = self.currentlist.decodeUrl(codedItem)
                    dia = DialogProgress()
                    dia.create('SportsDevil', 'Get videos...' + it['title'])
                    dia.update(0)
                    if it != None:
                        items = self.getVideos(it, dia)
                        if items:
                            for it in items:
                                item = self.createListItem(it)
                                uc = sys.argv[0] + '?mode=' + str(Mode.PLAY) + '&url=' + self.currentlist.codeUrl(it)
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
                    item = self.currentlist.decodeUrl(codedItem)
                    url = urllib.unquote(item['url'])
                    title = item['title']
                    self.downloadVideo(url, title)

                xbmcplugin.endOfDirectory(handle=self.handle)
                log('End of directory')

        except Exception, e:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            dialog = xbmcgui.Dialog()
            dialog.ok('SportsDevil Error', 'Error running SportsDevil.\n\nReason:\n' + str(e))
