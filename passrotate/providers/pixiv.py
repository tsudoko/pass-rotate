from passrotate.provider import Provider, ProviderOption, register_provider
from passrotate.forms import get_form
import requests
from urllib.parse import urlparse

class Pixiv(Provider):
    """
    [pixiv.net]
    username=Your pixiv username
    """
    name = "pixiv"
    domains = [
        "www.pixiv.net",
        "touch.pixiv.net"
    ]
    options = {
        "username": ProviderOption(str, "Your pixiv username")
    }

    def __init__(self, options):
        self.username = options["username"]

    def prepare(self, old_password):
        self._session = requests.Session()
        r = self._session.get("https://accounts.pixiv.net/login")
        self._form = get_form(r.text, action="/login")
        self._form.update({
            "pixiv_id": self.username,
            "password": old_password
        })
        r = self._session.post("https://accounts.pixiv.net/api/login",
                data=self._form)
        r = self._session.get("https://www.pixiv.net/setting_userdata.php",
                params={"type": "password"})
        url = urlparse(r.url)
        if url.path != "/setting_userdata.php":
            raise Exception("Current password for pixiv is incorrect")
        self._form = get_form(r.text, action="setting_userdata.php")

    def execute(self, old_password, new_password):
        self._form.update({
            "check_pass": old_password
        })
        r = self._session.post("https://www.pixiv.net/setting_userdata.php",
                data=self._form)

        self._form = get_form(r.text, action="setting_userdata.php")
        self._form.update({
            "new_password_1": new_password,
            "new_password_2": new_password
        })
        r = self._session.post("https://www.pixiv.net/setting_userdata.php",
                data=self._form)
        url = urlparse(r.url)
        if url.path == "/setting_userdata.php":
            raise Exception("Failed to update pixiv password")

register_provider(Pixiv)
