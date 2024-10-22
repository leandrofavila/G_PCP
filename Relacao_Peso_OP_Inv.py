from Con_BD import DB
import win32com.client as win32
import codecs

inv = win32.gencache.EnsureDispatch("Inventor.ApprenticeServer")

db = DB()
peso_focco = db.peso_ordens()
peso_focco['QTDE'] = peso_focco['QTDE'].astype(int)


caminhos = set(codecs.open(r"Z:\PCP\Leandro\kaminhos.txt", "r").readlines())
caminho = {}
for idx, vals in peso_focco.iterrows():
    for line in caminhos:
        if ("\\" + (str(vals['COD_ITEM'])) + ".ipt") in line:
            line = line.rstrip().removeprefix('file://')
            caminho[vals['COD_ITEM']] = line
            break


peso_focco['CAMINHOS'] = peso_focco['COD_ITEM'].map(caminho)



dic_peso_inv = {}
for idx, item in peso_focco.iterrows():
    try:
        apprenticeDoc = inv.Open(item['CAMINHOS'])
        oPropSets = apprenticeDoc.PropertySets
        PropertySet = oPropSets.Item("Design Tracking Properties")
        peso_inv = round(PropertySet.Item(39).Value / 1000, 3)
        if peso_inv:
            dic_peso_inv[item['COD_ITEM']] = peso_inv
    except Exception as err:
        print(err)


peso_focco['PESO_INV'] = peso_focco['COD_ITEM'].map(dic_peso_inv)
peso_focco = peso_focco.dropna(subset=['PESO_INV'])
peso_focco = peso_focco.drop('CAMINHOS', axis=1)
peso_focco['PESO_INV'] = round(peso_focco['PESO_INV'] * peso_focco['QTDE'], 2)

peso_focco['Diferenca'] = peso_focco['PESO'] - peso_focco['PESO_INV']

peso_focco = peso_focco[peso_focco['Diferenca'] > 1]

print(peso_focco.to_string())
