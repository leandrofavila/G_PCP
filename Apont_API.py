from Extrai_Dados_Arranjos import TRATA_PDF
from Con_BD import DB
from Com_Focco_API import APONT


db_instance = DB()
data_arranjo = TRATA_PDF('12236941')

dt_arr = data_arranjo.get_data()
print(dt_arr.to_string())

df_apontamentos = db_instance.qtd_ops_apont_parciais(dt_arr['num_ordem'].tolist())
df_apontamentos[['QTD_ORDEM', 'QTD_APONT']] = df_apontamentos[['QTD_ORDEM', 'QTD_APONT']].astype('Int64')
df_apontamentos = df_apontamentos.groupby(['NUM_ORDEM', 'QTD_ORDEM', 'OPERACAO', 'SEQ'], as_index=False)['QTD_APONT'].sum()
df_apontamentos['qtd_disponivel'] = df_apontamentos['QTD_ORDEM'] - df_apontamentos['QTD_APONT']
#df_apontamentos = df_apontamentos[df_apontamentos['qtd_disponivel'] > 0]

df_apontamentos = df_apontamentos.sort_values(by='SEQ')
print(df_apontamentos.to_string())

apont = APONT()
cond = (df_apontamentos['OPERACAO'] == 'CORTAR') & (df_apontamentos['SEQ'] == 10)
