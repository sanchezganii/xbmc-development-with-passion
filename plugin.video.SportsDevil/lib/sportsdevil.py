# -*- coding: latin-1 -*-

from globals import *
from string import *
from helpers import *
from CListItem import CListItem

import customConversions as cc

import xbmcplugin, xbmcaddon
import sys, os.path
import urllib,urllib2, filecmp
import re, random, string, shutil
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import cookielib, htmlentitydefs
import socket, base64

import customCfg

__settings__ = xbmcaddon.Addon(id='plugin.video.SportsDevil')
__language__ = __settings__.getLocalizedString

rootDir = __settings__.getAddonInfo('path')

if rootDir[-1] == ';':rootDir = rootDir[0:-1]
cacheDir = os.path.join(rootDir, 'cache')
resDir = os.path.join(rootDir, 'resources')
imgDir = os.path.join(resDir, 'images')
modulesDir = os.path.join(resDir, 'modules')
catchersDir = os.path.join(resDir,'catchers')
dictsDir = os.path.join(resDir,'dictionaries')

pluginFanart = os.path.join(rootDir, 'fanart.jpg')

pluginDataDir = xbmc.translatePath('special://profile/addon_data/plugin.video.SportsDevil')
favouritesFolder = os.path.join(pluginDataDir, 'favourites')
favouritesFile = os.path.join(favouritesFolder, 'favourites.cfg')
#socket.setdefaulttimeout(20)


enable_debug = True

def setCurrentUrl(url):
    setFileContent(os.path.join(cacheDir, 'currenturl'), url)

def setLastUrl(url):
    setFileContent(os.path.join(cacheDir, 'lasturl'), url)

def getLastUrl():
    url = getFileContent(os.path.join(cacheDir, 'lasturl'))
    return url

def setCurrentCfg(path):
    setFileContent(os.path.join(cacheDir, 'currentcfg'), path)

def getCurrentCfg():
    path = getFileContent(os.path.join(cacheDir, 'currentcfg'))
    return path

def replaceFromDict(filename, wrd):
    pathImp = os.path.join(dictsDir, filename + '.txt')
    if not (os.path.exists(pathImp)):
        log('Skipped Replacement: ' + filename)
    dict = smart_unicode(getFileContent(pathImp))
    dict = dict.replace('\r\n','\n')

    p_reg = re.compile('^[^\r\n]+$', re.IGNORECASE + re.DOTALL + re.MULTILINE)
    m_reg = p_reg.findall(dict)

    word = smart_unicode(wrd).replace(u'Ü','&Uuml;').replace(u'Ö','&Ouml;').replace(u'Ä','&Auml;')
    try:
      if m_reg and len(m_reg) > 0:
          index = ''
          words = []
          newword = ''
          for m in m_reg:
              if not m.startswith(' '):
                  index = m
                  del words[:]
              else:
                  replWord = m.strip()
                  words.append(replWord)
                  if word.find(' ') != -1:
                    newword = word.replace(replWord,index)

              if (word in words) or (word == index):
                  return index

          if newword != '' and newword != word:
            return newword
    except:
      log('Skipped Replacement: ' + word)

    return word



def getHTML(url, referer='', ignoreCache=False, demystify=False):
    cache = os.path.join(cacheDir, 'page.html')

    if url == getLastUrl() and not ignoreCache:
        log('Get source of \'' + url + '\' from Cache')
        data = smart_unicode(getFileContent(cache))
    else:
        data = smart_unicode(getSource(url, referer, demystify))

        # Cache url
        setLastUrl(url)

        # Cache page
        setFileContent(cache, data)

    return data


def parseCommand(txt):
    command = {"command": txt, "params": ""}
    if txt.find("(") > -1:
        command["command"] = txt[0:txt.find("(")]
        command["params"] = txt[len(command["command"]) + 1:-1]
    return command


