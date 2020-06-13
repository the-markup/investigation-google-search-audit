"""
Painting Abstractions
=====================
These scripts utilized the p5 package to visualize how we
categorize and stain Google search pages.

It can operate on a blank canvas, essentially drawing colors to
represent the real estate for each category.

It can also draw directly on a screenshot to display which 
element is which cagegory.

Author: Leon Yin
"""

import os
import sys
import json
import time
import tempfile
import argparse
import tempfile

from PIL import Image
import pandas as pd
from p5 import (
    size, 
    no_loop, 
    no_stroke,
    background,
    fill,
    rect,
    run,
    save,
    text,
    create_font,
    text_font,
    load_image,
    image,
    tint
)

from timeout import timeout
from config import (
    width,
    cat2color, 
    white
)

# command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--input', nargs='?', const=1, type=str, 
                    help='What is the filepath for the input JSON?')
parser.add_argument('--output', nargs='?', const=1, type=str, 
                    help='What is the filepath for the output IMG')
parser.add_argument('--img', nargs='?', const=None, type=str, 
                    help='What is the filepath for the reference IMG')
parser.add_argument('--verbose', nargs='?', const=None, type=int, 
                    help='Should we display updates')
args = vars(parser.parse_args())

# read the file into Pandas and set some global variables...
fn = args['input']
fn_img = args['img']
fn_out = args['output']
fn_img_out = args['output'].replace('.png', '_img.png')
verbose = args['verbose'] == 1

# check if the file exists
if os.path.exists(fn_out):
    if verbose:
        print(f"File {fn_out} exists.")
    sys.exit()
    
# make directory
dir_name = os.path.dirname(fn_out)
if dir_name:
    os.makedirs(dir_name, exist_ok=True) 

# read the file
df = pd.read_json(fn, lines=True)
df.loc[:, 'label'] = df['category'].str.split('-').str.get(0)
if verbose:
    print(f"Drawings {len(df)} shapes.")

if fn_img:
    if verbose:
        print(f"Loading image {fn_img}.")
    img = load_image(fn_img)
    
@timeout(60 * 5)
def setup():
    if verbose:
        print(f"Setting up.")
    if fn_img:
        furthest_element = img.height
        size(img.width, img.height)
    else:
        furthest_element = df.location.str.get('y').max()
        furthest_element_height = df[
            df.location.str.get('y') == furthest_element
        ].dimensions.str.get('height').tolist()[0]
        length = int(furthest_element_height + furthest_element + 10)
        size(375, length)
    if verbose:
        print(f"Length of canvas is {furthest_element} px.")
    no_loop()

@timeout(60 * 5)
def draw():
    if verbose:
        print(f"Drawing background.")
    background('#ffffff')
    no_stroke()
    
    # draw non-organic elements
    if verbose:
        print(f"Drawing shapes...")
    for i, row in df[(df.area_page != 0) & 
                     (~df.label.isin(['organic', 'ads']))].iterrows():
        dimensions = row['dimensions']
        location = row['location']
        category = row['category']
        color = cat2color[category.split('-')[0]]

        h = dimensions['height'] 
        w = dimensions['width']
        x = location['x']
        y = location['y']
        
        c = fill(color)
        rect((x, y), w, h)
        
    for i, row in df[(df.area_page != 0) & 
                     (df.label == 'ads')].iterrows():
        dimensions = row['dimensions']
        location = row['location']
        category = row['category']
        color = cat2color[category.split('-')[0]]

        h = dimensions['height'] 
        w = dimensions['width']
        x = location['x']
        y = location['y']
        
        c = fill(color)
        rect((x, y), w, h)
    
    # draw organic elements
    for i, row in df[(df.area_page != 0) & 
                     (df.label == 'organic')].iterrows():
        dimensions = row['dimensions']
        location = row['location']
        category = row['category']
        color = cat2color[category.split('-')[0]]

        h = dimensions['height']
        w = dimensions['width']
        x = location['x']
        y = location['y']
        
        c = fill(color)
        rect((x, y), w, h)
    
    # draw buttons elements
    for i, row in df[(df.area_page != 0) & 
                     (df.category == 'link-button')].iterrows():
        dimensions = row['dimensions']
        location = row['location']
        category = row['category']
        color = cat2color[category.split('-')[0]]

        h = dimensions['height']
        w = dimensions['width']
        x = location['x']
        y = location['y']
        
        c = fill(color)
        rect((x, y), w, h)
    
    if fn_img:
        tint(255, 60)
        image(img, (0, 0))
    
    if verbose:
        print(f"Saving file")
    
    # save the file...
    save(fn_out)
    os.rename(fn_out.replace('.png', 
                             '0000.png'), fn_out)
    # draw reference image
    if verbose:
        print(f"Done.")
    exit()

@timeout(60 * 3)
def main():
    run()

if __name__ == '__main__':
    main()
