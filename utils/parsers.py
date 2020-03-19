"""
These are functions that find a great deal of different elements within a Google search
Leon Yin
"""

import re
from typing import Union
from typing import Dict, List

from bs4 import BeautifulSoup, element
from urlexpander import get_domain
from .config import javascript, google_domains


def xpath_soup(element : Union[element.Tag, 
                               element.NavigableString]) -> str:
    """Generate xpath from BeautifulSoup4 element."""
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

def element_to_dict(elm : Union[element.Tag, element.NavigableString], 
                    category : str, 
                    url : Union[str, bool] = None, 
                    domain : str = 'google.com') -> Dict:
    """Structures an element for the dataset"""
    text = elm.text
    tag = elm.name
    xpath = xpath_soup(elm)
    element_class = '|'.join(elm.get('class', list()))
    attrs = elm.attrs
    row = {
        'text' : text,
        'link' : url,
        'domain' : domain,
        'xpath' : xpath,
        'element_class' : element_class,
        'category' : category,
        'element' : elm,
        'tag' : tag,
        'attrs' : attrs
    }
        
    return row

### General parsers
def link_parser(body):
    """
    Parses all a tags with `href` attributes. 
    Decides if the url is `organic`, or from a Google property
    such as "youtube" or google ad services.
    """
    data = []
    for elm in body.find_all('a', href=True, 
                             attrs={'data-amp' : False}):
        url = elm['href']
        domain = get_domain(url)
        category = 'link-google'
        if url in javascript:
            domain = 'google.com'
            category = 'link-javascript'
            # skip call, share, and save icons
            if any(elm.find_all('div', text=re.compile('Call|Share|Save'))):
                continue
        
        # links to Google Ad services...
        elif domain[0] == '/':
            if domain.split('?')[0] == '/aclk': # check this
                category = 'ads-google_ad_services'
            domain = 'google.com'

        elif domain == 'googleadservices.com':
            category = 'ads-google_ad_services'
    
                
        elif domain not in javascript + ['google.com']:
            """
            This is mostly logic for organic, but it applies to links
            that are from Google. This is to find then entire element
            link + hyperlink for search results
            """
            category = 'organic'
            if (not any(e for e in elm.attrs if e in ['data-ved', 'target'])
                  and not any(elm.find_all('g-img', recursive=True))):
                # get the sibling of the parent of the link
                elm_potential_text = elm.parent.find_next_sibling('div')
                if elm_potential_text and not 'data-attrid' in elm.parent.attrs:
                    if any(elm_potential_text.find_all('div', recursive=True,
                                                         attrs={"role" : False,
                                                                "aria-level" : False,
                                                                "jsname" : False})):
                            category = 'organic-search_result_1a'
                            elm = elm.parent # limit this
                            if 'data-ved' not in elm.attrs:
                                elm = elm.parent
                        
                    elif any(elm_potential_text.find_all('span', recursive=True,
                                                         text = True,
                                                         attrs={"role" : False,
                                                                "aria-level" : False})):
                        category = 'organic-search_result_1b'
                        elm = elm.parent.parent
                else:
                    elm_potential_text = elm.parent.parent.find_next_sibling('div')
                    if elm_potential_text and elm.parent.name != 'h3':
                        if any(elm_potential_text.find_all('div', recursive=True,
                                                         text = True,
                                                         attrs={"role" : False,
                                                                "aria-level" : False,
                                                                "jsname" : False})):
                            category = 'organic-search_result_2a'
                            elm = elm.parent.parent.parent
                            
                        elif any(elm_potential_text.find_all('span', recursive=True,
                                                         text = True,
                                                         attrs={"role" : False,
                                                                "aria-level" : False})):
                            category = 'organic-search_result_2b'
                            elm = elm.parent.parent.parent
                        elif any(elm_potential_text.find_all('table', recursive=True,
                                                             attrs={"class" : True})):
                            category = 'organic-search_result_2c'
                            elm = elm.parent.parent.parent
                # tweets
                if 'gws-twitter-link' in elm.attrs.get('class', []):
                    for _ in range(3):
                        elm = elm.parent
                    category = 'organic-tweet_1'
        
        # set categories for Google products
        if domain == 'youtube.com':
            if 'organic-' in category:
                category = category.replace('organic-', 'link-youtube_')
            else:
                category = 'link-youtube'
            if 'tabindex' in elm.attrs:
                for div in elm.find_all('div'):
                    elm = div
                    break
            
        elif domain in javascript + ['google.com']:
            if 'organic-' in category:
                category = category.replace('organic-', 'link-google_')
            else:
                category = 'link-google'
            if 'data-merchant-id' in elm.attrs:
                category = 'ads-merchant'
            elif 'aclk?' in url:
                category = 'ads-google_ad_services'
            elif elm.parent.parent.name == 'g-tray-header':
                check = elm.parent.parent
                if 'style' in check.attrs:
                    for _ in range(2):
                        elm = elm.parent
                    if 'organic-' in category:
                        category = category.replace('organic-', 'link-button_2_')
                    else:
                        category = 'link-button_2'
            elif elm.parent.parent.parent.name == 'g-inner-card' and elm.name == 'a':
                if 'organic-' in category:
                    category = category.replace('organic-', 'link-google_2_')
                else:
                    category = 'link-google_2'
                for _ in range(3):
                    elm = elm.parent
                    
        row = element_to_dict(elm, url=url, 
                              domain=domain, 
                              category=category)
        data.append(row)  
    
    return data

