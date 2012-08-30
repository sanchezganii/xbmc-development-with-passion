# -*- coding: utf-8 -*-

import xbmc, xbmcgui
import urllib
import os

import zipfile

repo_url = 'http://xbmc-development-with-passion.googlecode.com/svn/branches/custom/'
pluginDataDir = xbmc.translatePath('special://profile/addon_data/plugin.video.SportsDevil')
customModulesDir = os.path.join(pluginDataDir, 'custom')


def get_dir_listing(url):
    httptag = "http://"
    if url[:7] != httptag:
        url = httptag+url
    parts = url.split("/")
    site = parts[0]
    dir = "/" + "/".join(parts[1:])

    f = urllib.urlopen(url)
    response = f.read()

    text = response.split("\n")
    urls = []
    tag=' href="'
    for line in text:
        if tag in line.lower():
            for i, c in enumerate(line):
                # print line[i:i+len(tag)].lower()
                if tag == line[i:i+len(tag)].lower():
                    # print line.strip("\n")
                    #                             <tr><td><a id="nav" href="Newsletter.html">Newsletter</a></td></tr>
                    # extract the url
                    textline = line[i+len(tag):]
                    # print textline.strip("\n")
                    # Newsletter.html">Newsletter</a></td></tr>
                    end = textline.find('"')
                    # print end 15
                    u = textline[:end]
                    if not httptag in u and not ".." in u and not "&#109;&#97;&#105;&#108;&#116;&#111;&#58;" in u and not "mailto:" in u:
                        if url[-1] != "/":
                            u = url+"/"+u
                        else:
                            u = url+u
                        if not "/." in u:
                            urls.append(u)

    return urls


def download(url, file_path):
    urllib.urlretrieve(url, file_path)
    return os.path.isfile(file_path)


def extract(file, dir):                
    if not dir.endswith(':') and not os.path.exists(dir):
        os.mkdir(dir)

    zf = zipfile.ZipFile(file)

    for i, name in enumerate(zf.namelist()):
        if not name.endswith('/'):
            outfile = open(os.path.join(dir, name), 'wb')
            outfile.write(zf.read(name))
            outfile.flush()
            outfile.close()
                

if not os.path.exists(customModulesDir):
    os.makedirs(customModulesDir, 0777)

xbmc.executebuiltin( "ActivateWindow(busydialog)" )
files = get_dir_listing(repo_url)
xbmc.executebuiltin( "Dialog.Close(busydialog)" )

menuItems = map(lambda x: x.replace(repo_url,'').replace('.zip',''), files)

select = xbmcgui.Dialog().select('Select module', menuItems)
if select != -1:
    target = os.path.join(customModulesDir, menuItems[select] + '.zip')
    
    xbmc.executebuiltin( "ActivateWindow(busydialog)" )
    success = download(files[select], target)
    xbmc.executebuiltin( "Dialog.Close(busydialog)" )

    dlg = xbmcgui.Dialog()
    if success:
        extract(target, customModulesDir)
        os.remove(target)
        
        # refresh container if SportsDevil is active
        currContainer = xbmc.getInfoLabel('Container.FolderPath')
        if currContainer == 'plugin://plugin.video.SportsDevil/':
            xbmc.executebuiltin('Container.Refresh()')
        
        dlg.ok('SportsDevil Info', 'Download successful')
    else:
        dlg.ok('SportsDevil Info', 'Download failed')
