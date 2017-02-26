from passrotate.provider import Provider, ProviderOption, register_provider
from passrotate.forms import get_form
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests

class Linode(Provider):
    """
    [linode.com]
    username=Your Linode username
    expires=Optional, months till new password expires (0, 1, 3, 6, 12)
    """
    name = "Linode"
    domains = [
        "linode.com",
    ]
    options = {
        "username": ProviderOption(str, "Your Linode username"),
        "expires": ProviderOption({
            "Never": "0",
            "1 month": "1",
            "3 months": "3",
            "6 months": "6",
            "12 months": "12",
        }, "Password expiry")
    }

    def __init__(self, options):
        self.username = options["username"]
        self.expiry = options.get("expires") or "0"

    def prepare(self, old_password):
        self._session = requests.Session()
        r = self._session.get("https://manager.linode.com")
        form = get_form(r.text, id="CFForm_1")
        form.update({
            "auth_username": self.username,
            "auth_password": old_password,
        })
        r = self._session.post("https://manager.linode.com/session/login", data=form)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title")
        # TODO: TOTP
        if title.text != "Session Engaged!":
            raise Exception("Unable to log into Linode with your current password")
        r = self._session.get("https://manager.linode.com/profile/index")
        # Linode has a weird form on this page
        soup = BeautifulSoup(r.text, "html.parser")
        inputs = soup.find_all("input")
        form = {
            i.get("name", "" ): i.get("value", "") or "" for i in inputs if i.get("name", "")
        }
        form.update({ "auth_password": old_password })
        r = self._session.post("https://manager.linode.com/profile/reauth", data=form)
        r = self._session.get("https://manager.linode.com/profile/auth")
        # This form is also weird. Why you gotta be weird, Linode?
        soup = BeautifulSoup(r.text, "html.parser")
        self._form = {
            "authenticity_token": soup.find("input", attrs={ "name": "authenticity_token" }).get("value", "")
        }

    def execute(self, old_password, new_password):
        self._form.update({
            "password": new_password,
            "password2": new_password,
            "expires": self.expiry
        })
        r = self._session.post("https://manager.linode.com/profile/password", data=self._form)
        if r.status_code != 200:
            raise Exception("Failed to update Linode password")

register_provider(Linode)
