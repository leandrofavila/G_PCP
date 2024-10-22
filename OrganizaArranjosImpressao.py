from PyPDF2 import *
import tkinter as tk
from tkinter import filedialog
from Con_BD import DB
import re
import pandas as pd
import math
import os


db = DB()


def paths():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Selecione um ou mais arquivos PDF")
    return file_paths if file_paths else ''


def extract_ops():
    ops = []
    arr_ops = []
    pattern = re.compile(r'[0-9]{1,2} [0-9]{5,6} [0-9]{1,2} [0-9]{1,5}.[0-9]{1,4} mm [0-9]{1,5}.[0-9]{1,4} mm [0-9]{6,7}')
    arr_op_dic = {}
    for path in paths():
        ops_arr = []
        reader = PdfReader(path)
        num_pages = len(reader.pages)
        for pages in range(0, num_pages):
            page = reader.pages[pages]
            text = page.extract_text().split('\n')
            for line in text:
                found_ops = pattern.findall(line)
                ops_arr.append(found_ops)
                ops.extend(found_ops)
        arr_op_dic[os.path.basename(path)] = ops
    arr_ops.append(arr_op_dic)
    lis_arr = []
    for vals in ops:
        temp_lis = list(str(x) for x in vals.split(' '))
        dic_arr = {
            'COD_ITEM': temp_lis[1],
            'QTDE': temp_lis[2],
            'NUM_ORDEM': temp_lis[7]
        }
        lis_arr.append(dic_arr)
    df_ops_arr = pd.DataFrame(lis_arr)
    df_ops_arr = df_ops_arr.groupby(['COD_ITEM', 'NUM_ORDEM'])['QTDE'].sum().reset_index()
    print(df_ops_arr.to_string())
    lis = list(set(int(x) for x in df_ops_arr['NUM_ORDEM'].to_list()))
    print(len(lis))
    print(len(set(lis)))
    quit() if len(lis) != len(set(lis)) else print('imprimindo...')
    print(lis)

    open_print = 'print'
    for i in lis:
        encontrado = False

        try:
            os.startfile("C:\\Users\\pcp03\\PycharmProjects\\G_PCP\\splited_pdfs\\" + str(i) + ".pdf", open_print)
            encontrado = True
        except FileNotFoundError:
            print(f'Não achou a op {i}')
        if encontrado:
            continue
    quit()
    return df_ops_arr


def cars_arr():
    lis_op_arr = extract_ops()['NUM_ORDEM'].to_list()
    df_ops_arr = db.op_data(lis_op_arr)
    cars_in_arr = set(str(x) for x in df_ops_arr['CAR'].tolist() if not math.isnan(x))
    ops_bd = db.progamaveis_car(cars_in_arr)
    df_programaveis_bd_ops_arr = pd.merge(ops_bd, df_ops_arr, on='NUM_ORDEM', how='left')
    print(df_programaveis_bd_ops_arr.to_string())

    qtd_n_bate = df_programaveis_bd_ops_arr[
        df_programaveis_bd_ops_arr['QTDE_x'] - df_programaveis_bd_ops_arr['QTDE_x'] != 0]
    print('Para estes as quantidades não batem', qtd_n_bate.to_string())

    df_programaveis_bd_ops_arr['is_na'] = df_programaveis_bd_ops_arr['COD_ITEM_y'].isna()
    n_encontrados = df_programaveis_bd_ops_arr.loc[df_programaveis_bd_ops_arr['is_na'] == True, 'COD_ITEM_x'].to_list()

    print('Para estes as não foi encontrado arranjos no range selecionado', n_encontrados)

    return df_programaveis_bd_ops_arr



def monta_pdf_arr_op():
    merger = PdfMerger()
    ops = cars_arr()
    print(ops.to_string())
    quit()
    for val in ops:
        op = rf"C:\Users\pcp03\PycharmProjects\G_PCP\splited_pdfs\{val}.pdf"
        merger.append(op) if op not in merger.inputs else None
        ops.remove(val)

    #ops = rf"C:\Users\pcp03\PycharmProjects\G_PCP\rodada_amarelas_brancas\{car}_.pdf"
    merger.write(ops)
    os.startfile(ops, 'open')



cars_arr()
