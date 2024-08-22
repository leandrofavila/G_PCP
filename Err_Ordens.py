from Con_BD import DB

db = DB()
lista_planej = db.planejador_errado()
print(lista_planej.to_string())
#nao tem planejador padrao


def verifi_planejador():
    global lista_planej
    err_planej = {}
    for idx, op in lista_planej.iterrows():
        if 'PUNCIONADEIRA' in list(str(op['SEQ']).split('|')) and op['PLANEJADOR'] != 'PL004 - PUNCIONADEIRA (PRODUCAO)':
            err_planej[op['NUM_ORDEM']] = [op['PLANEJADOR'], 'PL004 - PUNCIONADEIRA (PRODUCAO)']

        if 'LIMPAR-PLASMA' in list(str(op['SEQ']).split('|')) and op['PLANEJADOR'] != 'PL002 - PLASMA (PRODUCAO)':
            err_planej[op['NUM_ORDEM']] = [op['PLANEJADOR'], 'PL002 - PLASMA (PRODUCAO)']

        print(op['PLANEJADOR'])

    return err_planej


print(verifi_planejador())
