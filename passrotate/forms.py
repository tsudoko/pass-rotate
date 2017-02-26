from bs4 import BeautifulSoup

def get_form(text, type="form", **kwargs):
    soup = BeautifulSoup(text, "html.parser")
    form = soup.find(type, attrs=kwargs)
    inputs = form.find_all("input")
    data = {
        i.get("name", "" ): i.get("value", "") or "" for i in inputs if i.get("name", "")
    }
    return data
