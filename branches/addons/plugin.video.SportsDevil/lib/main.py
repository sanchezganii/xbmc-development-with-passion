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

enable_debug = True
__settings__ = xbmcaddon.Addon(id='plugin.video.SportsDevil')
__language__ = __settings__.getLocalizedString



class Main:

    def __init__(self):
        log('Initializing SportsDevil')
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
        if videoItem == None:
            return

        url = videoItem.getInfo('url')
        url = urllib.unquote_plus(url)

        title = videoItem.getInfo('videoTitle')
        if not title:
            title = videoItem.getInfo('title')
            if not title:
                title = 'unknown'

        try:
            icon = videoItem.getInfo('icon')
        except:
            icon = os.path.join(imgDir, 'video.png')

        try:
            urllib.urlretrieve(icon, os.path.join(cacheDir, 'thumb.tbn'))
            icon = os.path.join(cacheDir, 'thumb.tbn')
        except:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            icon = os.path.join(imgDir, 'video.png')

        listitem = xbmcgui.ListItem(title, title, icon, icon)
        listitem.setInfo('video', {'Title':title})

        for video_info_name in videoItem.infos_names:
            try:
                listitem.setInfo(type = 'Video', infoLabels = {video_info_name: videoItem.getInfo(video_info_name)})
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
            log('Cancelled')
            return None

        downloader = Downloader(__language__)
        file = downloader.downloadMovie(url, path, first_clean_filename(title), self.videoExtension)

        if file == None:
            log ('Download cancelled')
        else:
            log('Video ' + url + ' downloaded to ' + file)

        return file

    def getVideos(self, lItem, dia = None):
        allitems = []
        currentName = lItem.getInfo('title')
        if lItem.getInfo('type').find('video') != -1:
            if dia:
                dia.update(0, 'Get video...', currentName,lItem.getInfo('title'))
            allitems.append(lItem)
        else:
            if dia:
                dia.update(0, 'Get video...', currentName)

            cfg = lItem.getInfo('cfg')
            url = lItem.getInfo('url')
            tmpList = CItemsList()

            # Load cfg file
            result = tmpList.loadLocal(cfg, lItem = lItem)

            # Load url and parse
            if not (url.endswith('.cfg') or url.endswith('.list')) :
                result = tmpList.loadRemote(url, False, lItem = lItem)

            if len(tmpList.items) == 0:
                # try to find redirect
                red = findRedirect(url)
                if red != url:
                    setCurrentUrl(red)
                    lItem.setInfo('url',red)
                    children = self.getVideos(lItem,dia)
                    if children:
                        allitems.extend(children)
                else:
                    # nothing found
                    return None
            else:
                for item in tmpList.items:
                    if item.getInfo('type').find('video') != -1:
                        allitems.append(item)
                        if dia:
                            dia.update(0, 'Get video...',currentName,item.getInfo('title'))

                    else:
                        currentName = item.getInfo('title')
                        if dia:
                            dia.update(0, 'Get video...', currentName)
                        children = self.getVideos(item,dia)
                        if children:
                            allitems.extend(children)


        return allitems

    def parseView(self, url):
        lItem = self.currentlist.decodeUrl(url)
        url = lItem.getInfo('url')
        ext = self.currentlist.getFileExtension(url)

        if ext == 'cfg' or ext == 'list':
            result = self.currentlist.loadLocal(url, lItem = lItem)
            self.curr_file = url
        else:
            result = self.currentlist.loadRemote(url, lItem = lItem)

        # if there is nothing to scrape
        if not ((ext == 'cfg' or ext == 'list') and self.currentlist.start == ''):
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
                            tmpCfg = lItem.getInfo('cfg')
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
                    startUrl = lItem.getInfo('url')

                condition = condition and (len(self.currentlist.items) == 0 and i < maxIt)
                i += 1


            # Remove double entries
            urls = []
            for i in range(len(self.currentlist.items)-1,-1,-1):
                item = self.currentlist.items[i]
                tmpUrl = item.getInfo('url')
                tmpCfg = item.getInfo('cfg')
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
            m.setInfo('definedIn',self.curr_file)

            try:
                m_type = m.getInfo('type')
            except:
                m_type = 'rss'

            if m_type == 'search' and 'once' in m.infos_names:
                p_reg = re.compile('^' + m.getInfo('once') + '$', re.IGNORECASE + re.DOTALL + re.MULTILINE)
                m_reg = p_reg.match(unquote_safe(url))
                if  (m_reg is None):
                    continue

            self.addListItem(m, len(self.currentlist.items))

        return result

    def autoselect(self, list):
        item = None
        while list.skill.find('autoselect') != -1 and len(list.items) == 1:
            m = list.items[0]
            try:
                m_type = m.getInfo('type')
            except:
                m_type = 'rss'

            if m_type == 'rss':
                try:
                    log('Autoselect - ' + m.getInfo('title'))
                    tmpCfg = m.getInfo('cfg')
                    tmpUrl = m.getInfo('url')
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
        title = clean_safe(item.getInfo('title'))

        icon = item.getInfo('icon')
        if icon:
            liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
        else:
            liz = xbmcgui.ListItem(title)

        fanart = item.getInfo('fanart')
        if not fanart:
            fanart = pluginFanart
        liz.setProperty('fanart_image', fanart)

        for video_info_name in item.infos_names:
            if video_info_name.find('context.') != -1:
                try:
                    cItem = item
                    cItem.setInfo('type', 'rss')
                    cItem.setInfo('url', item.getInfo(video_info_name))
                    action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?url=' + self.currentlist.codeUrl(cItem))
                    liz.addContextMenuItems([(video_info_name[video_info_name.find('.') + 1:], action)])
                except:
                    pass
            if video_info_name != 'url' and video_info_name != 'title' and video_info_name != 'icon' and video_info_name != 'type' and video_info_name != 'extension' and video_info_name.find('.tmp') == -1 and video_info_name.find('.append') == -1 and video_info_name.find('context.') == -1:
                try:
                    info_value = item.getInfo(video_info_name)
                    if video_info_name.find('.int') != -1:
                        liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name[:video_info_name.find('.int')]): int(info_value)})
                    elif video_info_name.find('.tmp') != -1:
                        liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name[:video_info_name.find('.tmp')]): info_value})
                    else:
                        liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name): info_value})
                except:
                    pass
        return liz

    def addListItem(self,  lItem, totalItems):
        liz = self.createListItem(lItem)

        m_type = lItem.getInfo('type')
        if not m_type:
            m_type = 'rss'

        contextMenuItems = []

        # Queue
        action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(Mode.QUEUE) + '&url=' + self.currentlist.codeUrl(lItem))
        #action = 'XBMC.Action(Queue)'
        contextMenuItems.append(("Queue",action))

        if self.curr_file.endswith('favourites.cfg') or self.curr_file.startswith("favfolders/"):
            # Remove from favourites
            action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(Mode.REMOVEFROMFAVOURITES) + '&url=' + self.currentlist.codeUrl(lItem))
            contextMenuItems.append(("Remove",action))
            # Edit label
            action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(Mode.EDITITEM) + '&url=' + self.currentlist.codeUrl(lItem))
            contextMenuItems.append(("Edit",action))

        else:
            if lItem.getInfo('title') != "Favourites":
                # Add to favourites
                action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(Mode.ADDTOFAVOURITES) + '&url=' + self.currentlist.codeUrl(lItem))
                contextMenuItems.append(("Add to SportsDevil favourites",action))



        if m_type.find('video') > -1:
            #u = lItem.getInfo('url')
            u = sys.argv[0] + '?mode=' + str(Mode.PLAY) + '&url=' + self.currentlist.codeUrl(lItem)
            action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(Mode.DOWNLOAD) + '&url=' + self.currentlist.codeUrl(lItem))
            contextMenuItems.append(("Download",action))

            liz.setProperty('IsPlayable','true')
            isFolder = False
        elif m_type.find('command') > -1:
            u = sys.argv[0] + '?mode=' + str(Mode.EXECUTE) + '&url=' + self.currentlist.codeUrl(lItem)
            isFolder = False
        else:
            u = sys.argv[0] + '?mode=' + str(Mode.VIEW) + '&url=' + self.currentlist.codeUrl(lItem)
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
                    url = item.getInfo('url')
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
                    dia = xbmcgui.DialogProgress()
                    dia.create('SportsDevil', 'Get videos...')
                    it = self.currentlist.decodeUrl(codedItem)
                    if it != None:
                        items = self.getVideos(it, dia)
                        if items:
                            for it in items:
                                item = self.createListItem(it)
                                uc = sys.argv[0] + '?mode=' + str(Mode.PLAY) + '&url=' + self.currentlist.codeUrl(it)
                                item.setProperty('IsPlayable', 'true')
                                item.setProperty('IsFolder','false')
                                xbmc.PlayList(1).add(uc, item)
                            xbmc.sleep(500)
                            resultLen = len(items)
                            msg = 'Queued ' + str(resultLen) + ' video'
                            if resultLen > 1:
                                msg += 's'
                            dia.update(0, msg,'')
                        else:
                            dia.update(0, 'No items found','')
                        xbmc.sleep(1000)
                    dia.close()


                elif mode == Mode.DOWNLOAD:
                    item = self.currentlist.decodeUrl(codedItem)
                    url = item.getInfo('url')
                    title = item.getInfo('title')
                    url = urllib.unquote(url)
                    self.downloadVideo(url, title)

                xbmcplugin.endOfDirectory(handle=self.handle)
                log('End of directory')

        except Exception, e:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            dialog = xbmcgui.Dialog()
            dialog.ok('SportsDevil Error', 'Error running SportsDevil.\n\nReason:\n' + str(e))
