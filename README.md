# Google Search Audit
This repository contains code to reproduce the findings featured in our story, "[Google’s Top Search Result? Surprise! It’s Google](https://themarkup.org/google-the-giant/2020/07/28/google-search-results-prioritize-google-products-over-competitors)" from our series, [Google the Giant](https://themarkup.org/series/google-the-giant).

Our methodology is described in "[How We Analyzed Google’s Search Results](https://themarkup.org/google-the-giant/2020/07/28/how-we-analyzed-google-search-results-web-assay-parsing-tool)".

The the figures and tables from our analysis can be found in the `data` folder. <br>
Since our full dataset was too large to place in GitHub, we provide a subset in the `data-subsample` folder. <br>
To use the full dataset, please refer to the [Download data](#download-data).

Our novel spatial web parsing tool can be found in `utils/web_assay.py`.

Jupyter notebooks used for data preprocessing and analysis are avialble in the `notebooks` folder.<br>
Descriptions for each notebook are outlined in the [Notebooks](#notebooks) section below.

## Installation
### Python
Make sure you have Python 3.6+ installed, we used [Miniconda](https://docs.conda.io/en/latest/miniconda.html) to create a Python 3.8 virtual environment.

Then install the Python packages:<br>
`pip install -r requirements.txt`

Some of the packages have additional dependencies (`geckodriver`, `xvfb`, `GLFW`) noted in the sections below.

### geckodriver for [Selenium](https://selenium-python.readthedocs.io/installation.html)
[Selenium](https://selenium-python.readthedocs.io/installation.html) is used to perform browser automation during the data collection and preprocessing steps. Although we download Selenium when we install the Python requirements (above), you must make sure to also download Firefox, which requires [geckodriver](https://github.com/mozilla/geckodriver/releases). Detailed installation instructions are in Selenium's [documentation](https://selenium-python.readthedocs.io/installation.html).

### xvfb for [PyVirtualDisplay](https://pyvirtualdisplay.readthedocs.io/en/latest/#installation)
We use [PyVirtualDisplay](https://github.com/ponty/pyvirtualdisplay#installation) for headless browsing. Although this is covered in the Python requirements file, double check you have dependencies such as `xvfb` installed. There are detailed instructions in PyVirtualDisplay's [documentation](https://github.com/ponty/pyvirtualdisplay#installation). If you don't need to do headless browsing this is not a requirement.

For Debian:
```
sudo apt-get install xvfb xserver-xephyr vnc4server xfonts-base
```

### GLFW for [p5](https://p5.readthedocs.io/en/latest/index.html)
We use a native Python port of the graphing library [p5.js](https://p5js.org/) to programatically draw shapes. p5 uses [GLFW](https://www.glfw.org/download.html) for certain operations on OpenGL graphics, the requirements differ a bit based on your operating system, please check the p5 [documentation](https://p5.readthedocs.io/en/latest/install.html) to assure you have the necessary requisites. 

For Mac OS:
```
brew install glfw
```

For Debian:
```
sudo apt-get install libglfw3-dev libglfw3
```

## Download data
This repo features a subset (N=400) of our final dataset (N=15K) in the `data_subsample/` directory.
The subset sufficiently illustrates our methodology and provides comparable numbers to the full dataset.

However, if you want to use the full dataset, you can find it here:
```
# To reproduce the data preprocessing in its entirety start with the HTML files here:
https://markup-public-data.s3.amazonaws.com/google-search-audit/input_files.tar.xz

# To reproduce the analysis you just need the spatial metadata jsonl files parsed from the HTML files:
https://markup-public-data.s3.amazonaws.com/google-search-audit/intermediary_files.tar.xz
```

Or if you trust us, you can run the following script:
```
sh data/download-full-dataset.sh
```
The script will download two tar.xz files and unpack them in the `data/` folder.

We suggest a dry-run with the subset data found in `data_subsample/` before doing this!

After you have the full dataset, you can flip this switch in beginning of the Jupyter notebooks in `notebooks/`.
```
use_full_dataset = True
```

## Tests
After downloading Selenium, make sure it is working!
We created tests to make sure that these drivers work and that you can emulate a mobile device. This is necessary in the data preprocessing step to get the location and dimensions of elements.

here is how to do those tests.

Change directories to the tests folder:
```
cd tests
```

Then there are two tests -- one which tests parser fuctionality
```
python test_parsers.py
```
and one which tests the full web assay flow using several examples in the `data/tests` folder.
```
python test_assay.py
```

## Notebooks
If you want to reroduce our results, the notebooks should be run sequentially.<br>
However, if you want quick overview of the methodology you only need to concern yourself with the notebooks with an asterix(*). 

### 0-demo-web-assay.ipynb *
A practical demo of Web assays functionality on an search result. This walks through the underlying code that is explaing in our methodlogy.

### 1-run-assay.ipynb
This runs the web assay flow on the entirety of the input dataset of HTML pages we collected.

### 2-preprocess-assay-output.ipynb *
Data preprocessing. Includes standardizing categories returned by parsers, normalizing the length of web pages, and calculating area in 50 quantiles.

### 3-data-analyis.ipynb *
The main analysis notebook that reproduces the figures and tables found in our findings section.

### 4-changes-in-definitions.ipynb
A thought experiment that shows how our calculations for Google and non-Google real estate would change had we considered different interpretations of what is included in each category. This is in our limitations section.

### 5-analysis-by-trending-topic.ipynb
Shows how calculations of real estate differ among different clusters of searches. Searches are grouped together based on unique "entities", or search topics from Google trends. This is in our limitations section.

### 6-error-analysis.ipynb
After spotchecking 700-some stained searches, we were able to calculate error rates for the accuracy of our classifications and the precision of our real estate boundries. We further measure the impact of our technical shortcomings, by accounting for the pixels we mis-or-under-classified. This is in our appendix.

## utils/
This folder contains helper functions and code for our spatial web parsing tool, Web assay.
```
utils/
├── config.py
├── draw_img.py
├── parsers.py
├── prodigy
│   ├── config
│   │   ├── prodigy.json
│   │   └── serp-help.html
│   └── search_audit.py
├── timeout.py
└── web_assay.py

```

The base class and Google search web assay are in `utils/web_assay.py`.<br>
The 68 web parsers we use to categorize elements of the Google search page are in `utils/parsers.py`.<br>
You will find more context about how they work in the appendix of our methodlogy paper.<br>
Our wrapper around p5.js is in `utils/draw_img.py`.<br>
Instructions for the annotation tool Prodity is in `utils/prodigy`. Our annotation guide for error checking stained screenshots is in `utils/prodigy/config/serp-help.html`.

## data/
This directory is where intermediaries and outputs from the full dataset are saved.
```
data/
├── assets
│   ├── stained-screenshot-examples
│   └── assay-flow.png
├── error_analysis
│   ├── adrianne-annotations.csv.gz
│   ├── adrianne-pixel-errors.csv
│   ├── leon-annotations.csv.gz
│   └── leon-pixel-errors.csv
├── output
│   ├── figures
│   └── tables
└── test
    ├── input_local_searches
    ├── intermediate_local_searches
    └── parser_output
```
`data/assets/stained-screenshot-examples` contains examples of screenshots stained using web assay- our novel web parsing tool.
`data/error_analysis` contains spot check data from two annotators.<br>
`data/output` contains tables and figures used in our _Show your work_ article.<br>
`data/test` contains some sample search results' HTML for tests and the demo notebook `notebooks/0-demo-web-assay.ipynb`.

If you download the [full dataset](#download-data), the contents should be extracted into `data/`, mirroring the organization of `data_subsample/`.

## data_subsample/
`data_subsample/` contains the raw HTML (`data_subsample/input/`) and intermediaries for a random subsset of 400 search results from our 15K sample.
```
data_subsample/
├── input
│   └── google_search
└── intermediary
    ├── element_metadata.jsonl.gz
    └── google_search
```
This smaller dataset is shipped with the repository to demonstrate our methodology in a timely and less resource intensive manner than the full dataset.

`element_metadata.json1.gz` is the preprocessed spatial element metadata returned from web assay. The bulk of our analysis uses this dataset, whether it be from the subset or the full dataset.

## Licensing
Copyright 2020, The Markup News Inc.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.