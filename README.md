picasa2xmp
==========

[picasa2xmp](https://github.com/ckeller42/picasa2xmp) is a command line tool to extract face tag information from picasa ini files and contacts and storing it as xmp sidecar files.

Dependencies
------------

[picasa3meta](https://github.com/vosbergw/picasa3meta) is needed for reading the picasa database. (btw the metaSave tool was used as a template for this script)
Additionally exiv2 and exiftool is needed.

Why do I need xmp sidecar files when I can store everything in the jpeg?
-----------------------------------------------------------------------

The [xmp specification](https://partners.adobe.com/public/developer/en/xmp/sdk/XMPspecification.pdf) describes sidecar files only for raw data. For jpeg images the xmp information is stored in the image. Thats why lightroom does not parse sidecar files for jpegs.
This can be a real pain if you have an incremental backup solution.
Every metadata modification changes the file and causes an increase in my backup space.
Fortunately digikam and darktable also work with xmp sidecar files for jpegs.
If you have a image file (e.g. test.jpg) the corresponding sidecar file should be names test.jpg.xmp


So what does this script do?
----------------------------

It processes all picasa.ini files in the specified folder and stores the
updated xmp files in the specified output meta data folder.

```
> ./picasa2xmp.py --photos <imagefolder> --dest <outmetafolder>
```

If there already is a xmp file with the original image this file is used and update.
If there is no xmp file a sidecar file from the image is created. 
Face rectangles are then added as `xmp mwg-rs.Regions`.
Additionally `HierarchicalSubject` tags of the form `people|Name` are added to the xmp file.


Todo
----

This script is still under testing and is a quick hack.
Always make a backup of your data.
It currently uses exiv2 and exiftool for adding the xmp data to the files.
Would be great to change this to pyexiv2 but I was to lazy to do that yet.
