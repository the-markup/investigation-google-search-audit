"""
Configuration variables
=======================
For web assay and other things!

Author: Leon Yin
"""


import os

# Variables for the Selenium client
headless = True
user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1'
width = 375 # width of iPhoneX screen in pixels
height = 812 # height of iPhoneX screen 
window_size = (width, height)

# some pixel sizes for analysis
viewport_width = 363
header = 160

# color values for stains
blue = "#6cb1ee"
red = "#ea4335"
yellow = "#fbbc05"
green = "#34a853"
white = "#ffffff"
black = "#b2b2b2"

# the first word before hyphens in element categories are the keys.
cat2color = {
    'organic' : black,
    'amp' : blue,
    'answer' : green,
    'link' : yellow,
    'ads' : red,
}

# opacity = .9

# lists for preprocessing
javascript = [
    '#', 
    'javascript:void(0);', 
    'javascript:void(0)'
]

# domains of interest
google_domains = [
    'google.com',
    'youtube.com',
    'googleadservices.com'
]

# this is for annotations for utils/draw.py
font_file = '/Library/Fonts/Arial.ttf'