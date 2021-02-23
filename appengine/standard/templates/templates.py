import os
import random
import string
import hashlib
import jinja2
import webapp2
import codecs
import cgi
import re
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def escape_html(s):
    return cgi.escape(s, quote = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        # gets items out of url
        items = self.request.get_all("food")
        # passes items into the html shopping_list template
        self.render("shopping_list.html", items = items)

class FizzBuzzHandler(Handler):
    def get(self):
        n = self.request.get("n", 0)
        n = n and int(n) # if n: n = int(n):
        self.render("fizzbuzz.html", n = n)

class Rot13Handler(Handler):
    def get(self):
        self.render("rot13.html")

    def post(self):
        text = self.request.get("text");
        if text:
            text = codecs.encode(text, "rot_13")
            self.render("rot13.html", text = text)
        else:
            self.render("rot13.html")


def validateName(username):
    x = re.search("^[a-zA-Z0-9_-]{3,20}$", username)
    if x:
        return username
    else:
        errorName = "error"
        return errorName


def validatePassword(password):
    x = re.search("^.{3,20}$", password)
    if x:
        return password
    else:
        password = "error"
        return password

def validatePasswordIdentical(first, second):
    if first == second:
        return first, second
    else:
        identical = "error"
        return identical

def validateEmail(email):
    x = re.search("^[\S]+@[\S]+.[\S]+$", email)
    if x:
        return email
    else:
        email = "error"
        return email

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(",")[1]
    return h == make_pw_hash(name, pw, salt)

class Cookies(db.Model):
    username = db.StringProperty(required = True)
    #h = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class SignUpHandler(Handler):
    def write_form(self, errorName="", PasswordError="", EmailError=""):
        self.render("signup.html")

    def get(self):
        self.write_form()

    def post(self):
        have_error = False
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        username = validateName(username)
        password = validateName(password)
        verify = validatePasswordIdentical(password, verify)

        if email:
            email = validateEmail(email)

        params = dict(username=username, email=email)

        if username == "error":
            params["errorName"] = "That is not a valid username"
            have_error = True

        if password == "error":
            params["PasswordError"] =  "That wasn't a valid password"
            have_error = True

        if verify == "error":
            params["VerifyError"] = "Your passwords didn't match."
            have_error = True

        if email == "error":
            params["EmailError"] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render("signup.html", **params)
        else:
            username = username.encode("ascii", "ignore")
            password = password.encode("ascii", "ignore")
            #h = make_pw_hash(username, password, salt=None)

            if email != "":
                email = email
            else:
                email = " "

            check_name = db.GqlQuery("SELECT * FROM Cookies WHERE username='%s'" % username)
            if check_name:
                for name in check_name:
                    params["errorName"] = "This username is in use"
                self.render("signup.html", **params)

            else:
                    #h_pw = make_pw_hash(username, password, salt=None)  h = h_pw,
                p = Cookies(username = username,  email = email)
                p.put()
                self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/; password=%s'
                                           % (username, password))
                self.redirect("/welcome")


class WelcomeHandler(Handler):
    def get(self):
        username = self.request.cookie.get("name")
        self.render("welcome.html", username = username)



app = webapp2.WSGIApplication( [("/", MainPage),
                                ("/fizzbuzz", FizzBuzzHandler),
                                ("/rot13", Rot13Handler),
                                ("/signup", SignUpHandler),
                                ("/welcome", WelcomeHandler)
                                ], debug = True)
