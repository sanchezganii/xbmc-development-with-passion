# -*- coding: latin-1 -*-

from string import *
from helpers import *

import sys, os.path
import re, string

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

#####################################################
__addon__ = xbmcaddon.Addon(id='plugin.video.SportsDevil')
__language__ = __addon__.getLocalizedString


rootDir = __addon__.getAddonInfo('path')

if rootDir[-1] == ';':rootDir = rootDir[0:-1]
cacheDir = os.path.join(rootDir, 'cache')
resDir = os.path.join(rootDir, 'resources')
modulesDir = os.path.join(resDir, 'modules')
catchersDir = os.path.join(resDir,'catchers')



def containsImport(data):
    m_reg = findall(data,'(@IMPORT=([^@]+)@)')
    return (m_reg is not None and len(m_reg) > 0)

def replaceImport(data):
    m_reg = findall(data,'(@IMPORT=([^@]+)@)')
    if not (m_reg is None or len(m_reg) == 0):
        for idat in m_reg:
            filename = idat[1]
            pathImp = xbmc.translatePath(os.path.join(modulesDir, filename))
            if not os.path.exists(pathImp):
                from sportsdevil import getCurrentCfg
                tmpPath = os.path.dirname(getCurrentCfg())
                pathImp = xbmc.translatePath(os.path.join(tmpPath ,filename))
                if not (os.path.exists(pathImp)):
                    log('Skipped Import: ' + filename)
                    continue
            dataImp = getFileContent(pathImp)
            dataImp = dataImp.replace('\r\n','\n')
            data = data.replace(idat[0], dataImp)
    return data

def replacePlatform(data):
    m_reg = findall(data,'(@PLATFORM@)')
    if not (m_reg is None or len(m_reg) == 0):
      for idat in m_reg:
          data = data.replace(idat, os.environ.get('OS'))
    return data

def replaceCurrentUrl(data):
    m_reg = findall(data,'(@CURRENT_URL@)')
    if not (m_reg is None or len(m_reg) == 0):
      url = getCurrentUrl()
      for idat in m_reg:
          data = data.replace(idat,url)
    return data

def getCurrentUrl():
    url = getFileContent(os.path.join(cacheDir, 'currenturl'))
    return url


def replaceLanguage(data):
    m_reg = findall(data,'(@LANGUAGE@)')
    if m_reg:
        language = xbmc.getLanguage()
        for idat in m_reg:
            if lower(language).startswith('german'):
                data = data.replace(idat, 'de')
            else:
                data = data.replace(idat, 'en')
    return data

#####################################################
def customCfgReplacements(data, params=[]):

      #Imports
      while containsImport(data):
        data = replaceImport(data)

      #Parameters
      i=1
      for par in params:
          matches = findall(data,'(@PARAM' + str(i) + '@)')
          if matches:
              for m in matches:
                  ptemp = str(par).strip()
                  data = data.replace(m, ptemp)
          i = i + 1

      #Catchers
      m_reg = findall(data,'(#*@CATCH\([^\)]+\)@)')
      if not (m_reg is None or len(m_reg) == 0):
          for idat in m_reg:
              if idat.startswith('#'):
                continue
              ps = idat[7:-2].strip().split(',')
              pathImp = xbmc.translatePath(os.path.join(catchersDir, ps[0].strip() + '.txt'))
              if not (os.path.exists(pathImp)):
                  log('Skipped Catcher: ' + ps[0].strip())
                  continue
              dataImp = getFileContent(pathImp)
              dataImp = dataImp.replace('@PARAM1@',ps[1].strip())
              if len(ps) > 2:
                i = 2
                for p in ps:
                    dataImp = dataImp.replace('@PARAM' + str(i) + '@',ps[i].strip())
                    i += 1
              dataImp = dataImp.replace('\r\n','\n')
              data = data.replace(idat, dataImp)

      #Current url
      data = replaceCurrentUrl(data)

      #Platform
      data = replacePlatform(data)

      #Language
      data = replaceLanguage(data)



      #Conditions
      starts = [match.start() for match in re.finditer(re.escape('@IF('), data)]
      for j in range(len(starts)-1,-1,-1):
          s = starts[j]
          p_reg = re.compile('((@IF\((.+?)\)@).*?(@ENDIF@))', re.IGNORECASE + re.DOTALL + re.MULTILINE)
          m_reg = p_reg.findall(data[s:])
          if not (m_reg is None or len(m_reg) == 0):
              for m in m_reg:
                  new_reg=p_reg.match(m[0])
                  condStr = new_reg.group(3)
                  hidePassage=False
                  if condStr.find('==') != -1:
                      condArr=condStr.split('==')
                      hidePassage = condArr[0].strip().lower() != condArr[1].strip().lower()
                  elif condStr.find('!=') != -1:
                      condArr=condStr.split('!=')
                      hidePassage = condArr[0].strip().lower() == condArr[1].strip().lower()

                  if hidePassage:
                      data = data.replace(str(new_reg.group(1)),'')
                  else:
                      tmpdata = str(new_reg.group(1))
                      tmpdata = tmpdata.replace(str(new_reg.group(2)),'',1)
                      tmpdata = tmpdata[:-len(str(new_reg.group(4)))]
                      data = data.replace(str(new_reg.group(1)),tmpdata)


      return data
