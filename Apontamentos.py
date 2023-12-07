from Con_BD import DB
from Dispara_Email import DisparaEmail
import pandas as pd

db_instance = DB()


def df_apont():
    df = db_instance.apont()
    cols = ["NUM_ORDEM", "SEQ", "QTDE", "QUANTIDADE", "DT"]
    df[cols] = df[cols].fillna(0).apply(pd.to_numeric, errors='coerce').astype(int)
    df_0 = df[df['QUANTIDADE'] == 0]
    df['soma'] = df.groupby(['NUM_ORDEM', 'SEQ', 'QTDE'])['QUANTIDADE'].transform('sum')
    df['comp'] = df['soma'] == df['QTDE']
    df = df[df['comp'] == False].reset_index()
    df_maior = df[df['soma'] > df['QTDE']]
    return df_0, df_maior, df


def apont_0():
    df_0 = df_apont()[0]
    if not df_0.empty:
        quit()
        corpo_email = 'Favor atentar para os apontamentos com quantidade 0 nas ordens:\n \n '

        for idx, x in df_0.iterrows():
            if str(x['NUM_ORDEM']) not in corpo_email:
                corpo_email += f"\t-{x['NUM_ORDEM']} na sequência {str(x['OPERACAO']).rjust(3)}.\n"

        corpo_email += '''\nQualquer duvida estou a disposição.\n\nEmail de envio automatico, favor não responder.'''
        dispara_email = DisparaEmail(corpo_email)
        dispara_email.dispara_email("Ordens com quantidade apontada 0")
    else:
        print('Não há ordens com quantidade 0 no apontamento')


def apont_maior():
    df_maior = df_apont()[1]
    if not df_maior.empty:
        corpo_email = 'Favor atentar para os apontamentos com quantidade maior que a demanda:\n \n '

        for idx, x in df_maior.iterrows():
            corpo_email += f"\t-{x['NUM_ORDEM']} na operação {x['OPERACAO'].rjust(3)}.\n"

        corpo_email += '''\nQualquer duvida estou a disposição.\n\nEmail de envio automatico, favor não responder.'''
        dispara_email = DisparaEmail(corpo_email)
        dispara_email.dispara_email("Ordens com quantidade apontamento maior que da OP")
    else:
        print('Não há ordens com quantidade maior que a demanda')


def apont_parcial():
    df = df_apont()[2]
    if not df.empty:
        corpo_email = 'Favor atentar para os apontamentos parciais:\n \n '

        for idx, x in df.iterrows():
            corpo_email += f"\t-{x['NUM_ORDEM']} na operação {str(x['OPERACAO']).rjust(13)} quantidade da OP " \
                           f"{str(x['QTDE']).rjust(3)} apontada {str(x['QUANTIDADE']).rjust(3)}.\n"
        corpo_email += '___________________________________________________________________________________________\n\n'
        corpo_email += '''\nQualquer duvida estou a disposição.\n\nEmail de envio automatico, favor não responder.'''
        dispara_email = DisparaEmail(corpo_email)
        dispara_email.dispara_email("Ordens com apontamentos parciais")
    else:
        print('Não há ordens com apontamento parcial')


def err_consumos():
    df_consumos = pd.concat([db_instance.consumo('>', 'MIN', '<>'), db_instance.consumo('<', 'MAX', '=')],
                            ignore_index=True)
    if not df_consumos.empty:
        corpo_email = "Favor atentar para as OP's com consumos de demanda na operação errada:\n \n"

        for idx, x in df_consumos.iterrows():
            corpo_email += f"\t-{x['NUM_ORDEM']} possui  {x['COD_ITEM']} " \
                           f"{'consumo' if x['COD_ITEM'] == 1 else 'consumos'} na operação {x['DESCRICAO']}, embora  " \
                           f"essa não seja a {'ultima' if x['DESCRICAO'] == 'PINTAR' else 'primeira'} operação.\n"

        corpo_email += '___________________________________________________________________________________________\n\n'
        corpo_email += '''\nQualquer duvida estou a disposição.\n\nEmail de envio automatico, favor não responder.'''
        dispara_email = DisparaEmail(corpo_email)
        dispara_email.dispara_email("Consumos na operação errada.")
    else:
        print('Não há ordens com consumos errados')


apont_0()
apont_maior()
apont_parcial()
err_consumos()
