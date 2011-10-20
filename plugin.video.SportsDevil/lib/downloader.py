# -*- coding: latin-1 -*-

from string import *
from helpers import *

import sys, os.path
import re, string

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

class Downloader:
    def __init__(self, language):
        self.pDialog = None
        self.language = language

    def downloadMovie(self, url, path, title, extension):
        if not os.path.exists(path):
            log('Path does not exist')
            return None
        if title == '':
            log('No title given')
            return None

        file_path = xbmc.makeLegalFilename(os.path.join(path, title + extension))
        file_path = urllib.unquote_plus(file_path)
        # Overwrite existing file?
        if os.path.isfile(file_path):
            dia = xbmcgui.Dialog()
            if not dia.yesno('Overwrite?', file_path):
                title = getKeyboard(default = urllib.unquote_plus(title), heading = self.language(30102))
                if not title:
                    return None
                file_path = xbmc.makeLegalFilename(os.path.join(path, title + extension))
                file_path = urllib.unquote_plus(file_path)
        try:
            # Setup progress dialog and download
            self.pDialog = xbmcgui.DialogProgress()
            self.pDialog.create('SportsDevil', self.language(30050), self.language(30051))
            urllib.urlretrieve(url, file_path, self.video_report_hook)
            self.pDialog.close()
            return file_path
        except IOError:
            self.pDialog.close()
            dia = xbmcgui.Dialog()
            dia.ok('SportsDevil Info', self.language(30053))
        except KeyboardInterrupt:
            self.pDialog.close()
            pass
        return None


    def video_report_hook(self, count, blocksize, totalsize):
        percent = int(float(count * blocksize * 100) / totalsize)
        self.pDialog.update(percent, self.language(30050), self.language(30051))
        if self.pDialog.iscanceled():
            raise KeyboardInterrupt
