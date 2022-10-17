#!/bin/bash

curl -X GET \
  <UrlToFile> \
  -o sendvid.py

file1="/users/pi/updater/repo/file.py"
file2="/users/pi/updater/file.py"

if cmp -s "$file1" "$file2"; then
    # same, do nothing
    echo "same"
else
    # different
    echo "different"
    cp $file1 $file2

    reboot
fi
