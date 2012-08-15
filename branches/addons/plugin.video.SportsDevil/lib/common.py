# -*- coding: latin-1 -*-

import os


#------------------------------------------------------------------------------
# xbmc related
#------------------------------------------------------------------------------
import xbmc, xbmcaddon

__settings__ = xbmcaddon.Addon(id='plugin.video.SportsDevil')
translate = __settings__.getLocalizedString
log = xbmc.log
enable_debug = True
language = xbmc.getLanguage

def getSetting(name):
    return __settings__.getSetting(name)

def setSetting(name, value):
    __settings__.setSetting(id=name, value=value)

def showNotification(title, message):
    xbmc.executebuiltin('Notification(' + title + ',' + str(message) + ')')

def runPlugin(url):
    xbmc.executebuiltin('XBMC.RunPlugin(' + url +')')

#------------------------------------------------------------------------------
# dialogs
#------------------------------------------------------------------------------
from dialogs.dialogProgress import DialogProgress
from dialogs.dialogQuestion import DialogQuestion
from dialogs.dialogBrowser import DialogBrowser
from dialogs.dialogInfo import DialogInfo
from dialogs.dialogError import DialogError

from utils.xbmcUtils import getKeyboard

def ask(question):
    diaQuestion = DialogQuestion()
    return diaQuestion.ask(question)

def showInfo(message):
    diaInfo = DialogInfo()
    diaInfo.show(message)

def showError(message):
    diaError = DialogError()
    diaError.show(message)

def browseFolders(head):
    diaFolder = DialogBrowser()
    return diaFolder.browseFolders(head)

def showOSK(defaultText='', title='', hidden=False):
    return getKeyboard(defaultText, title, hidden)


#------------------------------------------------------------------------------
# web related
#------------------------------------------------------------------------------
from utils.regexUtils import parseTextToGroups
from utils.webUtils import CachedWebRequest

def getHTML(url, referer='', ignoreCache=False, demystify=False):
    cookiePath = xbmc.translatePath(os.path.join(Paths.cacheDir, 'cookies.lwp'))
    request = CachedWebRequest(cookiePath, Paths.cacheDir)
    return request.getSource(url, referer, ignoreCache, demystify)


def parseWebsite(source, regex, referer='', variables=[]):
    def parseWebsiteToGroups(url, regex, referer=''):
        data = getHTML(url, referer)
        return parseTextToGroups(data, regex)

    groups = parseWebsiteToGroups(source, regex, referer)

    if variables == []:
        if groups:
            return groups[0]
        else:
            return ''
    else:
        resultArr = {}
        i = 0
        for v in variables:
            if groups:
                resultArr[v] = groups[i]
            else:
                resultArr[v] = ''
            i += 1
        return resultArr





#------------------------------------------------------------------------------
# classes with constants
#------------------------------------------------------------------------------
class Paths:
    rootDir = __settings__.getAddonInfo('path')

    if rootDir[-1] == ';':
        rootDir = rootDir[0:-1]

    cacheDir = os.path.join(rootDir, 'cache')
    resDir = os.path.join(rootDir, 'resources')
    imgDir = os.path.join(resDir, 'images')
    modulesDir = os.path.join(resDir, 'modules')
    catchersDir = os.path.join(resDir,'catchers')
    dictsDir = os.path.join(resDir,'dictionaries')

    pluginFanart = os.path.join(rootDir, 'fanart.jpg')
    defaultVideoIcon = os.path.join(imgDir, 'video.png')
    defaultCategoryIcon = os.path.join(imgDir, 'folder.png')    

    pluginDataDir = xbmc.translatePath('special://profile/addon_data/plugin.video.SportsDevil')
    favouritesFolder = os.path.join(pluginDataDir, 'favourites')
    favouritesFile = os.path.join(favouritesFolder, 'favourites.cfg')







