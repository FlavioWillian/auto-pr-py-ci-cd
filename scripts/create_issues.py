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
                        if "// TODO:" in line or "# TODO:" in line:
                            todos_encontrados.append((file_path, i, line.strip()))
    return todos_encontrados

# Função para criar uma issue no GitHub
def criar_issue(file, line, descricao):
    issue_title = f"TODO encontrado em {file}:{line}"
    issue_body = f"### Arquivo: `{file}`\nLinha: {line}\n\n**Descrição:**\n```\n{descricao}\n```"

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    payload = {"title": issue_title, "body": issue_body, "labels": ["todo"]}

    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 201:
        issue = response.json()
        print(f"Issue criada: {issue['html_url']}")
        return issue["id"]
    else:
        print(f"Erro ao criar Issue: {response.json()}")
        return None

# Função para adicionar a Issue ao Projeto
def adicionar_issue_ao_projeto(issue_id):
    PROJECT_ID = "PVT_kwHOBr5Do84AxJ68"  # Substitua pelo ID do seu projeto
    payload = {
        "query": """
        mutation {
            addProjectV2ItemById(input: {projectId: "PROJECT_ID", contentId: "ISSUE_ID"}) {
                item {
                    id
                }
            }
        }
        """
    }
    
    payload["query"] = payload["query"].replace("PROJECT_ID", str(PROJECT_ID)).replace("ISSUE_ID", str(issue_id))

    response = requests.post("https://api.github.com/graphql", json=payload, headers=HEADERS)

    if response.status_code == 200:
        print(f"Issue adicionada ao projeto V2: {PROJECT_ID}")
        print(f"Resposta da API: {response.json()}")
    else:
        print(f"Erro ao adicionar Issue ao projeto: {response.json()}")

# Executar as funções
if __name__ == "__main__":
    todos = encontrar_todos()
    for file, line, descricao in todos:
        issue_id = criar_issue(file, line, descricao)
        if issue_id:
            adicionar_issue_ao_projeto(issue_id)
