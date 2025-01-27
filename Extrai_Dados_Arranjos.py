import re
from PyPDF2 import PdfReader
import pandas as pd
import os


class TRATA_PDF:
    def __init__(self, cod_barras):
        self.cod_barras = cod_barras
        self.text = None
        self.ct = 0
        self.extract_text_from_page()



    def find_pdf(self):
        base_name = self.cod_barras[:7]

        arranjo = f'Y:\\Cnc\\Plasma_Cnc\\Pdf_Xml\\{base_name}.PDF'
        if os.path.exists(arranjo):
            return arranjo

        arranjo = f'Y:\\Cnc\\Laser\\PDF_laser\\{base_name}.PDF'
        if os.path.exists(arranjo):
            return arranjo

        arranjo = f'Y:\\Cnc\\Puncionadeira_Cnc\\PDF_Xml\\{base_name}.PDF'
        if os.path.exists(arranjo):
            return arranjo

        print('Arranjo não encontrado em nenhum dos diretórios.')
        return None


    def extract_text_from_page(self, pagina=None, pagina_end=None):
        pg = int(self.cod_barras[7:]) - 1
        path = self.find_pdf()
        reader = PdfReader(path)

        print(pg, pagina,  pagina_end)

        if pagina is not None:
            pg += pagina


        if pagina_end is not None:
            try:
                for pages in range(pg, pagina_end):
                    page = reader.pages[pages]
                    self.text = page.extract_text()
                    print(self.text)
                    quit()
            except IndexError:
                self.text = None



        try:
            page = reader.pages[pg]
            self.text = page.extract_text()
        except IndexError:
            self.text = None

        if self.text is None or self.cod_barras not in self.text:
            print(self.cod_barras in self.text)
            self.ct += 1
            if self.ct >= len(reader.pages):
                return None
            return self.extract_text_from_page(pagina=self.ct)

        if 'Tempo Total do EventoTEMPO SETUP' not in self.text:
            print('Tempo Total do EventoTEMPO SETUP' in self.text)
            pg_end = pg + 2
            return self.extract_text_from_page(pagina_end=pg_end)

        return self.text


    def get_data(self):
        multiplicador = self.get_multiplicador()

        ordens_qtd = []
        if self.text is not None:
            ordens_qtd.extend(re.findall(
                r'^\d+\s\d+\s\d+\s\d+\.\d{2}\smm\s\d+\.\d{2}\smm\s\d+$', self.text, flags=re.MULTILINE
            ))
        else:
            print("Pagina não encontrada ou vazia.")
            quit()

        lis_to_dic = [list(w.split()) for w in set(ordens_qtd)]

        column_names = ['id', 'cod_item', 'qtd', 'Width', 'Width_Unit', 'Height', 'Height_Unit', 'num_ordem']

        df = pd.DataFrame(lis_to_dic, columns=column_names)
        df = df.drop(columns=['id', 'Width_Unit', 'Height_Unit'])

        df = df.groupby(['cod_item', 'Width', 'Height', 'num_ordem'], as_index=False)['qtd'].sum()

        df['qtd'] = df['qtd'].astype(int) * int(multiplicador)
        return df


    def get_multiplicador(self):
        if self.text is not None:
            match = re.search(r'Peso total:\d+', self.text)
        else:
            return "Pagina não encontrada no arranjo ou vazia"

        if match is None:
            self.text = self.extract_text_from_page(int(self.cod_barras[7:]) + 1)
            match = re.search(r'Peso total:\d+', self.text)

        multiplicador = match.group(0)[11:]

        return multiplicador


if __name__ == "__main__":
    #todo em arranjos como 12246731 não ta retornando valores da prozima pagina deve retornar 13 itens retorna somente 10
    tr_pdf = TRATA_PDF('12246731')
    print(tr_pdf.get_data().to_string())

