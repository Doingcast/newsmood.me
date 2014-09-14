import webapp2
from webapp2_extras import jinja2
import urllib
from google.appengine.api import urlfetch
from datetime import date, timedelta
from HTMLParser import HTMLParser
import json
import logging

HP_KEY = '08002bd7-6107-41a6-8aef-d067dc823d70'
PARSER_TOKEN = '841f04fafb770c310d4aa9876a10a155ea922817'
initial_date = date.today() - timedelta(days = 30)

def get_relative_news(text):
    """
    Returns a list of news related to the text
    """
    params = {
        'indexes': 'news_eng',
        'text': text.encode('utf8'),
        'min_date': initial_date.strftime('%Y-%m-%d'),
        'apikey': HP_KEY,
        'summary': 'context'
    }
    form_data = urllib.urlencode(params)
    resp = urlfetch.fetch(
        url = "https://api.idolondemand.com/1/api/sync/querytextindex/v1?%s" % form_data,
        method= urlfetch.GET,
        deadline=60
    )
    resp = json.loads(resp.content)
    logging.info("### get_relative_news ###")
    logging.info(resp)
    return resp['documents']

def parser_main_content(url):
    """
    Extract the main content of a given URL
    """
    params = {
        'url' : url,
        'token' : PARSER_TOKEN,
        }
    form_data = urllib.urlencode(params)
    resp = urlfetch.fetch(
        url = "https://readability.com/api/content/v1/parser?%s" % form_data,
        method = urlfetch.GET,
        deadline=60
    )
    resp = json.loads(resp.content)
    logging.info("### parser_main_content ###")
    # logging.info(resp.content)
    return resp

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
        'text': text.encode('utf8'),
        'apikey': HP_KEY,
        'lang': lang
    }
    form_data = urllib.urlencode(params)
    resp = urlfetch.fetch(
        url = "https://api.idolondemand.com/1/api/sync/analyzesentiment/v1",
        method = urlfetch.POST,
        payload=form_data,
        deadline=60
    )
    resp = json.loads(resp.content)
    logging.info("### get_mood ###")
    logging.info(resp)
    return resp

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
            strip_tags(parser_main_content(news['reference'])['content'].replace('\n',' ').replace('  ',' '))
            )
        m = get_mood(main_content)
        moods.append(
            {
                'score': m['aggregate']['score'],
                'sentiment': m['aggregate']['sentiment'],
                'url': news['reference'],
                'title': news['title'],
                'summary':news['summary']
            }
        )
    return moods


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)