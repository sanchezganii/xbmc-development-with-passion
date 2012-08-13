# -*- coding: latin-1 -*-

import os
import random
from encodingUtils import smart_unicode


#######################################
# File Helpers
#######################################

def getFileExtension(filename):
    ext_pos = filename.rfind('.')
    if ext_pos != -1:
        return filename[ext_pos+1:]
    else:
        return ''


def findInSubdirectory(filename, subdirectory=''):
    if subdirectory:
        path = subdirectory
    else:
        path = os.getcwd()
    for root, dirs, names in os.walk(path):
        if filename in names:
            return os.path.join(root, filename)
    raise 'File not found'


def cleanFilename(s):
    if not s:
        return ''
    badchars = '\\/:*?\"<>|'
    for c in badchars:
        s = s.replace(c, '')
    return s;


def randomFilename(directory, chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', length = 8, prefix = '', suffix = '', attempts = 10000):
    for attempt in range(attempts):
        filename = ''.join([random.choice(chars) for i in range(length)])
        filename = prefix + filename + suffix
        if not os.path.exists(os.path.join(directory, filename)):
            return filename
    return None


def getFileContent(filename):
    try:
        f = open(filename,'r')
        txt = f.read()
        f.close()
        return txt
    except:
        return ''

def setFileContent(filename, txt):
    try:
        f = open(filename, 'w')
        f.write(smart_unicode(txt).encode('utf-8'))
        f.close()
        return True
    except:
        return False

def appendFileContent(filename, txt):
    try:
        f = open(filename, 'a')
        f.write(smart_unicode(txt).encode('utf-8'))
        f.close()
        return True
    except:
        return False
