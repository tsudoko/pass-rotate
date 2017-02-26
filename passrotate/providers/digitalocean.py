from passrotate.provider import Provider, ProviderOption, register_provider
from passrotate.forms import get_form
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import requests

class DigitalOcean(Provider):
    """
    [digitalocean.com]
    email=Your Digital Ocean email address
    """
    name = "Digital Ocean"
    domains = [
        "digitalocean.com",
    ]
    options = {
        "email": ProviderOption(str, "Your Digital Ocean email address")
    }

    def __init__(self, options):
        self.email = options["email"]

    def prepare(self, old_password):
        self._session = requests.Session()
        r = self._session.get("https://cloud.digitalocean.com/login")
        form = get_form(r.text, id="new_user")
        form.update({
            "user[email]": self.email,
            "user[password]": old_password,
        })
        r = self._session.post("https://cloud.digitalocean.com/sessions", data=form)
        url = urlparse(r.url)
        if url.path != "/droplets":
            raise Exception("Unable to log into Digital Ocean with current password")
        soup = BeautifulSoup(r.text, "html.parser")
        for script in soup.find_all("script"):
            text = script.text.strip()
            if text.startswith("window.currentUser = "):
                j = json.loads(text[:text.index("\n")][len("window.currentUser = "):])
                self._user_id = j.get("uuid")
                break
        if not self._user_id:
            raise Exception("Unable to extract user ID")
        r = self._session.get("https://cloud.digitalocean.com/settings/profile?i=" +
                self._user_id[:6])
        soup = BeautifulSoup(r.text, "html.parser")
        self._csrf_token = soup.find("meta", attrs={ "name": "csrf-token" }).get("content", "")
        self._user = self._session.get("https://cloud.digitalocean.com/api/v1/users/" +
                self._user_id).json()

    def execute(self, old_password, new_password):
        self._user["user"].update({
            "current_password": old_password,
            "password": new_password,
            "password_confirmation": new_password,
        })
        r = self._session.put("https://cloud.digitalocean.com/api/v1/users/" + self._user_id,
                json=self._user, headers={
                    "X-CSRF-Token": self._csrf_token
                })
        if r.status_code != 200:
            raise Exception("Failed to update Digital Ocean password")

register_provider(DigitalOcean)
