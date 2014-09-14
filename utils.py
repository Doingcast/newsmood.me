import requests
from datetime import date, timedelta

HP_KEY = '08002bd7-6107-41a6-8aef-d067dc823d70'
PARSER_TOKEN = '841f04fafb770c310d4aa9876a10a155ea922817'
initial_date = date.today() - timedelta(days = 30)

def get_relative_news(text):
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

    return resp.json()

def parser_main_content(url):
    params = {
        'url' : url,
        'token' : PARSER_TOKEN,
    }
    resp = requests.get(
        "https://readability.com/api/content/v1/parser",
        params = params
    )

    return resp.json()