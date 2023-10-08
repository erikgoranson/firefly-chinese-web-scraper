import requests
from bs4 import BeautifulSoup
import re
 
def get_field_value(post_field):
    splits = post_field.split(':')
    if 1 < len(splits):
        return splits[1].strip()
    return splits

#rename me
def get_chinese_data(): 
    # get all the data from each post
    
    output_data_list = []
    
    base_url = 'https://fireflychinese.com/'
    blog_pages = 7 # blog has not been updated since 2012. will add something to dynamically check page count if it becomes applicable
    
    for i in range(0, blog_pages):
        if i == 1:
            url = base_url
        else:
            url = f'{base_url}page/{i}'
            
        #logging
        data = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        print(f'check: {i}')
        
        try: 
            page_content = soup.find('div', class_='postcontainer')
            posts = page_content.find_all('div', class_='video')
        except Exception:
            #logging
            raise
    
        for post in posts:
        
            output_data = dict() 
        
            try:
                post_fields = post.find_all('p')
            except Exception:
                #logging
                raise
        
            #title stuff
            raw_title = post_fields[0].text
            title_parenthetical = re.findall('\(([^)]+)', raw_title)[0] #text from inside the parentheses of each title
            #print('raw title what', raw_title)
            title_splits = title_parenthetical.split(', ', 1)
            #print('title splits: ', title_splits)
            title_sub_splits = title_splits[1].split(' ')

            output_data['episode_number'] = title_splits[0] 
            output_data['episode_title'] = title_sub_splits[0]#.replace('“').replace('”')
            output_data['episode_timestamp'] = title_sub_splits[1]
        
        
            #other fields
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
                print("youtube" in frame.get('src'))
    
                #print(frame.get('src'))
                if "youtube" in frame.get('src'):
                    output_data['episode_clip'] = frame.get('src')
                if "soundcloud" in frame.get('src'):
                    output_data['pronunciation'] = frame.get('src')

            #print(post_fields[0])
        
            output_data_list.append(output_data)
        
    print(output_data_list)
        
###############################

if __name__ == '__main__':
    get_chinese_data()