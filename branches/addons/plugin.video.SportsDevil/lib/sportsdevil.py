# -*- coding: latin-1 -*-

from string import *
from helpers import *

import xbmcplugin, xbmcaddon
import sys, os.path
import urllib,urllib2, filecmp
import re, random, string, shutil
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import cookielib, htmlentitydefs
import socket, base64

import customCfg

#import locale

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

#socket.setdefaulttimeout(20)


enable_debug = True

def setCurrentUrl(url):
    f = open(os.path.join(cacheDir, 'currenturl'), 'w')
    f.write(url)
    f.close()



def setLastUrl(url):
    f = open(os.path.join(cacheDir, 'lasturl'), 'w')
    f.write(url)
    f.close()


def getLastUrl():
    url = getFileContent(os.path.join(cacheDir, 'lasturl'))
    return url

def setCurrentCfg(path):
    f = open(os.path.join(cacheDir, 'currentcfg'), 'w')
    f.write(path)
    f.close()

def getCurrentCfg():
    path = getFileContent(os.path.join(cacheDir, 'currentcfg'))
    return path







def replaceFromDict(filename, wrd):
    pathImp = xbmc.translatePath(os.path.join(dictsDir, filename + '.txt'))
    if not (os.path.exists(pathImp)):
        log('Skipped Replacement: ' + filename)
    dict = getFileContent(pathImp)
    dict = dict.replace('\r\n','\n')

    p_reg = re.compile('^[^\r\n]+$', re.IGNORECASE + re.DOTALL + re.MULTILINE)
    m_reg = p_reg.findall(dict)

    word = wrd.replace(u'Ü','&Uuml;').replace(u'Ö','&Ouml;').replace(u'Ä','&Auml;')
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
        data = getFileContent(cache)
    else:
        data = getSource(url, referer, demystify)

        # Cache url
        setLastUrl(url)

        # Cache page
        f = open(cache, 'w')
        f.write(data)
        f.close()
    return data

def ifStringEmpty(str, trueStr, falseStr):
    if str == '':
        return trueStr
    else:
        return falseStr

def isOnline(url):
    txheaders = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18', 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
    req = Request(url, None, txheaders)
    try:
        handle = urlopen(req)
        return True
    except:
        return False


def ifExists(url, trueStr, falseStr):
    if isOnline(url):
        return trueStr
    else:
        return falseStr

