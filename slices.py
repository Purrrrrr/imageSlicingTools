from lib import Continuous, Irregular

def mergeSlices(slice1,slice2):
    isIrregular = slice1[0] is Irregular or slice2 is Irregular
    newType = Irregular if isIrregular else Continuous

    return (newType, slice1[1], slice1[2]+slice2[2])

def combineSlicesOfSameType(slices):
    newSlices = []
    curSlice = slices[0]

    for cur in slices[1:]:
      if cur[0] is curSlice[0]:
          curSlice = mergeSlices(curSlice, cur)
      else:
          newSlices.append(curSlice)
          curSlice = cur

    if curSlice[2] > 0:
        newSlices.append(curSlice)

    return newSlices


def longestContinuousSlice(slices):
    longest = (None,0,0)

    for cur in slices:
        if cur[0] == Continuous and cur[2] > longest[2]:
            longest = cur

    if longest[0] is None:
        return None
    
    return longest

def pruneSlices(slices, treshold = 5):
    newSlices = []
    curSlice = slices[0]

    for cur in slices[1:]:
      if cur[2] <= treshold:
          curSlice = mergeSlices(curSlice, cur)
      else:
          newSlices.append(curSlice)
          curSlice = cur

    if curSlice[2] > 0:
        newSlices.append(curSlice)

    return combineSlicesOfSameType(newSlices)