def amp_parser(body : element.Tag) -> List[Dict]:
    """
    AMP links which look like regular links.
    Makes a distinction between search results
    with text and regular links
    """
    data =[]
    for elm in body.find_all("a", attrs={'data-amp' : True}):
        category = 'amp-card'
        url = elm["data-amp"]
        domain = get_domain(url)
        parent = elm.parent.parent.parent
        if ('data-amp-st' not in elm.attrs
              and parent.get('role') != 'listitem'
              and not elm.parent.parent.get('data-hveid')
              and not parent.parent.parent.name == 'g-card'):
            if any(e for e in parent.find_all('span',
                                               recursive=True,
                                               text = True,
                                               attrs={"role" : False,
                                                      "aria-level" : False,
                                                      "class" : True}) 
                   if len(e.text) > 50):
                elm = parent
                category = 'amp-search_result_2'
                
            else:
                parent = elm.parent.parent
                for div in parent.find_all('div',
                                           recursive=True,
                                           attrs={"role" : False,
                                                  'style' : False,
                                                  'data-ved' : False,
                                                  'jscontroller' : False,
                                                  "aria-level" : False,
                                                  "class" : True}):
                    if div.text:
                        elm = parent
                        category = 'amp-search_result_3'
                    else:
                        if any(_ for _ in div.find_all('span',
                                          text=True, 
                                          attrs={'class' : True})
                               if len(_.text) > 50):
                            elm = parent
                            category = 'amp-search_result_3b'

        if domain == 'google.com':
            category += '_google'
        if 'data-amp-st' in elm.attrs:
            category = 'amp-visual_stories'
        row = element_to_dict(elm, url=url,
                              domain=domain,
                              category=category)
        data.append(row)
        
    return data

def button_parser(body : element.Tag) -> List[Dict]:
    """
    Elements that link. Typically an entire element
    Can caputre a lot, especially when no anchor is called.
    In this case, it can caputure sport_schedule and sport_standing
    """
    data = []
    for elm in body.find_all(role='link', attrs={'href' : False,
                                                 'data-href' : False,
                                                 'jsaction' : True,
                                                 'data-fp-link' : False}):
        row = element_to_dict(elm, category='link-button')
        data.append(row)
    return data

def links_alt_parser(body: element.Tag) -> List[Dict]:
    """elements that have a data-href. buttons usually."""
    data =[]
    for elm in body.find_all('a', attrs= {'data-href':True}): # remove 'div'
        row = element_to_dict(elm, category= 'link-google_alt')
        data.append(row)
        
    return data

def load_more_parser(body: element.Tag) -> List[Dict]:
    """A button that either loads more of a page or gives a popup"""
    data = []
    for elm in body.find_all(attrs={'aria-label' : re.compile('^.*More.*$')}):
        if elm.name == 'span':
            elm = elm.parent
        row = element_to_dict(elm, category='link-load_more')
        data.append(row)
    return data

def tweet_parser(body : element.Tag) -> List[Dict]:
    """Full clickable Tweet cards embedded in page"""
    data = []
    for elm in body.find_all('div',  attrs={'data-init-vis' : True,
                                            'data-author' : True,
                                            'data-hveid' : True}):
        row = element_to_dict(elm, 
                              category='organic-tweet_2',
                              domain='twitter.com')
        data.append(row)
    return data                               

