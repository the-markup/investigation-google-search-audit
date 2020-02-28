"""
Analysis utils
Author - Leon Yin

This script contains the WebAssay base class and GoogleWebAssay class.
These scripts are used to create web drivers, identify different kinds
of elements on a web page, calculate area, and stain the page.
"""

import os
import sys
import time
import warnings
import inspect
from subprocess import Popen, PIPE
from typing import Union, Dict, List
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from PIL import Image
import selenium
from selenium import webdriver
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup, element


from .config import (
    cat2color,
    google_domains 
)

def xpath_prune(df : pd.DataFrame,
                col : str = 'xpath') -> pd.DataFrame:
    """
    For a list of xpaths, removes all children where parent is present.
    This is to avoid substrings that are duplicate-like.
    
    First we get all unique xpaths, sort them, then iterate through in pairs.
    Within each pair, we check if the xpath is in the nextpath, suggesting that the xpath
    might be a parent.
    
    If the nextpath is a child of the xpath parent, we look at subseqent xpaths against
    the xpath parent.
    """
    xpaths = df[col].unique().tolist()
    xpaths.sort()
    children_with_parent = []
    for i in range(len(xpaths) - 1):
        # get the current xpath and the next xpath
        xpath = xpaths[i]
        nextpath = xpaths[i + 1]
        # check if the xpath hasn't already been processed
        if xpath in children_with_parent:
            continue

        # check if the xpath is in the next xpath.
        if xpath in nextpath:
            children_with_parent.append(nextpath)
            # check subsequents
            for nextpath_ in xpaths[i + 1:]:
                if xpath in nextpath_:
                    children_with_parent.append(nextpath_)
                else:
                    continue
    # filter out children
    xpaths_childless = [x for x in xpaths if x not in children_with_parent]
    df = df[df[col].isin(xpaths_childless)]
    
    return df

def hierarchy(df, check_list, col='xpath'):
    """
    Respects an xpath hierarchy.
    If there is a xpath clash, then the xpath in `df` is removed.
    df in this case must "bend the knee."
    checks_list > df
    """
    xpaths = df[col].unique().tolist()    
    override = []
    for xpath in xpaths:
        # check if check_list has parents of anything in xpath
        if any([x in xpath for x in check_list]):
            override.append(xpath)
        # check if xpath is parent to anything in check_list
        elif any([xpath in x for x in check_list]):
            override.append(xpath)
    df = df[~df[col].isin(override)]
    return df
         
    
def paint_abstract_representation(fn_metadata, fn_out, 
                                  fn_img = None, verbose=False,
                                   script = '../utils/draw_img.py'):
        """
        Turns the results of the stain into an abstract representaion.
        This calls a script written in p5. The functions don't work in notebooks.
        Read more about the function here:
        
        Giving a reference image draws the abstract over the reference image.
        """
        if not os.path.exists(fn_metadata):
            raise ValueError(f"The input file {fn_metadata} does not exist.")
        command = [
            'python', script,
            '--input', fn_metadata,
            '--output', fn_out,
        ]
        
        if fn_img:
            command += ['--img',  fn_img]
        if verbose:
            print(' '.join(command))
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        return stdout

