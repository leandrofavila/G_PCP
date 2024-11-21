import requests
import json
from datetime import datetime, timezone, timedelta


with open("config.json", "r") as cred:
    config = json.load(cred)

BASE_URL = config["BASE_URL"]
APONTAMENTO_ENDPOINT = config["APONTAMENTO_ENDPOINT"]
USER = config["USER"]
PASSWORD = config["PASSWORD"]


class APONT:
    def __init__(self, operacao_id=None, qtd_apont=None, func_id=None):
        dt_now = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%dT%H:%M:%S%z")
        self.dt_time = dt_now[:-2] + ":" + dt_now[-2:]
        self.apontamento_data = {
            "OrdemRoteiro": {
                "ID": operacao_id
            },
            "Quantidade": qtd_apont,
            "DataApontamento": self.dt_time,
            "TipoApontamento": {
                "ID": "TP"
            },
            "DataHoraInicio": None,
            "DataHoraFim": None,
            "Tempo": None,
            "QtdeHomens": None,
            "Intervalo": None,
            "Funcionario": {
                "ID": func_id
            },
            "Final": True,
            "Usuario": "Apontamento API",
            "OrigemApontamento": "API"
        }


    def get_auth_token(self):
        auth_url = f"{BASE_URL}"
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
        headers = {
            "Authorization": f"Bearer {self.get_auth_token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(APONTAMENTO_ENDPOINT, headers=headers, json=self.apontamento_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print("Erro ao enviar o apontamento:", e)
            return None
