import requests
import json
from datetime import datetime, timezone, timedelta


with open("config.json", "r") as cred:
    config = json.load(cred)

AUTHENTICATION = config["AUTHENTICATION"]
APONTAMENTO_ENDPOINT = config["APONTAMENTO_ENDPOINT"]
USER = config["USER"]
PASSWORD = config["PASSWORD"]


class APONT:
    def __init__(self, operacao_id=None, qtd_apont=None, func_id=None, final=False):
        dt_now = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%dT%H:%M:%S%z")
        self.dt_time = dt_now[:-2] + ":" + dt_now[-2:]
        self.final = final
        self.apontamento_data = {
            "OrdemRoteiro": {
                "ID": operacao_id
            },
            "Quantidade": qtd_apont,
            "DataApontamento": self.dt_time,
            "TipoApontamento": {
                "ID": "IH"
            },
            "DataHoraInicio": self.dt_time,
            "DataHoraFim": self.dt_time,
            "Tempo": 0,
            "QtdeHomens": None,
            "Intervalo": None,
            "Funcionario": {
                "ID": func_id
            },
            "Final": self.final,
            "Usuario": "Apontamento API",
            "OrigemApontamento": "API"
        }
# todo - setar final como True somente se a quantidade fechar com a quantidade da ordem



    def get_auth_token(self):
        auth_url = f"{AUTHENTICATION}"
        payload = {
            "User": USER,
            "Password": PASSWORD,
            "AllowNewSession": True
        }

        try:
            response = requests.post(auth_url, json=payload)
            response.raise_for_status()
            data = response.json()
            if data.get("IsSuccessful"):
                return data["Token"]
            else:
                print("Erro na autenticação:", data.get("CustomErrorMessage"))
                return None
        except requests.RequestException as e:
            print("Erro ao autenticar:", e)
            return None


    def send_apontamento(self):
        token = self.get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(APONTAMENTO_ENDPOINT, headers=headers, json=self.apontamento_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print("Erro ao enviar o apontamento:", e)
            return None



if __name__ == "__main__":
    aponta = APONT(1950753, 6, 2272, False)#1224735
    aponta.send_apontamento()

