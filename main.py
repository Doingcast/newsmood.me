import webapp2
from utils import get_news_mood
import json

class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, webapp2!')

class GetJson(webapp2.RequestHandler):
    def get(self):
        text = self.request.get('text')
        if text:
            resp = get_news_mood(text)
        else:
            resp = ""

        self.response.write(json.dumps(resp))

app = webapp2.WSGIApplication([
    ('/', HelloWebapp2),
    ('/get', GetJson),
    ], debug=True)