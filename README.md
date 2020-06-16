# Google Search Audit
This repository contains code to reproduce the findings featured in our story, "[TK]()" from our series, [Google the Giant]().

Our methodology is described in "[How We Analyzed Google Search Results]()".

The data from our analysis can be found in the `data` folder. <br>
However, since our initial dataset was too large to place here, we provide a subsample in the `data-subsample` folder. Read more about this in [Download data]() below,

Our open-sourced spatial web scraping tool can be found in `utils/web_assay.py`.

The Jupyter Notebooks for data preprocessing and analysis are avialble in the notebooks folder. Descriptions for each notebook are outlined in the Notebooks section below.

## Installation
### Python
Make sure you have Python 3.6+ installed, we used [Miniconda](https://docs.conda.io/en/latest/miniconda.html) to create a Python 3.8 virtual environment.

Then install the Python packages:<br>
`pip install -r requirements.txt`

### [Selenium](https://selenium-python.readthedocs.io/installation.html)
[Selenium](https://selenium-python.readthedocs.io/installation.html) is used to perform browser automation during the data collection and preprocessing steps. Although we download Selenium when we install the Python requirements (above), you must make sure to also download Firefox, which requires [geckodriver](https://github.com/mozilla/geckodriver/releases). Detailed installation instructions are in Selenium's [documentation](https://selenium-python.readthedocs.io/installation.html).

### [PyVirtualDisplay](https://pyvirtualdisplay.readthedocs.io/en/latest/#installation) (Optional)
We use [PyVirtualDisplay](https://pyvirtualdisplay.readthedocs.io/en/latest/#installation) for headless browsing. Although this is covered in the Python requirements file, double check you have dependencies such as `xvfb` installed. There are detailed instructions in PyVirtualDisplay's [documentation](https://pyvirtualdisplay.readthedocs.io/en/latest/#installation). If you don't need to do headless browsing this is not a requirement.

### [p5](https://p5.readthedocs.io/en/latest/index.html)
We use a native Python port of the graphing library [p5.js](https://p5js.org/) to programatically draw shapes. Graphics libraries have differing requirements based on operating system, please check the p5 [documentation](https://p5.readthedocs.io/en/latest/install.html) to assure you have the necessary requisites.


## Download data
This repo features a sub-sample (N=400) of our final dataset (N=15K) in the `data_subsample/` directory.
We do this to illustrate our methodology and provide ballpark numbers.

However, if you want to use the full dataset, you can find it here:
```
TK
```

The script will download a tar.gz file and unarchive it in that directory.

Download the tar file here:
`Url to something`

Here's a command that works for us:
`curl {url} data/; tar sfadf`

Please be sure to place the contents in the `data/` directory, and set
```
subsample = False
```
Within Jupyter notebooks.


## Tests
After downloading Selenium, make sure it is working!
We created tests to make sure that these drivers work and that you can emulate a mobile device. This is necessary in the data preprocessing step to get the location and dimensions of elements.

here is how to do that test:

## Notebooks
Notebooks should be run sequentially.
The first notebook launches a mobile emulator and illustrates how our parsers work. Use this as a sanity check to see how your own searches are annotated.

## Utils
This folder contains helper functions and code for our spatial web scraping tool.

## License
