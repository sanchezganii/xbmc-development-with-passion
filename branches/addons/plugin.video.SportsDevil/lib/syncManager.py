# -*- coding: latin-1 -*-

import os
import urllib
from urlparse import urlparse

import utils.regexUtils as rU
import utils.scrapingUtils as sU
import utils.fileUtils as fU
import utils.githubUtils as github


# enums

class SyncSourceType:
    CATCHERS = 1
    MODULES = 2    


# entities

class SyncManager:
    def __init__(self):
        self.sources = []
    
    def __getSourceByName__(self, name):
        found = filter(lambda x : x.name == name, self.sources)
        if found and len(found) > 0:
            return found[0]
        return None
    
    def addSource(self, name, sourceType, url):
        if not self.__getSourceByName__(name):
            self.sources.append(SyncSource(name, sourceType, url))
    
    def removeSource(self, name):
        source = self.__getSourceByName__(name)
        if source:
            self.sources.remove(source)
    
    def setSourceEnabledState(self, name, enabled):
        source = self.__getSourceByName__(name)
        if source:
            source.enabled = enabled
    
    def getSources(self):
        if len(self.sources) > 0:
            return map(lambda x : x.name, self.sources)
        else:
            return None
    
    
    def getUpdates(self, sourceType, localCachePath):
        updates = {}
        
        def battleSyncObjects(source, target):
            if source.checksum != target.checksum:
                return source
            else:
                return target
        
        def battleUpdates(uSource, uTarget):
            winner = battleSyncObjects(uSource.source, uTarget.source)
            if winner == uSource.source:
                return uSource
            else:
                return uTarget
            
        def addToUpdates(update):
            if not updates.has_key(update.name):
                updates[update.name] = update
            else:
                updates[update.name] = battleUpdates(update, updates[update.name])
        
        if len(self.sources) == 0:
            return None
                
        local = self.__getLocalFiles__(localCachePath)
        
        for source in self.sources:
            if source.enabled and source.type == sourceType:
                syncObjects = source.getFiles()
                if not syncObjects:
                    continue
                for obj in syncObjects:
                    name = obj.name
                    found = filter(lambda x : x.name == name, local)
                    if found and len(found) > 0:
                        old = found[0]
                        winner = battleSyncObjects(obj, old)
                        if winner == obj:
                            addToUpdates(Update(name, obj, old))
                    else:
                        s = SyncObject()
                        s.name = name
                        s.file = os.path.join(localCachePath, name)
                        s.created = obj.created
                        s.checksum = obj.checksum
                        addToUpdates(Update(name, obj, s))
                            
        return updates
    
    
    def __getLocalFiles__(self, folder):            
        if folder:
            syncObjects = []
            for root, dirs, files in os.walk(folder, topdown = False):
                for name in files:
                    path = os.path.join(root, name)
                    obj = SyncObject()
                    obj.name = name
                    obj.file = path
                    obj.created = fU.lastModifiedAt(path)
                    obj.checksum = github.getGithash(path)
                    syncObjects.append(obj)
            return syncObjects
        
        return None
        
    
class SyncObject:
    def __init__(self):
        self.name = None
        self.file = None
        self.created = None
        self.checksum = None    


class Update:
    def __init__(self, name, source, target):
        self.name = name
        self.source = source
        self.target = target
    
    def do(self):
        if self.source and self.target:
            response = None
            try:
                f = urllib.urlopen(self.source.file)
                response = f.read()
                f.close()
            except:
                return False
                        
            fU.setFileContent(self.target.file, response)
            return True
        
        return False
    
    
class SyncSource:
    def __init__(self, name, sourceType, url):
        self.name = name
        self.type = sourceType
        self.url = url
        self.enabled = True
    
    def getFiles(self):
        url = self.url
        hostName = sU.getHostName(url)
        syncObjects = None
        if hostName == 'github.com':
            syncObjects = self.getFilesAPI()
            if not syncObjects:
                syncObjects = self.getFilesScrape()            
        return syncObjects


    # Attention! API calls are limited to 60 per hour

    def getFilesAPI(self):   
        url = self.url
        parts = urlparse(url)
        cleanPath = parts.path[1:]
        parts = cleanPath.split('/', 5)
        userName = parts[0]
        repoName = parts[1]
        branchName = parts[3]
        
        folderName = None
        if len(parts) > 4:
            folderName = parts[4]

        files = github.getFiles(userName, repoName, branchName, folderName)
        if not files:
            return None
        syncObjects = []
        for f in files:
            obj = SyncObject()
            obj.name = f.path
            obj.file =  "https://github.com/%s/%s/raw/%s/" % (userName, repoName, branchName)
            if folderName:
                obj.file += folderName + "/" 
            obj.file += obj.name
            obj.created = None # would be another request to github api
            obj.checksum = f.sha
            syncObjects.append(obj)
        return syncObjects
    
    def getFilesScrape(self):
        url = self.url
        response = None
        try:
            f = urllib.urlopen(url)
            response = f.read()
            f.close()
        except:
            return None
    
        matches = rU.findall(response, '<td class="content"><a href="([^"]+)"[^>]+id="([^"]+)".*?<td class="age"><time [^<]*title="([^"]+)"')
        if matches:
            syncObjects = []
            for m in matches:
                obj = SyncObject()
                obj.name = m[0].split('/')[-1]
                obj.file = ('https://github.com' + m[0]).replace('blob', 'raw')
                obj.checksum = m[1].split('-')[1]
                obj.created = github.getUpdatedAtFromString(m[2])
                syncObjects.append(obj)
            return syncObjects
        
        return None