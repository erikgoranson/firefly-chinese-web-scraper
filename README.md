![](./screenshot.png)

# Firefly Chinese Web Scraper

An application for scraping translations of the Chinese phrases which appeared in Firefly and Serenity from an old fansite, https://fireflychinese.kevinsullivansite.net. Needed data to seed an API I'm making soon and wanted an excuse to practice some snek along the way

## Installation

Install the required Python packages by navigating to the project's root directory and running the following command.

```base
# install requirements
pip install -r requirements.txt
```

## Usage

In a terminal, run the following command. (If no other arguments are supplied, all translations from episode one, part 1 are returned)

Example commands:

```bash
# Run the scraper
python scraper.py

# Help on running the script
python scraper.py --help

# View the retrieved web output in console
python scraper.py --verbose

# get all translations from all episodes and the movie
python scraper.py --film --tvseries

# Save output to a JSON file with the `--save` flag
python scraper.py --film --save 

# gets all translations from the specific url provided from https://fireflychinese.kevinsullivansite.net/ 
python scraper.py --url https://fireflychinese.kevinsullivansite.net/phrase/q.html

```

## Example output from the resulting JSON file

```json
[
  {
        "category": "Chinese Dialog",
        "foreign_word": "gen1 hou2zi5 bi3 diu1 shi3",
        "characters": "Simplified characters: \u8ddf\u7334\u5b50\u6bd4\u4e22\u5c4e / Traditional characters: \u8ddf\u7334\u5b50\u6bd4\u4e1f\u5c4e",
        "back_translation": "compete throwing excrement with a monkey",
        "script_mandarin_translation": "gun HOE-tze bee DIO-se",
        "script_english_translation": "engage in a feces hurling contest with a monkey",
        "context": "\u201cHeart of Gold\u201d [In unpublished version of script], Inara, about what the companion house could go and do",
        "additional_info": "https://fireflychinese.kevinsullivansite.net/title/heartofgold.html"
    }
]
```