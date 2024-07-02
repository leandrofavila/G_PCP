from Con_BD import DB
from Dispara_Email import DisparaEmail
import pandas as pd

db_instance = DB()
df = db_instance.op_abertas()


df_group = df.groupby('LOCAL_PROD')
df_res = {}

for grp, grp_df in df_group:
    df_res[grp] = grp_df.reset_index(drop=True)


writer = pd.ExcelWriter('Ops_abertas_mais_30_dias.xlsx', engine='openpyxl')
df_res['PROD. SEDE'].to_excel(writer, sheet_name='SEDE', index=False)
df_res['PROD. BEVILAQUA'].to_excel(writer, sheet_name='BEVILAQUA', index=False)
df_res['PROD. ALMOX'].to_excel(writer, sheet_name='ALMOX', index=False)
writer.close()


if df_res:
    corpo_email = '''
    \nSegue em anexo listagem de ordens em aberto a mais de 30 dias.
    \nQualquer duvida entrar em contato com o PCP.
    '''
    file_path = "C:\\Users\\pcp03\\PycharmProjects\\G_PCP\\Ops_abertas_mais_30_dias.xlsx"
    disp_email = DisparaEmail(corpo_email, "Ordens em aberto a mais de 30 dias.", "Ops_abertas_mais_30_dias.xlsx")
    disp_email.dispara_email()
else:
    print('Não há ordens')
