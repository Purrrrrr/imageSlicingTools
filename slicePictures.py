from PIL import Image
from files import writeFile, readFile
from imageslicer import getImageAreas
import pystache
import os, sys, subprocess
from tempfile import NamedTemporaryFile

infile = sys.argv[1]
outfile = sys.argv[2]
targetFilename =  ".".join(outfile.split(".")[:-1])
extension = "."+outfile.split(".")[-1]

image = Image.open(infile)
(imageWidth, imageHeight) = image.size
print "Size of image ",image.size

displayer = "display"
namedFiles = []

for area in  getImageAreas(image):
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
            identifier = "#"+identifier
            name = identifier
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

