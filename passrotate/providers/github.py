from passrotate.provider import Provider, ProviderOption, PromptType, register_provider
from passrotate.forms import get_form
from urllib.parse import urlparse
import requests

class GitHub(Provider):
    """
    [github.com]
    username=Your GitHub username
    """
    name = "GitHub"
    domains = [
        "github.com",
    ]
    options = {
        "username": ProviderOption(str, "Your GitHub username")
    }

    def __init__(self, options):
        self.username = options["username"]

    def prepare(self, old_password):
        self._session = requests.Session()
        r = self._session.get("https://github.com/login")
        form = get_form(r.text)
        form.update({
            "login": self.username,
            "password": old_password
        })
        r = self._session.post("https://github.com/session", data=form)
        if r.status_code != 200:
            raise Exception("Unable to log into GitHub account with current password")
        url = urlparse(r.url)
        while url.path == "/sessions/two-factor":
            form = get_form(r.text)
            code = self.prompt("Enter your two factor (TOTP) code", PromptType.totp)
            form.update({ "otp": code })
            r = self._session.post("https://github.com/sessions/two-factor", data=form)
            url = urlparse(r.url)
        r = self._session.get("https://github.com/settings/admin")
        self._form = get_form(r.text, id="change_password")

    def execute(self, old_password, new_password):
        self._form.update({
            "user[old_password]": old_password,
            "user[password]": new_password,
            "user[password_confirmation]": new_password,
        })
        r = self._session.post("https://github.com/account", data=self._form)

register_provider(GitHub)
