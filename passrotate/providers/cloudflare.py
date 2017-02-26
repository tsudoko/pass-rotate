from passrotate.provider import Provider, ProviderOption, register_provider
from passrotate.forms import get_form
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import json

def get_bootstrap(html):
    soup = BeautifulSoup(html, "html.parser")
    script = [s.text for s in soup.find_all("script") if s.text.startswith("window.bootstrap")][0]
    return json.loads(script[len("window.boostrap = "):-1])

class Cloudflare(Provider):
    """
    [cloudflare.com]
    email=Your Cloudflare email address
    """
    name = "Cloudflare"
    domains = [
        "cloudflare.com",
        "www.cloudflare.com"
    ]
    options = {
        "email": ProviderOption(str, "Your Cloudflare email address")
    }

    def __init__(self, options):
        self.email = options["email"]

    def prepare(self, old_password):
        self._session = requests.Session()
        r = self._session.get("https://www.cloudflare.com/a/login")
        bs = get_bootstrap(r.text)
        form = {
            "email": self.email,
            "password": old_password,
            "security_token": bs["data"]["security_token"]
        }
        r = self._session.post("https://www.cloudflare.com/a/login", data=form)
        url = urlparse(r.url)
        if url.path != "/a/overview":
            raise Exception("Failed to log into Cloudflare with current password")
        r = self._session.get("https://www.cloudflare.com/a/account/my-account")
        bs = get_bootstrap(r.text)
        self._atok = bs["atok"]

    def execute(self, old_password, new_password):
        r = self._session.put("https://www.cloudflare.com/api/v4/user/password", json={
            "new_password": new_password,
            "new_password_confirm": new_password,
            "old_password": old_password,
        }, headers={
            "x-atok": self._atok
        })
        if r.status_code != 200:
            raise Exception("Failed to update Cloudflare password")

register_provider(Cloudflare)
