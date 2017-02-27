from passrotate.provider import Provider, ProviderOption, PromptType, register_provider
import requests

class Discord(Provider):
    """
    [discordapp.com]
    email=Your Discord email address
    """
    name = "Discord"
    domains = [
        "discordapp.com"
    ]
    options = {
        "email": ProviderOption(str, "Your Discord email address")
    }

    def __init__(self, options):
        self.email = options["email"]

    def prepare(self, old_password):
        data = {
            "email": self.email,
            "password": old_password
        }

        self._session = requests.Session()
        r = self._session.post("https://discordapp.com/api/v6/auth/login",
                json=data)

        if r.status_code != 200:
            raise Exception("Unable to log into Discord with your current password: {}".format(r.json()))

        json = r.json()
        if json.get("mfa"):
            code = self.prompt("Enter your two factor (TOTP) code", PromptType.totp)
            data = {
                "code": code,
                "ticket": json.get("ticket")
            }
            r = self._session.post("https://discordapp.com/api/v6/auth/mfa/totp",
                    json=data)

            if r.status_code != 200:
                raise Exception("Failed to authenticate with the TOTP token: {}".format(r.json()))

        self._session.headers["authorization"] = r.json().get("token")

    def execute(self, old_password, new_password):
        data = {
            "password": old_password,
            "new_password": new_password
        }

        while True:
            r = self._session.patch("https://discordapp.com/api/v6/users/@me",
                    json=data)

            if r.status_code != 200:
                json = r.json()
                if json.get("code") == 60008:  # Invalid two-factor code
                    code = self.prompt("Enter your two factor (TOTP) code", PromptType.totp)
                    data["code"] = code
                else:
                    raise Exception("Failed to update Discord password: {}".format(json))
            else:
                break

register_provider(Discord)
