import webapp2
from webapp2_extras import jinja2
import json
from utils import get_news_mood, BaseHandler
from google.appengine.api import memcache


_instanceCache = dict()

class RootHandler(BaseHandler):
    def get(self):
        # Google's front end cache 15 min
        seconds_valid = 15*60 # 15 minutes
        self.response.headers['Cache-Control'] = "public, max-age=%d" % seconds_valid

        context = {'slogan': 'Extract and visualize sentiment from news'}
        q = self.request.get('q') if self.request.get('q') != '' else None
        if q:
            context['q'] = q
        self.render_response('index.html', **context)

class SearchHandler(BaseHandler):
    def post(self):
        # Google's front end cache 15 min
        seconds_valid = 15*60 # 15 minutes
        self.response.headers['Cache-Control'] = "public, max-age=%d" % seconds_valid

        # try to get resp from memcache, if success use, if not insert/update
        def get_resp_cache(query):
            data = memcache.get('resp_'+query)
            if data is not None:
                return data
            else:
                data = get_news_mood(query)
                memcache.add('resp_'+query, data, 6*60*60)
                return data

        query = self.request.get('query')
        if query:
            # resp = get_news_mood(query)
            resp = get_resp_cache(query)
        else:
            resp = ""
        
        # if 'query_'+query in _instanceCache:
        #     _instanceCache['query_'+query] = resp
        #     # ano_mes_dia

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(resp))

app = webapp2.WSGIApplication([
    ('/', RootHandler),
    ('/search', SearchHandler),
    ], debug=True)