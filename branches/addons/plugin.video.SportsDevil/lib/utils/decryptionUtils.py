# -*- coding: latin-1 -*-

import pyDes
import urllib
import re
from string import join

from regexUtils import parseTextToGroups
from webUtils import get_redirected_url



def encryptDES_ECB(data, key):
    data = data.encode()
    k = pyDes.des(key, pyDes.ECB, IV=None, pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.encrypt(data)
    assert k.decrypt(d, padmode=pyDes.PAD_PKCS5) == data
    return d

def encryptJimey(data):
    result = encryptDES_ECB(data,"PASSWORD").encode('base64').replace('/','').strip()
    return result


def doDemystify(data):

    # replace NUL
    data = data.replace('\0','')

    # unescape
    r = re.compile('unescape\(\s*["\']([^\'"]+)["\']')
    gs = r.findall(data)
    if gs:
        for g in gs:
            quoted=g
            data = data.replace(quoted, urllib.unquote_plus(quoted))

    # n98c4d2c
    if data.find('function n98c4d2c(') > -1:
        gs = parseTextToGroups(data, ".*n98c4d2c\(''\).*?'(%[^']+)'.*")
        if gs != None and gs != []:
            data = data.replace(gs[0],n98c4d2c(gs[0]))

    # o61a2a8f
    if data.find('function o61a2a8f(') > -1:
        gs = parseTextToGroups(data, ".*o61a2a8f\(''\).*?'(%[^']+)'.*")
        if gs != None and gs != []:
            data = data.replace(gs[0],o61a2a8f(gs[0]))

    # RrRrRrRr
    if data.find('function RrRrRrRr(') > -1:
        r = re.compile("(RrRrRrRr\(\"(.*?)\"\);)</SCRIPT>", re.IGNORECASE + re.DOTALL)
        gs = r.findall(data)
        if gs != None and gs != []:
            for g in gs:
                data = data.replace(g[0],RrRrRrRr(g[1].replace('\\','')))

    # hp_d01
    if data.find('function hp_d01(') > -1:
        r = re.compile("hp_d01\(unescape\(\"(.+?)\"\)\);//-->")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,hp_d01(g))

    # ew_dc
    if data.find('function ew_dc(') > -1:
        r = re.compile("ew_dc\(unescape\(\"(.+?)\"\)\);</SCRIPT>")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,ew_dc(g))

    # pbbfa0
    if data.find('function pbbfa0(') > -1:
        r = re.compile("pbbfa0\(''\).*?'(.+?)'.\+.unescape")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,pbbfa0(g))


    # util.de
    if data.find('Util.de') > -1:
        r = re.compile("Util.de\(unescape\(['\"](.+?)['\"]\)\)")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,g.decode('base64'))

    # 24cast
    if data.find('destreamer(') > -1:
        r = re.compile("destreamer\(\"(.+?)\"\)")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,destreamer(g))


    # Tiny url
    r = re.compile('[\'"](http://(?:www.)?tinyurl.com/[^\'"]+)[\'"]',re.IGNORECASE + re.DOTALL)
    m = r.findall(data)
    if m:
        for tiny in m:
            data = data.replace(tiny, get_redirected_url(tiny))


    return data














#------------------------------------------------------------------------------ 
# javascript functions
#------------------------------------------------------------------------------ 

def hp_d01(s):
    ar=[]
    os=""
    for i in range(0,len(s)-1):
        c = ord(s[i])
        if c < 128:
            c = c^2
        os += chr(c)
        if len(os) > 80:
            ar.append(os)
            os = ""
    o = join(ar,'') + os
    return o

def o61a2a8f(s):
    r = "";
    tmp = s.split("18267506");
    s = urllib.unquote(tmp[0]);
    k = urllib.unquote(tmp[1] + "511382");
    for i in range(0,len(s)-1):
        r += chr((int(k[i%len(k)])^ord(s[i]))+1);
    return r;

def n98c4d2c(s):
    txtArr = s.split('18234663')
    s = urllib.unquote(txtArr[0])
    t = urllib.unquote(txtArr[1] + '549351')
    tmp=''
    for i in range(0,len(s)-1):
        tmp += chr((int(t[i%len(t)])^ord(s[i]))+-6)
    return urllib.unquote(tmp)

def RrRrRrRr(teaabb):
    tttmmm=""
    l=len(teaabb)
    www = hhhhffff = int(round(l/2))
    if l<2*www:
        hhhhffff -= 1
    for i in range(0,hhhhffff-1):
        tttmmm = tttmmm + teaabb[i] + teaabb[i+hhhhffff]
    if l<2*www :
        tttmmm = tttmmm + teaabb[l-1]
    return tttmmm

def ew_dc(s):
    d=''
    a=[]
    for i in range(0, len(s)-1):
        c = ord(s[i])
        if (c<128):
            c = c^5
        d += chr(c)
        if (i+1) % 99 == 0:
            a.append(d)
            d=''
    r = join(a,'') + d
    return r

def pbbfa0(s):
    r = ""
    tmp = s.split("17753326")
    s = urllib.unquote(tmp[0])
    k = urllib.unquote(tmp[1] + "527117")
    for i in range(0,len(s)):
        r += chr((int(k[i%len(k)])^ord(s[i]))+7)
    return r

# used by 24cast
def destreamer(s):
    #remove all but[0-9A-Z]
    string = re.sub("[^0-9A-Z]", "", s.upper())
    result = ""
    nextchar = ""
    for i in range(0,len(string)-1):
        nextchar += string[i]
        if len(nextchar) == 2:
            result += ntos(int(nextchar,16))
            nextchar = ""
    return result

def ntos(n):
    n = hex(n)[2:]
    if len(n) == 1:
        n = "0" + n
    n = "%" + n
    return urllib.unquote(n)
