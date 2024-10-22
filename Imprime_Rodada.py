from PyPDF2 import *
import tkinter as tk
from tkinter import filedialog
import re
from Con_BD import DB
from Slice_Rodada import Slice
import os

db = DB()


def carregamento():
    carr = re.findall('[0-9]{4}00', str(path[0]))
    carr = carr[0]
    return carr


def paths():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Selecione um ou mais arquivos PDF")
    return file_paths if file_paths else ''


path = paths()
slice = Slice(path)
slice.roda_all()
quit()

car = carregamento()
ordens_agrupadas = slice.ordens_agrupadas


def remove_ordens():
    chave_para_remover = [
        'PL004 - PUNCIONADEIRA (PRODUCAO)',
        'PL002 - PLASMA (PRODUCAO)',
        'PL022 - LASER (PRODUCAO)'
        ]

    for planeja in chave_para_remover:
        if planeja in ordens_agrupadas:
            del ordens_agrupadas[planeja]

    ordens_rodada = [ordem for sublis in ordens_agrupadas.values() for ordem in sublis]
    return ordens_rodada



def imprime():
    merger = PdfMerger()
    #printer = win32print.OpenPrinter(impressora)
    #win32print.StartDocPrinter(printer, 1, ("Print Job", None, "RAW"))
    #win32print.StartPagePrinter(printer)
    ops = remove_ordens()
    for val in ops:
        op = rf"C:\Users\pcp03\PycharmProjects\G_PCP\splited_pdfs\{val}.pdf"
        merger.append(op) if op not in merger.inputs else None
        ops.remove(val)

    ops = rf"C:\Users\pcp03\PycharmProjects\G_PCP\rodada_amarelas_brancas\{car}_.pdf"
    merger.write(ops)
    os.startfile(ops, 'open')
    #win32api.ShellExecute(0, "print", ops, None, ".", 0)

    #win32print.EndPagePrinter(printer)
    #win32print.EndDocPrinter(printer)
    #win32print.ClosePrinter(printer)
    


imprime()
