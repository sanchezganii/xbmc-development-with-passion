# -*- coding: latin-1 -*-

class CList(object):
    
    def __init__(self):
        self.start = ''
        self.section = ''
        self.sort = ''
        self.cfg = ''
        self.skill = ''
        self.reference = ''     # for HTTP Header
        self.content = ''       # -"-
        self.items = []
        self.rules = []
        self.curr_url = ''

    def getVideos(self):
        return filter(lambda x: x['type'] == 'video', self.items)