import requests
import msvcrt
import json
import re
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

# Caminho para o arquivo JSON que contém as credenciais da API da Clara
token_data_clara = "C:\\Users\\Scripts\\Clara_Api-Chave_e_Certificado\\token-data.json"

# Carrega as credenciais da API da Clara a partir do arquivo JSON
with open(token_data_clara, 'r') as td:
    dados = json.load(td)

# Caminho para o arquivo JSON com credenciais da API do Notion
notion_credenciais_json = "C:\\Users\\Scripts\\notion_credenciais.json"

# Carrega as credenciais da API do Notion a partir do arquivo JSON
with open(notion_credenciais_json, 'r', encoding='utf-8') as nc:
    notion_credenciais = json.load(nc)

# URLs e endpoints da API da Clara
BASE_URL = "https://public-api.br.clara.com"
ENDPOINT = "/api/v2/transactions"
TOKEN_URL = "/oauth/token"

# Credenciais da API da Clara
CLARA_CLIENT_ID = dados["clientId"]
CLARA_CLIENT_SECRET = dados["clientSecret"]
CERT_FILE = "C:\\Users\\Scripts\\Clara_Api-Chave_e_Certificado\\public-key.crt"
KEY_FILE = "C:\\Users\\Scripts\\Clara_Api-Chave_e_Certificado\\private-key.key"
CA_CERT_FILE = "C:\\Users\\Scripts\\Clara_Api-Chave_e_Certificado\\ca-public-key.pem"

# Credenciais da API do Notion
NOTION_API_KEY = notion_credenciais["Clara_Cartoes_Key"]
NOTION_DATABASE_ID = notion_credenciais["Registro_de_Despesas_ID"]

# Caminho para o arquivo JSON de mapeamento de usuários do Notion
notion_users_json = "C:\\Users\\Scripts\\notion_users.json"

# Função para converter um objeto de data para o formato 'YYYY-MM-DD'
def convert_date_format(date_obj):
    """Converte um objeto de data para o formato 'YYYY-MM-DD'."""
    return date_obj.strftime("%Y-%m-%d")

# Calcula as datas de início e fim para o período de consulta (últimos 10 dias)
data_inicial = datetime.now() - timedelta(days=10)
data_final = datetime.now() - timedelta(days=1)

# Formata as datas para exibição
data_inicial_formatada = data_inicial.strftime('%Y-%m-%d')
data_final_formatada = data_final.strftime('%Y-%m-%d')

# Converte as datas para o formato 'YYYY-MM-DD'
PERIODOINICIAL_CONVERTIDO = convert_date_format(data_inicial)
PERIODOFINAL_CONVERTIDO = convert_date_format(data_final)

# Verifica se as datas foram convertidas corretamente
if not PERIODOINICIAL_CONVERTIDO or not PERIODOFINAL_CONVERTIDO:
    print("Erro na conversão de datas. Verifique o formato e tente novamente.")
else:
    # Define o período para a consulta na API da Clara
    PERIODO = f"?operationDateRangeStart={PERIODOINICIAL_CONVERTIDO}&operationDateRangeEnd={PERIODOFINAL_CONVERTIDO}"
    print(f"Período configurado automaticamente: {data_inicial_formatada} a {data_final_formatada}")

# Carrega o mapeamento de usuários do Notion a partir do arquivo JSON
with open(notion_users_json, 'r', encoding='utf-8') as f:
    notion_user_map = json.load(f)

# Mensagem de orientação que será incluída nas entradas do Notion
orientacoes = '''Orientações do financeiro:
Essa tarefa foi criada automaticamente com base nas suas despesas recentes. Por favor, atualize o título, preencha os campos necessários e anexe os documentos correspondentes.'''

# Função para obter o token de acesso da API da Clara
def get_access_token():
    """Obtém o token de acesso da API da Clara usando autenticação básica."""
    auth = HTTPBasicAuth(CLARA_CLIENT_ID, CLARA_CLIENT_SECRET)
    try:
        response = requests.post(
            f"{BASE_URL}{TOKEN_URL}",
            auth=auth,
            cert=(CERT_FILE, KEY_FILE),
            verify=CA_CERT_FILE
        )
        if response.status_code != 200:
            print(f"Erro ao obter token: {response.status_code} - {response.reason}")
            msvcrt.getch()
            exit()
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter token de acesso: {e}")
        msvcrt.getch()
        exit()

# Função para buscar dados da API da Clara
def get_api_data(access_token):
    """Busca dados da API da Clara usando o token de acesso."""
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            f"{BASE_URL}{ENDPOINT}{PERIODO}",
            headers=headers,
            cert=(CERT_FILE, KEY_FILE),
            verify=CA_CERT_FILE
        )
        if response.status_code != 200:
            print(f"Erro ao buscar dados: {response.status_code} - {response.reason}")
            msvcrt.getch()
            exit()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API Clara: {e}")
        msvcrt.getch()
        exit()

