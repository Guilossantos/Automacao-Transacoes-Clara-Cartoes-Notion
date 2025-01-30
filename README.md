Documentação do Código - Integração de transações Clara Cartões e Notion
Situação problema
Este código automatiza a integração entre a API da Clara Cartões e o Notion. Ele busca transações financeiras recentes da Instituição de Cartão de Crédito Corporativo Clara Cartões, processa os dados recentes e cria entradas correspondentes em um banco de dados do Notion. O objetivo é facilitar a identificação e o controle de despesas, pois para cada transação é criado uma task no Notion para que o responsável preste contas ao financeiro evitando atrasos em conciliação e a falta de gestão das despesas.
Objetivo
Este código integra a API Clara Cartões com a API do Notion para:
•	Obter transações recentes da Clara.
•	Processar as transações.
•	Criar novas entradas no Notion para as despesas que precisam ser identificadas.
________________________________________
Configuração Inicial
1. Dependências Necessárias
•	Bibliotecas Python:
o	requests: Para realizar chamadas às APIs.
o	msvcrt: Para pausa da execução no Windows.
o	json: Para manipulação de arquivos JSON.
o	re: Para trabalhar com expressões regulares.
o	datetime: Para manipulação de datas e intervalos de tempo.
o	requests.auth.HTTPBasicAuth: Para autenticação básica na API Clara.
2. Arquivos Necessários
•	token-data.json: Contém as credenciais para acesso à API Clara:
o	clientId
o	clientSecret
•	notion_credenciais.json: Contém as credenciais para acessar a API do Notion:
o	Clara_Cartoes_Key
o	Registro_de_Despesas_ID
•	Certificados e Chaves da API Clara:
o	Arquivo de certificado público: public-key.crt
o	Arquivo de chave privada: private-key.key
o	Certificado da autoridade certificadora: ca-public-key.pem
•	notion_users.json: Mapeamento de e-mails para IDs de usuários do Notion.
Exemplos de Arquivos de Configuração
token-data.json
{
  "clientId": "seu_client_id_aqui",
  "clientSecret": "seu_client_secret_aqui"
}
notion_credenciais.json
{
  "Clara_Cartoes_Key": "sua_chave_api_notion_aqui",
  "Registro_de_Despesas_ID": "id_do_banco_de_dados_notion_aqui"
}
notion_users.json
{
  "usuario1@empresa.com": "id_usuario1_notion",
  "usuario2@empresa.com": "id_usuario2_notion"
}
3. Configurações Adicionais
O período de transações a ser processado é configurado automaticamente para os últimos 7 dias, excluindo o dia atual.
________________________________________
Funções do Código
1. convert_date_format(date_obj)
Converte uma data para o formato YYYY-MM-DD.
2. get_access_token()
Obtém o token de acesso da API Clara usando autenticação básica.
•	Erro Tratado: Qualquer erro ao obter o token exibe uma mensagem e finaliza o programa.
3. get_api_data(access_token)
Faz uma chamada à API Clara para obter os dados das transações no período definido.
•	Parâmetros:
o	access_token: Token de acesso para autenticação.
•	Erro Tratado: Qualquer falha na requisição exibe uma mensagem e finaliza o programa.
4. retrieve_all_notion_uuids()
Busca todos os UUIDs existentes na base de dados do Notion para evitar duplicatas.
•	Iteração: Realiza paginação para buscar todos os resultados.
•	Erro Tratado: Qualquer falha na requisição exibe uma mensagem e finaliza o programa.
5. create_notion_entry(transaction, existing_uuids)
Cria uma nova entrada no Notion com base nos dados da transação.
•	Parâmetros:
o	transaction: Dados da transação da API Clara.
o	existing_uuids: Lista de UUIDs existentes no Notion.
•	Critérios de Ignoração:
o	Transações do tipo PAYMENT.
o	Transações já existentes no Notion.
o	Transações associadas a um e-mail específico.
•	Propriedades Criadas no Notion:
o	Orientações
o	UUID
o	Título
o	Nome
o	Data de Pagamento
o	Tipo de Transação
o	Nome do Usuário
o	E-mail
o	Valor
o	Moeda
o	Responsável (se houver correspondência de e-mail).
•	Erro Tratado: Qualquer falha na criação exibe uma mensagem e segue para a próxima transação.
6. process_and_create_notion_entries(data, existing_uuids)
Processa todas as transações recebidas e tenta criar entradas no Notion para as que atendem aos critérios.
•	Parâmetros:
o	data: Dados da API Clara.
o	existing_uuids: Lista de UUIDs existentes no Notion.
•	Saída: Exibe o total de entradas criadas.
________________________________________
Fluxo Principal
1.	Obtém o token de acesso da API Clara.
2.	Busca dados de transações recentes da API Clara.
3.	Recupera todos os UUIDs já existentes no Notion.
4.	Processa as transações e cria novas entradas no Notion para despesas identificáveis.
5.	Exibe o total de novas entradas criadas.
6.	Aguarda entrada do usuário para encerrar o programa.
________________________________________
Mensagens de Erro e Tratamento
•	Erro ao obter token: Finaliza o programa após exibir mensagem.
•	Erro ao buscar dados da API Clara: Finaliza o programa após exibir mensagem.
•	Erro ao buscar UUIDs do Notion: Finaliza o programa após exibir mensagem.
•	Erro ao criar entrada no Notion: Exibe mensagem e continua com as demais transações.
________________________________________
Possíveis Extensões
•	Adicionar logs detalhados em vez de apenas mensagens no console.
•	Implementar validações adicionais para os dados recebidos da API Clara.
•	Incluir suporte para reprocessar entradas ignoradas.
•	Criar interface para configurações dinâmicas de período.
________________________________________
Observações
•	Certifique-se de que os arquivos JSON e certificados estão atualizados e no caminho correto.
•	Revise o mapeamento de usuários para garantir a correta associação de responsabilidades no Notion.
•	O sistema é projetado para evitar duplicatas no Notion, mas é importante monitorar manualmente as entradas criadas.
