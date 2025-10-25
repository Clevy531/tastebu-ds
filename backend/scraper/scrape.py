from bs4 import BeautifulSoup
from pathlib import Path

path = Path("../htmls/west.txt")
html = path.read_text(encoding="utf-8")
soup = BeautifulSoup(html, "lxml")
# print(soup.prettify())
print(soup.title.string)