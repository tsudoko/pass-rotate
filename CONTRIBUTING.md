# Contributing

To get help, visit [#cmpwn on irc.freenode.net](http://webchat.freenode.net/?channels=cmpwn&uio=d4).

## Adding new password managers

If you'd like to write up a support script that can be used with the CLI for
your favorite password manager, add it to the `contrib/` directory.

## Adding new service providers

To add support for new service providers, add a file to `passrotate/providers/`.
Here's the bare-minimum:

```python
from passrotate.provider import Provider, ProviderOption, register_provider
from passrotate.forms import get_form
import requests

class YourProvider(Provider):
    # The docstring is shown in pass-rotate --provider-options yourprovider
    """
    [yourprovider.com]
    username=Your username
    # Other options, if applicable
    """
    name = "Your Provider"
    domains = [
        "yourprovider.com",
    ]
    options = {
        "username": ProviderOption(str, "Your username")
    }

    def __init__(self, options):
        self.username = options["username"]

    def prepare(self, old_password):
        pass # TODO

    def execute(self, old_password, new_password):
        pass # TODO

register_provider(YourProvider)
```

You'll want to import this file in `passrotate/providers/__init__.py`.

Then you have to reverse engineer the password reset process for the provider
you're trying to add. Most providers will want to use requests.Session to keep a
cookie jar available throughout the process, and them simulate a login in
prepare(). Then, in execute(), use the same session to submit the password
change form.

The reverse engineering process will largely involve your web browser's dev
tools. Use them to monitor network requests, then look for the relevant ones.
Look at forms and see what fields are present and try to deduce what's required
to complete the process. Look for notable cookies, and for things like CSRF
tokens. Check if your provider uses two-factor authentication, and test your
code with it enabled and disabled.

You can use `passrotate.form.get_form` to prepare a dict suitable for submission
to requests.Session.post derived from the inputs on a form in the response text.
Then you can add to this the appropriate fields from your options and the
supplied passwords.
