from typing import Optional
from google.cloud import iam_admin_v1
from google.cloud.iam_admin_v1 import types


def create_service_account(
    project_id: str, account_id: str, display_name: Optional[str] = None
    ) -> types.ServiceAccount:
    iam_admin_client = iam_admin_v1.IAMClient()

    # Configura a solicitação
    request = types.CreateServiceAccountRequest()
    request.account_id = account_id
    request.name = f"projects/{project_id}"

    service_account = types.ServiceAccount()
    service_account.display_name = display_name
    request.service_account = service_account

    # Cria a conta de serviço
    account = iam_admin_client.create_service_account(request=request)

    print(f"Created a service account: {account.email}")
    return account

# Substitua pelos seus valores
project_id = "Planejamento Semanal"
account_id = "minha-conta-id"
display_name = "Minha Conta de Serviço"

# Cria a conta de serviço
create_service_account(project_id, account_id, display_name)
