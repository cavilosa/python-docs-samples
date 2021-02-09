# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2

form = """
<form method="post" action="/testform">
    <input name="q">
    <input type="submit">
</form>
"""
# defaut method is get


class MainPage(webapp2.RequestHandler):
    def get(self):
        #self.response.headers['Content-Type'] = 'text/html'
        # default text/html for goggle aop engine - text/html
        self.response.write(form)

class TestHandler(webapp2.RequestHandler):
    def post(self): # with post method q parameter is not in url
        q = self.request.get("q")
        self.response.out.write(q)
        #self.response.headers['Content-Type'] = 'text/html'
        #self.response.out.write(self.request) # see HTTP request in browser
        #"""self.request.referer = shows main page"""

        # get inclides q in url and post includes the data in request body

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ("/testform", TestHandler)
], debug=True)