# Função para buscar todos os UUIDs existentes no Notion
def retrieve_all_notion_uuids():
    """Recupera todos os UUIDs existentes no banco de dados do Notion."""
    try:
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
        
        all_uuids = []
        has_more = True
        next_cursor = None

        # Loop para paginar os resultados da API do Notion
        while has_more:
            payload = {"page_size": 100}
            if next_cursor:
                payload["start_cursor"] = next_cursor

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"Erro ao buscar UUIDs do Notion: {response.status_code} - {response.reason}")
                msvcrt.getch()
                exit()

            data = response.json()
            results = data.get('results', [])

            # Extrai os UUIDs das entradas existentes
            for entry in results:
                properties = entry.get('properties', {})
                if 'UUID' in properties and 'rich_text' in properties['UUID'] and properties['UUID']['rich_text']:
                    all_uuids.append(properties['UUID']['rich_text'][0]['text']['content'])

            has_more = data.get('has_more', False)
            next_cursor = data.get('next_cursor', None)
        return all_uuids
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar UUIDs do Notion: {e}")
        msvcrt.getch()
        exit()

# Função para criar uma nova entrada no Notion
def create_notion_entry(transaction, existing_uuids):
    """Cria uma nova entrada no Notion com base nos dados da transação."""
    transaction_uuid = transaction.get('uuid')
    transaction_label = transaction.get('label')
    transaction_type = transaction.get('type')

    # Ignora transações de pagamento ou com labels específicas
    if "PAYMENT" in transaction_type.upper() or re.search(r'([2-9]|1[0-2])/[0-9]+', transaction_label):
        print(f"Transação {transaction_uuid} pagamento foi ignorada.")
        return False

    # Verifica se o UUID já existe no Notion
    if transaction_uuid in existing_uuids:
        print(f"Transação {transaction_uuid} já existe no Notion. Pulando criação.")
        return False

    # Cria o título da entrada no Notion
    transaction_title = f"Código - Despesa a identificar (Clara Cartões) {transaction_label}"
    email = transaction.get('card', {}).get('user', {}).get('username', '')

    # Recupera o ID do usuário no Notion com base no e-mail
    user_id = notion_user_map.get(email, None)

    # Prepara os dados para criar a entrada no Notion
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    notion_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Orientações": {"rich_text": [{"text": {"content": orientacoes}}]},
            "UUID": {"rich_text": [{"text": {"content": transaction_uuid}}]},
            "Título": {"rich_text": [{"text": {"content": transaction_label}}]},
            "Nome": {"title": [{"text": {"content": transaction_title}}]},
            "Data de Pagamento": {"date": {"start": transaction.get('operationDate')}},
            "Tipo de Transação": {"select": {"name": transaction.get('type')}},
            "Nome do Usuário": {"rich_text": [{"text": {"content": transaction.get('card', {}).get('user', {}).get('userFullName', '')}}]},
            "E-mail": {"rich_text": [{"text": {"content": email}}]},
            "Valor": {"number": transaction.get('amount', {}).get('value', 0)},
            "Moeda": {"rich_text": [{"text": {"content": transaction.get('amount', {}).get('currency', {}).get('code', '')}}]}
        }
    }

    # Adiciona o responsável se o ID do usuário for encontrado
    if user_id:
        notion_data["properties"]["Responsável"] = {"people": [{"id": user_id}]}

    try:
        # Envia a requisição para criar a entrada no Notion
        response = requests.post(url, headers=headers, json=notion_data)
        response.raise_for_status()
        print(f"Nova entrada criada para transação {transaction_uuid}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao criar entrada no Notion: {e}")
        return False

# Função para processar e criar entradas no Notion
def process_and_create_notion_entries(data, existing_uuids):
    """Processa os dados da API da Clara e cria entradas no Notion."""
    if not data or 'content' not in data:
        return

    content = data['content']
    created_count = 0

    # Itera sobre as transações e cria entradas no Notion
    for transaction in content:
        if create_notion_entry(transaction, existing_uuids):
            created_count += 1

    print(f"Total de novas entradas criadas: {created_count}")

# Ponto de entrada do script
if __name__ == "__main__":
    # Obtém o token de acesso da API da Clara
    access_token = get_access_token()

    if access_token:
        # Busca os dados da API da Clara
        api_data = get_api_data(access_token)
        if api_data:
            # Recupera todos os UUIDs existentes no Notion
            notion_uuids = retrieve_all_notion_uuids()
            # Processa os dados e cria entradas no Notion
            process_and_create_notion_entries(api_data, notion_uuids)

    # Aguarda a pressão de qualquer tecla para encerrar o script
    print("Pressione qualquer tecla para encerrar...")
    msvcrt.getch()