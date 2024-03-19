from Con_BD import DB
from jinja2 import Environment, FileSystemLoader
from Dispara_Email import DisparaEmail


env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('templates/index.html')

db_instance = DB()
df = db_instance.itens_comp_emb_nao()
#print(df.to_string())
curr_lis = df['Cod. Item Pai'].tolist()

with open(rf"C:\Users\pcp03\PycharmProjects\G_PCP\last_lis.txt", 'r') as txt:
    last_lis = [iten for iten in txt.read().split(', ')]
    print(last_lis)
    if last_lis is None or curr_lis != last_lis:
        df_filtered = df[~df['Cod. Item Pai'].isin(last_lis)]
        if not df_filtered.empty:
            html_content = template.render(df=df_filtered)

            with open('output.html', 'w', encoding='utf-8') as file:
                file.write(html_content)

            dispara_email = DisparaEmail(html_content, "ITENS COMPRADOS COM EMBARQUE NÃO")
            dispara_email.dispara_email()
    else:
        print('Não há itens novos para mandar por email.')

with open(rf"C:\Users\pcp03\PycharmProjects\G_PCP\last_lis.txt", 'w+') as text:
    text.write(', '.join(map(str, curr_lis)))