def see_all_parser(body : element.Tag) -> List[Dict]:
    """For "see all" buttons. check this"""
    data = []
    for elm in body.find_all("div", attrs={"aria-label" : "See all",
                                           "jsaction" : True,
                                           "role" : "button"}):
        row = element_to_dict(elm, category='link-load_see_all')
        data.append(row)
    return data                               

### KNOWLEDGE PANEL misc
def knowledge_panel_title_parser(body : element.Tag) -> List[Dict]:
    """The title of knowledge panels that are clickable"""
    data = []
    for elm in body.find_all(attrs={"data-ru_q" : True}):
        row = element_to_dict(elm, category= 'link-knowledge_panel_title')
        data.append(row)
    return data

def tab_parser(body : element.Tag) -> List[Dict]:
    """For tabs, sometimes on knowledge panels. # check this"""
    data = []
    for elm in body.find_all(role='tab'): # what if we get rid of 'a'
        row = element_to_dict(elm, category='link-knowledge_panel_tab')
        data.append(row)
    return data

def filter_parser(body : element.Tag) -> List[Dict]:
    """Checks for filters"""
    data = []
    for elm in body.find_all(attrs={"role" : "button", 
                                    "aria-pressed" : True}):
        row = element_to_dict(elm, category='link-filter')
        data.append(row)
    return data

def post_parser(body : element.Tag) -> List[Dict]:
    """Posts from the owner of a knowledge panel"""
    data = []
    for elm in body.find_all('div', attrs={'role' : 'button',
                                           'tabindex' : True,
                                           'jsaction' : re.compile(
                                              '^fire.enter_gallery_view')}):
        row = element_to_dict(elm, category='link-knowlege_panel_owner_post')
        data.append(row)
    return data

### LOCAL
def map_img_parser(body : element.Tag) -> List[Dict]:
    """Image of a Google map search that links to Google maps."""
    data = []
    for elm in body.find_all("img", attrs={"alt" : "map expand icon"}):
        for _ in range(4):
            elm = elm.parent
        row = element_to_dict(elm, category='link-google_map')
        data.append(row)
    return data

def local_hours_parser(body : element.Tag) -> List[Dict]:
    """Dropdown of daily hours of operation for a local business."""
    data = []
    for elm in body.find_all("div", attrs={'aria-label' : "Hours:"}):
        elm = elm.parent
        row = element_to_dict(elm, category='answer-local_hours_expand')

        data.append(row)
    return data

def local_popular_times_parser(body : element.Tag) -> List[Dict]:
    """A graph of popular times for local business."""
    data = []
    for elm in body.find_all('div', 
                             attrs={'aria-label' : re.compile(
                                "^Histogram showing popular times")}):
        elm = elm.parent
        row = element_to_dict(elm, category='answer-local_popular_times')
        data.append(row)
    return data

def local_map_result_parser(body : element.Tag) -> List[Dict]:
    """Map results with links that go to Goolge maps"""
    data = []
    for elm in body.find_all('a', attrs={"data-rc_f" : "rln",
                                         "data-ru_gwp" : True,
                                         "jsaction" : True}):
        row = element_to_dict(elm, category='link-local_google_maps_results')
        data.append(row)
    return data
    
def local_qa_parser(body : element.Tag) -> List[Dict]:
    """Q&A for local business"""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile(
                                 '^kc:/local:place')}):
        row = element_to_dict(elm, category='link-local_questions')
        data.append(row)
    return data

def local_menu_parser(body : element.Tag) -> List[Dict]:
    """Links to a Food menu hosted on Google"""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile(
                                 '^kc:/local:menu')}):
        row = element_to_dict(elm, category='link-local_menu')
        data.append(row)
    return data  

def local_details_parser(body : element.Tag) -> List[Dict]:
    """A click-able blurb about a local result."""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile(
                                 '^kc:/local:scalable attributes')}):
        row = element_to_dict(elm, category='answer-local_description')
        data.append(row)
    return data