def customConversion(item, src, convCommands):
    src = src.encode('utf-8')
    for convCommand in convCommands:
        pComm = parseCommand(convCommand)
        command = pComm["command"]
        params = pComm["params"]

        if command == 'convDate':
            src = cc.convDate(params, src)

        elif command == 'select':
            src = cc.select(params, src)
            if not src:
                continue

        elif command == 'smart_unicode':
            src = smart_unicode(params.strip("'").replace('%s', src))

        elif command == 'safeGerman':
            src = safeGerman(src)

        elif command == 'safeRegex':
            src = safeRegexEncoding(params.strip("'").replace('%s',smart_unicode(src)))

        elif command == 'replaceFromDict':
            src = replaceFromDict(str(params.strip('\'')),src)

        elif command == 'time':
            src = time.time()

        elif command == 'timediff':
            src = timediff(src,params.strip('\''))

        elif command == 'offset':
            if __settings__.getSetting('timeoffset') == 'true':
                src = cc.offset(params, src)

        elif command == 'getSource':
            src = cc.getSource(params, src)

        elif command == 'getRedirect':
            src = get_redirected_url(params.strip("'").replace('%s', src))

        elif command == 'quote':
            try:
                src = urllib.quote(params.strip("'").replace('%s', urllib.quote(src)))
            except:
                cleanParams = params.strip("'")
                cleanParams = cleanParams.replace("%s",src.encode('utf-8'))
                src = urllib.quote(cleanParams)

        elif command == 'unquote':
            src = urllib.unquote(params.strip("'").replace('%s', src))

        elif command == 'regex':
            src = cc.regex(params, src)

        elif command == 'parseText':
            src = cc.parseText(params, src)

        elif command == 'getInfo':
            src = cc.getInfo(item, params, src)

        elif command == 'decodeBase64':
            src = cc.decodeBase64(src)

        elif command == 'replace':
            src = cc.replace(params, src)

        elif command == 'replaceRegex':
            src = cc.replaceRegex(params, src)

        elif command == 'ifEmpty':
            src = cc.ifEmpty(params, src)

        elif command == 'isEqual':
            src = cc.isEqual(params, src)

        elif command == 'ifExists':
            src = cc.ifExists(params, src)

        elif command == 'encryptJimey':
            src = encryptJimey(params.strip("'").replace('%s', src))

        elif command == 'destreamer':
            src = destreamer(params.strip("'").replace('%s', src))

        elif command == 'unixTimestamp':
            src = getUnixTimestamp()

        elif command == 'urlMerge':
            src = cc.urlMerge(params, src)

        elif command == 'translate':
            try:
                src = __language__(int(src))
            except:
                src = src

        elif command == 'camelcase':
            src = smart_unicode(src)
            src = string.capwords(string.capwords(src,'-'))

        elif command == 'random':
            paramArr = params.split(',')
            min = int(paramArr[0])
            max = int(paramArr[1])
            src = str(random.randrange(min,max))

        elif command == 'debug':
            log('Debug from cfg file: ' + src)
    return src

class CItemInfo:
    def __init__(self):
        self.name = ''
        self.src = 'url'
        self.rule = ''
        self.default = ''
        self.build = ''
        self.convert = []

class CRuleItem:
    def __init__(self):
        self.infos = ''
        self.order = ''
        self.skill = ''
        self.curr = ''
        self.info_list = []
        self.url_build = ''

