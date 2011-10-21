from resources.lib.handler.hosterHandler import cHosterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from hosters.hoster import iHoster
from base64 import b64decode
from xbmc import log
from xbmc import LOGERROR

try:
  from json import loads
except ImportError:
  from simplejson import loads

class cHoster(iHoster):

  SETTINGS_URL = "http://www.videozer.com/player_control/settings.php?v="

  def __init__(self):
    self.__sDisplayName = 'VideoZer.com'
    self.__sFileName = self.__sDisplayName

  def getDisplayName(self):
    return  self.__sDisplayName

  def setDisplayName(self, sDisplayName):
    self.__sDisplayName = sDisplayName

  def setFileName(self, sFileName):
    self.__sFileName = sFileName

  def getFileName(self):
    return self.__sFileName

  def getPluginIdentifier(self):
    return 'videozer'

  def isDownloadable(self):
    return True

  def isJDownloaderable(self):
    return True

  def getPattern(self):
    return 'flashvars.file=\"([^\"]+)\"';

  def setUrl(self, sUrl):
    self.__sUrl = sUrl

  def checkUrl(self, sUrl):
    return True

  def getUrl(self):
    return self.__sUrl

  def getMediaLink(self):
    return self.__getMediaLinkForGuest()

  def __getMediaLinkForGuest(self):
    log("Generate direct media link from %s" % self.__sUrl)

    # Get the video id from the link
    sPattern = 'http://(?:www.)?videozer.com/(?:embed|video)?/(.*?)$'
    oParser = cParser()
    aResult = oParser.parse(self.__sUrl, sPattern)

    if not aResult[0]:
      log("The link does not contain a video id.", LOGERROR)
      return [False, ""]

    oRequest = cRequestHandler(cHoster.SETTINGS_URL + aResult[1][0])
    sHtmlContent = oRequest.request()

    # Try to load the datas from the sHtmlContent. This data should be json styled.
    aData = loads(sHtmlContent)

    # Decode the link from the json data settings.
    sMediaLink = b64decode(aData["cfg"]["environment"]["token1"])

    log("Generated direct media link %s" % sMediaLink)

    return [True, sMediaLink]
