from dataclasses import dataclass
from selectolax.parser import HTMLParser

f_path = "/home/pelka/Workspace/ecuachecks/parsed_html.html"

with open(f_path, 'r', encoding='utf-8') as file:
    html_content = file.read()


@dataclass
class SupaItem:
    nombre: str


tree = HTMLParser(html_content)

first_node = tree.css_first('div[id="form:dDetalle"] tr')
second_node = tree.css_first('div[id="form:d_pendientes"]')
data = first_node.html + second_node.html
data = HTMLParser(data)


# items = data.css('.tabla-columna-datos')
items = data.css("#form:j_idt183")

for item in items:
    print(item.text())