class CItemsList:
    def __init__(self):
        self.start = ''
        self.section = ''
        self.sort = ''
        self.cfg = ''
        self.skill = ''
        self.reference = ''     # for HTTP Header
        self.content = ''       # -"-
        self.items = []
        self.rules = []



    def videoCount(self):
        return len(filter(lambda x: x['type'] == 'video', self.items))

    def getVideo(self):
        for item in self.items:
            if item['type'] == 'video':
                return item


    def getItemFromList(self, listname, name):
        self.loadLocal(listname)
        for item in self.items:
            if item['url'] == name:
                return item
        return None

    def itemInLocalList(self, name):
        for item in self.items:
            if item['url'] == name:
                return True
        return False

    def getItem(self, name):
        item = None
        for root, dirs, files in os.walk(modulesDir):
            for listname in files:
                if getFileExtension(listname) == 'list':
                    item = self.getItemFromList(listname, name)
                if item != None:
                    return item
        return None

    def addItem(self, name):
        item = self.getItem(name)
        del self.items[:]
        try:
            self.loadLocal('entry.list')
        except:
            del self.items[:]
        if item and not self.itemInLocalList(name):
            self.items.append(item)
            self.saveList()
        return

    def removeItem(self, name):
        item = self.getItemFromList('entry.list', name)
        if item != None:
            self.items.remove(item)
            self.saveList()
        return

    def saveList(self):
        data = [ \
            '########################################################',
            '#             Added sites and live streams             #',
            '########################################################',
            'skill=remove',
            '########################################################'
            ]
        for item in self.items:
            data.append('title=' + item['title'])
            for info_name in item.infos_names:
                if info_name != 'url' and info_name != 'title':
                    data.append(info_name + '=' + item[info_name])
            data.append('url=' + item['url'])
            data.append('########################################################')

        setFileContent(os.path.join(modulesDir, 'entry.list'), '\n'.join(data))
        return

    def codeUrl(self, item, suffix = ''):
        params = ''

        for info_name in item.infos_names:
            if info_name != 'url' and info_name.find('.tmp') == -1:
                info_value = item[info_name]
                try:
                    keyValPair = smart_unicode(info_name) + ':' + urllib.quote(smart_unicode(info_value).encode('utf-8'))
                except:
                    keyValPair = smart_unicode(info_name) + ':' + smart_unicode(info_value)
                params += '&' + keyValPair
        try:
            params += '&url:' + smart_unicode(urllib.quote_plus(item['url']))
        except:
            params += '&url:' + item['url']

        if len(suffix) > 0:
            params += '.' + suffix
        return params.lstrip('&')

    def decodeUrl(self, url):
        item = CListItem()
        if url.find('&') == -1:
            item['url'] = clean_safe(url)
            return item

        keyValPairs = url.split('&')
        for keyValPair in keyValPairs:
            if keyValPair.find(':') > -1:
                key, val = keyValPair.split(':',1)
                item[key] = urllib.unquote_plus(val)
        return item

    def loadLocal(self, filename, lItem = None):
        params = []

        #get Parameters
        if filename.find('@') != -1:
            params = filename.split('@')
            filename = params[0]
            params.pop(0)

        cfg = filename
        if not os.path.exists(cfg):
            cfg = xbmc.translatePath(os.path.join(modulesDir, filename))
            if not os.path.exists(cfg):
                tmpPath = os.path.dirname(getCurrentCfg())
                cfg = xbmc.translatePath(os.path.join(tmpPath ,filename))
                if not os.path.exists(cfg):
                    if filename.find('/') > -1:
                        filename = filename.split('/')[1]
                    try:
                        cfg = findInSubdirectory(filename, modulesDir)
                    except:
                        try:
                            cfg = findInSubdirectory(filename, favouritesFolder)
                        except:
                            showMessage('File not found: ' + filename)
                            return


        self.cfg = cfg
        setCurrentCfg(self.cfg)

        #load file and apply parameters
        data = getFileContent(self.cfg)
        data = customCfg.customCfgReplacements(data, params)
        data = data.replace('\r\n', '\n').split('\n')

        #log
        msg = 'Local file ' +  filename + ' opened'
        if len(params) > 0:
            msg += ' with Parameter(s): '
            msg += ",".join(params)
        log(msg)

        items = []
        tmp = None

        if filename == 'sites.list':
            # Add Favourites
            tmp = CListItem()
            tmp['title'] = 'Favourites'
            tmp['type'] = 'rss'
            tmp['url'] = str(favouritesFile)
            items.append(tmp)
            tmp = None

        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = lower(m[:index]).strip()
                    value = m[index+1:].strip()

                    index = value.find('|')
                    if value[:index] == 'sports.devil.locale':
                        value = __language__(int(value[index+1:]))
                    elif value[:index] == 'sports.devil.image':
                        value = os.path.join(imgDir, value[index+1:])

                    if key == 'start':
                        self.start = value
                    elif key == 'section':
                        self.section = value
                    elif key == 'sort':
                        self.sort = value
                    elif key == 'skill':
                        self.skill = value
                    elif key == 'header':
                        index = value.find('|')
                        self.reference = value[:index]
                        self.content = value[index+1:]

                    elif key == 'item_infos':
                        rule_tmp = CRuleItem()
                        rule_tmp.infos = value
                    elif key == 'item_order':
                        rule_tmp.order = value
                    elif key == 'item_skill':
                        rule_tmp.skill = value
                    elif key == 'item_curr':
                        rule_tmp.curr = value

                    elif key.startswith('item_info'):
                        tmpkey = key[len('item_info'):]
                        if tmpkey == '_name':
                            info_tmp = CItemInfo()
                            index = value.find('|')
                            if value[:index] == 'sports.devil.context':
                                value = 'context.' + __language__(int(value[index+1:]))
                            info_tmp.name = value
                        elif tmpkey == '_from':
                            info_tmp.src = value
                        elif tmpkey == '':
                            info_tmp.rule = value
                        elif tmpkey == '_default':
                            info_tmp.default = value
                        elif tmpkey == '_convert':
                            info_tmp.convert.append(value)
                        elif tmpkey == '_build':
                            info_tmp.build = value
                            rule_tmp.info_list.append(info_tmp)

                    elif key == 'item_url_build':
                        rule_tmp.url_build = value
                        self.rules.append(rule_tmp)


                    # static menu items (without regex)
                    elif key == 'title':
                        tmp = CListItem()
                        tmp['title'] = value
                    elif key == 'type':
                        tmp['type'] = value
                    elif key == 'url':
                        tmp['url'] = value
                        if lItem:
                            tmp.merge(lItem)
                        items.append(tmp)
                        tmp = None
                    elif tmp != None:
                        tmp[key] = value


        if filename == favouritesFile:
            tmp = CListItem()
            tmp['title'] = 'Add item...'
            tmp['type'] = 'command'
            action = 'RunPlugin(%s)' % (sys.argv[0] + '?mode=' + str(Mode.ADDITEM) + '&url=')
            tmp['url'] = action
            items.append(tmp)
            tmp = None

        self.items = items

        if self.start != '':
            if getFileExtension(lItem['url']) == 'cfg':
                lItem['url'] = self.start
            self.loadRemote(lItem['url'], False, lItem)

        return 0


    def search(self):
        searchCache = os.path.join(cacheDir, 'search')
        try:
            curr_phrase = getFileContent(searchCache)
        except:
            curr_phrase = ''
        search_phrase = getKeyboard(default = curr_phrase, heading = __language__(30102))
        if search_phrase == '':
            return None
        xbmc.sleep(10)
        setFileContent(searchCache, search_phrase)

        return search_phrase


    def loadRemote(self, remote_url, recursive = True, lItem = None):
        setCurrentUrl(remote_url)

        try:
            curr_url = remote_url
            if recursive:
                if self.loadLocal(lItem['cfg'], lItem) != 0:
                    return -1
                if lItem['type'] == u'search':
                    search_phrase = self.search()
                    if not search_phrase:
                        return -1
                    curr_url = curr_url % (urllib.quote_plus(search_phrase))
                    lItem['type'] = 'rss'
                    lItem['url'] = curr_url

            count = 0

            i = 1
            maxits = 2
            ignoreCache = False
            demystify = False
            while count == 0 and i <= maxits:
                if i > 1:
                    ignoreCache = True
                    demystify =  True

                data = getHTML(curr_url, self.reference, ignoreCache, demystify)
                log('Remote URL ' + str(curr_url) + ' opened')

                if data == '':
                    return -1

                if self.section != '':
                    p = re.compile(self.section, re.IGNORECASE + re.DOTALL + re.UNICODE)
                    m = p.search(data)
                    if m:
                        data = m.group(0)
                    else:
                        log('section could not be found:' + self.section)

                count = self.parseItems(data, lItem)
                i += 1

            # Trivial: url is from known streamer
            if count == 0:
                count = self.parseItems('"' + curr_url + '"', lItem)

        except IOError:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            return -1


        return 0


    # Find list items
    def parseItems(self,data,lItem):
        for item_rule in self.rules:
            revid = re.compile(item_rule.infos, re.IGNORECASE + re.DOTALL + re.MULTILINE)
            for reinfos in revid.findall(data):
                tmp = CListItem()
                if item_rule.order.find('|') != -1:
                    tmp.infos_names = item_rule.order.split('|')
                    tmp.infos_values = list(reinfos)
                else:
                    tmp[item_rule.order] = reinfos

                for info in item_rule.info_list:
                    info_value = tmp[info.name]
                    if info_value:
                        if info.build.find('%s') != -1:
                            tmpVal = smart_unicode(info.build % smart_unicode(info_value))
                            tmp[info.name] = tmpVal
                        continue

                    if info.build.find('%s') != -1:
                        if info.src.__contains__('+'):
                          tmpArr = info.src.split('+')
                          src = ''
                          for t in tmpArr:
                            t = t.strip()
                            if t.find('\'') != -1:
                              src = src + t.strip('\'')
                            else:
                              src = src + smart_unicode(tmp[t])
                        elif info.src.__contains__('||'):
                            vars = info.src.split('||')
                            src = firstNonEmpty(tmp, vars)
                        else:
                          src = tmp[info.src]

                        if src and info.convert != []:
                            src = customConversion(tmp, src, info.convert)
                            if isinstance(src, dict):
                                for dKey in src:
                                    tmp[dKey] = src[dKey]
                                src = src.values()[0]

                        info_value = info.build % (smart_unicode(src))
                    else:
                        info_value = info.build

                    tmp[info.name] = info_value


                tmp['url'] = smart_unicode(item_rule.url_build % (smart_unicode(tmp['url'])))
                tmp.merge(lItem)
                if item_rule.skill.find('append') != -1:
                    tmp['url'] = curr_url + tmp['url']

                if item_rule.skill.find('space') != -1:
                    tmp['title'] = ' %s ' % tmp['title'].strip()

                self.items.append(tmp)

        return len(self.items)
