from PIL import Image

def eq(pix1, pix2):
  return pix1 == pix2

def pixelsNearEnough(pix1, pix2):
  for (val1, val2) in zip(pix1, pix2):
    if abs(val1-val2) > 5:
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



