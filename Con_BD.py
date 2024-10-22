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
            r"  AND ( "
            r"    EXTRACT(YEAR FROM MOV.DT_APONT) = EXTRACT(YEAR FROM SYSDATE) OR "
            r"    EXTRACT(YEAR FROM MOV.DT_APONT) = EXTRACT(YEAR FROM SYSDATE) - 1 "
            r"  ) "
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
            r"AND ROT.SEQ " + sentido + " ( "
            r"    SELECT " + lado + "(SEQ)  "
            r"    FROM FOCCO3I.TORDENS_ROT SUB_ROT  "
            r"    WHERE SUB_ROT.ORDEM_ID = ROT.ORDEM_ID "
            r") "
            r"AND EMP.COD_ITEM IS NOT NULL "
            r"AND EMP.COD_ITEM " + igualdade + " 55955 "
            r"GROUP BY TOR.NUM_ORDEM, TOP.DESCRICAO, ROT.SEQ "
        )
        df_consumos = pd.DataFrame(cur.fetchall(), columns=["NUM_ORDEM", "COD_ITEM", "DESCRICAO", "SEQ"])
        cur.close()
        return df_consumos

    def itens_comp_emb_nao(self):
        cur = self.get_connection()
        cur.execute(
            r"SELECT DISTINCT TITPAI.COD_ITEM, CAD.SEQ_ORD, TITFIL.COD_ITEM, TITFIL.DESC_TECNICA, "
            r"DECODE(CAD.EMBARQUE, '0', 'NAO', '1', 'SIM') EMBARQUE "
            r"FROM FOCCO3I.TITENS_ENGENHARIA ENGPAI "
            r"INNER JOIN FOCCO3I.TITENS_EMPR EMPPAI       ON EMPPAI.ID = ENGPAI.ITEMPR_ID "
            r"INNER JOIN FOCCO3I.TITENS TITPAI            ON TITPAI.ID = EMPPAI.ITEM_ID "
            r"INNER JOIN FOCCO3I.TCAD_EST_ITE CAD         ON CAD.PAI_ID = TITPAI.ID "
            r"INNER JOIN FOCCO3I.TITENS TITFIL            ON TITFIL.ID = CAD.FILHO_ID "
            r"INNER JOIN FOCCO3I.TITENS_EMPR EMPFIL       ON EMPFIL.ITEM_ID = TITFIL.ID "
            r"INNER JOIN FOCCO3I.TITENS_ENGENHARIA ENGFIL ON ENGFIL.ITEMPR_ID = EMPFIL.ID "
            r"INNER JOIN FOCCO3I.TITENS_PLANEJAMENTO PLA  ON PLA.ITEMPR_ID = EMPPAI.ID "
            r"WHERE CAD.EMBARQUE = 0 "
            r"AND (PLA.FANTASMA = 1 OR ENGPAI.TP_ESTRUTURA IN ('C')) "
            r"AND ENGFIL.TP_ITEM IN ('C') "
            r"AND TITFIL.COD_ITEM NOT IN (55955) "
            r"AND TITFIL.SIT=1 "
            r"AND TITPAI.SIT=1 "
            r"AND TITPAI.DESC_TECNICA NOT LIKE '%KIT PARAF%' "
            r"AND TITFIL.DESC_TECNICA NOT LIKE '%NAO USAR%' "
        )
        comp_emb_no = pd.DataFrame(cur.fetchall(), columns=["Cod. Item Pai", "Seq. na Estrutura",
                                                            "Cod. Filho", "Desc. Técnica", "Valor do Campo Embarque"])
        cur.close()
        return comp_emb_no

    def op_abertas(self):
        cur = self.get_connection()
        cur.execute(
            r"SELECT TOR.NUM_ORDEM, TOR.QTDE, TIT.COD_ITEM, TIT.DESC_TECNICA, "
            r"EXTRACT(MONTH FROM TOR.DT_EMISSAO) AS MES,  "
            r"CAR.CARREGAMENTO, TFUN.NOME AS PLANEJADOR, CAR.SITUACAO, CAR.DESCRICAO, "
            r"CASE "
            r"    WHEN TFUN.NOME LIKE '%PL003 - GUILHOTINA (PRODUCAO)%' THEN 'PROD. SEDE' "
            r"    WHEN TFUN.NOME LIKE '%PL002 - PLASMA (PRODUCAO)%' THEN 'PROD. SEDE' "
            r"    WHEN TFUN.NOME LIKE '%PL004 - PUNCIONADEIRA (PRODUCAO)%' THEN 'PROD. SEDE' "
            r"    WHEN TFUN.NOME LIKE '%PL001 - SERRA FITA (PRODUCAO)%' THEN 'PROD. SEDE' "
            r"    WHEN TFUN.NOME LIKE '%PL010 - SOLDA (PRODUCAO)%' THEN 'PROD. SEDE' "
            r"    WHEN TFUN.NOME LIKE '%PL007 - METALEIRA (PRODUCAO)%' THEN 'PROD. SEDE' "
            r"    WHEN TFUN.NOME LIKE '%PL008 - USINAGEM (PRODUCAO)%' THEN 'PROD. SEDE' "
            r"    WHEN TFUN.NOME LIKE '%PL005 - PRENSA (PRODUCAO)%' THEN 'PROD. SEDE' "
            r"    WHEN TFUN.NOME LIKE '%PL006 - FICEP (PRODUCAO)%' THEN 'PROD. SEDE' "
            r"    WHEN TFUN.NOME LIKE '%PL009 - PRE-MONTAGEM (PRODUCAO)%' THEN 'PROD. BEVILAQUA' "
            r"    WHEN TFUN.NOME LIKE '%PL011 - PINTURA (PRODUCAO)%' THEN 'PROD. BEVILAQUA' "
            r"    WHEN TFUN.NOME LIKE '%PL021 - PLANEJADOR ALMOX%' THEN 'PROD. ALMOX' "
            r"    ELSE 'NULL' "
            r"END AS LOCAL_PROD "
            r"FROM FOCCO3I.TORDENS TOR "
            r"INNER JOIN FOCCO3I.TITENS_PLANEJAMENTO TPL         ON TPL.ID = TOR.ITPL_ID "
            r"INNER JOIN FOCCO3I.TITENS TIT                      ON TIT.COD_ITEM = TPL.COD_ITEM "
            r"LEFT JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VINC      ON TOR.ID = VINC.ORDEM_ID "
            r"LEFT JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON VINC.CARERGAM_ID = CAR.ID "
            r"LEFT JOIN FOCCO3I.TITENS_PLAN_FUNC PLA             ON TPL.ID = PLA.ITPL_ID "
            r"LEFT JOIN FOCCO3I.TFUNCIONARIOS TFUN               ON PLA.FUNC_ID = TFUN.ID "
            r"WHERE TOR.DT_EMISSAO < (SYSDATE - INTERVAL '30' DAY) "
            r"AND TOR.TIPO_ORDEM IN ('OFM', 'OFA') "
        )
        ops_abertas = pd.DataFrame(cur.fetchall(), columns=["NUM_ORDEM", "QTDE", "COD_ITEM", "DESC_TECNICA",
                                                            "MES", "CARREGAMENTO", "PLANEJADOR", "SIT_CARREGAMENTO",
                                                            "DESC_PEDIDO", "LOCAL_PROD"])
        cur.close()
        return ops_abertas

    def planejador_errado(self):
        cur = self.get_connection()
        cur.execute(
            r"SELECT TOR.NUM_ORDEM, TFU.NOME,  LISTAGG(TOP.DESCRICAO || '|' || MAQ.DESCRICAO || '|') WITHIN GROUP (ORDER BY ROT.ID) AS SEQ "
            r"FROM FOCCO3I.TORDENS TOR "
            r"INNER JOIN FOCCO3I.TFUNCIONARIOS TFU    ON TFU.ID = TOR.FUNC_ID "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ROT      ON ROT.ORDEM_ID = TOR.ID "
            r"INNER JOIN FOCCO3I.TROTEIRO TRO         ON ROT.TROTEIRO_ID = TRO.ID "
            r"INNER JOIN FOCCO3I.TOPERACAO TOP        ON TRO.OPERACAO_ID = TOP.ID "
            r"INNER JOIN FOCCO3I.TROT_FAB_MAQ RMAQ    ON RMAQ.TROTEIRO_ID = TRO.ID "
            r"INNER JOIN FOCCO3I.TMAQUINAS MAQ        ON RMAQ.MAQUINA_ID = MAQ.ID  "
            r"WHERE TOR.TIPO_ORDEM IN ('OFA','OFM') "
            r"GROUP BY TOR.NUM_ORDEM, TFU.NOME "
        )
        planejador_errado = pd.DataFrame(cur.fetchall(), columns=["NUM_ORDEM", "PLANEJADOR", "SEQ"])
        cur.close()
        return planejador_errado

    def filhas_pm(self, car, num_ordem):
        cur = self.get_connection()
        num_ordem = ', '.join(num_ordem)
        cur.execute(
            r"SELECT DISTINCT TOR.NUM_ORDEM "
            r"FROM FOCCO3I.TCAD_EST_ITE EST "
            r"INNER JOIN FOCCO3I.TITENS FIL                       ON FIL.ID = EST.FILHO_ID "
            r"INNER JOIN FOCCO3I.TITENS_EMPR EMP                  ON EMP.ITEM_ID = FIL.ID "
            r"INNER JOIN FOCCO3I.TITENS_ENGENHARIA ENG            ON ENG.ITEMPR_ID = EMP.ID "
            r"INNER JOIN FOCCO3I.TITENS_PLANEJAMENTO PLA          ON PLA.ITEMPR_ID = EMP.ID "
            r"INNER JOIN FOCCO3I.TORDENS TOR                      ON TOR.ITPL_ID = PLA.ID "
            r"INNER JOIN FOCCO3I.TDEMANDAS TDE                    ON PLA.ID = TDE.ITPL_ID "
            r"INNER JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VINC      ON TOR.ID = VINC.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON VINC.CARERGAM_ID = CAR.ID                                            "
            r"WHERE ENG.TP_ITEM = 'F' "
            r"AND PLA.FANTASMA = 0 "
            r"AND TDE.ALMOX_ID NOT IN (590, 591) "
            r"AND CAR.CARREGAMENTO IN (" + str(car) + ") "
            r"START WITH EST.PAI_ID IN ( "
            r"            SELECT TIT.ID FROM FOCCO3I.TITENS TIT "
            r"            INNER JOIN FOCCO3I.TITENS_PLANEJAMENTO PLA  ON PLA.COD_ITEM = TIT.COD_ITEM "
            r"            INNER JOIN FOCCO3I.TORDENS TOR              ON TOR.ITPL_ID = PLA.ID  "
            r"            WHERE TOR.NUM_ORDEM IN (" + str(num_ordem) + ") "
            r"            ) "
            r"CONNECT BY PRIOR EST.FILHO_ID = EST.PAI_ID "
        )
        filhas_pm = pd.DataFrame(cur.fetchall(), columns=["NUM_ORDEM"])
        cur.close()
        return filhas_pm["NUM_ORDEM"].tolist()

    def ordens_carregamento(self, car, pms_only=None):
        cur = self.get_connection()
        if pms_only:
            pms = "AND TFUN.NOME = 'PL009 - PRE-MONTAGEM (PRODUCAO)'"
        else:
            pms = ''
        cur.execute(
            r"SELECT DISTINCT TOR.NUM_ORDEM, TPL.COD_ITEM, TIT.DESC_TECNICA, TOR.QTDE "
            r"FROM FOCCO3I.TITENS_PLANEJAMENTO TPL "
            r"INNER JOIN FOCCO3I.TITENS_EMPR EMP                  ON TPL.ITEMPR_ID = EMP.ID "
            r"INNER JOIN FOCCO3I.TITENS TIT                       ON EMP.ITEM_ID = TIT.ID  "
            r"INNER JOIN FOCCO3I.TORDENS TOR                      ON TPL.ID = TOR.ITPL_ID "
            r"INNER JOIN FOCCO3I.TDEMANDAS TDE                    ON TOR.ID = TDE.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ROT                  ON TOR.ID = ROT.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TORD_ROT_FAB_MAQ FAB             ON ROT.ID = FAB.TORDEN_ROT_ID "
            r"INNER JOIN FOCCO3I.TMAQUINAS MAQ                    ON FAB.MAQUINA_ID = MAQ.ID "
            r"INNER JOIN FOCCO3I.TITENS_PLAN_FUNC PLA             ON TPL.ID = PLA.ITPL_ID "
            r"INNER JOIN FOCCO3I.TFUNCIONARIOS TFUN               ON PLA.FUNC_ID = TFUN.ID "
            r"INNER JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VINC      ON TOR.ID = VINC.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON VINC.CARERGAM_ID = CAR.ID "
            r"WHERE CAR.CARREGAMENTO IN (" + car + ")  "
            r"" + pms + " "
        )
        ordens_pm_carregamento = pd.DataFrame(cur.fetchall(), columns=["NUM_ORDEM", "COD_ITEM", "DESC_TECNICA", "QTDE"])
        cur.close()
        return ordens_pm_carregamento

    def peso_ordens(self):
        cur = self.get_connection()
        cur.execute(
            r"SELECT ROUND(SUM(TDE.QTDE_ORIGINAL),2)AS PESO_OP, TOR.NUM_ORDEM, TPL.COD_ITEM, TOR.QTDE "
            r"FROM FOCCO3I.TORDENS TOR "
            r"INNER JOIN FOCCO3I.TDEMANDAS TDE            ON TDE.ORDEM_ID = TOR.ID "
            r"INNER JOIN FOCCO3I.TITENS_PLANEJAMENTO TPL  ON TPL.ID = TOR.ITPL_ID "
            r"AND TPL.COD_ITEM <> 55955 "
            r"AND TOR.TIPO_ORDEM IN ('OFA', 'OFM') "
            r"GROUP BY TPL.COD_ITEM, TOR.NUM_ORDEM, TOR.QTDE "
            r"ORDER BY TOR.NUM_ORDEM DESC "
        )
        peso_ordens = pd.DataFrame(cur.fetchall(), columns=["PESO", "NUM_ORDEM", "COD_ITEM", "QTDE"])
        cur.close()
        return peso_ordens

    def op_data(self, lis_op):
        lis_op = ', '.join(lis_op)
        cur = self.get_connection()
        cur.execute(
            r"SELECT DISTINCT TOR.NUM_ORDEM, TOR.QTDE, TPL.COD_ITEM, TIT.DESC_TECNICA, TOR.TMASC_ITEM_ID, TOR.TIPO_ORDEM, fun.NOME, CAR.CARREGAMENTO "
            r"FROM FOCCO3I.TORDENS TOR "
            r"INNER JOIN FOCCO3I.TITENS_PLANEJAMENTO TPL          ON TPL.ID = TOR.ITPL_ID "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ROT                  ON ROT.ORDEM_ID = TOR.ID "
            r"INNER JOIN FOCCO3I.TORD_ROT_FAB_MAQ FAB             ON ROT.ID = FAB.TORDEN_ROT_ID "
            r"INNER JOIN FOCCO3I.TMAQUINAS MAQ                    ON FAB.MAQUINA_ID = MAQ.ID "
            r"INNER JOIN FOCCO3I.TROTEIRO TRO                     ON TRO.ID = ROT.TROTEIRO_ID                    "
            r"INNER JOIN FOCCO3I.TOPERACAO TOP                    ON TRO.OPERACAO_ID = TOP.ID "
            r"INNER JOIN FOCCO3I.TITENS TIT                       ON TIT.COD_ITEM = TPL.COD_ITEM "
            r"INNER JOIN FOCCO3I.TITENS_PLAN_FUNC TFUN            ON TFUN.ITPL_ID = TPL.ID "
            r"INNER JOIN FOCCO3I.TFUNCIONARIOS FUN                ON FUN.ID = TFUN.FUNC_ID "
            r"LEFT JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VINC       ON TOR.ID = VINC.ORDEM_ID "
            r"LEFT JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR   ON VINC.CARERGAM_ID = CAR.ID "
            r"WHERE TOR.NUM_ORDEM IN (" + lis_op + ") "
        )
        op_data = pd.DataFrame(cur.fetchall(), columns=["NUM_ORDEM", "QTDE", "COD_ITEM", "DESC_TECNICA",
                                                        "MASC", "OFE", "PL", "CAR"])
        cur.close()
        return op_data



    def progamaveis_car(self, carregamento):
        cur = self.get_connection()
        carregamento = ', '.join(carregamento)
        cur.execute(
            r"SELECT DISTINCT TPL.COD_ITEM,  "
            r"TOR.NUM_ORDEM, "
            r"TOR.QTDE  "
            r"FROM FOCCO3I.TITENS_PLANEJAMENTO TPL "
            r"INNER JOIN FOCCO3I.TITENS_EMPR EMP      ON TPL.ITEMPR_ID = EMP.ID "
            r"INNER JOIN FOCCO3I.TITENS TIT           ON EMP.ITEM_ID = TIT.ID  "
            r"INNER JOIN FOCCO3I.TORDENS TOR          ON TPL.ID = TOR.ITPL_ID "
            r"INNER JOIN FOCCO3I.TDEMANDAS TDE        ON TOR.ID = TDE.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ROT      ON TOR.ID = ROT.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TORD_ROT_FAB_MAQ FAB ON ROT.ID = FAB.TORDEN_ROT_ID "
            r"INNER JOIN FOCCO3I.TMAQUINAS MAQ        ON FAB.MAQUINA_ID = MAQ.ID "
            r"INNER JOIN FOCCO3I.TITENS_PLAN_FUNC PLA ON TPL.ID = PLA.ITPL_ID "
            r"INNER JOIN FOCCO3I.TFUNCIONARIOS TFUN   ON PLA.FUNC_ID = TFUN.ID "
            r"WHERE TOR.ID IN( "
            r"                SELECT TOR.ID "
            r"                FROM FOCCO3I.TORDENS TOR "
            r"                INNER JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VINC      ON TOR.ID = VINC.ORDEM_ID "
            r"                INNER JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON VINC.CARERGAM_ID = CAR.ID "
            r"                WHERE CAR.CARREGAMENTO IN ("+str(carregamento)+") "                                                                                                                                                                      
            r"                ) "  
            r"AND (MAQ.DESCRICAO LIKE '%PUNCIONADEIRA%'  OR MAQ.DESCRICAO LIKE '%LASER%' OR MAQ.DESCRICAO LIKE '%PLASMA%') "  
            r"GROUP BY TPL.COD_ITEM, TOR.NUM_ORDEM, TOR.QTDE, TIT.DESC_TECNICA, TFUN.NOME, TOR.tipo_ordem "
        )
        progamaveis_car = cur.fetchall()
        progamaveis_car = pd.DataFrame(progamaveis_car, columns=['COD_ITEM', 'NUM_ORDEM', 'QTDE'])
        return progamaveis_car
    