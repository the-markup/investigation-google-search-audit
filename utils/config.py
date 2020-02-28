import os

# directories
version = '0.0.1'
is_local = True

# if is_local:
#     base_dir = '../data'
#     data_dir_in = f'{base_dir}/raw_input'
#     data_dir_stain = f'{base_dir}/intermediary/v{version}/2_stained_html'
#     data_dir_metadata =  f'{base_dir}/intermediary/v{version}/1_element_metadata'
# #     data_dir_screenshots = f'{base_dir}/screenshots/'
#     data_dir_abstract = f'{base_dir}/intermediary/v{version}/3_abstract_painting'
#     for _dir in [base_dir, data_dir_in,
#                  data_dir_stain, data_dir_metadata, 
#                 data_dir_abstract]:
#         os.makedirs(_dir, exist_ok=True)
# else:
#     base_dir = 's3://markup-investigations-google'
#     data_dir_in = f'{base_dir}/searches' 
#     data_dir_stain = f'{base_dir}/processed_data/v{version}/stained_html'
#     data_dir_metadata =  f'{base_dir}/processed_data/v{version}/calculations'
#     data_dir_screenshots = f'{base_dir}/processed_data/v{version}/screenshots'
#     data_dir_abstract = f'{base_dir}/processed_data/v{version}/abstract_stain'
    

# stuff for the selnium client
headless = True
user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1'
width = 375
height = 812
window_size = (width, height)

# color values for stains
blue = "#6cb1ee"
red = "#ea4335"
yellow = "#fbbc05"
green = "#34a853"
white = "#ffffff"
black = "#b2b2b2"

# the first word before hyphens in element categories are the keys.
cat2color = {
    'link' : yellow,
    'amp' : blue,
    'ads' : red,
    'answer' : green,
    'organic' : black
}

# opacity = .9

# lists for preprocessing
javascript = [
    '#', 'javascript:void(0);', 'javascript:void(0)'
]

# domains of interest
google_domains = [
    'google.com',
    'youtube.com',
    'googleadservices.com'
]

# this is for annotations for utils/draw.py
font_file = '/Library/Fonts/Arial.ttf'