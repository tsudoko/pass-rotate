from passrotate.provider import Provider, ProviderOption, PromptType, register_provider
from passrotate.forms import get_form
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, parse_qs

class Twitter(Provider):
    """
    [twitter.com]
    username=Your Twitter username
    """
    name = "Twitter"
    domains = [
        "twitter.com",
        "m.twitter.com"
    ]
    options = {
        "username": ProviderOption(str, "Your Twitter username")
    }

    def __init__(self, options):
        self.username = options["username"]

    def prepare(self, old_password):
        self._session = requests.Session()
        r = self._session.get("https://mobile.twitter.com/login")
        tk = self._session.cookies.get("_mb_tk")
        if not tk or r.status_code != 200:
            return False
        r = self._session.post("https://mobile.twitter.com/sessions", data={
            "authenticity_token": tk,
            "session[username_or_email]": self.username,
            "session[password]": old_password,
            "remember_me": 0,
            "wfa": 1,
            "redirect_after_login": "/home"
        })
        url = urlparse(r.url)
        if url.path == "/login/error":
            raise Exception("Current password for Twitter is incorrect")
        if url.path == "/account/locked":
            raise Exception("Twitter has locked us out of further login attempts")
        while url.path == "/account/login_verification":
            data = get_form(r.text)
            challenge_type = data.get("challenge_type")
            if challenge_type == "Sms":
                response = self.prompt("Enter your SMS authorization code", PromptType.sms)
            else:
                raise Exception("Unsupported two-factor method '{}'".format(challenge_type))
            data.update({ "challenge_response": response })
            r = self._session.post(
                    "https://mobile.twitter.com/account/login_verification",
                    data=data)
            url = urlparse(r.url)
        r = self._session.get("https://twitter.com")
        r = self._session.get("https://twitter.com/settings/password")
        self._form = get_form(r.text, id="password-form")

    def execute(self, old_password, new_password):
        self._form.update({
            "current_password": old_password,
            "user_password": new_password,
            "user_password_confirmation": new_password,
        })
        r = self._session.post("https://twitter.com/settings/passwords/update",
                data=self._form, headers={
                    "origin": "https://twitter.com",
                    "referer": "https://twitter.com/settings/password"
                })

register_provider(Twitter)