def customConversion(item, src, convCommands):
    for convCommand in convCommands:
        if convCommand.startswith('convDate'):
            params = convCommand[9:-1]
            if params.find("','") != -1:
                paramArr = params.split("','")
                oldfrmt = paramArr[0].strip('\'')
                newfrmt = paramArr[1].strip('\'')
                src = convDate(src,str(oldfrmt), str(newfrmt))
            else:
                params = params.strip('\'')
                src = convDate(src,params)

        elif convCommand == 'smart_unicode':
            src = smart_unicode(convCommand[14:-1].strip('\'').replace('%s', src))

        elif convCommand == 'safeGerman':
            src = safeGerman(src)

        elif convCommand.startswith('safeRegex'):
            src = safeRegexEncoding(convCommand[10:-1].strip("'").replace('%s',smart_unicode(src)))

        elif convCommand.startswith('replaceFromDict('):
            params = convCommand[16:-1]
            params = params.strip('\'')
            src = replaceFromDict(str(params),src)

        elif convCommand.startswith('time('):
            src = time.time()

        elif convCommand.startswith('timediff'):
            params = convCommand[9:-1]
            params = params.strip('\'')
            src = timediff(src,params)

        elif convCommand.startswith('offset'):
            if __settings__.getSetting('timeoffset') == 'true':
                params = convCommand[7:-1]
                paramArr = params.split("','")
                t = paramArr[0].strip("'").replace('%s', src)
                o = paramArr[1].strip("'").replace('%s', src)

                fak = 1
                if o[0] == '-':
                    fak = -1
                    o = o[1:]

                pageOffSeconds = fak*(int(o.split(':')[0]) * 3600 + int(o.split(':')[1])*60)
                localOffSeconds = -1 * time.timezone
                offSeconds = localOffSeconds - pageOffSeconds

                ti = datetime.datetime(2000,1,1,int(t.split(':')[0]),int(t.split(':')[1]))

                offset=ti + datetime.timedelta(seconds=offSeconds)

                src = offset.strftime('%H:%M')



        elif convCommand.startswith('getSource'):
            params = convCommand[10:-1]
            paramPage = ''
            paramReferer = ''
            if params.find('\',\'') > -1:
                paramArr = params.split('\',\'')
                paramPage = paramArr[0].strip('\'')
                paramReferer = paramArr[1].strip('\'')
            else:
                paramPage = params.strip('\',\'')

            paramPage = paramPage.replace('%s', src)
            return getHTML(paramPage,paramReferer)

        elif convCommand.startswith('getRedirect'):
            param = convCommand[12:-1].strip("'")
            src = get_redirected_url(param.replace('%s', src))

        elif convCommand.startswith('quote'):
            param = convCommand[6:-1].strip("'")
            src = urllib.quote(param.replace('%s', urllib.quote(src)))
        elif convCommand.startswith('unquote'):
            param = convCommand[8:-1].strip("'")
            src = urllib.unquote(param.replace('%s', src))

        elif convCommand.startswith('regex'):
            src = smart_unicode(src)
            params = convCommand[6:-1]
            paramArr = params.split("','")
            paramText = paramArr[0].strip("'").replace('%s', src)
            paramRegex = paramArr[1].strip("'").replace('%s', src)
            p = re.compile(paramRegex, re.IGNORECASE + re.DOTALL + re.MULTILINE)
            m = p.match(paramText)
            if m:
              src = m.group(1)

        elif convCommand.startswith('parseText'):
            src = smart_unicode(src)
            params = convCommand[10:-1]
            paramArr = params.split("','")

            text = paramArr[0].strip("'").replace('%s',src)
            regex = paramArr[1].strip("'").replace('%s', src)
            vars = []
            if len(paramArr) > 2:
                vars = paramArr[2].strip("'").split('|')
            src = parseText(text, regex, vars)

        elif convCommand.startswith('getInfo'):
            src = smart_unicode(src)
            params = convCommand[8:-1]
            paramArr = params.split("','")
            paramPage = paramArr[0].strip("'").replace('%s', src)
            paramPage = urllib.unquote(paramPage)
            paramRegex = paramArr[1].strip("'").replace('%s', src)
            referer = ''
            vars=[]
            if len(paramArr) > 2:
                referer = paramArr[2].strip("'")
                referer = referer.replace('%s', src)
                if referer.startswith('@') and referer.endswith('@'):
                    referer = item.getInfo(referer.strip('@'))
            if len(paramArr) > 3:
                vars = paramArr[3].strip("'").split('|')
            log('Get Info from: "'+ paramPage + '" from "' + referer + '"')
            data = getHTML(paramPage, referer, referer!='')
            src = parseText(data, paramRegex,vars)

        elif convCommand.startswith('decodeBase64'):
            src = src.strip('.js').replace('%3D','=')
            try:
                src = src.decode('base-64').replace('qo','')
            except:
                src = src

        elif convCommand.startswith('replace('):
            src = smart_unicode(src)
            params = convCommand[8:-1]
            paramArr = params.split('\',\'')
            paramstr = paramArr[0].replace('%s', src).strip('\'')
            paramSrch = paramArr[1].strip('\'')
            paramRepl = paramArr[2].strip('\'')
            src = paramstr.replace(paramSrch,paramRepl)
        elif convCommand.startswith('replaceRegex'):
            src = smart_unicode(src)
            params = convCommand[13:-1]
            paramArr = params.split('\',\'')
            paramStr = paramArr[0].replace('%s', src).strip('\'')
            paramSrch = paramArr[1].strip('\'')
            paramRepl = paramArr[2].strip('\'')

            r = re.compile(paramSrch, re.DOTALL + re.IGNORECASE)
            ms = r.findall(paramStr)
            if ms:
                for m in ms:
                    paramStr = paramStr.replace(m, paramRepl,1)
                src = paramStr

        elif convCommand.startswith('ifEmpty'):
            params = convCommand[8:-1]
            paramArr = params.split("','")

            paramSource = paramArr[0].strip("'").replace('%s', src)
            paramTrue = paramArr[1].strip("'").replace('%s', src)
            paramFalse = paramArr[2].strip("'").replace('%s', src)

            src = ifStringEmpty(paramSource, paramTrue, paramFalse)

        elif convCommand.startswith('isEqual'):
            params = convCommand[8:-1]
            paramArr = params.split("','")

            paramSource = paramArr[0].strip("'").replace('%s', src)
            paramComp = paramArr[1].strip("'").replace('%s', src)
            paramTrue = paramArr[2].strip("'").replace('%s', src)
            paramFalse = paramArr[3].strip("'").replace('%s', src)

            if (paramSource == paramComp):
                src = paramTrue
            else:
                src = paramFalse

        elif convCommand.startswith('ifExists'):
            params = convCommand[9:-1]
            paramArr = params.split("','")

            paramSource = paramArr[0].strip("'").replace('%s', src)
            paramTrue = paramArr[1].strip("'").replace('%s', src)
            paramFalse = paramArr[2].strip("'").replace('%s', src)

            src = ifExists(paramSource, paramTrue, paramFalse)

        elif convCommand.startswith('encryptJimey'):
            param = convCommand[13:-1].strip("'")
            param = param.replace('%s', src)
            src = encryptJimey(param)

        elif convCommand.startswith('destreamer'):
            param = convCommand[11:-1].strip("'")
            param = param.replace('%s', src)
            src = destreamer(param)

        elif convCommand.startswith('unixTimestamp'):
            src = getUnixTimestamp()

        elif convCommand.startswith('urlMerge'):
            params = convCommand[9:-1].strip("'")
            paramArr = params.split("','")
            paramTrunk = paramArr[0].strip("'").replace('%s', src)
            paramFile= paramArr[1].strip("'").replace('%s', src)

            if not paramFile.startswith('http'):
                from urlparse import urlparse
                up = urlparse(urllib.unquote(paramTrunk))
                if paramFile.startswith('/'):
                    src = urllib.basejoin(up[0] + '://' + up[1],paramFile)
                else:
                    src = urllib.basejoin(up[0] + '://' + up[1] + '/' + up[2],paramFile)

        elif convCommand == 'translate':
            try:
                src = __language__(int(src))
            except:
                src = src

        elif convCommand.startswith('random'):
            params = convCommand[7:-1]
            paramArr = params.split(',')
            min = int(paramArr[0])
            max = int(paramArr[1])
            src = str(random.randrange(min,max))

        elif convCommand == 'debug':
            log('Debug from cfg file: ' + src)
    return src



