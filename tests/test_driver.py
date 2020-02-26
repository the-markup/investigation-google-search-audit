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

sys.path.append('../')
from utils.driver_utils import (
    init_browser,
    close_browser,
    scroll_top,
    bot_mitigation,
    search,
    screenshot,
    screenshot_full,
    save_source
)

from config import (
    browser_params
)

def get_context(data_dir : str, 
                keyword : str) -> dict:
    """
    dictionary of file destionations
    """
    context = {
        'local_screenshot_full' : os.path.join(data_dir, 
                                               f"screenshot_full_{keyword}.png"),
        'local_screenshot' :  os.path.join(data_dir, 
                                           f"screenshot_{keyword}.png"),
        'local_html' :  os.path.join(data_dir, 
                                     f"page_source_{keyword}.html")
    }
    
    return context


class TestDriver(unittest.TestCase):
    '''
    This class contains three functions that are run in the order 
    (the name of the first and last matter!).
    '''
    refresh_searches = False
    data_dir = 'data/live_tests'
    os.makedirs(data_dir, exist_ok=True)
    test_keyword = 'doomer girlfriend'
    
    @classmethod
    def setUpClass(cls):
        """
        Set up the emulator
        """
        search_engine = 'google'
        device = 'iPhone X'
        headless = 1

        user_agent = browser_params[device]['user-agent']
        size = browser_params[device]['dimensions']
        
        # create the mobile emulator
        (cls.driver,  cls.display) = init_browser(user_agent=user_agent,
                                         size=size,
                                         headless=headless)
        
        cls.context = get_context(cls.data_dir, 
                                  cls.test_keyword)
       
    def test_internet(self):
        homepage_url = f"http://www.google.com"
        self.driver.get(homepage_url)
        time.sleep(random.randrange(1, 3))
    
    def test_search(self):
        result = search(driver=self.driver, 
                        search_query=self.test_keyword)
        self.assertTrue(result)
    
    def test_bot_mitigation(self):
        result = bot_mitigation(self.driver)
        self.assertTrue(result)
    
    def test_screenshot_full(self):
        result = screenshot_full(self.driver, 
                                 self.context,
                                 is_local=True)
        self.assertTrue(result)
    
    def test_save_source(self):
        result = save_source(self.driver,
                             self.context,
                             is_local=True)
        self.assertTrue(result)
    
    def test_screenshot(self):
        scroll_top(self.driver)
        result = screenshot(self.driver, 
                            self.context, 
                            is_local=True)
        self.assertTrue(result)
            
    def test_workflow(self):
        """
        Test the full workflow... 
        """
        search_inputs = 'data/searches.txt'
        with open(search_inputs, 'r') as f:
            queries = f.read().split('\n')
        for search_query in queries:
            self.context = get_context(self.data_dir, 
                                       search_query)
            if os.path.exists(self.context['local_html']) and not self.refresh_searches:
                continue
            
            result = search(driver=self.driver, 
                            search_query=search_query)
            bot_mitigation(self.driver)
            result = save_source(self.driver,
                             self.context,
                             is_local=True)
            screenshot_full(self.driver, 
                            self.context,
                            is_local=True)
            self.assertTrue(result)
    
    
    @classmethod
    def tearDownClass(cls):
        """
        Close the emulator
        """
        close_browser(cls.driver, cls.display)
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestDriver.refresh_searches = sys.argv.pop()
    unittest.main()