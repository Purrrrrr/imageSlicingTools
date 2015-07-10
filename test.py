from PIL import Image
from lib import getImageColumns, getImageRows, Continuous, Irregular
from slices import pruneSlices, longestContinuousSlice
import os, sys

infile = sys.argv[1]
image = Image.open(infile)
print image.size

columns = getImageColumns(image);
rows = getImageRows(image);

print "Rows: ",rows
print "Columns: ",columns

def pickLongestSlide(slices):
    slices = pruneSlices(slices)
    longest = longestContinuousSlice(slices)
    if longest is None:
        return slices

    newslices = []
    if (longest[1] > 0):
        newslices.append((Irregular,0, longest[1]))

    newslices.append(longest) 

    endPoint = slices[-1][1]+slices[-1][2]
    if (longest[1]+longest[2] < endPoint):
        newslices.append((Irregular,longest[1]+longest[2], endPoint-(longest[1]+longest[2])))

    return newslices

rows = pickLongestSlide(rows)
columns = pickLongestSlide(columns)

print "Picked rows: ",   rows
print "Picked columns: ",columns

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
        print box, saveTo
        cropped.save(saveTo)

