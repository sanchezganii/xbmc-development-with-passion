# -*- coding: latin-1 -*-

from helpers import *
import sportsdevil, helpers

from string import *
import xbmcplugin, xbmcaddon
import sys, os.path
import urllib,urllib2, filecmp
import re, random, string, shutil
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import cookielib, htmlentitydefs
import socket, base64
import pyDes

def convDate(params, src):
    if params.find("','") != -1:
        paramArr = params.split("','")
        oldfrmt = paramArr[0].strip('\'')
        newfrmt = paramArr[1].strip('\'')
        return helpers.convDate(src,str(oldfrmt), str(newfrmt))
    else:
        params = params.strip('\'')
        return helpers.convDate(src,params)

def offset(params, src):
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

    return offset.strftime('%H:%M')

def getSource(params, src):
    paramPage = ''
    paramReferer = ''
    if params.find('\',\'') > -1:
        paramArr = params.split('\',\'')
        paramPage = paramArr[0].strip('\'')
        paramReferer = paramArr[1].strip('\'')
    else:
        paramPage = params.strip('\',\'')

    paramPage = paramPage.replace('%s', src)
    return sportsdevil.getHTML(paramPage,paramReferer)

def regex(params, src):
    src = smart_unicode(src)
    paramArr = params.split("','")
    paramText = paramArr[0].strip("'").replace('%s', src)
    paramRegex = paramArr[1].strip("'").replace('%s', src)
    p = re.compile(paramRegex, re.IGNORECASE + re.DOTALL + re.MULTILINE)
    m = p.match(paramText)
    if m:
      return m.group(1)
    return src

def parseText(params, src):
    src = smart_unicode(src)
    paramArr = params.split("','")

    text = paramArr[0].strip("'").replace('%s',src)
    regex = paramArr[1].strip("'").replace('%s', src)
    vars = []
    if len(paramArr) > 2:
        vars = paramArr[2].strip("'").split('|')
    return helpers.parseText(text, regex, vars)

def getInfo(item, params, src):
    src = smart_unicode(src)
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
    data = sportsdevil.getHTML(paramPage, referer, referer!='')
    return helpers.parseText(data, paramRegex, vars)

def decodeBase64(src):
    src = src.strip('.js').replace('%3D','=')
    try:
        return src.decode('base-64').replace('qo','')
    except:
        return src

def replace(params, src):
    src = smart_unicode(src)
    paramArr = params.split('\',\'')
    paramstr = paramArr[0].replace('%s', src).strip('\'')
    paramSrch = paramArr[1].strip('\'')
    paramRepl = paramArr[2].strip('\'')
    return paramstr.replace(paramSrch,paramRepl)

def replaceRegex(params, src):
    src = smart_unicode(src)
    paramArr = params.split('\',\'')
    paramStr = paramArr[0].replace('%s', src).strip('\'')
    paramSrch = paramArr[1].strip('\'')
    paramRepl = paramArr[2].strip('\'')

    r = re.compile(paramSrch, re.DOTALL + re.IGNORECASE)
    ms = r.findall(paramStr)
    if ms:
        for m in ms:
            paramStr = paramStr.replace(m, paramRepl,1)
        return paramStr
    return src

def ifEmpty(params, src):
    paramArr = params.split("','")
    paramSource = paramArr[0].strip("'").replace('%s', src)
    paramTrue = paramArr[1].strip("'").replace('%s', src)
    paramFalse = paramArr[2].strip("'").replace('%s', src)
    return helpers.ifStringEmpty(paramSource, paramTrue, paramFalse)

def isEqual(params, src):
    paramArr = params.split("','")
    paramSource = paramArr[0].strip("'").replace('%s', src)
    paramComp = paramArr[1].strip("'").replace('%s', src)
    paramTrue = paramArr[2].strip("'").replace('%s', src)
    paramFalse = paramArr[3].strip("'").replace('%s', src)

    if (paramSource == paramComp):
        return paramTrue
    else:
        return paramFalse

def ifExists(params, src):
    paramArr = params.split("','")
    paramSource = paramArr[0].strip("'").replace('%s', src)
    paramTrue = paramArr[1].strip("'").replace('%s', src)
    paramFalse = paramArr[2].strip("'").replace('%s', src)
    return helpers.ifExists(paramSource, paramTrue, paramFalse)

def urlMerge(params, src):
    params = params.strip("'")
    paramArr = params.split("','")
    paramTrunk = paramArr[0].strip("'").replace('%s', src)
    paramFile= paramArr[1].strip("'").replace('%s', src)

    if not paramFile.startswith('http'):
        from urlparse import urlparse
        up = urlparse(urllib.unquote(paramTrunk))
        if paramFile.startswith('/'):
            return urllib.basejoin(up[0] + '://' + up[1],paramFile)
        else:
            return urllib.basejoin(up[0] + '://' + up[1] + '/' + up[2],paramFile)
    return src
