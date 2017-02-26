from enum import Enum
from getpass import getpass

_providers = list()
_provider_map = dict()
_provider_domains = dict()

def register_provider(provider):
    _providers.append(provider)
    _provider_map[provider.name] = provider
    for d in provider.domains:
        _provider_domains[d] = provider

def get_provider(domain):
    return _provider_map.get(domain) or _provider_domains.get(domain)

def get_providers():
    return _providers

def _getpass_prompt(prompt, prompt_type):
    return getpass(prompt=prompt + ": ")

_prompt = _getpass_prompt

def set_prompt(prompt):
    global _prompt
    _prompt = prompt

class PromptType(Enum):
    generic = "generic"
    totp = "totp"
    sms = "sms"

class ProviderOption:
    def __init__(self, type, doc, optional=False):
        self.type = type
        self.doc = doc
        self.optional = optional

class Provider:
    def prompt(self, prompt, prompt_type):
        global _prompt
        return _prompt(prompt, prompt_type)

import passrotate.providers
