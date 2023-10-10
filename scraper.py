import requests
from bs4 import BeautifulSoup
import re
import json
import logging
import argparse

OUTPUT_FILE = 'firefly_chinese.json'

BASE_URL = 'https://fireflychinese.kevinsullivansite.net/'

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

PARSER = argparse.ArgumentParser(description='A webscraper for fireflychinese.kevinsullivansite.net')
PARSER.add_argument('-s', '--save', action='store_true', help='save the output to JSON')
PARSER.add_argument('-v', '--verbose', action='store_true', help='print the scraped data to the console')

# old
PARSER.add_argument('-p', '--page', default=7, type=int, help='the max number of pages to parse from the blog. default is 7 (all currently available pages since 2012)')

PARSER.add_argument('-u', '--url', default=None, type=str, help='the specific url at fireflychinese.kevinsullivansite.net from which to retrieve chinese translation data') # add validation that confirms this begins with https://fireflychinese.kevinsullivansite.net/ and ends with .html. all pages there do this

PARSER.add_argument('-t', '--tvseries', action='store_true', help='gets all from all the episodes in Firefly')

PARSER.add_argument('-f', '--film', action='store_true', help='gets all from Serenity') 
ARGS = PARSER.parse_args()
 
# returns the value from the given field from a fireflychinese post
def get_field_value(post_field):
    splits = post_field.split(':')
    if 1 < len(splits):
        return splits[1].strip()
    return post_field

def save_as_json(list):
    try:
        with open(OUTPUT_FILE, mode='w', encoding='utf-8') as output_file:
            json.dump(list, output_file, indent=4)
    except Exception:
        LOGGER.error(f'An error occurred while trying to save scraped data to json: {Exception}')
        raise

def print_output_data(output_list):
    print('-------------')
    for item in output_list:
        for key, value in item.items():
            print(f'{key}:\t\t', value)
        print('-------------')

# scrapes information from each post at https://fireflychinese.com/
# loops through all existing pages - currently hardcoded to seven due to no new updates in 10+ years
def get_firefly_chinese_data(): 
    output_data_list = []
    
    base_url = 'https://fireflychinese.com/'
    
    for i in range(0, ARGS.page):
        if i == 1:
            url = base_url
        else:
            url = f'{base_url}page/{i}'
            
        try:
            data = requests.get(url)
            soup = BeautifulSoup(data.content, 'html.parser')
            page_content = soup.find('div', class_='postcontainer')
            posts = page_content.find_all('div', class_='video')
        except Exception:
            LOGGER.error(f'An error occurred while parsing HTML on {url}')
            raise
        
        for i, post in enumerate(posts):
        
            output_data = dict() 
        
            try:
                post_fields = post.find_all('p')
            except Exception:
                LOGGER.error(f'An error occurred while parsing HTML on post {i} of {url}')
                raise
        
            """
            retrieve and sanitize title info
            normally formatted such as 'River calls Mal a son of a drooling whore and a monkey (Ep5, “Safe” 2:54)'
            break this up into three values 
            """
            raw_title = post_fields[0].text
            title_parenthetical = re.findall('\(([^)]+)', raw_title)[0] # get text from inside of the parentheses on each title
            
            # split values into their individual components
            title_splits = title_parenthetical.split(', ', 1)
            title_sub_splits = title_splits[1].split('”') 
            if len(title_sub_splits) == 1:
                # sometimes title name is formatted like "title"\xa0 instead of “title”
                title_sub_splits = title_splits[1].split(u'\xa0') 


            # clean up the episode number as an actual num as it is inconsistently labled 'ep' or 'episode '
            raw_episode_number = title_splits[0]
            episode_number = re.sub(r'[^\d]', '', raw_episode_number)

            output_data['episode_number'] = episode_number
            output_data['episode_title'] = title_sub_splits[0].replace('“', '')
            output_data['episode_timestamp'] = title_sub_splits[1].strip()
        
            # remaining fields (basically KVPs)
            output_data['chinese'] = get_field_value(post_fields[1].text)
            output_data['english_translation'] = get_field_value(post_fields[2].text)
            output_data['context'] = get_field_value(post_fields[3].text)
            output_data['usage'] = get_field_value(post_fields[4].text)
            output_data['execution'] = get_field_value(post_fields[5].text)
        
        
            # links
            output_data['episode_clip'] = None
            output_data['pronunciation'] = None
            iframes = post.find_all('iframe')
            for frame in iframes:
                if "youtube" in frame.get('src'):
                    output_data['episode_clip'] = frame.get('src')
                if "soundcloud" in frame.get('src'):
                    output_data['pronunciation'] = frame.get('src')

            output_data_list.append(output_data)
            LOGGER.info(f'Added data from {raw_title} to output data')
        
    if not ARGS.save or ARGS.verbose:
        print_output_data(output_data_list)
        
    if ARGS.save:
        LOGGER.info(f'Saving data to {OUTPUT_FILE}')
        save_as_json(output_data_list)
    else:
        LOGGER.info('Output data is ready. To save to JSON, use the --save flag')

