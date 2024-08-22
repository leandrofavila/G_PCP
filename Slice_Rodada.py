from PyPDF2 import *
import re
from PyPDF2 import PdfReader


class Slice:
    def __init__(self, path):
        self.path = path

    ordens_agrupadas = {}


    @staticmethod
    def agrupa_ordens(text, op):
        planejadores = [
            'PL011 - PINTURA (PRODUCAO)', 'PL010 - SOLDA (PRODUCAO)', 'PL008 - USINAGEM (PRODUCAO)',
            'PLANEJADOR PADRAO', 'PL007 - METALEIRA (PRODUCAO)', 'PL005 - PRENSA (PRODUCAO)',
            'PL003 - GUILHOTINA (PRODUCAO)', 'PL012 - EXTERNO (SERVICO DE TERCEIRO)', 'PL002 - PLASMA (PRODUCAO)',
            'PL004 - PUNCIONADEIRA (PRODUCAO)', 'PL001 - SERRA FITA (PRODUCAO)', 'PL021 - PLANEJADOR ALMOX',
            'PL009 - PRE-MONTAGEM (PRODUCAO)'
        ]
        for pl in planejadores:
            for w in text:
                if pl in w:
                    if pl not in Slice.ordens_agrupadas:
                        Slice.ordens_agrupadas[pl] = []
                    Slice.ordens_agrupadas[pl].append(op)
        return Slice.ordens_agrupadas



    def roda_all(self):
        reader = PdfReader(self.path[0], strict=False)
        pgs_to_split = []
        for pg in range(len(reader.pages)):
            pg_obj = reader.pages[pg]
            text = pg_obj.extract_text().split('\n')
            linha_ordem = re.search('ORDEM DE FABRICAÇÃO(\d+)', str(text))
            if linha_ordem:
                cur_op = linha_ordem.group(1)
                self.agrupa_ordens(text, cur_op)
                pgs_to_split.append(pg)
                fin_pg = 4 if bool(re.search('Pag.: 1 de 2', str(text))) else 2
                writer = PdfWriter()
                [writer.add_page(reader.pages[w]) for w in range(min(pgs_to_split),
                                                                 max(pgs_to_split) + fin_pg)]
                with open(f"splited_pdfs\\{cur_op}.pdf", "wb") as output_stream:
                    writer.write(output_stream)
            pgs_to_split.clear()
