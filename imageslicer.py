from PIL import Image

def eq(pix1, pix2):
  return pix1 == pix2

def pixelsNearEnough(pix1, pix2, treshold=4):
  for (val1, val2) in zip(pix1, pix2):
    if abs(val1-val2) > treshold:
      return False
  return True

def rowsEqual(image, row1,row2, treshold = 0):
    dissimilar = 0
    treshold = image.size[1]*treshold
    equal = pixelsNearEnough if image.mode in ('RGA', 'RGBA') else eq

    for x in range(image.size[0]):
        if not equal(image.getpixel((x,row1)),image.getpixel((x,row2))):
            dissimilar += 1
        if dissimilar > treshold:
            return False

    return True

def columnsEqual(image, column1,column2, treshold = 0):
    dissimilar = 0
    treshold = image.size[0]*treshold
    for y in range(image.size[1]):
        if image.getpixel((column1, y)) != image.getpixel((column2, y)):
            dissimilar += 1
        if dissimilar > treshold:
            return False

    return True

class C:
  def __repr__(self):
    return "Continuous"

class I:
  def __repr__(self):
    return "Irregular"

Continuous = C()
Irregular = I()

def getImageSlices(image, isContinuous, stop, start = 0):
  currentType  = None
  currentStart = start
  currentLen   = 1
  #slice :: (Type,Starting position, length)
  slices = []

  for x in range(start, stop-1):
    newType = Continuous if isContinuous(image, x,x+1) else Irregular
    if currentType is newType or currentType is None:
      currentLen += 1;
      currentType = newType
    else:
      slices.append((currentType, currentStart, currentLen))
      currentType  = None
      currentStart = x+1
      currentLen   = 1
  
  if currentLen > 0:
    slices.append((currentType, currentStart, currentLen))

  return slices

def getImageColumns(image):
  stop = image.size[0]
  return getImageSlices(image, columnsEqual, stop)

def getImageRows(image):
  stop = image.size[1]
  return getImageSlices(image, rowsEqual, stop)

class PixelSet:
  __counter = 0

  def __init__(self, pixel):
    self.set = set(pixel)
    self.bounds = list(pixel) + [pixel[0]+1, pixel[1]+1]
    self.mergedTo = None
    self.identity = PixelSet.__counter
    PixelSet.__counter += 1

  def addPixel(self,pixel):
    if self.mergedTo:
      return self.mergedTo.addPixel(pixel)
    self.set.add(pixel)
    self.bounds[0] = min(self.bounds[0], pixel[0])
    self.bounds[1] = min(self.bounds[1], pixel[1])
    self.bounds[2] = max(self.bounds[2], pixel[0]+1)
    self.bounds[3] = max(self.bounds[3], pixel[1]+1)
  
  def mergeTo(self, other):
    if self is other:
      return
    if other.mergedTo:
      return self.mergeTo(other.mergedTo)
    if self.mergedTo:
      return self.mergedTo.mergeTo(other)
    
    other.identity = self.identity
    other.mergedTo = self
    self.bounds[0] = min(self.bounds[0], other.bounds[0])
    self.bounds[1] = min(self.bounds[1], other.bounds[1])
    self.bounds[2] = max(self.bounds[2], other.bounds[2])
    self.bounds[3] = max(self.bounds[3], other.bounds[3])

  def size(self):
    return (self.bounds[2]-self.bounds[0], self.bounds[3]-self.bounds[1])
  def center(self):
    return (self.bounds[0]+self.bounds[2]/2, self.bounds[1]+self.bounds[3]/2)
  def width(self):
    return self.bounds[2]-self.bounds[0]
  def height(self):
    return self.bounds[3]-self.bounds[1]

  def __str__(self):
    return "PixelSet with bounds "+str(self.bounds)+" and size "+str(self.size())

def isNotTransparent(pixel, treshold):
  return pixel[3] > treshold

def getImageAreas(image, backgroundColor = None, treshold = 0):
  width = image.size[0]
  areas = []
  lastRowSets = [None for _ in range(width)]
  
  if backgroundColor:
    if len(backgroundColor) < 4 and image.mode == "RGBA":
      backgroundColor = backgroundColor+(255,)
    isOpaque = lambda x: x != backgroundColor

    if treshold > 0:
      isOpaque = lambda x: not pixelsNearEnough(x, backgroundColor, treshold)

  else: 
    if image.mode != "RGBA": 
      raise Exception('Only the RGBA picture format is supported')
    isOpaque = lambda x: isNotTransparent(x, treshold)

  for y in range(image.size[1]):
    currentRowSets = [None for _ in range(width)]
    currentSet = None
    for x in range(width):
      pos = (x,y)
      if isOpaque(image.getpixel(pos)):
        if currentSet:
          currentSet.addPixel(pos)
        else:
          currentSet = PixelSet(pos)
          areas.append(currentSet)
        
        if lastRowSets[x] is not None and lastRowSets[x].identity != currentSet.identity:
          currentSet.mergeTo(lastRowSets[x])

      else:
        currentSet = None

      currentRowSets[x] = currentSet

    lastRowSets = currentRowSets 

  
  return filter(lambda a: a.mergedTo is None, areas)

def combineAreas(areas, minSize):
  (minW, minH) = minSize
  isLargeEnough = lambda area: area.width() > minW and area.height() > minH
  largeEnough = filter(isLargeEnough, areas)
  tooSmall = filter(lambda x: not isLargeEnough(x), areas)

  def isNear(area,other,minSize):
    (x1,y1)= area.center()
    (x2,y2) = other.center()
    (w1,h1)= area.size()
    (w2,h2) = other.size()
    
    if abs(x1-x2)-(w1-w2)/2 > minSize[0]:
      return False
    if abs(y1-y2)-(h1-h2)/2 > minSize[1]:
      return False

    return True
    
  for area in tooSmall:
    for area2 in tooSmall:
      if area.identity == area2.identity: 
        continue
      if isNear(area, area2, minSize):
        area.mergeTo(area2)

  return largeEnough + filter(lambda a: a.mergedTo is None, tooSmall)
  

