"""
Painting Abstractions
Leon Yin

Order
1. Google Answers
2. Google Links
3. Ads
4. Organic
5. AMP
6. Google link buttons
"""

import os
import sys
import json
import time
import tempfile
import argparse
import tempfile

from PIL import Image
import s3
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

from config import (
    width,
    cat2color, 
    white, 
    data_dir_in,
    data_dir_metadata,
    data_dir_abstract,
    font_file,
    is_local
)

parser = argparse.ArgumentParser()
parser.add_argument('--input', nargs='?', const=1, type=str, 
                    help='What is the filepath for the input JSON?')
parser.add_argument('--output', nargs='?', const=1, type=str, 
                    help='What is the filepath for the output IMG')
parser.add_argument('--img', nargs='?', const=None, type=str, 
                    help='What is the filepath for the reference IMG')
args = vars(parser.parse_args())

# read the file into Pandas and set some global variables...
fn = args['input']
fn_img = args['img']
fn_out = args['output']
fn_img_out = args['output'].replace('.png', '_img.png')

# check if the file exists
# if os.path.exists(fn_out):
#     sys.exit()
    
# make directory
dir_name = os.path.dirname(fn_out)
if dir_name:
    os.makedirs(dir_name, exist_ok=True) 

# read the file
df = pd.read_json(fn, lines=True)

print(len(df))

# What font to use?
# font = create_font(font_file, 16) 
if fn_img:
    img = load_image(fn_img)

def setup():
    if fn_img:
        size(img.width, img.height)
    else:
        furthest_element = df.location.str.get('y').max()
        furthest_element_height = df[df.location.str.get('y') == furthest_element].dimensions.str.get('height')
        length = int(furthest_element_height + furthest_element + 10)
        size(375, length)
    no_loop()

def draw():
    background('#ffffff')
    no_stroke()
    
    # draw non-organic elements
    for i, row in df[(df.area_page != 0) & 
                     (~df.category.isin(['organic', 'ads']))].iterrows():
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
                     (df.category == 'ads')].iterrows():
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
                     (df.category == 'organic')].iterrows():
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

    # save the file...
    save(fn_out)
    os.rename(fn_out.replace('.png', 
                             '0000.png'), fn_out)
    # draw reference image
    exit()

if __name__ == '__main__':
    run()