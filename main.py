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
    elif request_args and "name" in request_args:
        name = request_args["name"]

    return jsonify({"message": f"Olá, {name}!"}), 200
