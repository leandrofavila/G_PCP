from PyPDF2 import *
import glob
import re
from time import time
import os

tot_time = time()


def paths():
    return glob.glob(r"R:\Mapeamento_Focco\ORDENS\*.pdf")


class Varre_pdf:
    def __init__(self, path_):
        self.path_ = path_


    def estract_ops(self):
        listao = []
        with open(rf"C:\Users\pcp03\PycharmProjects\G_PCP\historico_pdf_revisados.csv", 'r+', newline='') as csv_:
            csv_dt = csv_.read().split('\n')
            csv_dt = list(map(lambda x: x.rstrip('\r'), filter(None, csv_dt)))
            basename = str(os.path.basename(path))
            if basename not in csv_dt:
                csv_.write(basename + '\n')
                reader = PdfReader(path)
                num_pages = len(reader.pages)

                for pages in range(0, num_pages):
                    page = reader.pages[pages]
                    text = page.extract_text().split('\n')
                    listao.append(text)

            listao = [vals for sub in listao for vals in sub]
        return listao


    def agrupa_conta(self):
        ct_item = 0
        item_ = ''
        op_ = ''
        n_op = False
        grp_lis = []
        for value in self.estract_ops():
            if 'ORDEM DE FABRICAÇÃO' in value:
                n_op = True
                op_ = ''.join(dig for dig in value if dig.isdigit())

            if 'Item : ' in value:
                item_ = re.findall('[0-9]{5,6}', value)
                #item_ = item_[0] if item_ else print('te liga --> ', value)
                if item_ == '54830':
                    item_ = None
                ct_item = 0

            if item_ and item_ in value and n_op:
                ct_item += 1
                grp_lis.append([op_, item_, ct_item])
        return grp_lis


    def get_max(self):
        max_ct = {}
        for op, item, ct in self.agrupa_conta():
            chave = (op, item)
            max_ct[chave] = max(max_ct.get(chave, 0), ct)
        return max_ct


    def get_dif(self):
        for key, val in self.get_max().items():
            if val < 3:
                print(key, self.path_)





for path in paths():
    dasda = Varre_pdf(path)
    dasda.get_dif()


end = time()
_, rem = divmod(end - tot_time, 3600)
minutes, seconds = divmod(rem, 60)
print("{:0>2}:{:02}".format(int(minutes), int(seconds)))
