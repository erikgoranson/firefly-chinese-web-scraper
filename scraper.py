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
PARSER.add_argument('-u', '--url', default=None, type=str, help='the specific url at fireflychinese.kevinsullivansite.net from which to retrieve chinese translation data') 
PARSER.add_argument('-t', '--tvseries', action='store_true', help='gets all from all the episodes in Firefly')
PARSER.add_argument('-f', '--film', action='store_true', help='gets all from Serenity') 
ARGS = PARSER.parse_args()
 
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

# returns the target urls from https://fireflychinese.kevinsullivansite.net/ to be scraped 
def get_urls():
    urls = []
    
    # if url argument received, only scrape translations from that address
    if ARGS.url:
        urls.append(ARGS.url)
        
        if not ARGS.url.startswith('https://fireflychinese.kevinsullivansite.net/') :
            LOGGER.error('The provided url must come from https://fireflychinese.kevinsullivansite.net/ - please try again')
            exit()
        
        return urls
    
    # if no arguments provided, only scrape translations from episode 1, part 1
    if not ARGS.film and not ARGS.tvseries:
        urls = ['https://fireflychinese.kevinsullivansite.net/title/serenitypt1.html']
        return urls
    
    # for all else, return a list of applicable urls
    urlFragments = []
    
    if ARGS.tvseries:
        urlFragments.extend(['serenitypt1', 'serenitypt2', 'thetrainjob', 'bushwhacked', 'shindig', 'safe', 'ourmrsreynolds', 'jaynestown', 'outofgas', 'ariel', 'warstories', 'trash', 'themessage', 'heartofgold', 'objectsinspace'])
    
    if ARGS.film:
        urlFragments.append('serenitymovie')
        
    for fragment in urlFragments:
        urls.append(f'https://fireflychinese.kevinsullivansite.net/title/{fragment}.html')
        
    return urls

# scrapes translations from https://fireflychinese.kevinsullivansite.net/ at the given url(s)
def get_firefly_chinese_data(urls):
    output_data_list = []
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
            output_data['category'] = None
            output_data['foreign_word'] = None
            output_data['characters'] = None
            output_data['back_translation'] = None
            output_data['script_mandarin_translation'] = None
            output_data['script_english_translation'] = None
            output_data['context'] = None
            output_data['additional_info'] = url
            
            # categorize by the previous h2 heading
            prev_heading = str(pc.find_previous_sibling('h2').text)
            print(prev_heading)
            output_data['category'] = prev_heading
            
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
        urls = get_urls()
        get_firefly_chinese_data(urls)
    except Exception:
        LOGGER.error(Exception)
        raise 