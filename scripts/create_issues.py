import os
import requests
import re

# Configurações do GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Regex para capturar TODOs no formato: # Todo(Em maiusculo): [Título] - Descrição
TODO_PATTERN = re.compile(r"# TODO: \[(.*?)\] - (.*)")

# Função para encontrar TODOs nos arquivos
def encontrar_todos(diretorio="."):
    todos_encontrados = []
    for root, _, files in os.walk(diretorio):
        for file in files:
            if file.endswith(".py"):  # Apenas arquivos Python
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, start=1):
                        match = TODO_PATTERN.search(line)
                        if match:
                            titulo = match.group(1).strip()
                            descricao = match.group(2).strip()
                            todos_encontrados.append((file_path, i, titulo, descricao))  # Retorna 4 valores
    return todos_encontrados

def obter_issue_node_id(issue_number):
    """ Obtém o ID Global da Issue via GraphQL """
    query = f"""
    query {{
        repository(owner: "{REPO_OWNER}", name: "{REPO_NAME}") {{
            issue(number: {issue_number}) {{
                id
            }}
        }}
    }}
    """
    response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=HEADERS)

    if response.status_code == 200:
        issue_id = response.json()["data"]["repository"]["issue"]["id"]
        print(f"Node ID da Issue: {issue_id}")
        print(f"Response: {response.json()}")
        return issue_id
    else:
        print(f"Erro ao obter Node ID da Issue: {response.json()}")
        return None

def issue_existe(titulo):
    """Verifica se uma Issue com o mesmo título já existe no repositório."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        issues = response.json()
        for issue in issues:
            if issue["title"] == titulo:
                print(f"Issue já existe: {issue['html_url']}")
                return True  # A Issue já existe
    else:
        print(f"Erro ao verificar Issues existentes: {response.json()}")
    
    return False  # A Issue não existe


# Função para criar uma issue no GitHub
def criar_issue(file, line, titulo, descricao):
    
    # Verifica se a Issue já existe
    if issue_existe(titulo):
        print(f"⚠️ Issue já existe para '{titulo}', ignorando criação.")
        return None
    
    issue_title = titulo

    issue_body = f"""
    ### 📌 TODO Detectado no Código

    📂 **Arquivo:** [`{file}`](https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/main/{file}#L{line})  
    📍 **Linha:** {line}

    📝 **Descrição:**  
    {descricao}

    ---
    🔗 Criado automaticamente via GitHub Actions.
    """

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    payload = {
        "title": issue_title,
        "body": issue_body,
        "labels": ["todo"]
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    
    if response.status_code == 201:
        issue = response.json()
        print(f"Issue criada: {issue['html_url']}")
        
        # Buscar o Global ID da Issue via GraphQL
        node_id = obter_issue_node_id(issue["number"])
        return node_id
    else:
        print(f"Erro ao criar Issue: {response.json()}")
        return None

# Função para adicionar a Issue ao Projeto
def adicionar_issue_ao_projeto(issue_id):
    PROJECT_ID = "PVT_kwHOBr5Do84AxJ68"  # Substitua pelo ID do seu projeto
    query = f"""
    mutation {{
        addProjectV2ItemById(input: {{ projectId: "{PROJECT_ID}", contentId: "{issue_id}" }}) {{
            item {{
                id
            }}
        }}
    }}
    """

    response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=HEADERS)

    if response.status_code == 200:
        print(f"Issue adicionada ao projeto {PROJECT_ID}")

        # Obter ID do item adicionado ao projeto
        item_id = response.json()["data"]["addProjectV2ItemById"]["item"]["id"]

        # Definir status ou campo customizado (opcional)
        query_status = f"""
        mutation {{
            updateProjectV2ItemFieldValue(input: {{
                projectId: "{PROJECT_ID}",
                itemId: "{item_id}",
                fieldId: "PVTSSF_lAHOBr5Do84AxJ68zgnT9Sc",
                value: {{ singleSelectOptionId: "f75ad846" }}
            }}) {{
                projectV2Item {{
                    id
                }}
            }}
        }}
        """

        response_status = requests.post("https://api.github.com/graphql", json={"query": query_status}, headers=HEADERS)

        if response_status.status_code == 200:
            print(f"Status atualizado para 'To Do' no projeto {PROJECT_ID}")
        else:
            print(f"Erro ao atualizar status: {response_status.json()}")

    else:
        print(f"Erro ao adicionar Issue ao projeto: {response.json()}")

# Executar as funções
if __name__ == "__main__":
    todos = encontrar_todos()
    for file, line, titulo, descricao in todos:
        issue_id = criar_issue(file, line, titulo, descricao)
        if issue_id:
            adicionar_issue_ao_projeto(issue_id)