class WebAssay:
    """
    This is a base class that is built ontop a Selenium driver.
    
    Inherit from this class to
    1. parse web pages, 
    2 calculate the area and position of elements, and 
    3. stain HTML page for parsed elements.
    
    It can be used as a base class for variants of WebAssay.
    You must implement a `run` function to use thie base class.
    """
    def __init__(self, 
                 user_agent : str, 
                 window_size : tuple, 
                 headless = False, 
                 parser_functions : List = [], 
                 color_palette : Dict = {},
                 warpped_height_px : int = 700, 
                 reset_driver_after : int = 50):
        """
        `headless` should be set to True if you want a headless web browser.
        `color_palette` is a dictionary that maps from element category to a 
          hex color.
        `parser_functions` a list of parser functions. 
          Where a parser function takes bs4, and returns a list of dictionaries. 
          Be sure to make one of those keys contains `category`, 
          if you're using a `color_pallette` and want to stain images.
        `warpped_height_px` is the minimum y-distance in pixels to consider 
          an element warpped.
        """
        # functions that take bs4 and return a list of dicts.
        self.parser_functions = parser_functions
        if len(self.parser_functions) == 0:
            raise ValueError("Please assign parser_functions!")
        
        # browser params
        self.window_size = window_size
        self.width, self.height = window_size
        self.user_agent = user_agent
        self.headless = headless
        self._init_browser()
        
        # optional params
        self.color_palette = color_palette # dictionary of category to color.
        self.warpped_height = warpped_height_px # skip elements whose height exceeds.

        # friends we make along the way
        self.error_files = [] # which files are not parsed correctly?
        self.element_metadata = pd.DataFrame() # the most recent element metadata.
        self.driver_reset_counter = 0 # driver will reset at `reset_driver_after`.
        self.reset_driver_after = reset_driver_after

    
    def _init_browser(self):
        """
        Initalizes a selenium browser with proper `user_agent` and window `size`.
        Set `headless` to True to have a headless browser. 
        Keep the default as False to help debug.
        """
        self.display = False
        if self.headless:
            self.display = Display(visible = 0,
                                   size=(self.width + 10, 
                                         self.height + 10))
            self.display.start()

        # Set up user agent
        profile = webdriver.FirefoxProfile() 
        profile.set_preference("general.useragent.override", 
                               self.user_agent)
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        driver = webdriver.Firefox(profile, 
                                   capabilities=firefox_capabilities)
        driver.set_window_size(*self.window_size)
        self.driver = driver

    
    def close_driver(self):
        """Closes the driver"""
        self.driver.quit()
        if not isinstance(self.display, bool):
            self.display.stop()
    
    def restart_driver(self):
        """Restarts drivers and display"""
        self.close_driver()
        self._init_browser()
        self.driver_reset_counter = 0
        time.sleep(2)
        
    def save_source(self, fn : str):
        """Saves the source code of a page."""
        with open(fn, 'w') as f:
            f.write(self.driver.page_source)
        
    def screenshot_full(self, fn : str):
        """
        Takes a full screenshot. There are other methods that work
        better with a headless browser (such as expanding the window).
        
        The screenshot is resized to the original dimensions.
        For whatever reason, I get higher res images by the default
        screenshot.
        
        The standard size allows us to mark up the screenshot with the
        element metadata in `paint_abstract_representation`.
        """
        body = self.driver.find_element_by_tag_name('body')
        body.screenshot(fn)
        
        # resize image
        img = Image.open(fn)
        img.thumbnail((body.rect['width'], 1e6), 
                      Image.ANTIALIAS)
        img.save(fn)
        
    def identify_elements(self, body : Union[element.Tag, 
                          element.NavigableString]) -> List:
        """ 
        Runs every parser in `self.parser_functions` through the web page.
        The results are appended to the `data` output.
        """
        data = []
        for parser in self.parser_functions:
            results = parser(body)
            data.extend(results)
        return data
    
    def stain_element(self,
                      xpath : str, 
                      category : str,
                      color : str = '#ffffff',
                      opacity : float = 0.9) -> bool:
        """
        Alters the HTML of a page.
        Stains elements located in `xpath` with `color` by overwritting style.
        Also sets a new param of markup_category = `category`.
        """
        try:
            elm = self.driver.find_element_by_xpath(xpath)
        except: # couldn't find element
            return False
        if not elm.is_displayed(): 
            return False
        
        style = elm.get_attribute('style')
        custom_style = f"background-color: {color} !important; " \
                        f"outline-color: {color} !important; " \
                        f"outline-style: solid !important; " \
                        f"opacity: {opacity}"
        if style:
            style += '; ' + custom_style
        else:
            style = custom_style

        self.driver.execute_script(
            f"arguments[0].setAttribute('style','{style}')", elm
        )
        self.driver.execute_script(
            f"arguments[0].setAttribute('markup_category','{category}')", elm
        )
        
        return True

    def _calc_area(self, 
                   rect : dict,
                   width : int = 1e6,
                   height : int = 1e6) -> float:
        """
        Given a `rect` from selenium, 
        (see the `rect` module from selenium elements)
        we're able to locate the coordinates of corners
        of a rectangular element and calculate the area.

        Set the `width` and `height` params to create boundries.
        `np.clip` will restrict the given `h` and `w` to
        the bounds of the screen.
        """
        x = rect.get('x')
        # take care of neg values
        x = np.clip(x, a_min=0, a_max=1e6)
        y = rect.get('y')
        h = rect.get('height')
        w = rect.get('width')

        # calculate the top left X coord, top right X coord
        tl_x = np.clip(x,     0, width)
        tr_x = np.clip(x + w, 0, width)
        # and the top right Y coord and bottom right Y coord
        tr_y = np.clip(y,     0, height)
        br_y = np.clip(y + h, 0, height)

        # calculate the width and height (length) of the rectangle and the area.
        rect_w = tr_x - tl_x 
        rect_h = br_y - tr_y
        rect_a = rect_w * rect_h

        return rect_a
    
    def calculate_element_area(self, xpath : str) -> Dict:
        """
        Selenium will try to find an element based on the `xpath`.
        If it is found, calculate the `area` that element occupies 
        on first screen (`area`) and whole page (`area_page`).
        
        If the element is warpped or empty, return an empty dict.
        """
        # get the element based on the xpath
        try:
            elm = self.driver.find_element_by_xpath(xpath)
        except: # couldn't find element
            return {}
    
        # get dimensions of element
        rect = elm.rect
        # skip warped elements
        if rect['height'] >= self.warpped_height:
            return {'is_warpped' : True}

        # adjust the dimensions by clipping if necessay
        if elm.is_displayed():    
            area = self._calc_area(rect, *self.window_size)
            area_page = self._calc_area(rect, width=self.width)
            meta = {
                'xpath' : xpath,
                'dimensions' : elm.size,
                'location' : elm.location,
                'area' : area,
                'area_page' : area_page,
            }
            
            return meta
    
    def open_local_html(self, fn):
        """Opens a local HTML page in the emulator."""
        local_file = 'file://' + os.path.abspath(fn)
        if self.driver.current_url != local_file:
            self.driver.get(local_file)

    def run(self):
        """
        This function must be overwritten in the inherited class.
        
        Should contain the following steps:
        1. Read either the current page on the driver or a local HTML file 
           `fn` into bs4...
           
        2. Identify elements by sending the contents of the HTML through each 
           parser in `parser_functions`. 
           Do this by calling `self.identify_elements()` on the page.
           
        3. For each element, `self.calculate_element_area()`, 
           and optionally `self.stain_element()` if self.stain = True.
           
        4. Assign `self.element_metadata` with the latest element metadata.
        
        And then anything else is up to you.
        """
        raise NotImplementedError
        
        
