#!/usr/bin/env python
from optparse import OptionParser
import os
import ConfigParser
import shutil
import plistlib

SIZES = (16, 32, 48)
RESULT_FILENAME_FORMAT = "{size}_{basename}{extension}"
class SourceThemeInvalid(Exception):
    pass

class DestinationInvalid(Exception):
    pass


def _strip_prefix(filename):
    return filename.replace("gnome-mime-", "")


def _find_symlinks_in_path(path, plist):
    if 'Synonyms' not in plist:
        plist['Synonyms'] = {}
    synonyms = plist['Synonyms']
    for filename in os.listdir(path):
        file = os.path.join(path, filename)
        if os.path.islink(file):
            link_to = os.path.basename(os.readlink(file))
            link_to_id = os.path.splitext(_strip_prefix(link_to))[0]
            link_from_id = os.path.splitext(_strip_prefix(filename))[0]
            if link_from_id in synonyms and link_to_id!=synonyms[link_from_id]:
                print "Warning! Multiply values for symlink {filename} -> {link_to}".format(filename=filename, link_to=link_to)
            if link_from_id!=link_to_id:
                synonyms[link_from_id] = link_to_id


def _safe_mkdir(dirname):
    try:
        os.mkdir(dirname)
    except OSError:
        if not os.path.exists(dirname) or not os.path.isdir(dirname):
            raise DestinationInvalid


def _copy_icons(path, size, destination):
    for filename in os.listdir(path):
        file = os.path.join(path, filename)
        if os.path.isfile(file):
            basename, ext = os.path.splitext(filename)
            new_filename = RESULT_FILENAME_FORMAT.format(size=size, basename=_strip_prefix(basename), extension=ext)
            new_file_path = os.path.join(destination, new_filename)
            shutil.copyfile(file, new_file_path)
            print "{oldfile} -> {newfile}".format(oldfile=file, newfile=new_file_path)


def generate_icons_from_gnome_theme(source, destination):
    index_theme_path = os.path.join(source, "index.theme")
    if not os.path.exists(index_theme_path):
        raise SourceThemeInvalid
    config = ConfigParser.RawConfigParser()
    config.read(index_theme_path)
    directories = config.get("Icon Theme", "Directories").split(",")
    paths = []
    actual_sizes = set()
    paths_by_sizes = {}
    for directory in directories:
        size = config.getint(directory, "Size")
        context = config.get(directory, "Context")
        itype = config.get(directory, "Type")

        if context.lower()=="mimetypes" and itype.lower()=="fixed" and size in SIZES:
            path = os.path.join(source, directory)
            paths.append(path)
            if size in paths_by_sizes:
                raise SourceThemeInvalid
            paths_by_sizes[size] = path
            actual_sizes.add(size)

    plist = {"Info":{
        "ThemeName": config.get("Icon Theme", "Name"),
        "ThemeComment": config.get("Icon Theme", "Comment"),
        "Sizes":list(actual_sizes),
        "FilenameFormat":RESULT_FILENAME_FORMAT
    }
    }

    destination_icons = os.path.join(destination, "Icons")
    _safe_mkdir(destination_icons)

    for size, path in paths_by_sizes.items():
        _find_symlinks_in_path(path, plist)
        _copy_icons(path=path, size=size, destination=destination_icons)

    plist_filename = os.path.join(destination, "FileTypeIcons.plist")
    plistlib.writePlist(plist, plist_filename)


    

if __name__=="__main__":
    parser = OptionParser()

    parser.add_option("-i", "--input-directory", dest="input", default="Faenza",
                  help="path to GNOME theme", metavar="INPUT_DIRECTORY")
    parser.add_option("-o", "--output-directory", dest="output", default=os.path.join("..", "Resources"),
                      help="path to output Resources directory")

    (options, args) = parser.parse_args()
    generate_icons_from_gnome_theme(source=options.input, destination=options.output)