from passrotate.provider import Provider, ProviderOption, register_provider
from passrotate.forms import get_form
import requests

class YCombinator(Provider):
    """
    [news.ycombinator.com]
    username=Your Hacker News username
    """
    name = "YCombinator"
    domains = [
        "ycombinator.com",
        "news.ycombinator.com"
    ]
    options = {
        "username": ProviderOption(str, "Your Hacker News username")
    }

    def __init__(self, options):
        self.username = options["username"]

    def prepare(self, old_password):
        self._session = requests.Session()
        r = self._session.post("https://news.ycombinator.com/login", data={
            "acct": self.username,
            "pw": old_password
        }, allow_redirects=False)
        if "Bad login" in r.text:
            raise Exception("Unable to log into Hacker News with old password")
        r = self._session.get("https://news.ycombinator.com/changepw")
        self._form = get_form(r.text)

    def execute(self, old_password, new_password):
        self._form.update({ "oldpw": old_password, "pw": new_password })
        r = self._session.post("https://news.ycombinator.com/r",
                data=self._form, allow_redirects=False)
        if r.status_code != 302:
            raise Exception("Failed to update Hacker News password")

register_provider(YCombinator)
