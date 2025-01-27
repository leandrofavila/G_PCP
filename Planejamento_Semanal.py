import pandas as pd

url = "https://docs.google.com/spreadsheets/d/1NVus19YE11fISGlWok06pflN5kVPRisixiVBp_0mUtU/export?format=csv&gid=0"
df = pd.read_csv(url, names=[
    "CLIENTE", "PEDIDO", "PROJETO", "DESCRIÇÃO DO EQUIPAMENTO", "DATA", "FRETE", "TIPO DE VEICULO", "MOTORISTA",
    "ENTREGA", "CARREGAMENTOS", "SUPRIMENTOS", "PRAZO CONTRATO", "OBSERVAÇÕES GERAIS", "???", "????", "?????", "??????"
    , "???????", "????????", "?????????", "???????????"
])


month_rows = df['DESCRIÇÃO DO EQUIPAMENTO'].str.contains(r"MÊS \d{2} -", na=False)
month_indices = df[month_rows].index

week_rows = df['DESCRIÇÃO DO EQUIPAMENTO'].str.contains(r"SEMANA \d{2} -", na=False)
week_indices = df[month_rows].index

dfs = {}
for i, start_idx in enumerate(month_indices):
    month_name = df.loc[start_idx, 'DESCRIÇÃO DO EQUIPAMENTO'].strip()

    end_idx = month_indices[i + 1]if i + 1 < len(month_indices) else len(df)

    dfs[month_name] = df.loc[start_idx + 2: end_idx].reset_index(drop=True)


for month, sub_df in dfs.items():
    print(month)
    sub_df = sub_df.dropna(how='all')
    print(sub_df.to_string())
    print('-' * 200)











# todo -pela API, depende de autorizações na conta da empresa -_-
#import pandas as pd
#import gspread
#from oauth2client.service_account import ServiceAccountCredentials
#
## Configuração do acesso
#scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
#client = gspread.authorize(credentials)
#
## Acessar a planilha pelo ID
#spreadsheet_id = "1NVus19YE11fISGlWok06pflN5kVPRisixiVBp_0mUtU"
#sheet = client.open_by_key(spreadsheet_id).sheet1
#
## Obter os dados como DataFrame
#data = sheet.get_all_records()
#df = pd.DataFrame(data)
#
#print(df.head())
#