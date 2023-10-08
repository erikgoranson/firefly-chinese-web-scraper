import requests
from bs4 import BeautifulSoup
import re
import json
import logging
import argparse

OUTPUT_FILE = 'firefly_chinese.json'

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

PARSER = argparse.ArgumentParser(description='A webscraper for FireflyChinese.com')
PARSER.add_argument('-s', '--save', action='store_true', help='save the output to JSON')
PARSER.add_argument('-v', '--verbose', action='store_true', help='print the scraped data to the console')
PARSER.add_argument('-p', '--page', default=7, type=int, help='the max number of pages to parse from the blog. default is 7 (all currently available pages since 2012)')
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
            print(f'{key}:\t', value)
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

if __name__ == '__main__':
    try:
        get_firefly_chinese_data()
    except Exception:
        LOGGER.error(Exception)
        raise 