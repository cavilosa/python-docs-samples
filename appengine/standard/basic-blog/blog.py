import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class NewPost(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        self.render("blog.html")


class SubmittedPost(Handler):
    def get(self, id="", subject="", content=""):
        self.render("permalink.html")


class NewPostHandler(Handler):
    def render_front(self, subject="", content="", error="", id=""):
        self.render("newpost.html", subject=subject, content = content,
                    error = error, id = id)

    def get(self):
        self.render_front()

    def post(self):
        have_error = False
        subject = self.request.get("subject")
        content = self.request.get("content")

        if content and subject:
            p = NewPost(subject=subject, content=content)
            p.put()
            id = p.key()
            self.redirect("/blog/%s" % id)
        else:
            error = "title and content should be present"
            self.render_front(subject, content, error)

app = webapp2.WSGIApplication( [("/blog", MainPage),
                                ("/blog/newpost", NewPostHandler),
                                ("/blog/([A-Za-z0-9-]+)", SubmittedPost )
                                ], debug = True)
