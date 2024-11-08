from Extrai_Dados_Arranjos import TRATA_PDF
from Con_BD import DB

db_instance = DB()
data_arranjo = TRATA_PDF('12109406')

dt_arr = data_arranjo.get_data()
print(dt_arr.to_string())

df_apontamentos = db_instance.qtd_ops_apont_parciais(dt_arr['num_ordem'].tolist())
df_apontamentos[['QTD_ORDEM', 'QTD_APONT']] = df_apontamentos[['QTD_ORDEM', 'QTD_APONT']].astype(int)


print(df_apontamentos.to_string())
