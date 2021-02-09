import os

import webapp2

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class MainPage(Handler):
    def get(self):
        self.write("Hello")

app = webapp2.WSGIApplication( [("/", MainPage)], debug = True)
