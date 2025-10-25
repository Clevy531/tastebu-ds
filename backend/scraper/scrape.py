import requests
from bs4 import BeautifulSoup

url = "https://www.bu.edu/dining/location/west/#menu"
headers = {"User-Agent": "tastebu-hackathon/1.0 (+contact@example.com)"}

resp = requests.get(url, headers=headers, timeout=20)
resp.raise_for_status()  # throws if 4xx/5xx

html = resp.text
soup = BeautifulSoup(html, "lxml")  # or "html.parser"
print(soup.find_all("p"))
