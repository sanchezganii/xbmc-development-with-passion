# -*- coding: latin-1 -*-

import sys, os
import traceback
import urllib, urllib2
import cookielib
import re
from fileUtils import setFileContent, getFileContent
import encodingUtils as enc



Request = urllib2.Request
urlopen = urllib2.urlopen

defaultHeaders = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18', 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}


def get_redirected_url(url):
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
    request = opener.open(url)
    return request.url

def isOnline(url):
    req = Request(url, None, defaultHeaders)
    try:
        urlopen(req)
        return True
    except:
        return False

#------------------------------------------------------------------------------ 


class WebRequest(object):
    
    def __init__(self, cookiePath):
        self.cj = cookielib.LWPCookieJar(cookiePath)
        if self.cj:
            try:
                self.cj.load()
            except:
                self.cj.save()
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
            urllib2.install_opener(self.opener)
    
    def getSource(self, url, referer=None):
        url = urllib.unquote_plus(url)
        if not referer:
            referer = url
    
        req = Request(url, None, defaultHeaders)
        req.add_header('Referer', referer)
    
        try:
            handle = urlopen(req)
        except:
            traceback.print_exc(file = sys.stdout)
            return None
    
        data = handle.read()
        handle.close()
       
        self.cj.save()
    
        return data
    
    
#------------------------------------------------------------------------------ 


class DemystifiedWebRequest(WebRequest):
 
    def __init__(self, cookiePath):
        super(DemystifiedWebRequest,self).__init__(cookiePath)
        
    def getSource(self, url, referer='', demystify=False):
        data = super(DemystifiedWebRequest, self).getSource(url, referer)
        if not data:
            return None
         
        if not demystify:
            # remove comments
            r = re.compile('<!--.*?(?!//)-->', re.IGNORECASE + re.DOTALL + re.MULTILINE)
            m = r.findall(data)
            if m:
                for comment in m:
                    data = data.replace(comment,'')
        else:
            import decryptionUtils as crypt
            data = crypt.doDemystify(data)
    
        return data

#------------------------------------------------------------------------------ 
    
    
class CachedWebRequest(DemystifiedWebRequest):
    
    def __init__(self, cookiePath, cachePath):
        super(CachedWebRequest,self).__init__(cookiePath)
        self.cachePath = cachePath
        self.cachedSourcePath = os.path.join(self.cachePath, 'page.html')
        self.currentUrlPath = os.path.join(self.cachePath, 'currenturl')
        self.lastUrlPath = os.path.join(self.cachePath, 'lasturl')
        
    def __setLastUrl(self, url):
        setFileContent(self.lastUrlPath, url)

    def __getCachedSource(self):
        data = enc.smart_unicode(getFileContent(self.cachedSourcePath))
        return data
    
    def getLastUrl(self):
        url = getFileContent(self.lastUrlPath)
        return url
    
    def getSource(self, url, referer='', ignoreCache=False, demystify=False):

        if url == self.getLastUrl() and not ignoreCache:
            data = self.__getCachedSource()
        else:
            data = enc.smart_unicode(super(CachedWebRequest,self).getSource(url, referer, demystify))
            if data:
                # Cache url
                self.__setLastUrl(url)
                # Cache page
                setFileContent(self.cachedSourcePath, data)
        return data    
        