def trailer_parser(body : element.Tag) -> List[Dict]:
    """For trailer images in Movie knowledge panels."""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : 'kc:/media_common/media_item:video_clips',
                                   'lang' : True,
                                    'data-md' : True}):
        for thumb in elm.find_all('div', 
                                  attrs={'role' : 'button',
                                         'data-logged' : True,
                                         'data-index' : True,
                                         'style' : True}):
            row = element_to_dict(thumb, category='answer-trailer')
            data.append(row)
    return data

def youtube_parser(body):
    """For embedded videos"""
    data = []
    for video in body.find_all("inline-video",
                               attrs = {'data-video-id' : True}):
        row = element_to_dict(video, 
                              category='link-youtube_embed',
                              domain='youtube.com')
        data.append(row)
    return data

def flights_parser(body : element.Tag) -> List[Dict]:
    """Featured snippet. Highlights the entire box"""
    data = []
    for elm in body.find_all('div',
                             attrs={'data-fltid' : True,
                                    'data-flt-ve' : True,
                                    'role' : 'region'}):
        row = element_to_dict(elm, 
                              category='link-flights_1')
        data.append(row)
    return data

def flights2_parser(body : element.Tag) -> List[Dict]:
    """Featured snippet. Highlights the entire box"""
    data = []
    for elm in body.find_all('div',
                             attrs={'data-price-graph-bulk-scroll-size' : True,
                                    'data-black-unclickable-header' : True}):
        row = element_to_dict(elm, 
                              category='link-flights_2')
        data.append(row)
    return data

### ANSWERS
# def featured_snippet_parser(body : element.Tag) -> List[Dict]:
#     """Featured snippet. Highlights the entire box"""
#     data = []
#     for elm in body.find_all('h2', text= 'Featured snippet from the web'):
#         elm = elm.parent
#         for span in elm.find_all('span', recursive=True, attrs={'class' : True}):
#             # check the span is text, and not the text of a hyperlink.
#             if span.text and span.parent.name != 'a':
#                 row = element_to_dict(span, category='answer-feature_snippet_1')
#                 data.append(row)
#         for ul in elm.find_all('ul', recursive=True, attrs={'class' : True}):
#             row = element_to_dict(ul, category='answer-feature_snippet_2')
#             data.append(row)
            
#     return data

def featured_snippet_answer_short_parser(body : element.Tag) -> List[Dict]:
    """Gets short answers, like "how many calories are in uranmium"?"""
    data = []
    for elm in body.find_all('div', attrs = {'data-tts' : "answers",
                                             'data-tts-text' : True,
                                             'class' : True}):
        if elm.text:
            row = element_to_dict(elm, category='answer-feature_snippet_answer_short')
            data.append(row)
    return data

def rich_text_parser(body : element.Tag) -> List[Dict]:
    """
    Answers scraped from the web and presented as a paragraph.
    Collects the span that houses the text, so area is the rect of the span.
    Remove "datta-attrid" : False to get all short text answers as well...
    """
    data = []
    for elm in body.find_all('div', 
                             attrs={'jsaction' : re.compile(
                                 "^desclink:")}):
        for span in elm.find_all('span',
                                 recursive=True):
            if span.text:
                if (span.text not in ['See results about']
                      and not any(span.find_all('a', href=True))
                      and len(span.text) > 50):
                    row = element_to_dict(span, category='answer-richtext')
                    data.append(row)
        for ul in elm.find_all('ul', recursive=True, attrs={'class' : True}):
            row = element_to_dict(ul, category='answer-richtext')
            data.append(row)

    return data

def knowledge_panel_answer_parser(body : element.Tag) -> List[Dict]:
    """
    Answers scraped from the web and presented as a paragraph.
    Collects the span that houses the text, so area is the rect of the span.
    """
    data = []
    for elm in body.find_all('h2', attrs={'class' : True}):
        if not elm.text:
            continue
        if elm.text != 'Description':
            continue
        for span in elm.parent.find_all('span',
                                        attrs={'jsslot':False},
                                        recursive=True):
            if span.text:
                if (len(span.text) > 50 and 
                      not any(span.find_all('a', href=True))):
                    row = element_to_dict(span, category='answer-knowledge_panel_answer_1')
                    data.append(row)
                    break
            
    return data

