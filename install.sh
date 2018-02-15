#!/bin/bash

cat header.txt > shape.txt
sed -e "s/	[0-9]*$//" code.txt >> shape.txt
txt2mb shape.txt shape.mb
cp shape.mb ~/.config/fcitx/table
fcitx -r 2> /dev/null
