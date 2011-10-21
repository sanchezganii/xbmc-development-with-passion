import os, sys
import re
from helpers import *
import md5
from zipfile import ZipFile
from distutils.version import StrictVersion, LooseVersion

repoPath = "../repo/"
addonsPath = "../addons/"


class Packer:
    """
        Packs all addons as zip archives and move them into the corresponding repo folder.
    """
    def __init__( self ):
        # pack files
        self._pack_addons()
        # notify user
        print "Finished packing addons"


    def _pack_addons(self):
        addons = os.listdir(addonsPath)
        for addon in addons:
            relPath = os.path.join(addonsPath, addon)
            if not os.path.isdir(relPath): continue
            try:
                xmlfile = os.path.join(relPath, 'addon.xml')
                version = self._get_version(xmlfile)
                targetPath = os.path.join(repoPath, addon)
                if not os.path.isdir(targetPath):
                    os.mkdir(targetPath)
                zipfile = os.path.join(targetPath, addon + '-' + version + '.zip')
                zipdir(relPath, zipfile, False, addonsPath)

            except Exception, e:
                print(e)


    def _get_version(self, addonxml):
        data = getFileContent(addonxml)
        r = re.compile('(?:id|name)="[^"]+"\s*version="([^"]+)"', re.DOTALL + re.IGNORECASE)
        m = r.findall(data)
        if m:
            return m[0]

class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """
    def __init__( self ):
        self.addon_xmls = []
        # generate files
        self._generate_addons_file()
        self._generate_md5_file()
        # notify user
        print "Finished updating addons xml and md5 files"


    def _get_newer_file(self, file1, file2):
        t1 = os.path.getctime(file1)
        t2 = os.path.getctime(file2)
        if t1 > t2:
            return file1
        else:
            return file2


    def _get_highest_version(self, zips):
        name = ''
        versions = []
        r = re.compile('(.*?)-(\d+\.\d+.*?)\.zip', re.DOTALL + re.IGNORECASE)
        for zipfile in zips:
            m = r.findall(zipfile)
            if m:
                name = m[0][0]
                versions.append(m[0][1])

        highestVersion = ''
        for version in versions:
            if highestVersion == '':
                highestVersion = version
                continue
            else:
                if LooseVersion(highestVersion) < LooseVersion(version):
                    highestVersion =  version

        return name + '-' + highestVersion + '.zip'


    def _generate_addons_file( self ):
        # addon list
        addons = os.listdir(repoPath)

        # loop thru and add each addons addon.xml file
        for addon in addons:
            relPath = os.path.join(repoPath, addon)
            try:
                # skip any file or .svn folder
                if ( not os.path.isdir(relPath) or addon == ".svn" ): continue

                # get all zip files
                zips = []
                for files in os.listdir(relPath):
                    if files.endswith(".zip"):
                        zips.append(files)

                # find ZIP file with highest version
                newestZip = self._get_highest_version(zips)

                # get addon.xml from this file and store its content
                try:
                    with ZipFile(os.path.join(relPath, newestZip), 'r') as myzip:
                        tmpxml = myzip.read(addon + '/addon.xml').splitlines()
                        offset = 0
                        if ( tmpxml[0].find( "<?xml" ) >= 0 ):
                            offset=1
                        tmpxml = "\n".join(tmpxml[offset:]).strip()
                        self.addon_xmls.append(tmpxml)
                except Exception, e:
                    print(e)

            except Exception, e:
                print(e)

        # final addons.xml text
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n"
        addons_xml += "\n".join(self.addon_xmls).strip()
        addons_xml += u"\n</addons>\n"

        # save addons.xml
        setFileContent(addons_xml.encode( "UTF-8" ), os.path.join(repoPath, 'addons.xml') )


    def _generate_md5_file( self ):
        try:
            # create a new md5 hash
            m = md5.new( open( os.path.join(repoPath, 'addons.xml') ).read() ).hexdigest()
            # save file
            setFileContent(m, os.path.join(repoPath, 'addons.xml.md5') )
        except Exception, e:
            # oops
            print "An error occurred creating addons.xml.md5 file!\n%s" % ( e, )




if ( __name__ == "__main__" ):
    # start
    Packer()
    Generator()
