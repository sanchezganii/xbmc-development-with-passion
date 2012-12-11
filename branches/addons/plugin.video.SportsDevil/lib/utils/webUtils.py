# -*- coding: latin-1 -*-

import sys, os
import traceback
import urllib, urllib2
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
        self.cookiePath = cookiePath
        self.cj = None
        ClientCookie = None
        cookielib = None

        try:                                    # Let's see if cookielib is available
            import cookielib
        except ImportError:
            pass
        else:
            import urllib2
            self.urlopen = urllib2.urlopen
            self.cj = cookielib.LWPCookieJar()       # This is a subclass of FileCookieJar that has useful load and save methods
            self.Request = urllib2.Request

        if not cookielib:                   # If importing cookielib fails let's try ClientCookie
            try:
                import ClientCookie
            except ImportError:
                import urllib2
                self.urlopen = urllib2.urlopen
                self.Request = urllib2.Request
            else:
                self.urlopen = ClientCookie.urlopen
                self.cj = ClientCookie.LWPCookieJar()
                self.Request = ClientCookie.Request

        if self.cj != None:                                  # now we have to install our CookieJar so that it is used as the default CookieProcessor in the default opener handler
            if os.path.isfile(cookiePath):
                self.cj.load(cookiePath)
            if cookielib:
                self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
                urllib2.install_opener(self.opener)
            else:
                self.opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(self.cj))
                ClientCookie.install_opener(self.opener)


    def getSource(self, url, referer=None):
        url = urllib.unquote_plus(url)
        if not referer:
            referer = url

        try:
            req = Request(url, None, defaultHeaders)            # create a request object
            req.add_header('Referer', referer)                  # set referer
            handle = urlopen(req)                               # and open it to return a handle on the url
        except IOError, e:
            #traceback.print_exc(file = sys.stdout)
            print 'Failed to open "%s".' % url
            if hasattr(e, 'code'):
                print 'Failed with error code - %s.' % e.code
            elif hasattr(e, 'reason'):
                print "The error object has the following 'reason' attribute :", e.reason
                print "This usually means the server doesn't exist, is down, or we don't have an internet connection."
        else:
            #print 'Here are the headers of the page :'
            #print handle.info()                             # handle.read() returns the page, handle.geturl() returns the true url of the page fetched (in case urlopen has followed any redirects, which it sometimes does)
            data = handle.read()
            handle.close()

            if self.cj:
#                print 'These are the cookies we have received so far :'
#                for index, cookie in enumerate(self.cj):
#                    print index, '  :  ', cookie
                self.cj.save(self.cookiePath)                     # save the cookies again

            return data

        return None


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
        try:
            data = getFileContent(self.cachedSourcePath)
            data = enc.smart_unicode(data)
        except:
            #data = data.decode('utf-8')
            pass
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