def knowledge_panel_answer_2_parser(body: element.Tag) -> List[Dict]:
    """
    Another variant of answers from knowledge panels
    """
    data = []
    for elm in body.find_all('div', attrs={"aria-level" : "3", 
                                           "role" : "heading",
                                           "data-hveid" : True,
                                           "class" : True}):
        for span in elm.find_all('span',
                                 recursive=True,  
                                 attrs={'class' : True}):
            if span.text:
                row = element_to_dict(elm, category='answer-knowledge_panel_answer_2')
                data.append(row)
    return data

def med_answer_parser(body : element.Tag) -> List[Dict]:
    """Long answers and descriptions of medical conditions"""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile(
                                 "^kc:/medicine/")}):
        elm = elm.parent.parent
        row = element_to_dict(elm, category='answer-medical')
        data.append(row)
    return data

def date_answer_parser(body : element.Tag) -> List[Dict]:
    """An answer for a date, like 'When is valentines day?'"""
    data = []
    for elm in body.find_all('h2', text='Date Result'):
        elm = elm.parent.parent
        row = element_to_dict(elm, category='answer-date')
        data.append(row)
    return data

def date_answers_2_parser(body : element.Tag) -> List[Dict]:
    """An answer for a date, like 'When is valentines day?'"""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile(
                                    "^kc:/events/holiday:dates")}):
        row = element_to_dict(elm, category='answer-date_2')
        data.append(row)
    return data

def answer_dropdown_parser(body : element.Tag) -> List[Dict]:
    """Dropdown answers. Typically leads to more links"""
    data = []
    for elm in body.find_all('div',  
                             attrs={'data-async-context-required' : "q",
                                    'data-jiis' : 'up',
                                    'data-async-type' : True,
                                    'id' : True, 
                                    'jsname' : True}):
        for div in elm.find_all('div', 
                                attrs={'role' : 'button',
                                       'tabindex' : '0',
                                       'jsaction' : True,
                                       'data-ved' : True}):
            row = element_to_dict(div, category='answer-expand_1')
            data.append(row)
    return data
    
def expand_answer_parser(body : element.Tag) -> List[Dict]:
    """Exapndable answers. Typically leads to more links"""
    data = []
    for elm in body.find_all(attrs={'aria-expanded' : 'false',
                                    'role' : 'button'}):
        row = element_to_dict(elm, category='answer-expand_2')
        data.append(row)
    return data
    
def expanded_answer_parser(body : element.Tag) -> List[Dict]:
    """Exapnded answers. Typically leads to more links"""
    data = []
    for elm in body.find_all('div',
                             attrs={'aria-expanded' : 'true',
                                    'role' : 'heading'}):
        row = element_to_dict(elm, category='answer-expand_3')
        data.append(row)
    return data
    
def lyric_parser(body : element.Tag) -> List[Dict]:
    """Lyrics to songs"""
    data = []
    for elm in body.find_all('div',
                             attrs={'data-attrid' : re.compile(
                                 '^kc:/music/recording_cluster:lyrics')}):
        row = element_to_dict(elm, category='answer-lyrics')
        data.append(row)
    return data
        
def tv_parser(body : element.Tag) -> List[Dict]:
    """Air time for TV shows"""
    data = []
    for elm in body.find_all('div',
                             attrs={'data-attrid' : re.compile(
                                 '^kc:/(.*?):livetv')}):
        row = element_to_dict(elm, category='answer-tv_episodes')
        data.append(row)
    return data

def dict_def_parser(body : element.Tag) -> List[Dict]:
    """Dictionary definitions, gets the whole card."""
    data = []
    for elm in body.find_all('div', attrs={'id' : 'dictionary-modules'}):
        row = element_to_dict(elm, category='answer-dictionary')
        data.append(row)
    return data
        
def sport_stats_parser(body : element.Tag) -> List[Dict]:
    """Stats on atheletes."""
    data = []
    for elm in body.find_all('div',
                             attrs={'data-attrid' : re.compile(
                                 "^kc:/sports/pro_athlete:stats")}):
        row = element_to_dict(elm, category='answer-sport_stats')
        data.append(row)
    return data

def food_nutrition_parser(body : element.Tag) -> List[Dict]:
    """Nutrition facts, much like the consumer label of physical groceries."""
    data = []
    for elm in body.find_all('div',
                             attrs={'data-attrid' : re.compile(
                                 "^kc:/food/food:energy")}):
        elm = elm.parent
        row = element_to_dict(elm, category='answer-food_nutrients')
        data.append(row)
    return data

