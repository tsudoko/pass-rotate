from passrotate.provider import register_provider, ProviderOption
from bs4 import BeautifulSoup
import requests

class YCombinator:
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
        soup = BeautifulSoup(r.text, "html.parser")
        hidden_inputs = soup.find_all("input", type="hidden")
        self._form = { i.get("name", ""): i.get("value", "") for i in hidden_inputs }

    def execute(self, old_password, new_password):
        self._form.update({ "oldpw": old_password, "pw": new_password })
        r = self._session.post("https://news.ycombinator.com/r",
                data=self._form, allow_redirects=False)
        if r.status_code != 302:
            raise Exception("Failed to update Hacker News password")

register_provider(YCombinator)
