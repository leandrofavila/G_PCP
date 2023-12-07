from Con_BD import DB
from jinja2 import Environment, FileSystemLoader
from Dispara_Email import DisparaEmail


env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('templates/index.html')
db_instance = DB()
df = db_instance.itens_comp_emb_nao()
html_content = template.render(df=df)

with open('output.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

dispara_email = DisparaEmail(html_content)

dispara_email.dispara_email("ITENS COMPRADOS COM EMBARQUE NÃO")
