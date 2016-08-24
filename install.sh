#!/usr/bin/env bash
# Installs the FadeToSong plugin for Rhythmbox
# Copyright (C) 2016 Pedro Guridi <pedro.guridi@gmail.com>

name=FadeToSong
path=~/.local/share/rhythmbox/plugins/$name
files=( LICENSE $name.plugin $name.py README.md )

if [ -d "$path" ]; then
  rm -rf $path
fi

mkdir -p $path

for file in "${files[@]}"
do
  cp $file $path
done

sudo cp ./org.gnome.rhythmbox.plugins.fadetosong.gschema.xml /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
