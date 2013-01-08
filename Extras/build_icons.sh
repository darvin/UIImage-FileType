#!/bin/sh

FAENZA_URL="https://faenza-icon-theme.googlecode.com/files/faenza-icon-theme_1.3.zip"
BATIK_URL="http://www.gtlib.gatech.edu/pub/apache/xmlgraphics/batik/batik-1.7.zip"
mkdir ./build
#curl $FAENZA_URL > ./build/faenza.zip
#curl $BATIK_URL > ./build/batik.zip

unzip ./build/batik.zip -d ./build/batik
export BATIK_RASTERIZER_PATH=./build/batik/batik-1.7/batik-rasterizer.jar

unzip ./build/faenza.zip -d ./build/faenza

FAENZA_THEME_DIR="./build/FaenzaThemeDirUnpacked"
RESULT_DIR="./Icons"
mkdir $RESULT_DIR

mkdir $FAENZA_THEME_DIR
tar xzf ./build/faenza/Faenza.tar.gz -C $FAENZA_THEME_DIR

python ./generate_icons_from_gnome_theme.py -i $FAENZA_THEME_DIR/Faenza/ -o $RESULT_DIR -f json -s 32 16 64 128
