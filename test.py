from PIL import Image
from lib import getImageColumns, getImageRows, Continuous, Irregular
from slices import pickLongestSlide
import pystache
import os, sys

infile = sys.argv[1]
image = Image.open(infile)
print "Size of image ",image.size

columns = getImageColumns(image);
rows = getImageRows(image);

print "Rows: ",rows
print "Columns: ",columns

rows = pickLongestSlide(rows)
columns = pickLongestSlide(columns)

print "Picked rows: ",   rows
print "Picked columns: ",columns

if len(rows) == 1 and len(columns) == 1:
    print "Nothing to slice!"
    exit()

def addPrefixesToBorders(slices, prefixList):
    if len(slices) == 1:
        return [("", slices[0])]
    def getPrefix(prefixList, slice):
        if slice[0] is Irregular:
            return prefixList.pop(0)
        return ""
      
    return [(getPrefix(prefixList, slice), slice) for slice in slices]

rowSlices = addPrefixesToBorders(rows, ["_top", "_bottom"])
columnSlices = addPrefixesToBorders(columns, ["_left", "_right"])

print rowSlices
print columnSlices

outfile = sys.argv[2]
filename =  ".".join(outfile.split(".")[:-1])
extension = "."+outfile.split(".")[-1]

#Image generation
for (rowprefix, row) in rowSlices:
    for (columnprefix, column) in columnSlices:
        #(left, upper, right, lower)
        top = row[1]
        left = column[1]
        width = column[2]
        height = row[2]

        if (column[0] is Continuous):
            left += width//2
            width = 1

        if (row[0] is Continuous):
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
    template = "horizonalbox"
elif len(columns) == 1:
    template = "verticalbox"

scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
htmlTestTemplate = scriptPath+"/templates/testbox.html"
htmlTemplate = scriptPath+"/templates/"+template+".html"
scssTemplate = scriptPath+"/templates/"+template+".scss"

with open(htmlTestTemplate, "r") as file:
    htmlTestTemplate = file.read()

with open(htmlTemplate, "r") as file:
    htmlTemplate = file.read()

with open(scssTemplate, "r") as file:
    scssTemplate = file.read()

html = pystache.render(htmlTemplate, values)
scss = pystache.render(scssTemplate, values)
htmlTest = pystache.render(htmlTestTemplate, {"name": boxName, "html": html})

with open(filename+"-test.html", "w") as file:
    file.write(htmlTest)

with open(filename+".html", "w") as file:
    file.write(html)

with open(filename+".scss", "w") as file:
    file.write(scss)

