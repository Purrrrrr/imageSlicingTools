# imageSlicingTools

Contains two tools to slice an image file to pieces.
One for slicing a container box image to a resizable HTML container box,
and another to grab a bunch of pictures in a transparent png and save them to separate image files
with an accompanying CSS file with a record of their positions.

The tools depend on the pillow imaging library for python
and the sass tool to compile some SCSS.

# slicebox.py

Slices a box image to pieces trying to figure out
which portions of the image can be repeated.

Usage:
slicebox.py box.png target/box.png

The above generates the following files in the dir target:
* box.html (The code for the box itself)
* box.scss (SCSS stylesheet for the box)
* box.css  (CSS stylesheet for the box)
* box-test.html (A standalone test file to see the result in a browser)
* box_top_left.png, box_top_right.png, etc. (The image files for the box)

#slicePictures.py

Given a transparent png, slices it into its constituent parts.
It then shows the using the "display" utility and asks you to name each of
them. The ones you name are saved with that name and a HTML and CSS file
are generated to show how to position the sliced images in an HTML page.

slicePictures.py images.png target/images.png

The above generates the files target/images.html and target/images.css
plus an image in the target directory for each subimage you named.
