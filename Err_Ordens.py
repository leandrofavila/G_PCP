from Con_BD import DB

db = DB()
lista_planej = db.planejador_errado()


print(lista_planej.to_string())
# nao tem planejador padrao


def verifi_planejador():
    global lista_planej
    err_planej = {}
    for idx, op in lista_planej.iterrows():
        if 'PUNCIONADEIRA' in list(str(op['SEQ']).split('|')) and op['PLANEJADOR'] != 'PL004 - PUNCIONADEIRA (PRODUCAO)':
            err_planej[op['NUM_ORDEM']] = [op['PLANEJADOR'], 'PL004 - PUNCIONADEIRA (PRODUCAO)']

        if 'LIMPAR-PLASMA' in list(str(op['SEQ']).split('|')) and op['PLANEJADOR'] != 'PL002 - PLASMA (PRODUCAO)':
            err_planej[op['NUM_ORDEM']] = [op['PLANEJADOR'], 'PL002 - PLASMA (PRODUCAO)']

        # print(op['PLANEJADOR'])

    return err_planej


def verif_oper():
    err_operacao = {}
    for idx, op in lista_planej.iterrows():
        ver_list = list(str(op['SEQ']).split('|'))
        if 'CORTAR' in ver_list[0]:
            if ver_list[1] not in ['PLASMA', 'PUNCIONADEIRA', 'LASER', 'GUILHOTINA', 'SERRA-FITA', 'METALEIRA',
                                   'LIXADEIRA']:
                err_operacao[op['NUM_ORDEM']] = f"Cortar com maquina errada{[ver_list[0], ver_list[1]]}"
        if 'PONTEAR' in ver_list[0]:
            if ver_list[1] not in ['MIG']:
                err_operacao[op['NUM_ORDEM']] = f"Pontear sem mig{[ver_list[0], ver_list[1]]}"
        for i in range(len(ver_list) - 1):
            if ver_list[i] == 'SOLDAR' and ver_list[i + 1] != 'MIG':
                err_operacao[op['NUM_ORDEM']] = f"Soldar sem mig{[ver_list[0], ver_list[1]]}"
    return err_operacao


print(verif_oper())
