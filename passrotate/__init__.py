from passrotate.provider import get_provider, get_providers
import passrotate.providers
from getpass import getpass

def _getpass_prompt(prompt, prompt_type):
    return getpass(prompt=prompt + ": ")

class PassRotate():
    def __init__(self):
        self.prompt = _getpass_prompt

    def get_provider_class(self, name):
        return get_provider(name)

    def get_provider(self, name, options):
        cls = self.get_provider_class(name)
        if not cls:
            return None
        instance = cls(options)
        instance._prompt = self.prompt
        return instance

    def get_providers(self):
        return get_providers()

    def set_prompt(self, prompt):
        self.prompt = prompt
