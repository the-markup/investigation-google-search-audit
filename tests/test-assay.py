"""
This should test that a browser can open up.
Check the browser's params.

Test that google search works once.
Then on a set in inputs
"""
import os
import sys
import time
import random
import unittest
import inspect
import glob
import warnings
warnings.filterwarnings('ignore')

sys.path.append('../')
from utils.config import (
    window_size,
    user_agent,
    cat2color
)
import utils.parsers as P
from utils.analysis import (
    GoogleWebAssay,
    paint_abstract_representation
)

parser_functions = [
    o[1] for o in inspect.getmembers(P)
    if inspect.isfunction(o[1]) and
    '_parser' in o[0]
]
len(parser_functions)

headless = False
data_dir = '../data/test/input_local_searches'
intermediate_dir = '../data/test/intermediate_local_searches'
for d in [data_dir, intermediate_dir]:
    os.makedirs(d, exist_ok=True)

def get_context(fn):
    '''
    Get file paths for output files
    '''
    fn_metadata = fn.replace(data_dir, intermediate_dir) \
                    .replace('.html', '.ndjson') \
                    .replace('webpage_raw', 'parsed_meta') \
                    .replace('html/', 'json/')
    
    fn_stained_html = fn.replace(data_dir, intermediate_dir) \
                        .replace('.html', '_stained.html') 
    
    fn_screenshot = fn.replace(data_dir, intermediate_dir) \
                      .replace('.html', '_screenshot.png') \
    
    fn_abstract_img = fn_screenshot.replace('screenshot', 
                                            'abstract_painting')
    
    return fn_metadata, fn_stained_html, fn_screenshot, fn_abstract_img

class TestAssay(unittest.TestCase):
    '''
    This class contains three functions that are run in the order 
    (the name of the first and last matter!).
    '''
    refresh_searches = False
    
    @classmethod
    def setUpClass(self):
        """
        Set up the emulator
        """        
        self.user_agent = user_agent
        self.window_size = window_size
        self.parser_functions = parser_functions
        self.color_palette = cat2color
        self.headless = headless
        self.files_input = glob.glob(os.path.join(
            data_dir, '*.html')
        )
        print(len(self.files_input))
        self.assay = GoogleWebAssay(user_agent = self.user_agent,
                                   window_size = self.window_size,
                                   parser_functions = self.parser_functions,
                                   color_palette = self.color_palette,
                                   headless = self.headless)
        
    
    def test_open_local_file(self):
        success = False
        fn = self.files_input[0]
        print(fn)
        try:
            self.assay.open_local_html(fn)
            success = True
        except Exception as e:
            print(e)
            pass
        self.assertTrue(success)
        
    def screenshot(self):
        pass
    def run_assay(self):
        success = False
        fn = self.files_input[0]
        fn_metadata, _, fn_screenshot, fn_abstract_img = get_context(fn)
        print(_)
        try:
            self.assay.run(fn, 
                           fn_metadata=fn_metadata, 
                           stain=False)
            success = True
        except Exception as e:
            print(e)
            pass
        self.assertTrue(success)
            
    def run_assay_stain(self):
        success = False
        fn = self.files_input[0]
        fn_metadata, _, fn_screenshot, fn_abstract_img = get_context(fn)
        try:
            self.assay.run(fn, 
                           fn_metadata=fn_metadata, 
                           fn_stained_html=_,
                           stain=True)
            success = True
        except Exception as e:
            print(e)
            pass
        self.assertTrue(success)
        
    def test_run_assay_on_files(self):
        success = False        
        try:
            for fn in self.files_input[1:]:
                fn_metadata, _, fn_screenshot, fn_abstract_img = get_context(fn)
                self.assay.open_local_html(fn)
                self.assay.screenshot_full(fn_screenshot)
                self.assay.run(fn, 
                               fn_metadata=fn_metadata, 
                               fn_stained_html=_,
                               stain=True)
                paint_abstract_representation(fn_metadata=fn_metadata,
                                  fn_out=fn_abstract_img.replace('.png', '_img.png'),
                                  fn_img=fn_screenshot)
                
            success = True
        except Exception as e:
            print(e)
            pass
        
        self.assertTrue(success)
        

    def full_run_assay(self):
        pass
    def compare_metadata(self):
        pass
    
    @classmethod
    def tearDownClass(self):
        """
        Close the emulator
        """
        self.assay.close_driver()
          
if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestDriver.refresh_searches = sys.argv.pop()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=ImportWarning)
        unittest.main()