def quote_parser(body : element.Tag) -> List[Dict]:
    """A table of quotes by a person"""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : 'kc:/people/person:quote'}):
        row = element_to_dict(elm, category='answer-quote')
        data.append(row)
    return data

def finance_quarterly_financial_parser(body : element.Tag) -> List[Dict]:
    """A table of financial info"""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile(
                                        "^kc:/finance/stock:")}):
        if "carousel" not in elm.get('data-attrid'):
            row = element_to_dict(elm, category='answer-finance_stocks')
            data.append(row)
    return data

### AD Parsers
def ads_local_parser(body : element.Tag) -> List[Dict]:
    """Localized ADs"""
    data = []
    for elm in body.find_all('li', 
                             attrs={'class' : re.compile("^ads-")}):
        row = element_to_dict(elm, category='ads-text')
        data.append(row)
    return data
  
def ads_general_parser(body : element.Tag) -> List[Dict]:
    """Catches ADs with a disclaimer and transparency button"""
    data = []
    xpath_body = xpath_soup(body)
    for elm in body.find_all('div', attrs={'aria-label' : 'Why these ads?'}):
        for _ in range(6):
            if xpath_soup(elm.parent) != xpath_body:
                elm = elm.parent
        row = element_to_dict(elm, category='ads-general')
        data.append(row)
    return data

def ads_aria_parser(body : element.Tag) -> List[Dict]:
    """Catches ADs with a accessibility features"""
    data = []
    for elm in body.find_all(attrs={'aria-label' : 'Ad'}):
        row = element_to_dict(elm, category='ads-aria')
        data.append(row)
    return data
    
def ads_product_refinements_parser(body : element.Tag) -> List[Dict]:
    """ads for products with filters."""
    data = []
    for elm in body.find_all('h3', text=re.compile("Suggested Refinements|Filters List")):
        for _ in range(1):
            elm = elm.parent
        row = element_to_dict(elm, category='link-filter_product_refinement')
        data.append(row)
    return data

def ads_product_parser(body : element.Tag) -> List[Dict]:
    """Product Ads see "best blenders"."""
    data = []
    for elm in body.find_all("g-inner-card", 
                             attrs={'data-premium' : "1",
                                    'class' : True,
                                    'jsname' : True}):
        elm = elm.parent
        row = element_to_dict(elm, category='ads-product')
        data.append(row)
    return data

def ads_gws_refinement_parser(body : element.Tag) -> List[Dict]:
    """Typically for filters on product refinement"""
    data = []
    for elm in body.find_all("g-inner-card", 
                             attrs={'jsaction' : 'fire.refinement_click',
                                    'role' : 'button',
                                    'data-premium' : False,
                                    'class' : True}):
        elm = elm.parent
        row = element_to_dict(elm, category='link-filter_refinement')
        data.append(row)
    return data

def product_refinement_parser(body : element.Tag) -> List[Dict]:
    """Another drop down button to filter sponsored products"""
    data = []
    for elm in body.find_all("span",
                             attrs={'class' : True, 'jscontroller': True, 
                                    'data-immersive' : True, 
                                    'jsaction' : re.compile("^menu_item_selected")}):
        row = element_to_dict(elm, category='link-filter_product')
        data.append(row)
    return data

### MISC products
def rating_parser(body : element.Tag) -> List[Dict]:
    """Ratings on Google"""
    data = []
    xpath_body = xpath_soup(body)

    for elm in body.find_all('span', 
                             attrs={"aria-label" : re.compile("^Rated")}):
        for _ in range(4):
            if xpath_soup(elm.parent) != xpath_body:
                elm = elm.parent
        row = element_to_dict(elm, category='link-reviews_rating')
        data.append(row)
    return data

def reviews_parser(body : element.Tag) -> List[Dict]:
    """Reviews from users on Google"""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-dtl' :re.compile("DETAILS|REVIEWS")}):
        for span in elm.parent.find_all('span', 
                                        recursive = True,
                                        attrs={'data-hveid' : True}):
            row = element_to_dict(span, category='answer-product-details')
            data.append(row)    
        row = element_to_dict(elm, category='link-reviews_details')
        data.append(row)    
    return data

