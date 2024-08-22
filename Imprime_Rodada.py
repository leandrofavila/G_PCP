from PyPDF2 import *
import glob
import tkinter as tk
from tkinter import filedialog
import re
from Con_BD import DB
from Slice_Rodada import Slice
import itertools
import os


db = DB()


def carregamento():
    carr = re.findall('[0-9]{4}00', str(path[0]))
    carr = carr[0]
    return carr


def paths():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Selecione um arquivo PDF")
    return glob.glob(file_path) if file_path else ''


path = paths()
slice = Slice(path)
slice.roda_all()
car = carregamento()
ordens_agrupadas = slice.ordens_agrupadas

chave_para_remover = 'PL004 - PUNCIONADEIRA (PRODUCAO)'
if chave_para_remover in ordens_agrupadas:
    del ordens_agrupadas[chave_para_remover]

ordens_rodada = [ordem for sublis in ordens_agrupadas.values() for ordem in sublis]


def brancas_amarelas():
    pm = list(itertools.chain.from_iterable(v for k, v in ordens_agrupadas.items() if re.search('PL009 - PRE-MONTAGEM', k)))
    amarelas = []
    if pm:
        amarelas = db.filhas_pm(car, pm)
    brancas = [i for i in ordens_rodada if i not in amarelas]
    ordens_agrupadas_cor = {'brancas': brancas, 'amarelas': amarelas}
    print(ordens_agrupadas_cor)
    print('brancas', len(brancas), 'amarelas', len(amarelas))
    return ordens_agrupadas_cor


def imprime(cor, ops, impressora):
    merger = PdfMerger()
    #printer = win32print.OpenPrinter(impressora)
    #win32print.StartDocPrinter(printer, 1, ("Print Job", None, "RAW"))
    #win32print.StartPagePrinter(printer)
    for val in ops:
        op = rf"C:\Users\pcp03\PycharmProjects\G_PCP\splited_pdfs\{val}.pdf"
        merger.append(op) if op not in merger.inputs else None
        ops.remove(val)

    ops = rf"C:\Users\pcp03\PycharmProjects\G_PCP\rodada_amarelas_brancas\{car}_{cor}.pdf"
    merger.write(ops)
    os.startfile(ops, 'open')
    #win32api.ShellExecute(0, "print", ops, None, ".", 0)
    #
    #win32print.EndPagePrinter(printer)
    #win32print.EndDocPrinter(printer)
    #win32print.ClosePrinter(printer)



for cor, lis_ops in brancas_amarelas().items():
    if cor == 'brancas':
        imprime(cor, lis_ops, r'\\alfa\LANIER SP5210DN_PCP_DUPLEX')
    if cor == 'amarelas':
        imprime(cor, lis_ops, r'LANIER SP5210DN_PCP_AMARELA')
        