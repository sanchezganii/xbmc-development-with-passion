# -*- coding: latin-1 -*-


import regexUtils as re
import urllib

def findFrames(data):
    if data.lower().find('frame') == -1:
        return None
    return re.findall(data, "(frame[^>]*)>")


def findVideoFrameLink(page, data):
    
    minheight=300
    minwidth=300
    
    frames = findFrames(data)
    if not frames:
        return None
    
    iframes = re.findall(data, "(frame[^>]* height=[\"']*(\d+)[\"']*[^>]*>)")

    if iframes:
        for iframe in iframes:

            height = int(iframe[1])
            if height > minheight:
                m = re.findall(iframe[0], "[ ]width=[\"']*(\d+[%]*)[\"']*")
                if m:
                    if m[0] == '100%':
                        width = minwidth+1
                    else:
                        width = int(m[0])
                    if width > minwidth:
                        m = re.findall(iframe[0], '[\'"\s]src=["\']*\s*([^"\' ]+)\s*["\']*')
                        if m:
                            link = m[0]
                            if not link.startswith('http://'):
                                from urlparse import urlparse
                                up = urlparse(urllib.unquote(page))
                                if link.startswith('/'):
                                    link = urllib.basejoin(up[0] + '://' + up[1],link)
                                else:
                                    link = urllib.basejoin(up[0] + '://' + up[1] + '/' + up[2],link)
                            return link.strip()

    # Alternative 1
    iframes = re.findall(data, "(frame[^>]*[\"; ]height:\s*(\d+)[^>]*>)")
    if iframes:
        for iframe in iframes:
            height = int(iframe[1])
            if height > minheight:
                m = re.findall(iframe[0], "[\"; ]width:\s*(\d+)")
                if m:
                    width = int(m[0])
                    if width > minwidth:
                        m = re.findall(iframe[0], '[ ]src=["\']*\s*([^"\' ]+)\s*["\']*')
                        if m:
                            link = m[0]
                            if not link.startswith('http://'):
                                link = urllib.basejoin(page,link)
                            return link.strip()

    # Alternative 2 (Frameset)
    iframes = re.findall(data, '<FRAMESET[^>]+100%[^>]+>\s*<FRAME[^>]+src="([^"]+)"')
    if iframes:
        link = iframes[0]
        if not link.startswith('http://'):
            link = urllib.basejoin(page,link)
        return link.strip()
        
    return None