def search_review_parser(body : element.Tag) -> List[Dict]:
    """Product Reviews from Google"""
    data = []
    for elm in body.find_all('button', 
                             attrs={'class' :re.compile(
                                 "^.*product_ads.*$")}):
        row = element_to_dict(elm, category='link-search_reviews')
        data.append(row)
    return data

def movie_showtimes_parser(body : element.Tag) -> List[Dict]:
    """Buttons for movie showtimes, opens a overlay with links."""
    data = []
    for elm in body.find_all('div', 
                             attrs={'aria-haspopup' : "dialog",
                                    'role' : 'button'}):
        row = element_to_dict(elm, category='link-movie_showtimes')
        data.append(row)
    return data

def video_top_answers_parser(body : element.Tag) -> List[Dict]:
    """Recorded answers to common questions, see "Thanksgiving"."""
    data = []
    for elm in body.find_all('img',
                             attrs={'alt' : re.compile("^Video"),
                                    'jsname' : True}):
        for _ in range(4):
            elm = elm.parent
        row = element_to_dict(elm, category='link-video_top_answer')
        data.append(row)
    return data

def ebook_parser(body : element.Tag) -> List[Dict]:
    data = []
    for elm in body.find_all('g-expandable-content',
                             attrs={'jscontroller' : True,
                                    'jsaction' : True,
                                    'jsshadow' : True,
                                    'aria-hidden' : True,
                                    'data-eb' : True,
                                    'data-mt' : True,
                                    'data-quie' : True,
                                    'data-ved' : True}):
        for div in elm.find_all('div', recursive=True,
                                attrs={'class' : True,
                                       'jsname' : True,
                                       'role' : 'button',
                                       'aria-haspopup' :True,
                                       'tabindex' : True,
                                       'jsaction' : True}):
            for e in div.find_all('div', text=True):
                category = 'organic'
                if e.text == 'Google Play Books':
                    category = 'link-google_play_books'
                row = element_to_dict(div, 
                                      category=category)
                data.append(row)
    return data

def fullpage_popup_parser(body : element.Tag) -> List[Dict]:
    """A clickthru of a fullpage. See events like "New Years Eve Party"."""
    data = []
    for elm in body.find_all('li', attrs={'data-encoded-docid' : True}):
        row = element_to_dict(elm, category='link-fullpage')
        data.append(row)
    return data

def category_bar_parser(body : element.Tag) -> List[Dict]:
    """A bar with a topic, like "sports"."""
    data = []
    for elm in body.find_all('div', 
                              attrs={'data-iv' : True,
                                     'data-q' : True,
                                     'data-ui' : True,
                                     'role' : 'button'}):
        row = element_to_dict(elm, category='link-topic')
        data.append(row)
    return data

def site_search_parser(body : element.Tag) -> List[Dict]:
    """Links to a Google search restricted to a site."""
    data = []
    for elm in body.find_all('form', attrs={"action" : '/search',
                                            "data-site" : True}):
        row = element_to_dict(elm, category='link-site_search')
        data.append(row)
    return data

def ugc_parser(body : element.Tag) -> List[Dict]:
    """user gnerated content, like reviews and tags"""
    data = []
    for elm in body.find_all('div',
                             attrs={'data-attrid' : re.compile('^kc:/ugc:')}):
        row = element_to_dict(elm, category='answer-ugc')
        data.append(row)
    return data

def img_reverse_parser(body : element.Tag) -> List[Dict]:
    """img elements that call a javascript function for reverse image search"""
    data = []
    for elm in body.find_all(attrs={'jsaction' : re.compile('^fire.ivg_o')}):
        for img in elm.find_all('img', recursive=True):
            row = element_to_dict(img, category='link-img_reverse')
            data.append(row)
            break
    return data

def link_3d_ar_model_parser(body : element.Tag) -> List[Dict]:
    """A 3d or AR model, usually of an animal"""
    data = []
    for elm in body.find_all("div",
                             attrs={"data-attrid" : re.compile(".ar:model")}):
        row = element_to_dict(elm, category='link-3d_ar_model')
        data.append(row)
    return data

def movie_parser(body : element.Tag) -> List[Dict]:
    """Trailers that for a movie embedded on page. Typically quite large."""
    data = []    
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile(
                                 "^kc:/film/film:trailer")}):
        row = element_to_dict(elm, category='link-movie_trailer')
        data.append(row)
    return data

