#!/usr/bin/env python
from optparse import OptionParser
import os
import ConfigParser
import shutil
import plistlib
import subprocess

SIZES = (40, 80)
RESULT_FILENAME_FORMAT = "{size}_{basename}{extension}"
BATIK_JAR_PATH = "/Users/darvin/Downloads/batik-1.7/batik-rasterizer.jar"


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


def _copy_icons(path, size, destination, only_basenames=None):
    for filename in os.listdir(path):
        file = os.path.join(path, filename)
        fullfilename = os.path.abspath(file)
        if os.path.isfile(file):
            basename, ext = os.path.splitext(filename)
            basename=_strip_prefix(basename)
            if ext not in (".svg", ".png"):
                continue
            if not only_basenames or basename in only_basenames:
                if ext==".svg":
                    subprocess.call(["/usr/bin/java","-jar",
                                     BATIK_JAR_PATH, fullfilename,
                                     "-m","image/png","-w",str(size), "-h", str(size)])
                    ext = ".png"
                    file = file.replace(".svg", ".png") #fixme

                if only_basenames:
                    new_basename = only_basenames[basename]
                else:
                    new_basename = basename
                new_filename = RESULT_FILENAME_FORMAT.format(size=size, basename=new_basename, extension=ext)
                new_file_path = os.path.join(destination, new_filename)
                shutil.copyfile(file, new_file_path)
                print "{oldfile} -> {newfile}".format(oldfile=file, newfile=new_file_path)


def _get_paths_from_config_for_context(config, directories, source_path, context):

    paths = []
    actual_sizes = set()
    paths_by_sizes = {}

    scalable_dir = None
    for directory in directories:
        size = config.getint(directory, "Size")
        current_context = config.get(directory, "Context")
        itype = config.get(directory, "Type")

        if current_context.lower()==context and (itype.lower()=="fixed" and size in SIZES):
            path = os.path.join(source_path, directory)
            paths.append(path)
            if size in paths_by_sizes:
                raise SourceThemeInvalid
            paths_by_sizes[size] = path
            actual_sizes.add(size)
        if current_context.lower()==context and itype.lower()=="scalable":
            scalable_dir = os.path.join(source_path, directory)

    if scalable_dir:
        for size in SIZES:
            if size not in actual_sizes:
                paths_by_sizes[size] = scalable_dir
                actual_sizes.add(size)
        paths.append(scalable_dir)
    return paths, paths_by_sizes, actual_sizes


def generate_icons_from_gnome_theme(source, destination):
    index_theme_path = os.path.join(source, "index.theme")
    if not os.path.exists(index_theme_path):
        raise SourceThemeInvalid
    config = ConfigParser.RawConfigParser()
    config.read(index_theme_path)
    directories = config.get("Icon Theme", "Directories").split(",")

    paths, paths_by_sizes, actual_sizes = _get_paths_from_config_for_context(config, directories, source, context="mimetypes")

    places_paths, places_paths_by_sizes, places_actual_sizes = _get_paths_from_config_for_context(config, directories, source, context="places")

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

    for size, path in places_paths_by_sizes.items():
        if size in actual_sizes:
            _copy_icons(path=path, size=size, destination=destination_icons, only_basenames={
                "folder":"text-directory",
                "folder-documents":"text-directory-documents",
            })


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