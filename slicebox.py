#!/usr/bin/python
from PIL import Image
from imageslicer import getImageColumns, getImageRows, Continuous, Irregular
from slices import pickBoxSlices
from files import writeFile, readFile
import pystache
import os, sys, subprocess

if len(sys.argv) < 3:
    print "Usage: slicebox.py infile.png outfile.png"
    exit()

infile = sys.argv[1]
image = Image.open(infile)
print "Size of image ",image.size

columns = getImageColumns(image);
rows = getImageRows(image);

print "Rows: ",rows
print "Columns: ",columns

rowSlices = pickBoxSlices(rows, "_top", "_bottom")
columnSlices = pickBoxSlices(columns, "_left", "_right")

print "Picked rows: ",   rowSlices
print "Picked columns: ",columnSlices

if len(rows) == 1 and len(columns) == 1:
    print "Nothing to slice!"
    exit()


outfile = sys.argv[2]
filename =  ".".join(outfile.split(".")[:-1])
extension = "."+outfile.split(".")[-1]

#Image generation
for row in rowSlices:
    for column in columnSlices:
        #(left, upper, right, lower)
        (rowprefix, _, top, height) = row
        (columnprefix, _, left, width) = column

        if (column[1] is Continuous):
            left += width//2
            width = 1

        if (row[1] is Continuous):
            top += height//2
            height = 1
        
        box = (left, top, left+width, top+height)
        cropped = image.crop(box)
        saveTo = filename+columnprefix+rowprefix+extension
        print "Saving... ",box, saveTo
        cropped.save(saveTo)

#CSS+HTML generation
boxName = os.path.basename(filename)
values = {
  "left": 0,
  'right':0,
  'top':0,
  'bottom':0,
  'width': image.size[0],
  'height': image.size[1],
  'name': boxName,
  'extension': extension
}

if rowSlices[0][0] != "":
    values["top"] = rows[0][2]
if rowSlices[-1][0] != "":
    values["bottom"] = rows[-1][2]
if columnSlices[0][0] != "":
    values["left"] = columns[0][2]
if columnSlices[-1][0] != "":
    values["right"] = columns[-1][2]

template = "fullbox"
if len(rows) == 1:
    template = "horizontalbox"
elif len(columns) == 1:
    template = "verticalbox"

scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
htmlTestTemplate = readFile(scriptPath+"/templates/testbox.html")
htmlTemplate = readFile(scriptPath+"/templates/"+template+".html")
scssTemplate = readFile(scriptPath+"/templates/"+template+".scss")

html = pystache.render(htmlTemplate, values)
scss = pystache.render(scssTemplate, values)
htmlTest = pystache.render(htmlTestTemplate, 
        {"name": boxName, "html": html})

writeFile(filename+"-test.html", htmlTest)
writeFile(filename+".html", html)
writeFile(filename+".scss", scss)
print "Creating CSS file from SCSS..."
with open(filename+".css", "w") as file:
    subprocess.call(["sass", filename+".scss"], stdout=file)

print "Done"
