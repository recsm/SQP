#!/bin/bash

echo "Script Starting.."
echo "start For loop"
for pic in `ls *.png`
do
    echo "converting $pic"
    newname=`echo $pic | sed -e 's/^\(.*\)\.png$/\1\.gif/g'`
    convert $pic $newname
done
echo "finished"

