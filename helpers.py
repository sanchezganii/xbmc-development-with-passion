import os
from zipfile import ZipFile, ZIP_DEFLATED
from contextlib import closing


def zipdir( basedir, archivename, includeBaseDir=False, startAt=None):
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(basedir):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                if startAt:
                    zfn = absfn[len(startAt):]
                else:
                    zfn = absfn[len(basedir)+len(os.sep):] #if you want to use the relative path (basedir excluded)
                if includeBaseDir:
                    z.write(absfn, absfn)
                else:
                    z.write(absfn, zfn)
    return archivename


def getFileContent(filename):
    try:
        f = open(filename,'r')
        txt = f.read()
        f.close()
        return txt
    except:
        return ''

def setFileContent(data, filename):
    try:
        # write data to the file
        open( filename, "w" ).write( data )
    except Exception, e:
        # oops
        print "An error occurred saving %s file!\n%s" % ( filename, e, )


def yn_choice(message, default='y'):
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = raw_input("%s (%s) " % (message, choices))
    values = ('y', 'yes', '') if default == 'y' else ('y', 'yes')
    return True if choice.strip().lower() in values else False
