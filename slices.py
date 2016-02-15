from imageslicer import Continuous, Irregular

def mergeSlices(slice1,slice2):
    return (Irregular, slice1[1], slice1[2]+slice2[2])

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
    curSize = curSlice[2]

    for cur in slices[1:]:
      if curSize < treshold and cur[2] <= treshold:
          curSlice = mergeSlices(curSlice, cur)
      else:
          newSlices.append(curSlice)
          curSlice = cur
          curSize = cur[2] 

    if curSlice[2] > 0:
        newSlices.append(curSlice)

    return combineSlicesOfSameType(newSlices)

def pickBoxSlices(slices, firstPrefix, secondPrefix):
    slices = pruneSlices(slices)
    longest = longestContinuousSlice(slices)
    if longest is None:
        return [('',)+slice for slice in slices]

    newslices = []
    if (longest[1] > 0):
        newslices.append((firstPrefix, Irregular,0, longest[1]))

    newslices.append(('',) + longest)

    endPoint = slices[-1][1]+slices[-1][2]
    if (longest[1]+longest[2] < endPoint):
        newslices.append((secondPrefix, Irregular,longest[1]+longest[2], endPoint-(longest[1]+longest[2])))

    return newslices
