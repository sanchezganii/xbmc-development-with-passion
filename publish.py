import os, sys
import re
from helpers import *
import md5
from zipfile import ZipFile, ZipInfo

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
                zipfile = os.path.join(repoPath, addon, addon + '-' + version + '.zip')
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
        # generate files
        self._generate_addons_file()
        self._generate_md5_file()
        # notify user
        print "Finished updating addons xml and md5 files"

    def _generate_addons_file( self ):
        # addon list
        addons = os.listdir(repoPath)
        # final addons text
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n"
        # loop thru and add each addons addon.xml file
        for addon in addons:
            relPath = os.path.join(repoPath, addon)
            try:
                # skip any file or .svn folder
                if ( not os.path.isdir(relPath) or addon == ".svn" ): continue

                # get all zip files
                newestZip = ''
                for files in os.listdir(relPath):
                    if files.endswith(".zip"):
                        if newestZip == '':
                            newestZip = files
                        else:
                            t1 = os.path.getctime(os.path.join(relPath,files))
                            t2 = os.path.getctime(os.path.join(relPath,newestZip))
                            if t1 > t2:
                                newestZip = files
                try:
                    with ZipFile(os.path.join(relPath, newestZip), 'r') as myzip:
                        myzip.extract(addon + '/addon.xml', relPath)
                        sourcexml = os.path.join(relPath, addon, 'addon.xml')
                        targetxml = os.path.join(relPath, 'addon.xml')
                        if os.path.isfile(targetxml):
                            os.remove(targetxml)
                        os.rename(sourcexml, targetxml)
                        os.rmdir(os.path.join(relPath, addon))
                except Exception, e:
                    print(e)

                # create path
                _path = os.path.join( relPath, "addon.xml" )
                # split lines for stripping
                xml_lines = open( _path, "r" ).read().splitlines()
                # new addon
                addon_xml = ""
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if ( line.find( "<?xml" ) >= 0 ): continue
                    # add line
                    addon_xml += unicode( line.rstrip() + "\n", "UTF-8" )
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
            except Exception, e:
                # missing or poorly formatted addon.xml
                print "Excluding %s for %s" % ( _path, e, )
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u"\n</addons>\n"
        # save file
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
