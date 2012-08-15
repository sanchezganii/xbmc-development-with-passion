import sys
import string
import urllib


class CListItem(object):
    
    def __init__(self):
        self.infos_names = []
        self.infos_values = []

    def __getitem__(self, key):
        return self.getInfo(key)

    def __setitem__(self, key, value):
        self.setInfo(key, value)

    def getInfo(self, key):
        if self.infos_names.__contains__(key):
            return self.infos_values[self.infos_names.index(key)]
        return None

    def setInfo(self, key, value):
        if key in self.infos_names:
            self.infos_values[self.infos_names.index(key)] = value
        else:
            self.infos_names.append(key)
            self.infos_values.append(value)

    def merge(self, item):
        for info_name in item.infos_names:
            if not self[info_name]:
                self[info_name] = item[info_name]

    def __str__(self):
        txt = ''
        for info_name in self.infos_names:
            txt += string.ljust(info_name,15) +':\t' + self[info_name] + '\n'
        return txt
    



# STATIC FUNCTIONS

def create():
    return CListItem()

def toUrl(item):
    params = ''

    for info_name in item.infos_names:
        # Infos that will be passed to next level apart from url
        if info_name != 'url' and not info_name.endswith('.tmp'):
            
            info_value = item[info_name]
            value = smart_unicode(info_value)
            try:
                value = urllib.quote_plus(value.encode('utf-8'))
            except:
                sys.exc_clear()

            keyValPair = smart_unicode(info_name) + ':' + value
            params += '&' + keyValPair
            
        params = params.lstrip('&')
    
    # URL
    url = item['url']
    try:
        url = smart_unicode(urllib.quote_plus(url))
    except:
        sys.exc_clear()
    params += '&url:' + url

    return params


def fromUrl(url):
    item = CListItem()
    if url.find('&') == -1:
        item['url'] = smart_unicode(url)
        return item

    keyValPairs = url.split('&')
    for keyValPair in keyValPairs:
        if keyValPair.find(':') > -1:
            key, val = keyValPair.split(':',1)
            item[key] = urllib.unquote_plus(val)
    return item


def smart_unicode(s):
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s