def get_urls():
    
    urls = []
    
    # if url, just do that and return it directly
    
    if ARGS.url:
        #urls.append(ARGS.url)
        urls = ARGS.url
        urls = ['https://fireflychinese.kevinsullivansite.net/title/serenitypt1.html'] # fix this later
        print(urls)
        # validate the url, then return 
        return urls
    
    # if no params, only ep1 pt1 stuff
    if not ARGS.film and not ARGS.tvseries:
        # urls.append('serenitypt1')
        urls = ['https://fireflychinese.kevinsullivansite.net/title/serenitypt1.html']
        print(urls)
        # validate the url, then return 
        return urls
    
    # if tv, film, just make a big list and return that
    if ARGS.tvseries:
        urls.extend(['serenitypt1', 'serenitypt2', 'thetrainjob', 'bushwhacked', 'shindig', 'safe', 'ourmrsreynolds', 'jaynestown', 'outofgas', 'ariel', 'warstories', 'trash', 'themessage', 'heartofgold', 'objectsinspace'])
    
    if ARGS.film:
        urls.append('serenitymovie')
        
    # debug
    for i, url in enumerate(urls):
        #url = f'https://fireflychinese.kevinsullivansite.net/title/{url}.html'
        #print(url)
        urls[i] = f'https://fireflychinese.kevinsullivansite.net/title/{url}.html'
        print(urls[i])
    
    return urls



def redo(urls):
    output_data_list = []
    print('wat')
    for url in urls:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
            } # for wordpress security
            data = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(data.content, 'html.parser')
            page_content = soup.find('div', class_='content')
            
        except Exception:
            LOGGER.error(f'An error occurred while parsing HTML on {url}')
            raise
        
        for pc in page_content.find_all([ 'section']):
                
            output_data = dict() 
            output_data['foreign_word'] = None
            output_data['characters'] = None
            output_data['back_translation'] = None
            output_data['script_mandarin_translation'] = None
            output_data['script_english_translation'] = None
            output_data['context'] = None
            output_data['additional_info'] = url
            
            # exclude anything after this header
            # this will cause only live-action quotes to be returned
            prev_sib = str(pc.find_previous_sibling().text)
            if prev_sib == "Cut Chinese Dialog" or prev_sib == "Visible Chinese":
                break
            
            foreign_word = pc.find(class_="foreignword")
            if foreign_word is not None:
                output_data['foreign_word'] = foreign_word.text
                
                headentry = pc.find(class_="headentry")
                head_entries = headentry.find_all('li')
                for entry in head_entries:
                
                    # chinese characters 
                    if "characters" in entry.text: 
                        output_data['characters'] = entry.text
                        
                    if "Back-translation" in entry.text:
                        # remove all span and i tags from this element
                        for e in entry.find_all(['span','i']):
                            e.decompose()
                        
                        # remove all leading whitespace 
                        back_translation = entry.text.strip()
                        
                        # remove all brackets and their insides
                        back_translation = re.sub(r'\[(.*?)\]', '', back_translation)
                        
                        output_data['back_translation'] = back_translation
                    
                    if "Script Mandarin translation" in entry.text:
                        
                        script_mandarin_translation = entry.find(class_="primary")
                        if script_mandarin_translation is not None:
                            output_data['script_mandarin_translation'] = script_mandarin_translation.text
                        
                    if "Translated from script English" in entry.text:
                        script_english_translation = entry.find(class_="primary")
                        if script_english_translation is not None:
                            output_data['script_english_translation'] = script_english_translation.text
                        
                    if "Context" in entry.text:
                        for e in entry.find_all(class_='category'):
                            e.decompose()
                        output_data['context'] = entry.text.strip()
                        
                output_data_list.append(output_data)
                LOGGER.info(f'Added data from {foreign_word.text} to output data')
    
    if not ARGS.save or ARGS.verbose:
        print_output_data(output_data_list)
        
    if ARGS.save:
        LOGGER.info(f'Saving data to {OUTPUT_FILE}')
        save_as_json(output_data_list)
    else:
        LOGGER.info('Output data is ready. To save to JSON, use the --save flag')

if __name__ == '__main__':
    try:
        # get_firefly_chinese_data()
        urls = get_urls()
        redo(urls)
    except Exception:
        LOGGER.error(Exception)
        raise 