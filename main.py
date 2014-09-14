import webapp2
from webapp2_extras import jinja2
import json
from utils import get_news_mood, BaseHandler

class RootHandler(BaseHandler):
    def get(self):
        context = {'slogan': 'Extract and visualize sentiment from news'}
        self.render_response('index.html', **context)

class SearchHandler(BaseHandler):
    def post(self):
        query = self.request.get('query')
        if query:
            resp = get_news_mood(query)
        else:
            resp = ""

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(resp))

app = webapp2.WSGIApplication([
    ('/', RootHandler),
    ('/search', SearchHandler),
    ], debug=True)