class CListItem:
    def __init__(self):
        self.infos_names = []
        self.infos_values = []

    def getInfo(self, key):
        if self.infos_names.__contains__(key):
            return self.infos_values[self.infos_names.index(key)]
        return None

    def setInfo(self, key, value):
        if self.infos_names.__contains__(key):
            self.infos_values[self.infos_names.index(key)] = value
        else:
            self.infos_names.append(key)
            self.infos_values.append(value)

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


    def getFileExtension(self, filename):
        ext_pos = filename.rfind('.')
        if ext_pos != -1:
            return filename[ext_pos+1:]
        else:
            return ''


    def videoCount(self):
        count = 0
        for item in self.items:
            if item.getInfo('type').find('video') != -1:
                count = count +1
        return count

    def getVideo(self):
        for item in self.items:
            if item.getInfo('type').find('video') != -1:
                return item


    def getItemFromList(self, listname, name):
        self.loadLocal(listname)
        for item in self.items:
            if item.getInfo('url') == name:
                return item
        return None

    def itemInLocalList(self, name):
        for item in self.items:
            if item.getInfo('url') == name:
                return True
        return False

    def getItem(self, name):
        item = None
        for root, dirs, files in os.walk(modulesDir):
            for listname in files:
                if self.getFileExtension(listname) == 'list':
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
        f = open(str(os.path.join(modulesDir, 'entry.list')), 'w')
        f.write(smart_unicode('########################################################\n').encode('utf-8'))
        f.write(smart_unicode('#             Added sites and live streams             #\n').encode('utf-8'))
        f.write(smart_unicode('########################################################\n').encode('utf-8'))
        f.write(smart_unicode('skill=remove\n').encode('utf-8'))
        f.write(smart_unicode('########################################################\n').encode('utf-8'))
        for item in self.items:
            f.write(smart_unicode('title=' + item.getInfo('title') + '\n').encode('utf-8'))
            for info_name in item.infos_names:
                if info_name != 'url' and info_name != 'title':
                    f.write(smart_unicode(info_name + '=' + item.getInfo(info_name) + '\n').encode('utf-8'))
            f.write(smart_unicode('url=' + item.getInfo('url') + '\n').encode('utf-8'))
            f.write(smart_unicode('########################################################\n').encode('utf-8'))
        f.close()
        return

    def codeUrl(self, item, suffix = ''):
        params = ''

        for info_name in item.infos_names:
            if info_name != 'url' and info_name.find('.tmp') == -1:
                info_value = item.getInfo(info_name)
                try:
                    keyValPair = smart_unicode(info_name) + ':' + urllib.quote(smart_unicode(info_value))
                except:
                    keyValPair = smart_unicode(info_name) + ':' + smart_unicode(info_value)
                params += '&' + keyValPair

        params += '&url:' + smart_unicode(urllib.quote_plus(item.getInfo('url')))

        if len(suffix) > 0:
            params += '.' + suffix
        return params.lstrip('&')

    def decodeUrl(self, url, type = 'rss'):
        item = CListItem()
        if url.find('&') == -1:
            item.setInfo('url', clean_safe(url))
            item.setInfo('type',type)
            return item

        keyValPairs = url.split('&')
        for keyValPair in keyValPairs:
            if keyValPair.find(':') > -1:
                key, val = keyValPair.split(':',1)
                item.setInfo(key, urllib.unquote(val))

        if not item.getInfo('type'):
            item.setInfo('type', type)

        return item


    def loadLocal(self, filename, lItem = None):
        params = []

        #get Parameters
        if filename.find('@') != -1:
            params = filename.split('@')
            filename = params[0]
            params.pop(0)

        self.cfg = xbmc.translatePath(os.path.join(modulesDir, filename))

        if not os.path.exists(self.cfg):
            tmpPath = os.path.dirname(getCurrentCfg())
            self.cfg = xbmc.translatePath(os.path.join(tmpPath ,filename))
        else:
            setCurrentCfg(self.cfg)



        #load file and apply parameters
        data = getFileContent(self.cfg)
        data = customCfg.customCfgReplacements(data,params)
        data = data.replace('\r\n', '\n')
        data = data.split('\n')

        #log
        msg = 'Local file ' +  filename + ' opened'
        if len(params) > 0:
            msg += ' with Parameter(s): '
            msg += ",".join(params)
        log(msg)

        items = []
        tmp = None
        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = lower(m[:index])
                    value = m[index+1:]

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
                        tmp.setInfo('title', value)
                    elif key == 'type':
                        if value == 'once':
                            value = u'rss'
                        tmp.setInfo('type', value)
                    elif key == 'url':
                        tmp.setInfo('url', value)
                        if lItem != None:
                            for info_name in lItem.infos_names:
                                if not tmp.getInfo(info_name):
                                    tmp.setInfo(info_name, lItem.getInfo(info_name))
                        items.append(tmp)
                        tmp = None
                    elif tmp != None:
                        tmp.setInfo(key, value)
        self.items = items

        if self.start != '':
            if self.getFileExtension(lItem.getInfo('url')) == 'cfg':
                lItem.setInfo('url', self.start)
                self.loadRemote(self.start, False, lItem)
            else:
                self.loadRemote(lItem.getInfo('url'), False, lItem)

        return 0


    def search(self):
        searchCache = os.path.join(cacheDir, 'search')
        try:
            f = open(searchCache, 'r')
            curr_phrase = urllib.unquote_plus(f.read())
            f.close()
        except:
            curr_phrase = ''
        search_phrase = getKeyboard(default = curr_phrase, heading = __language__(30102))
        if search_phrase == '':
            return None
        xbmc.sleep(10)
        f = open(searchCache, 'w')
        f.write(search_phrase)
        f.close()

        return search_phrase


    def loadRemote(self, remote_url, recursive = True, lItem = None):
        setCurrentUrl(remote_url)

        try:
            curr_url = remote_url
            if recursive:
                try:
                    if self.loadLocal(lItem.getInfo('cfg'), lItem) != 0:
                        return -1
                except:
                    pass
                try:
                    if lItem.getInfo('type') == u'search':
                        search_phrase = self.search()
                        if not search_phrase:
                            return -1
                        curr_url = curr_url % (search_phrase)
                        lItem.setInfo('url', curr_url)
                        lItem.setInfo('type', u'rss')
                except:
                    pass
            data = getHTML(curr_url, self.reference)

            if data == '':
                return -1

            if self.section != '':
                p = re.compile('.*(' + self.section + ').*', re.IGNORECASE + re.DOTALL + re.MULTILINE)
                m = p.match(data)
                if m:
                    data = m.group(1)
                else:
                    log('section could not be found:' + self.section)

            log('Remote URL ' + str(curr_url) + ' opened')

        except IOError:
            if enable_debug:
                traceback.print_exc(file = sys.stdout)
            return -1


        count = self.parseItems(data,lItem)

        if count == 0:
            data = getHTML(curr_url, self.reference, ignoreCache=True, demystify=True)
            if self.section != '':
                p = re.compile('.*(' + self.section + ').*', re.IGNORECASE + re.DOTALL + re.MULTILINE)
                m = p.match(data)
                if m:
                    data = m.group(1)
                else:
                    log('section could not be found:' + self.section)
            count = self.parseItems(data,lItem)

        return 0


    # Find list items
    def parseItems(self,data,lItem):

        lock = False
        for item_rule in self.rules:
            if item_rule.skill.find('lock') != -1 and lock:
                continue

            # variables needed in loop
            one_found = False
            f = None

            revid = re.compile(item_rule.infos, re.IGNORECASE + re.DOTALL + re.MULTILINE)
            for reinfos in revid.findall(data):
                if item_rule.skill.find('lock') != -1 and lock:
                    continue
                tmp = CListItem()
                if item_rule.order.find('|') != -1:
                    tmp.infos_names = item_rule.order.split('|')
                    tmp.infos_values = list(reinfos)
                else:
                    tmp.setInfo(item_rule.order, reinfos)

                for info in item_rule.info_list:
                    info_value = tmp.getInfo(info.name)
                    if info_value:
                        if info.build.find('%s') != -1:
                            tmpVal = smart_unicode(info.build % smart_unicode(info_value))
                            tmp.setInfo(info.name, tmpVal)
                        continue

                    if info.build.find('%s') != -1:
                        if info.src.find('+') != -1:
                          tmpArr = info.src.split('+')
                          src = ''
                          for t in tmpArr:
                            t = t.strip()
                            if t.find('\'') != -1:
                              src = src + t.strip('\'')
                            else:
                              src = src + smart_unicode(tmp.getInfo(t))
                        elif info.src.find('||') != -1:
                            vars = info.src.split('||')
                            src = firstNonEmpty(tmp, vars)
                        else:
                          src = tmp.getInfo(info.src)

                        if info.convert != []:
                            src = customConversion(tmp, src, info.convert)
                            if isinstance(src, dict):
                                for dKey in src:
                                    tmp.setInfo(dKey, src[dKey])
                                src = src.values()[0]

                        info_value = info.build % (smart_unicode(src))
                    else:
                        info_value = info.build

                    tmp.setInfo(info.name, info_value)


                tmp.setInfo('url', smart_unicode(item_rule.url_build % (smart_unicode(tmp.getInfo('url')))))

                for info_name in lItem.infos_names:
                    if not tmp.getInfo(info_name):
                        tmp.setInfo(info_name, lItem.getInfo(info_name))


                if item_rule.skill.find('append') != -1:
                    tmp.setInfo('url', curr_url + tmp.getInfo('url'))

                if item_rule.skill.find('space') != -1:
                    tmp.setInfo('title', ' ' + tmp.getInfo('title').lstrip().rstrip() + ' ')

                if item_rule.skill.find('directory') != -1:
                    one_found = True
                    if f == None:
                        catfilename = randomFilename(prefix=(self.cfg + '.dir.'), suffix = '.list')
                        f = open(str(os.path.join(cacheDir, catfilename)), 'w')
                        f.write(smart_unicode('########################################################\n').encode('utf-8'))
                        f.write(smart_unicode('#                    Temporary file                    #\n').encode('utf-8'))
                        f.write(smart_unicode('########################################################\n').encode('utf-8'))

                    f.write(smart_unicode('title=' + tmp.getInfo('title') + '\n').encode('utf-8'))
                    for info_name in tmp.infos_names:
                        if info_name != 'url' and info_name != 'title':
                            f.write(smart_unicode(info_name + '=' + tmp.getInfo(info_name) + '\n').encode('utf-8'))
                    f.write(smart_unicode('url=' + tmp.getInfo('url') + '\n').encode('utf-8'))
                    f.write(smart_unicode('########################################################\n').encode('utf-8'))
                else:
                    self.items.append(tmp)
                if item_rule.skill.find('lock') != -1:
                    lock = True

            if one_found:
                tmp = CListItem()
                tmp.setInfo('url', catfilename)
                for info in item_rule.info_list:
                    if info.name == 'title':
                        tmp.setInfo('title', ' ' + info.build + ' ')
                    elif info.name == 'icon':
                        icon = info.default
                        if icon == '':
                            icon = info.build
                        tmp.setInfo('icon', icon)
                for info_name in lItem.infos_names:
                    if not tmp.getInfo(info_name):
                        tmp.setInfo(info_name, lItem.getInfo(info_name))
                self.items.append(tmp)
                if item_rule.skill.find('lock') != -1:
                    lock = True
            if f != None:
                f.write(smart_unicode('########################################################\n').encode('utf-8'))
                f.close()
        return len(self.items)