def watchlist_parser(body : element.Tag) -> List[Dict]:
    """Icons for "watched" and "add to watchlist"."""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile(
                                 '^kc:(.*?):media_actions')}):
        for child in elm.find_all('div', recursive=True,
                                  attrs={'role' : 'button',
                                         'jsdata' : True,
                                         'jscontroller' : True}):
            row = element_to_dict(child, category='link-watchlist')
            data.append(row)
    return data

def educational_course_offering_parser(body : element.Tag) -> List[Dict]:
    """Courses offered by an educational insitution."""
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile(
                                   '^/(.*?)/majors')}):
        for span in elm.find_all('span'):
            row = element_to_dict(span.parent, category='answer-courses')
            data.append(row)
    return data

def health_knowledge_panel_parser(body : element.Tag) -> List[Dict]:
    """Specs for health."""
    data = []
    for elm in body.find_all('div', 
                             attrs={'id' : re.compile('^knowledge-health'),
                                    'data-ved' : True}):
        for div in elm.find_all('div',
                                attrs={'class' : True,
                                       'data-ved' : True,
                                       'jscontroller' : False,
                                       'jsname' : False}):
            if div.text:
                row = element_to_dict(div, category='answer-knowledge_health')
                data.append(row)      
    return data

def conversion_parser(body : element.Tag) -> List[Dict]:
    """See "how many ounces in a cup"."""
    data = []
    for elm in body.find_all('h2', text='Unit Converter'):
        row = element_to_dict(elm.parent, category='answer-unit_converter')
        data.append(row)     
    return data

def related_local_biz_parser(body : element.Tag) -> List[Dict]:
    """Additional Google searches for local businesses."""
    data = []
    
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile('^kc:/local:sideways refinements')}):
        for item in elm.find_all('kp-carousel-item'):
            for link in item.find_all('a'):
                row = element_to_dict(link, 
                                      category='link-local_people_also_search')
                data.append(row)
    return data

def sports_table_parser(body : element.Tag) -> List[Dict]:
    """Tables of sports info"""
    data = []
    for elm in body.find_all('g-expandable-content',
                             attrs = {'aria-hidden' : 'false',
                                      'style' : True,
                                      'jscontroller' : True,
                                      'jsaction' : True}):
         for table in elm.find_all('table', recursive=True, 
                                   attrs={'class' : True}):
            row = element_to_dict(table, 
                                  category='answer-sports_table')
            data.append(row)
    return data

def knowledge_panel_factoids_parser(body : element.Tag) -> List[Dict]:
    """
    Factoids parsed from the open web.
    Only finds those without links, the links will show up as 'link-google' ala the link_parser.
    """
    data = []
    for elm in body.find_all('div', 
                             attrs={'data-attrid' : re.compile('^(kc:|ss:|hw:|okra:)'),
                                    'lang' : True}):
        for span in elm.find_all('span', recursive=True, 
                                 attrs={'role' : False, 
                                        'aria-level' : False,
                                        'jsaction' : False}):
            if (span.text 
                  and len(span.text) > 1):
                
                not_under_link = True
                # make sure the span doesn't have an organic link.
                for link in span.find_all('a', href=True):
                    link_domain = get_domain(link['href'])
                    if (link_domain not in javascript + ['google.com']
                          and link_domain[0] != '/'):
                        not_under_link = False
                        
                # make sure the span isn't in a link
                check = span
                for _ in range(4):
                    check = check.parent
                    if check.name == 'a':
                        not_under_link = False
                        break
                if not_under_link:
                    row = element_to_dict(span, 
                                          category='answer-knowledge_graph_factoid')
                    data.append(row)         
    return data

def map_parser(body : element.Tag) -> List[Dict]:
    """Links to a map."""
    data = []
    for elm in body.find_all('h2', text='Map Results'):
        for div in elm.parent.find_all('div', recursive=True,
                                       attrs={'class' : re.compile('^.*map.*$')}):
      
            row = element_to_dict(div, category='link-google_map_2')
            data.append(row)   
    return data

def vote_parser(body : element.Tag) -> List[Dict]:
    """Sponsored votes."""
    data = []
    for elm in body.find_all('div', 
                             attrs={'jsaction' : re.compile("^submit_votes")}):
        row = element_to_dict(elm, category='ads-votes')
        data.append(row)   
    return data
        