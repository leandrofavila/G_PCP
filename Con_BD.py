import pandas as pd
import cx_Oracle


class DB:
    def __init__(self):
        self.db_connection = None

    @staticmethod
    def get_connection():
        dsn = cx_Oracle.makedsn("10.40.3.10", 1521, service_name="f3ipro")
        connection = cx_Oracle.connect(user=r"focco_consulta", password=r'consulta3i08', dsn=dsn, encoding="UTF-8")
        cur = connection.cursor()
        return cur


    def apont(self):
        cur = self.get_connection()
        cur.execute(
            r"SELECT TOR.NUM_ORDEM, ROT.SEQ, TOR.QTDE, MOV.QUANTIDADE, EXTRACT(MONTH FROM MOV.DT_APONT), TOP.DESCRICAO "
            r"FROM FOCCO3I.TORDENS TOR "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ORD  ON TOR.ID = ORD.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TROTEIRO ROT     ON ORD.TROTEIRO_ID = ROT.ID "
            r"INNER JOIN FOCCO3I.TOPERACAO TOP    ON ROT.OPERACAO_ID = TOP.ID "
            r"LEFT JOIN FOCCO3I.TORDENS_MOVTO MOV ON MOV.TORDEN_ROT_ID = ORD.ID "
            r"WHERE EXTRACT(MONTH FROM MOV.DT_APONT) = EXTRACT(MONTH FROM SYSDATE) "
            r"AND EXTRACT(YEAR FROM MOV.DT_APONT) = EXTRACT(YEAR FROM SYSDATE) "
        )
        df = pd.DataFrame(cur.fetchall(), columns=["NUM_ORDEM", "SEQ", "QTDE", "QUANTIDADE", "DT", "OPERACAO"])
        cur.close()
        return df


    def consumo(self, sentido, lado, igualdade):
        cur = self.get_connection()
        cur.execute(
            r"SELECT TOR.NUM_ORDEM, COUNT(EMP.COD_ITEM), TOP.DESCRICAO, ROT.SEQ  "
            r"FROM FOCCO3I.TORDENS TOR "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ROT  ON ROT.ORDEM_ID = TOR.ID "
            r"INNER JOIN FOCCO3I.TROTEIRO TRO     ON TRO.ID = ROT.TROTEIRO_ID "
            r"INNER JOIN FOCCO3I.TOPERACAO TOP    ON TRO.OPERACAO_ID = TOP.ID "
            r"LEFT JOIN FOCCO3I.TCONSUMOS TCO     ON TCO.TROTEIRO_ID = TRO.ID "
            r"LEFT JOIN FOCCO3I.TITENS_EMPR EMP   ON TCO.ITEMPR_ID = EMP.ID "
            r"WHERE TOR.TIPO_ORDEM IN ('OFA') "
            r"AND ROT.SEQ "+sentido+" ( "
            r"    SELECT "+lado+"(SEQ)  "
            r"    FROM FOCCO3I.TORDENS_ROT SUB_ROT  "
            r"    WHERE SUB_ROT.ORDEM_ID = ROT.ORDEM_ID "
            r") "
            r"AND EMP.COD_ITEM IS NOT NULL "
            r"AND EMP.COD_ITEM "+igualdade+" 55955 " 
            r"GROUP BY TOR.NUM_ORDEM, TOP.DESCRICAO, ROT.SEQ "
        )
        df_consumos = pd.DataFrame(cur.fetchall(), columns=["NUM_ORDEM", "COD_ITEM", "DESCRICAO", "SEQ"])
        cur.close()
        return df_consumos



    def itens_comp_emb_nao(self):
        cur = self.get_connection()
        cur.execute(
            r"SELECT TITENS.COD_ITEM, TCAD_EST_ITE.SEQ_ORD, TITENS1.COD_ITEM, TITENS1.DESC_TECNICA,  "
            r"DECODE(TCAD_EST_ITE.EMBARQUE, '0', 'NAO', '1', 'SIM') EMBARQUE "
            r"FROM FOCCO3I.TITENS_ENGENHARIA TITENS_ENGENHARIA, "
            r"FOCCO3I.TITENS_EMPR TITENS_EMPR, "
            r"FOCCO3I.TITENS_EMPR TITENS_EMPR1, "
            r"FOCCO3I.TITENS_ENGENHARIA TITENS_ENGENHARIA1, "
            r"FOCCO3I.TITENS TITENS, "
            r"FOCCO3I.TCAD_EST_ITE TCAD_EST_ITE, "
            r"FOCCO3I.TITENS TITENS1 "
            r"WHERE TITENS_EMPR.ID = TITENS_ENGENHARIA.ITEMPR_ID "
            r"AND TITENS.ID = TITENS_EMPR.ITEM_ID "
            r"AND TITENS1.ID = TITENS_EMPR1.ITEM_ID "
            r"AND TITENS_EMPR1.ID = TITENS_ENGENHARIA1.ITEMPR_ID "
            r"AND TITENS1.ID = TCAD_EST_ITE.FILHO_ID "
            r"AND TITENS.ID = TCAD_EST_ITE.PAI_ID " 
            r"AND TITENS.ID IN (SELECT TIT.ID "
            r"                    FROM FOCCO3I.TITENS_EMPR TEMP "
            r"                    ,FOCCO3I.TITENS_PLANEJAMENTO TPLA "
            r"                    ,FOCCO3I.TITENS TIT "
            r"                    WHERE TEMP.ID=TPLA.ITEMPR_ID "
            r"                    AND TPLA.FANTASMA=1 "
            r"                    AND TEMP.ITEM_ID=TIT.ID "
            r"                    AND TEMP.EMPR_ID=1 "
            r"                    AND TIT.SIT=1) "
            r"AND TCAD_EST_ITE.EMBARQUE = 0 "
            r"AND TITENS1.DESC_TECNICA NOT LIKE '%NAO USAR%' "
            r"AND TITENS1.ID in (SELECT TIT.ID "
            r"                      FROM FOCCO3I.TITENS_EMPR TEMP "
            r"                      ,FOCCO3I.TITENS_PLANEJAMENTO TPLA "
            r"                      ,FOCCO3I.TITENS TIT "
            r"                      WHERE TEMP.ID=TPLA.ITEMPR_ID "
            r"                      AND TPLA.FANTASMA=0 "
            r"                      AND TEMP.ITEM_ID=TIT.ID "
            r"                      AND TEMP.EMPR_ID=1 "
            r"                      AND TIT.SIT=1) "
            r"AND TITENS_ENGENHARIA1.TP_ITEM IN ('C') "
            r"AND TITENS_ENGENHARIA.TP_ESTRUTURA IN ('I', 'C') "
            r"AND TITENS_EMPR.EMPR_ID = 1 "
            r"AND TITENS_EMPR1.EMPR_ID = 1 "
            r"AND TITENS.DESC_TECNICA NOT LIKE '%KIT PARAF%' "
            r"AND TITENS1.COD_ITEM NOT IN (55955)  "
        )
        comp_emb_no = pd.DataFrame(cur.fetchall(), columns=["Cod. Item Pai", "Seq. na Estrutura",
                                                            "Cod. Filho", "Desc. Técnica", "Valor do Campo Embarque"])
        cur.close()
        return comp_emb_no
