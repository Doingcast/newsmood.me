import requests
from datetime import date, timedelta
from HTMLParser import HTMLParser

HP_KEY = '08002bd7-6107-41a6-8aef-d067dc823d70'
PARSER_TOKEN = '841f04fafb770c310d4aa9876a10a155ea922817'
initial_date = date.today() - timedelta(days = 30)

def get_relative_news(text):
    """
    Returns a list of news related to the text
    """
    params = {
        'indexes': 'news_eng',
        'text': text,
        'min_date': initial_date.strftime('%Y-%m-%d'),
        'apikey': HP_KEY,
    }
    resp = requests.get(
        "https://api.idolondemand.com/1/api/sync/querytextindex/v1",
        params = params
    )
    try:
        return resp.json()['documents']
    except:
        print resp
        print text
        return "{}"

def parser_main_content(url):
    """
    Extract the main content of a given URL
    """
    params = {
        'url' : url,
        'token' : PARSER_TOKEN,
    }
    resp = requests.get(
        "https://readability.com/api/content/v1/parser",
        params = params
    )
    try:
        return resp.json()
    except:
        print resp
        print url
        return "{}"

class MLStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)
    def handle_charref(self, name):
        self.fed.append('&#%s;' % name)
    def get_data(self):
        return ''.join(self.fed)

def _strip_once(value):
    """
    Internal tag stripping utility used by strip_tags.
    """
    s = MLStripper()
    s.feed(value)
    s.close()
    return s.get_data()

def strip_tags(value):
    """Returns the given HTML with all tags stripped."""
    # Note: in typical case this loop executes _strip_once once. Loop condition
    # is redundant, but helps to reduce number of executions of _strip_once.
    while '<' in value and '>' in value:
        new_value = _strip_once(value)
        if new_value == value:
            # _strip_once was not able to detect more tags
            break
        value = new_value
    return value

def get_mood(text, lang = 'eng'):
    """
    Returns the mood of a given text
    """
    params = {
        'text': text,
        'apikey': HP_KEY,
        'lang': lang
    }
    resp = requests.get(
        "https://api.idolondemand.com/1/api/sync/analyzesentiment/v1",
        params = params
    )
    try:
        return resp.json()
    except:
        print resp
        print text
        return "{}"

def get_news_mood(text):
    """
    It does the magic.
        1. Get all news relative to the text
        2. Strip the best content of them
        3. Get_mood for those contents
    """
    moods = []
    for news in get_relative_news(text):
        main_content = "%s %s" % (
            news['title'],
            strip_tags(parser_main_content(news['reference'])['content'])
        )
        m = get_mood(main_content)
        moods.append(
            {
                'score': m['aggregate']['score'],
                'sentiment': m['aggregate']['sentiment'],
                'url': news['reference'],
                'title': news['title'],
            }
        )
    return moods