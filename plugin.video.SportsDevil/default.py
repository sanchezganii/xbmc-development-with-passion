import xbmc, xbmcgui
import sys, os, re
import urllib, urllib2
import xbmcaddon


__plugin__ = 'SportsDevil'
__author__ = 'MaxMustermann'
__url__ = ''
__svn_url__ = ''
__credits__ = 'VideoDevil developers'
__version__ = '1.6.5.1'
__settings__ = xbmcaddon.Addon(id='plugin.video.SportsDevil')
__cwd__ = __settings__.getAddonInfo('path')

rootDir = ( os.path.join( __cwd__, 'resources', 'lib' ) )
if rootDir[-1] == ';':rootDir = rootDir[0:-1]

class Main:
  def __init__(self):
    self.pDialog = None
    self.curr_file = ''
    self.run()

  def run(self):
    from lib import main
    main.Main()

win = Main()