class GoogleWebAssay(WebAssay):
    """
    It is used to parse Google search results.
    Specifically, it identifies elements by categories,
    stains them unique colors, and measures their expression
    on a web page.
    """
    def _record_error(self, fn, msg):
        """
        Logs an error and sets the element_metadata to zero.
        """
        error_msg = {
            'fn' : fn, 
            'error' : msg
        }
        self.error_files.append(error_msg)
        self.element_metadata = pd.DataFrame()
    
    def run(self, 
            fn : str = None, 
            fn_metadata : str = None, 
            fn_stained_html : str = None,
            stain : bool = False):
        """
        Calculates the area of elements, and optionally stains the page
        
        If no `fn`, uses the current page the driver is on.
        if `fn_metadata` or `fn_stained_html` are set, the contents
        will be written to these files.
        """
        # read the file into beautiful soup, go directly to search results.
        if fn:
            self.open_local_html(fn)
            self.input_filestream = open(fn).read()
        else:
            self.input_filestream = self.driver.page_source
        soup = BeautifulSoup(self.input_filestream)
        # Isolate the search results and remove footers and headers .
        for div in soup.find_all("div", {'id' : 'sfooter'}): 
            div.decompose()
        body = soup.find("div", attrs={'id' : 'cnt'})
        if not body:
            self._record_error(fn, 'No body of search result')
            return
        # HTMl -> initial dataframe of element metadata.
        elements = self.identify_elements(body)
        df = pd.DataFrame(elements)
        
        # split the organic elements from other elements
        non_google = df[~df.domain.isin(google_domains)]
        google = df[df.domain.isin(google_domains)]

        # remove review ratings from Google links. Links > Reviews
        xpath_links = df[df.category.isin(['link', 'organic'])].xpath.tolist()
        review_rating = google[google.category == 'answer-reviews_rating']
        google[google.category == 'answer-reviews_rating'] = \
            hierarchy(review_rating, xpath_links)
        google = google[~google.xpath.isnull()]
        
        # remove organic links from Ads. Ads > Organic links
        xpath_ads = google[
            google.category.str.contains('ads-')
        ].xpath.tolist()
        non_google = hierarchy(non_google, xpath_ads)

        # drop any duplicated elements that share the same xpath
        google.drop_duplicates(subset='xpath', inplace=True)
        non_google.drop_duplicates(subset='xpath', inplace=True)

        # drop children of parent xpaths
        google = xpath_prune(google, col="xpath")
        non_google = xpath_prune(non_google, col="xpath")

        # combine the organic and non-organic dataframes
        element_metadata_ = google.append(non_google)

        # Using XPATH, estimate the size of each element, and markup the html.
        rect_meta = []
        for _, elm in element_metadata_.iterrows():
            xpath = elm['xpath']
            category = elm['category']
            elm_area_meta = self.calculate_element_area(xpath)
            # stain things if we assign a color pallete.
            if self.color_palette and stain:
                color = self.color_palette.get(category.split('-')[0], '#ffffff')
                self.stain_element(xpath, color=color, category=category)
            # check that the response is OK. if warpped, quit.
            if not elm_area_meta:
                continue
            if elm_area_meta.get('is_warpped'):
                self._record_error(fn, 'Warpped element, page is corrupt.')
                return
            else:
                rect_meta.append(elm_area_meta)
        # Put the area metadata into a dataframe
        df_area = pd.DataFrame(rect_meta)
        if df_area.empty:
            self._record_error(fn, 'Empty area for entire page.')
            return
        # merge the element metadata with the area metadata based on xpath.
        df_area.xpath.drop_duplicates(inplace=True)
        df_area.location.astype(str).drop_duplicates(inplace=True)
        element_metadata = element_metadata_.merge(df_area, 
                                                   on='xpath', 
                                                   how='inner')
        # add a column, and save the metadata as a param.
        element_metadata.loc[:, 'fn_input'] = fn        
        self.element_metadata = element_metadata

        # save the merged element metadata
        if isinstance(fn_metadata, str):
            element_metadata.to_json(fn_metadata,
                                     orient='records',
                                     lines=True)
        # save the stained HTML
#         if isinstance(fn_stained_html, str):
#             with open(fn_stained_html, 'w') as f:
#                 f.write(self.driver.page_source)
                
        # restart the driver after 50 files
        if self.driver_reset_counter:
            self.driver_reset_counter += 1
            if self.driver_reset_counter >= self.reset_driver_after:
                self.restart_driver()