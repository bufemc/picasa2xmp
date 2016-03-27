#!/usr/bin/env python
'''

This file is part of picasa2xmp.

picasa2xmp is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

picasa2xmp is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with metaSave.  If not, see <http://www.gnu.org/licenses/>.


Copyright 2016 Christoph G. Keller <christoph.keller@gmx.net>

Parts from metaSave from Wayne Vosberg <wayne.vosberg@mindtunnel.com> 
have been used.

'''

import argparse
import os
import re
import sys
import fnmatch
import shutil

sys.path.append(os.path.join(os.getenv("HOME"), 'src', 'picasa3meta' ))
from picasa3meta import thumbindex, pmpinfo, iniinfo, exiv2meta, contacts




def testSys():
    cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK) for path in os.environ["PATH"].split(os.pathsep))

    if not cmd_exists('exiv2'):
        print "Need exiv2 command line tool"
        sys.exit(5)
        
    if not cmd_exists('exiftool'):
        print "Need exiftool command line tool"
        sys.exit(5)



def locatedir(pattern, start):
    '''Search for a directory'''
    for path, dirs, files in os.walk(os.path.abspath(start)):
        for d in fnmatch.filter(dirs, pattern):
            yield os.path.join(path, d)


def locate(pattern, start):
    '''Search for a file'''
    for path, dirs, files in os.walk(os.path.abspath(start)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


def writexmp(imgfname, outDir, rects, names):
    ''' Write the data to a xmp file'''

    # we need a base xmp file first
    origxmp = imgfname + '.xmp'
    xmpfname = imgfname.replace(os.path.dirname(imgfname), outDir) + '.xmp'
    
    if not os.path.isfile(origxmp):
        cmd = 'exiv2 -f -eX -l %s %s ' % (outDir, imgfname)

        result = os.system(cmd)
        if result != 0:
            return
        tmpxmp = imgfname.replace(os.path.dirname(imgfname), outDir)
        tmpxmp, file_extension = os.path.splitext(tmpxmp)
        tmpxmp = tmpxmp + '.xmp'
        shutil.move(tmpxmp, xmpfname)
    else:
        shutil.copyfile(imgfname + '.xmp', xmpfname)
        
    
    cmd = 'exiv2 -M "set Xmp.mwg-rs.Regions/mwg-rs:RegionList ''" %s' % xmpfname
    os.system(cmd.encode('utf-8'))

    for idx, item in enumerate(names):
        cmd = 'exiv2 -M \"set Xmp.mwg-rs.Regions/mwg-rs:RegionList[%d]/mwg-rs:Name \"%s" \" %s' % (idx+1, names[idx], xmpfname)
        os.system(cmd.encode('utf-8'))
        cmd = 'exiv2  -M \"set Xmp.mwg-rs.Regions/mwg-rs:RegionList[%d]/mwg-rs:Type Face \" %s' % (idx+1, xmpfname)
        os.system(cmd.encode('utf-8'))
        cmd = 'exiv2 -M \"set Xmp.mwg-rs.Regions/mwg-rs:RegionList[%d]/mwg-rs:Area/stArea:x %f \" %s' % (idx+1, rects[idx][0], xmpfname)
        os.system(cmd.encode('utf-8'))
        cmd = 'exiv2 -M \"set Xmp.mwg-rs.Regions/mwg-rs:RegionList[%d]/mwg-rs:Area/stArea:y %f \" %s' % (idx+1, rects[idx][1], xmpfname)
        os.system(cmd.encode('utf-8'))
        cmd = 'exiv2 -M \"set Xmp.mwg-rs.Regions/mwg-rs:RegionList[%d]/mwg-rs:Area/stArea:w %f \" %s' % (idx+1, rects[idx][2], xmpfname)
        os.system(cmd.encode('utf-8'))
        cmd = 'exiv2 -M \"set Xmp.mwg-rs.Regions/mwg-rs:RegionList[%d]/mwg-rs:Area/stArea:h %f \" %s' % (idx+1, rects[idx][3], xmpfname)
        os.system(cmd.encode('utf-8'))
        cmd = 'exiv2 -M \"set Xmp.mwg-rs.Regions/mwg-rs:RegionList[%d]/mwg-rs:Area/stArea:unit normalized\" %s' % (idx+1, xmpfname)
        os.system(cmd.encode('utf-8'))

        s = re.sub(r'^"|"$', '', names[idx])
        cmd = 'exiftool -q -q  -overwrite_original -XMP:HierarchicalSubject+=\"people|%s\" %s' % (s, xmpfname)
        os.system(cmd.encode('utf-8'))

        
def parseFaces(L):
    ''' 
    
    '''
    imgrects=[]
    irects=L.split(':')
    irects=irects[1]
    irects=irects.split(';')
    for currect in irects:
        currect=currect[ currect.find("(")+1 : currect.find(")") ]
        
        # get the face rectangle
        x0 = float(int(currect[0:4],16))/65536
        y0 = float(int(currect[4:8],16))/65536
        x1 = float(int(currect[8:12],16))/65536
        y1 = float(int(currect[12:16],16))/65536
        w = x1 - x0
        h = y1 - y0
        pxrect=[x0, y0, w, h]
        imgrects.append(pxrect)

    return imgrects

def parseNames(L):
    '''
    '''
    ifaces=L.split(':')
    ifaces=ifaces[1]
    imgfaces=ifaces.split(',')
    return imgfaces

def main():
    '''

    
    '''

    parser = argparse.ArgumentParser(
        description=
        "Collect all the image metadata I can find into one place.")
    parser.add_argument(
     '--path', action="store", dest='path', type=str, default="",
     help="Path to the Picasa database files. " \
     "If left off, search $HOME for directory Picasa3 containing " \
     "directories db3 and contacts")
    parser.add_argument(
     '--photos', action="store", dest="source", type=str, required=True,
     help="Path to the photo tree.  This directory tree will be "\
     "duplicated at <dest>/<basename of tree>.meta and all meta data "\
     "from the pmp databases, .picasa.ini files and exif info will be "\
     "placed there.\n**NOTHING UNDER THIS DIRECTORY WILL BE MODIFIED**")
    parser.add_argument(
        '--dest',
        action="store",
        dest="dest",
        type=str,
        default=os.getcwd(),
        help="Where to create the metadata tree.  Defaults to $CWD")
    args = parser.parse_args()

    if args.path == "":  # Picasa3/db3 not specified, look for it under $HOME
        for path in locatedir("Picasa3", os.environ['HOME']):
            if os.path.exists(os.path.join(path,"db3")) and \
             os.path.exists(os.path.join(path,"contacts")):
                args.path = path
                break

    # make sure the Picasa3 db files exist
    try:
        contactFile = locate("contacts.xml", args.path).next()
    except:
        print "error: contacts.xml  was " \
           "not found in any subdirectory under %s"%args.path
        return 2

    if args.path == "":
        print "no Picasa3 directory found in %s" % os.environ['HOME']
        print "please specify using --path"
    else:
        source = os.path.abspath(args.source)
        dest = os.path.abspath(os.path.join(args.dest, os.path.basename(source)
                                            + ".meta"))

        if re.match(source, args.dest):
            print "Destination (%s) is a subdirectory of source (%s)." \
             "  To avoid recursion I require these to be different." \
             "  Please change your working directory or specify a " \
             "destination with --dest"%(args.dest,source)
            return 2

        if os.path.exists(dest) :
            print "Destination (%s) already exists. "\
             "In order to be absolutely sure I do not overwrite " \
             "anything I require that the destination directory does not " \
             "previously exist. Please delete it or specify a different " \
             "destination with --dest"%dest
            #return 2


        con = contacts.Contacts(contactFile)
        
        iniO = []
        for ini in locate(".picasa.ini", source):
            iniO.append(iniinfo.IniInfo(ini, con))
                
        for myIni in iniO:
            curdestdir = myIni.filePath
            curdestdir = curdestdir.replace(source,dest)

            try:
                os.makedirs(curdestdir, 0750)
            except:
                pass
            
            for imageFile, iniEntrys in myIni.contents.iteritems():
                if imageFile == 'Contacts' or imageFile == 'Contacts2':
                    continue
                if not os.path.exists(os.path.join(myIni.filePath, imageFile)):
                    continue
                
                faces = []
                names =[]
                try:
                    for iniEntry in iniEntrys:
                        if iniEntry.startswith('faces'):
                            faces = parseFaces(iniEntry)
                        elif iniEntry.startswith('sfaces'):
                            names = parseNames(iniEntry)
                except:
                    pass

                writexmp(os.path.join(myIni.filePath, imageFile), curdestdir, faces, names)


if __name__ == "__main__":
    testSys()
    sys.exit(main())
