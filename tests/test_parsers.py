"""
This script is an abstract test for HTML parsers.
Use it for two reasons:
1. Checking if Google has made changes to search results.
2. Assuring parsers are still mostly working.

It is OK if some tests fail, it just means that the specific parser's
target was not in the input dataset.

This code ships with a default dataset. 
You can include an extra parameter of a directory with new HTML files to test.
"""


import os
import sys
import glob
import unittest
import inspect

import pandas as pd
from bs4 import BeautifulSoup
from parameterized import parameterized

# the software we're testing is in this directory as `utils`
sys.path.append('..')
import utils.parsers as P


functions_list = [o for o in inspect.getmembers(P)
                  if inspect.isfunction(o[1]) and
                  '_parser' in o[0]]

class TestParsers(unittest.TestCase):
    '''
    This class contains three functions that are run in the order 
    (the name of the first and last matter!).
    
    `test_abstract` is to be used by all parsers in `functions_list`.
    It iterates through the files read from `data_dir`, and sends each
    HTML file through the parsers. 
    
    If the parser targets exist, the parser will return a list of dictionaries.
    '''
    data_dir = '../data/tests/input'
    metadata_dir = '../data/tests/output'
    for d in [data_dir, metadata_dir]:
        os.makedirs(d, exist_ok=True)
    
    @classmethod
    def setUpClass(cls):
        '''
        Initializes parameters for HTML parsers.
        Note that every file is read into memory and placed within a BeautifulSoup object.
        '''
        # create an empty dictionary ro record metadata on tests
        cls.report = dict()
        
        
        # select the local directory with HTML files to test.
        if not os.path.isdir(cls.data_dir):
            raise Exception('The input directory does not exist.')
        cls.input_filenames = glob.glob(
            os.path.join(cls.data_dir, '*.html')
        )
        cls.n_inputs = len(cls.input_filenames)
        
        # read each HTML file into Beautiful soup and store them as a list in `parse_trees`
        soups = []
        for fn in cls.input_filenames:
            with open(fn) as f:
                filestream = f.read()
            soup = BeautifulSoup(filestream, 'lxml')
            soups.append(soup)
        cls.parse_trees = soups
    
    
    @parameterized.expand(functions_list)        
    def test_abstract(self, func_name, parser_func):
        '''
        This is the abstract of a test, thanks for the decorator, 
        each test will be parameterized by each tuple in `parser_params`.
        
        The tuple contains a function name and the parser function itself.
        
        The test sends all the input files in `soups` 
        To make sure these tests are accurate, make sure the at least one 
        inputs contain elements you're looking for...
        
        The results of the parsers are saved as a key-value pair in the `report` property
        '''
        
        results = []
        hits = 0
        for i, soup in enumerate(self.parse_trees):
            elements = parser_func(soup)
            if len(elements) != 0:
                hits += 1
                for item in elements:
                    item.update({'filename' : os.path.abspath(self.input_filenames[i])})
                results.extend(elements)
        
        self.assertTrue(hits != 0)
        self.report[func_name] = results
    
    @classmethod
    def tearDownClass(cls):
        '''
        This will provide some sort of aggregate statistic...
        We'll figure out what to do with this later.
        '''
        for test, data in cls.report.items():
            df = pd.DataFrame(data)
            fn_out = os.path.join(cls.metadata_dir, f"{test}_results.csv")
            df.to_csv(fn_out, index=False)
#             print(test)
#             print(df.head())
       
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestParsers.data_dir = sys.argv.pop()
    unittest.main()
