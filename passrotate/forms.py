from bs4 import BeautifulSoup

def get_form(text, **kwargs):
    soup = BeautifulSoup(text, "html.parser")
    form = soup.find("form", attrs=kwargs)
    inputs = form.find_all("input")
    data = {
        i.get("name", "" ): i.get("value", "") or "" for i in inputs if i.get("name", "")
    }
    return data
