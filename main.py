import functions_framework
from flask import jsonify, request

@functions_framework.http
def hello_gcp(request):
    """
    Função HTTP para GCP Function.
    Retorna uma mensagem de boas-vindas baseada no parâmetro 'name'.
    """
    # TODO: [Implementar autenticação JWT] - Adicionar middleware para validar tokens JWT nas requisições
    request_json = request.get_json(silent=True)
    request_args = request.args

    name = "Mundo"  # Valor padrão
    if request_json and "name" in request_json:
        name = request_json["name"]
        # TODO: [Criando task para o Edu ver] - A automação vai criar essa task e o edu vai poder fazer isso nos codigos tudo.
    elif request_args and "name" in request_args:
        name = request_args["name"]

    # TODO: [Criando mais uma TASK] - Essa Task é para testar a correção de criação duplicada do workflow
    return jsonify({"message": f"Olá, {name}!"}), 200
