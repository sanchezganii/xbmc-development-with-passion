# -*- coding: latin-1 -*-

import common
import sys, os, traceback
import time
import random
import re
import urllib
import string
from string import lower

from entities.CList import CList
from entities.CItemInfo import CItemInfo
from entities.CListItem import CListItem
from entities.CRuleItem import CRuleItem



import cfg.customReplacements as cr
import cfg.customConversions as cc

from utils import encodingUtils as enc
from utils import decryptionUtils as crypt
from utils import datetimeUtils as dt

from utils.webUtils import get_redirected_url
from utils.fileUtils import findInSubdirectory, getFileContent, getFileExtension
from utils.scrapingUtils import findVideoFrameLink


class Parser(object):

    ##########################################################
    # returns a list of items
    ##########################################################
    def parse(self, lItem):
        url = lItem['url']
        cfg = lItem['cfg']
        ext = getFileExtension(url)

        successfullyScraped = True

        if ext == 'cfg':
            tmpList = self.__loadLocal(url, lItem)
            if tmpList and tmpList.start != '':
                lItem['url'] = tmpList.start
                successfullyScraped = self.__loadRemote(tmpList, lItem)
        elif cfg:
            tmpList = self.__loadLocal(cfg, lItem)
            if tmpList:
                successfullyScraped = self.__loadRemote(tmpList, lItem)
        else:
            return None

        # autoselect
        if tmpList.skill.find('autoselect') != -1 and len(tmpList.items) == 1:
            m = tmpList.items[0]
            m_type = m['type']

            if m_type == 'rss':
                common.log('Autoselect - ' + m['title'])
                lItem = m
                tmpList = self.parse(lItem)

        if not tmpList:
            common.log("cfg file couldn't be loaded")
            return None
        if tmpList and successfullyScraped == False:
            common.log("cfg file successfully loaded, but scraping failed")

        return tmpList


    # loads cfg, creates list and sets up rules for scraping
    def __loadLocal(self, filename, lItem = None):
        params = []

        #get Parameters
        if filename.find('@') != -1:
            params = filename.split('@')
            filename = params.pop(0)

        # get cfg file
        cfg = filename
        if not os.path.exists(cfg):
            cfg = os.path.join(common.Paths.modulesDir, filename)
            if not os.path.exists(cfg):
                tmpPath = os.path.dirname(os.path.join(common.Paths.modulesDir, lItem["definedIn"]))
                cfg = os.path.join(tmpPath ,filename)
                if not os.path.exists(cfg):
                    if filename.find('/') > -1:
                        filename = filename.split('/')[1]
                    try:
                        cfg = findInSubdirectory(filename, common.Paths.modulesDir)
                    except:
                        try:
                            cfg = findInSubdirectory(filename, common.Paths.favouritesFolder)
                        except:
                            common.log('File not found: ' + filename)
                            return None

        #load file and apply parameters
        data = getFileContent(cfg)
        data = cr.CustomReplacements().replace(os.path.dirname(cfg), data, params)

        #log
        msg = 'Local file ' +  filename + ' opened'
        if len(params) > 0:
            msg += ' with Parameter(s): '
            msg += ",".join(params)
        common.log(msg)

        outputList = self.__parseCfg(filename, data, lItem)

        return outputList



    # scrape items according to rules and add them to the list
    def __loadRemote(self, inputList, lItem):

        try:
            inputList.curr_url = lItem['url']

            count = 0
            i = 1
            maxits = 2
            ignoreCache = False
            demystify = False
            startUrl = inputList.curr_url
            while count == 0 and i <= maxits:
                if i > 1:
                    ignoreCache = True
                    demystify =  True

                # Trivial: url is from known streamer
                items = self.__parseHtml(inputList.curr_url, '"' + inputList.curr_url + '"', inputList.rules, inputList.cfg, lItem)
                count = len(items)

                # try to find items in html source code
                if count == 0:
                    data = common.getHTML(inputList.curr_url, inputList.reference, ignoreCache, demystify)
                    if data == '':
                        return False

                    common.log('Remote URL ' + str(inputList.curr_url) + ' opened')

                    if inputList.section != '':
                        p = re.compile(inputList.section, re.IGNORECASE + re.DOTALL + re.UNICODE)
                        m = p.search(data)
                        if m:
                            data = m.group(0)
                        else:
                            common.log('section could not be found:' + inputList.section)

                    items = self.__parseHtml(inputList.curr_url, data, inputList.rules, inputList.cfg, lItem)
                    count = len(items)
                    common.log(str(count) + ' items found')

                # find redirects
                if count == 0:
                    red = self.__findRedirect(startUrl, inputList.curr_url)
                    if startUrl == red:
                        common.log('No redirect found')
                    else:
                        common.log('Redirect: ' + red)
                        inputList.curr_url = red
                        common.log(str(len(inputList.items)) + ' items ' + lItem['cfg'] + ' -> ' + red)
                        startUrl = red
                        i = 0

                i += 1


            if count != 0:
                inputList.items = inputList.items + items


        except IOError:
            if common.enable_debug:
                traceback.print_exc(file = sys.stdout)
            return False
        return True


    def __findRedirect(self, page, referer='', demystify=False):
        data = common.getHTML(page, referer = referer, demystify = demystify)

        link = findVideoFrameLink(page, data)
        if link:
            return link

        if not demystify:
            return self.__findRedirect(page, referer, True)

        return page


    def __parseCfg(self, cfgFile, data, lItem):
        tmpList = CList()

        data = data.replace('\r\n', '\n').split('\n')

        items = []
        tmp = None

        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = lower(m[:index]).strip()
                    value = m[index+1:]

                    index = value.find('|')
                    if value[:index] == 'sports.devil.locale':
                        value = common.translate(int(value[index+1:]))
                    elif value[:index] == 'sports.devil.image':
                        value = os.path.join(common.Paths.imgDir, value[index+1:])

                    if key == 'start':
                        tmpList.start = value
                    elif key == 'section':
                        tmpList.section = value
                    elif key == 'sort':
                        tmpList.sort = value
                    elif key == 'skill':
                        tmpList.skill = value
                    elif key == 'header':
                        index = value.find('|')
                        tmpList.reference = value[:index]
                        tmpList.content = value[index+1:]

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
                                value = 'context.' + common.translate(int(value[index+1:]))
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
                        tmpList.rules.append(rule_tmp)


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
                        tmp['definedIn'] = cfgFile
                        items.append(tmp)
                        tmp = None
                    elif tmp != None:
                        tmp[key] = value


        tmpList.items = items
        tmpList.cfg = cfgFile
        return tmpList


    def __parseHtml(self, url, data, rules, definedIn, lItem):

        items = []

        for item_rule in rules:
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
                            tmpVal = enc.smart_unicode(info.build % enc.smart_unicode(info_value))
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
                                    src = src + enc.smart_unicode(tmp[t])
                        elif info.src.__contains__('||'):
                            variables = info.src.split('||')
                            src = firstNonEmpty(tmp, variables)
                        else:
                            src = tmp[info.src]

                        if src and info.convert != []:
                            src = self.__parseCommands(tmp, src, info.convert)
                            if isinstance(src, dict):
                                for dKey in src:
                                    tmp[dKey] = src[dKey]
                                src = src.values()[0]

                        info_value = info.build % (enc.smart_unicode(src))
                    else:
                        info_value = info.build

                    tmp[info.name] = info_value


                tmp['url'] = enc.smart_unicode(item_rule.url_build % (enc.smart_unicode(tmp['url'])))
                tmp.merge(lItem)
                if item_rule.skill.find('append') != -1:
                    tmp['url'] = url + tmp['url']

                if item_rule.skill.find('space') != -1:
                    tmp['title'] = ' %s ' % tmp['title'].strip()

                tmp['definedIn'] = definedIn
                items.append(tmp)

        return items


    def __parseCommands(self, item, src, convCommands):
        # helping function
        def parseCommand(txt):
            command = {"command": txt, "params": ""}
            if txt.find("(") > -1:
                command["command"] = txt[0:txt.find("(")]
                command["params"] = txt[len(command["command"]) + 1:-1]
            return command

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
                src = enc.smart_unicode(params.strip("'").replace('%s', src))

            elif command == 'safeGerman':
                src = enc.safeGerman(src)

            elif command == 'safeRegex':
                src = enc.safeRegexEncoding(params.strip("'").replace('%s', enc.smart_unicode(src)))

            elif command == 'replaceFromDict':
                dictName = str(params.strip('\''))
                path = os.path.join(common.Paths.dictsDir, dictName + '.txt')
                if not (os.path.exists(path)):
                    common.log('Dictionary file not found: ' + path)
                    continue
                src = cc.replaceFromDict(path, src)

            elif command == 'time':
                src = time.time()

            elif command == 'timediff':
                src = dt.timediff(src,params.strip('\''))

            elif command == 'offset':
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
                src = crypt.encryptJimey(params.strip("'").replace('%s', src))

            elif command == 'destreamer':
                src = crypt.destreamer(params.strip("'").replace('%s', src))

            elif command == 'unixTimestamp':
                src = dt.getUnixTimestamp()

            elif command == 'urlMerge':
                src = cc.urlMerge(params, src)

            elif command == 'translate':
                try:
                    src = common.translate(int(src))
                except:
                    src = src

            elif command == 'camelcase':
                src = enc.smart_unicode(src)
                src = string.capwords(string.capwords(src, '-'))

            elif command == 'random':
                paramArr = params.split(',')
                minimum = int(paramArr[0])
                maximum = int(paramArr[1])
                src = str(random.randrange(minimum,maximum))

            elif command == 'debug':
                common.log('Debug from cfg file: ' + src)
        return src





def firstNonEmpty(tmp, variables):
    for v in variables:
        vClean = v.strip()
        if vClean.find("'") != -1:
            vClean = vClean.strip("'")
        else:
            vClean = tmp.getInfo(vClean)

        if vClean != '':
            return vClean

    return ''


