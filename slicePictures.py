#!/usr/bin/python
from PIL import Image
from files import writeFile, readFile
from imageslicer import getImageAreas, combineAreas
import pystache
import argparse
import os, sys, subprocess
from tempfile import NamedTemporaryFile

cliParser = argparse.ArgumentParser(
          description="slicePictures - slice a picture into pieces that stand out from the background")
cliParser.add_argument("-t", "--treshold", 
        default=0,
        help="How far away a color can be from the background color to be consider a part of the background",
        required=False)
cliParser.add_argument("-b", "--background", 
        help="Give the background color to use either in the css rgb ff00ff syntax or as tuple (1,20,124)",
        required=False)
cliParser.add_argument("-s", "--minimumSize", 
        help="Give the minimum width and height of an image to cut. Smaller images are combined to form larger ones. The size is given in the format 100x100. The default is 16x16",
        required=False)
cliParser.add_argument("infile", help="Input file")
cliParser.add_argument("outfile", help="Output file naming schema. The filename, path and extension will be used in saving the images and accompanying CSS and HTML files")

args = cliParser.parse_args()
infile = args.infile
outfile = args.outfile
targetFilename =  ".".join(outfile.split(".")[:-1])
extension = "."+outfile.split(".")[-1]

def parseColor(colorStr):
    print(colorStr)
    if colorStr[0] == "#":
        colorStr = colorStr[1:]
        l = 2 if len(colorStr) in (6,8) else 1
        colors = [colorStr[x:x+l] for x in range(0,len(colorStr),l)]
        if l == 1:
            colors = map(lambda c: c+c, colors)
        colors = map(lambda x: int(x,16), colors)
        return tuple(colors)
    else:
        colors = colorStr.split(",")
        colors = map(int, colors)
        return tuple(colors)
    return None

def parseSize(sizeStr):
    size = sizeStr.split("x")
    return tuple(map(int, size))

backgroundColor = parseColor(args.background) if args.background else None
minimumSize = parseSize(args.minimumSize) if args.minimumSize else (16,16)
treshold = int(args.treshold) if args.treshold else 0

image = Image.open(infile)
(imageWidth, imageHeight) = image.size
print "Size of image ",image.size, "mode is ",image.mode

displayer = "display"
namedFiles = []

for area in combineAreas(getImageAreas(image, backgroundColor, treshold), minimumSize):
    size = area.size()

    print "Displaying", area

    cropped = image.crop(area.bounds)
    tmpFile = NamedTemporaryFile(delete=False)
    cropped.save(tmpFile, format="png")
    p = subprocess.Popen(["display", tmpFile.name])
    
    identifier = None
    try:
        identifier = raw_input("What is the #id or .class of the image shown just now? Just press enter to skip saving it\n");
        if identifier[0] not in ("#", "."):
            name = identifier
            identifier = "#"+identifier
        else:
            name = identifier[1:]

    except KeyboardInterrupt, e:
        break
    except:
        pass
    finally:
        os.unlink(tmpFile.name)
        p.kill()
    
    if identifier: 
        cropped.save(os.path.dirname(targetFilename)+"/"+name+extension)
        namedFiles.append((identifier,name+extension,area))

css = ""
innerhtml = ""
scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
cssTemplate = readFile(scriptPath+"/templates/imageArea.css")
htmlTemplate = readFile(scriptPath+"/templates/testbox.html")

for (identifier,filename,area) in namedFiles:
    css += pystache.render(cssTemplate, {
        "identifier": identifier,
        "filename": filename,
        "left": area.bounds[0],
        "top": area.bounds[1],
        "width": area.bounds[2]-area.bounds[0],
        "height": area.bounds[3]-area.bounds[1],
        "right": imageWidth-area.bounds[2],
        "bottom": imageHeight-area.bounds[3]
        })
    if identifier[0] == '.':
        innerhtml += "<div class='"+identifier[1:]+"'></div>\n"
    else: 
        innerhtml += "<div id='"+identifier[1:]+"'></div>\n"

html = pystache.render(htmlTemplate, {"name": os.path.basename(targetFilename), "html": innerhtml})

writeFile(targetFilename+".css",css)
writeFile(targetFilename+".html",html)

