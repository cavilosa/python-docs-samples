import os

import jinja2
import webapp2
import codecs
import cgi
import re
#import asyncio

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

class SignUpHandler(Handler):
    def write_form(self, errorName="", PasswordError="", EmailError=""):
        self.render("signup.html")

    def get(self):
        self.write_form()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        username = validateName(username)
        password = validateName(password)
        verify = validatePasswordIdentical(password, verify)
        email = validateEmail(email)

        if username == "error":
            email = self.request.get("email")
            username = self.request.get("username")
            errorName = "That is not a valid username"
            self.render("signup.html", errorName = errorName,
                    username = username, email = email)
        elif password == "error":
            email = self.request.get("email")
            username = self.request.get("username")
            PasswordError = "That wasn't a valid password"
            self.render("signup.html", username = username, email = email,
                                       PasswordError = PasswordError)
        elif verify == "error":
            email = self.request.get("email")
            username = self.request.get("username")
            VerifyError = "Your passwords didn't match."
            self.render("signup.html", username = username, email = email,
                                       VerifyError = VerifyError)
        elif username == "error" and password == "error":
            email = self.request.get("email")
            username = self.request.get("username")
            errorName = "That is not a valid username."
            PasswordError = "The password is invalid."
            self.render("signup.html", errorName = errorName,
                    username = username, PasswordError = PasswordError,
                    email = email)
        elif username == "error" and password == "error" and verify == "error":
            email = self.request.get("email")
            username = self.request.get("username")
            errorName = "That is not a valid username."
            PasswordError = "The password is invalid."
            VerifyError = "Your passwords didn't match."
            self.render("signup.html", errorName = errorName,
                    username = username, PasswordError = PasswordError,
                    email = email, VerifyError = VerifyError)
        elif password == "error" and verify == "error":
            email = self.request.get("email")
            username = self.request.get("username")
            PasswordError = "The password is invalid."
            VerifyError = "Your passwords didn't match."
            self.render("signup.html", username = username,
                        PasswordError = PasswordError, email = email,
                        VerifyError = VerifyError)
        elif email == "error":
            email = self.request.get("email")
            username = self.request.get("username")
            EmailError = "That's not a valid email."
            self.render("signup.html", username = username, email = email,
                        EmailError = EmailError)

        else:
            path = "/welcome?username=" + escape_html(username)
            self.redirect(path)


class WelcomeHandler(Handler):
    def get(self):
        username = self.request.get("username")
        self.render("welcome.html", username = username)


app = webapp2.WSGIApplication( [("/", MainPage),
                                ("/fizzbuzz", FizzBuzzHandler),
                                ("/rot13", Rot13Handler),
                                ("/signup", SignUpHandler),
                                ("/welcome", WelcomeHandler)
                                ], debug = True)
