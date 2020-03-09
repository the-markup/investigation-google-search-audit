# Google Search Audit
#### Leon Yin

This is a repository to reproduce the Markup's analysis of Goolgle search results.

In this repository, you'll find...
1. Jupyter notebooks for preprocessing and analyzing the data.
2. a data directory which can be popluated using this script:TK.
3. Tests for the parsers and mobile emulators used in the data preprocessing step.

If you don't plan on running the code in this notebook, and just want to read about how we stained things look here: TK

If you want to look at how we calculate pixel area look here: Tk

## Download data
The script will download a tar.gz file and unarchive it in that directory.

Download the tar file here:
`Url to something`

Here's a command that works for us:
`curl {url} data/; tar sfadf`


## Installation
### Python
Make sure you have Python 3.6+ installed, we used [Miniconda](https://docs.conda.io/en/latest/miniconda.html) to create a Python 3.8 environment.

Then install the Python packages:<br>
`pip install -r requirements.txt`

### [Selenium](https://selenium-python.readthedocs.io/installation.html)
[Selenium](https://selenium-python.readthedocs.io/installation.html) is used to perform browser automation during the data collection and preprocessing steps. Although we download Selenium when we install the Python requirements (above), you must make sure to also download Firefox, which requires [geckodriver](https://github.com/mozilla/geckodriver/releases). Detailed installation instructions are in Selenium's [documentation](https://selenium-python.readthedocs.io/installation.html).

### [PyVirtualDisplay](https://pyvirtualdisplay.readthedocs.io/en/latest/#installation) (Optional)
We use [PyVirtualDisplay](https://pyvirtualdisplay.readthedocs.io/en/latest/#installation) for headless browsing. Although this is covered in the Python requirements file, but double check you have dependencies like `xvfb` installed. There are detailed instructions in PyVirtualDisplay's [documentation](https://pyvirtualdisplay.readthedocs.io/en/latest/#installation). If you don't need to do headless browsing this is not a requirement that needs to work!

## Tests
After downloading Selenium, make sure it is working!
We created tests to make sure that these drivers work and that you can emulate a mobile device. This is necessary in the data preprocessing step to get the location and dimensions of elements.

here is how to do that test:

## Notebooks
Notebooks should be run sequentially.
The first notebook launches a mobile emulator and illustrates how our parsers work. Use this as a sanity check to see how your own searches are annotated.


# LEON TODO
- Document notebooks
    - util functions?
    - Configuration?
- Document tests
    - Create a test for parsed HTML compared to expected results.
- Document data
- Talk about installation.
- Document inputs and output, include data dictionary for each