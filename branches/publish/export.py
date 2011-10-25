import os, sys
import re
import shutil
from helpers import *

repoPath = "../repo/"
addonsPath = "../addons/"

class Test:
    """
        Copies all addon folders to a test installation of xbmc
    """
    def __init__( self, source='', target=''):
        #self.source = source
        #self.target = target

        # copy files
        if source != '':
            self._copy(source, target)
        else:
            self._copyAll(target)

        # notify user
        print "Finished"


    def _copy(self, source, target):
        sourcePath = os.path.join(addonsPath, source)
        if not os.path.isdir(sourcePath):
            print "Source not found: " + sourcePath
        elif not os.path.isdir(target):
            print "Target not found: " + target
        else:
            destPath = os.path.join(target, source)
            if os.path.isdir(destPath):
                shutil.rmtree(destPath)
            shutil.copytree(sourcePath, destPath)
            print 'Exported "' + source + '" to "' + target + '"'


    def _copyAll(self, target):
        addons = os.listdir(addonsPath)
        for addon in addons:
            destPath = os.path.join(target, addon)
            try:
                if os.path.isdir(destPath):
                    if not yn_choice('Overwrite "' + addon + '"'):
                        print 'Skipped "' + addon + '"'
                        continue
                    shutil.rmtree(destPath)
                shutil.copytree(os.path.join(addonsPath, addon), destPath)
                print 'Exported "' + addon + '"'

            except Exception, e:
                print(e)

if ( __name__ == "__main__" ):
    if len(sys.argv) > 1:
        source = ''
        if len(sys.argv) == 2:
            target = sys.argv[1]
        else:
            source =  sys.argv[1]
            target = sys.argv[2]

        # start
        Test(source, target)
    else:
        print "No arguments specified. Start with addon folder and targetPath"


