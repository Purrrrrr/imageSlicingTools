def writeFile(filename,data):
  with open(filename, "w") as file:
    file.write(data);

def readFile(filename):
  print "Writing ",filename, "..."
  with open(filename, "r") as file:
    return file.read()
