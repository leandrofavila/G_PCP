import re
from PyPDF2 import PdfReader
import pandas as pd
import os


class TRATA_PDF:
    def __init__(self, cod_barras):
        self.cod_barras = cod_barras
        self.text = None

    def find_pdf(self):
        base_name = self.cod_barras[:7]

        arranjo = f'Y:\\Cnc\\Plasma_Cnc\\Pdf_Xml\\{base_name}.PDF'
        if os.path.exists(arranjo):
            return arranjo

        arranjo = f'Y:\\Cnc\\Laser\\PDF_laser\\{base_name}.PDF'
        if os.path.exists(arranjo):
            return arranjo

        print('Arranjo não encontrado em nenhum dos diretórios.')
        return None

    def extract_text_from_page(self):
        # todo cuidado ta usando os ultimos digitos do codigo de barras como a pagina do arranjo pode ser que nem sempre bata esse valor confere

        if self.text is None:
            path = self.find_pdf()
            pagina = self.cod_barras[7:]
            reader = PdfReader(path)
            page = reader.pages[int(pagina)]
            self.text = page.extract_text()
            #print(self.text)
        return self.text

    def get_multiplicador(self):
        text = self.extract_text_from_page()
        match = re.search(r'Peso total:\d+', text)
        multiplicador = match.group(0)[11:]
        return multiplicador


    def get_data(self):
        ordens_qtd = []
        ordens_qtd.extend(re.findall(
            r'^\d+\s\d+\s\d+\s\d+\.\d{2}\smm\s\d+\.\d{2}\smm\s\d+$', self.extract_text_from_page(), flags=re.MULTILINE
        ))
        lis_to_dic = [list(w.split()) for w in set(ordens_qtd)]

        column_names = ['id', 'cod_item', 'qtd', 'Width', 'Width_Unit', 'Height', 'Height_Unit', 'num_ordem']

        df = pd.DataFrame(lis_to_dic, columns=column_names)
        df = df.drop(columns=['id', 'Width_Unit', 'Height_Unit'])

        df = df.groupby(['cod_item', 'Width', 'Height', 'num_ordem'], as_index=False)['qtd'].sum()
        multiplicador = self.get_multiplicador()
        df['qtd'] = df['qtd'].astype(int) * int(multiplicador)
        return df



if __name__ == "__main__":
    tr_pdf = TRATA_PDF('12109406')
    print(tr_pdf.get_data().to_string())
