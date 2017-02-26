from passrotate.provider import Provider, ProviderOption, PromptType, register_provider
from passrotate.forms import get_form
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import base64
import requests

class Namecheap(Provider):
    """
    [namecheap.com]
    username=Your Namecheap username
    """
    name = "NameCheap"
    domains = [
        "namecheap.com"
    ]
    options = {
        "username": ProviderOption(str, "Your Namecheap username")
    }

    def __init__(self, options):
        self.username = options["username"]

    def prepare(self, old_password):
        # what the hell is wrong with you Namecheap
        self._session = requests.Session()
        r = self._session.get("https://www.namecheap.com/myaccount/login.aspx")
        form = get_form(r.text, type="body")
        form.update({
            "LoginUserName": self.username,
            "LoginPassword": "*************",
            "hidden_LoginPassword": base64.b64encode(old_password.encode()).decode().rstrip("="),
            "ctl00$ctl00$ctl00$ctl00$base_content$web_base_content$home_content$page_content_left$ctl02$LoginButton":
                "Sign in and Continue"
        })
        r = self._session.post("https://www.namecheap.com/myaccount/login.aspx", data=form)
        url = urlparse(r.url)
        if url.path == "/myaccount/login.aspx":
            raise Exception("Failed to log into Namecheap with current password")
        if url.path == "/myaccount/twofa/secondauth.aspx":
            form = get_form(r.text, id="aspnetForm")
            form.update({
                "ctl00$ctl00$ctl00$ctl00$base_content$web_base_content$home_content$page_content_left$CntrlAuthorization$ddlVerifyMethod":
                    "Text",
                "ctl00$ctl00$ctl00$ctl00$base_content$web_base_content$home_content$page_content_left$CntrlAuthorization$btnSendVerification":
                    "Send Security Code"
            })
            r = self._session.post("https://www.namecheap.com/myaccount/twofa/secondauth.aspx", data=form)
            if "You have reached the limit" in r.text:
                raise Exception("Namecheap has locked us out of further 2FA attempts. Wait 60 minutes and try again.")
            while url.path == "/myaccount/twofa/secondauth.aspx":
                form = get_form(r.text, id="aspnetForm")
                code = self.prompt("Enter your SMS authorization code", PromptType.sms)
                form.update({
                    "ctl00$ctl00$ctl00$ctl00$base_content$web_base_content$home_content$page_content_left$CntrlAuthorization$txtAuthVerification":
                        code,
                })
                r = self._session.post("https://www.namecheap.com/myaccount/twofa/secondauth.aspx", data=form)
                url = urlparse(r.url)
        r = self._session.get("https://ap.www.namecheap.com/Profile/Security")
        soup = BeautifulSoup(r.text, "html.parser")
        self._ncCompliance = soup.find("input", attrs={ "name": "ncCompliance" }).get("value", "")

    def execute(self, old_password, new_password):
        r = self._session.post("https://ap.www.namecheap.com/profile/security/password/change", data={
            "newPassword": new_password,
            "oldPassword": old_password,
        }, headers={
            "_NcCompliance": self._ncCompliance
        } ,allow_redirects=False)
        if r.status_code != 200:
            raise Exception("Failed to update NameCheap password")

register_provider(Namecheap)
