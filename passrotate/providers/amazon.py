from passrotate.provider import Provider, ProviderOption, register_provider
from passrotate.forms import get_form
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode
import requests

class Amazon(Provider):
    """
    [amazon.com]
    username=Your Amazon.com username
    """
    name = "Amazon"
    domains = [
        "amazon.com",
        "www.amazon.com"
    ]
    options = {
        "email": ProviderOption(str, "Your Amazon email account")
    }

    def __init__(self, options):
        self._email = options["email"]

    def prepare(self, old_password):
        self._session = requests.Session()
        r = self._session.get("https://www.amazon.com/ap/signin?openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
        form = get_form(r.text, name="signIn")
        form.update({
            "email": self._email,
            "password": old_password
        })
        r = self._session.post("https://www.amazon.com/ap/signin",
                data=form, allow_redirects=False)
        if r.status_code != 302:
            raise Exception("Current password is not valid for amazon.com")
        r = self._session.get("https://www.amazon.com/gp/css/homepage.html")
        soup = BeautifulSoup(r.text, "html.parse")
        security_url = next([a for a in soup.find_all("a") if urlparse(a.href).path == "/ap/cnep"]).href
        r = self._session.get(security_url)
        form = get_form(r.text, id="cnep_1a_password_form")
        url = urlparse(r.url)
        r = self._session.get("https://www.amazon.com" + url.path + "?" + urlencode(form))
        self._form = get_form(r.text, action="/ap/cnep")
        raise Exception()

    def execute(self, old_password, new_password):
        pass

# TODO: requests has issues with the cookie jar for amazon
#register_provider(Amazon)
