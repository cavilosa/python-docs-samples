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
import hmac

secret = "secret"

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def escape_html(s):
    return cgi.escape(s, quote = True)

def make_secure_val(val):
    return "%s|%s" % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split("|")[0]
    if secure_val == make_secure_val(val):
        return val

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            "Set-Cookie", "%s=%s; Path=/" % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie("user_id")
        # reads the cookie, makes sure it is valid and sets user on the handler
        self.user = uid and User.by_id(int(uid))

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
    return '%s, %s' % (salt, h)

def valid_pw(name, pw, h):
    salt = h.split(",")[0]
    return h == make_pw_hash(name, pw, salt)

class User(db.Model):
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        u = User.all().filter("username=", name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(username=name,
                    pw_hash=pw_hash,
                    email=email)

class SignUpHandler(Handler):
    def write_form(self, errorName="", PasswordError="", EmailError=""):
        self.render("signup.html")

    def get(self):
        self.write_form()

    def post(self):
        have_error = False
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.verify = self.request.get("verify")
        self.email = self.request.get("email")

        self.username = validateName(self.username)
        self.password = validateName(self.password)
        self.verify = validatePasswordIdentical(self.password, self.verify)

        if self.email:
            self.email = validateEmail(self.email)

        params = dict(username=self.username, email=self.email)

        if self.username == "error":
            params["errorName"] = "That is not a valid username"
            have_error = True

        if self.password == "error":
            params["PasswordError"] =  "That wasn't a valid password"
            have_error = True

        if self.verify == "error":
            params["VerifyError"] = "Your passwords didn't match."
            have_error = True

        if self.email == "error":
            params["EmailError"] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render("signup.html", **params)
        else:
            u = User.all()
            u.filter("username =", self.username)
            r = u.get()
            if r:
                params = dict(username=self.username, email=self.email)
                params["errorName"] = "This username is in use"
                self.render("signup.html", **params)
            else:
                u = User.register(self.username, self.password, self.email)
                u.put()
                id = u.key().id()
                id_hash = make_secure_val(str(id))
                self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/'
                                                     % id_hash)
                self.redirect("/welcome")



class WelcomeHandler(Handler):
    def get(self):
        user_id = self.request.cookies.get("user_id")
        id = user_id.split("|")[0]
        h = user_id.split("|")[1]
        q = db.GqlQuery("SELECT * FROM User")
        usernames = [name.username for name in q]


        if check_secure_val(user_id):
            name = User.get_by_id(int(id))
            self.render("welcome.html", username = name.username, usernames=usernames)
        else:
            self.redirect("/signup")





app = webapp2.WSGIApplication( [("/", MainPage),
                                ("/fizzbuzz", FizzBuzzHandler),
                                ("/rot13", Rot13Handler),
                                ("/signup", SignUpHandler),
                                ("/welcome", WelcomeHandler)
                                ], debug = True)
