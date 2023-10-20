import pandas as pd
import requests
import json
import ast

# Carregando o DataFrame
data = pd.read_csv('newly_fetched_data.csv')

# Definindo a chave da API e outros parâmetros necessários
API_KEY = "" 
link = "https://api.openai.com/v1/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"}
id_modelo = "gpt-3.5-turbo-0301"

# Inicializando o prompt
base_prompt = """
Sua única tarefa é fornecer uma lista python dada a descrição da vaga a seguir, forneça uma lista Python com os seguintes elementos:

- O primeiro elemento é um número:
   1 para Analista de Dados (incluindo funções semelhantes como Analista de BI),
   2 para Cientista de Dados (incluindo Engenheiro de Machine Learning e Engenheiro de MLOPS),
   3 para Engenheiro de Dados,
   0 se for outro cargo ou não identificado.

- O segundo elemento é um número:
   1 se a vaga for remota,
   0 caso contrário.

- O terceiro elemento é uma string contendo um resumo da vaga em três linhas, como se estivesse recomendando a vaga a um candidato.

- O quarto elemento é uma string representando a senioridade da vaga: Sênior, Pleno ou Júnior, CASO NÃO ESTEJA EXPLICITO, VOCE DEVE JULGAR BASEADO NA DESCRIÇÃO.

IMPORTANTE: A RESPOSTA DEVE SER apenas uma lista com esses quatro elementos, sem nenhum texto adicional.

Descrição da vaga:
"""
final_warning = """
Lembre-se de formatar sua resposta da seguinte forma:
[ Código do Cargo, Trabalho Remoto, "Resumo da Vaga", "Nível de Senioridade"]
"""
# Lista para armazenar os resultados
results = []

def fetch_openai_response(prompt):
    body_mensagem = {
        "model": id_modelo,
        "messages": [{"role": "user", "content": prompt}]
    }
    print(f"Enviando solicitação para a API com o prompt:\n{prompt[:100]}...")  # Mostra os primeiros 100 caracteres do prompt
    requisicao = requests.post(link, headers=headers, data=json.dumps(body_mensagem))
    resposta = requisicao.json()
    # Verificando se "choices" está na resposta
    if "choices" in resposta:
        print("Resposta recebida da API:")
        print(resposta["choices"][0]["message"]["content"])  # Print do resultado da requisição
        return resposta["choices"][0]["message"]["content"]
    else:
        print("Erro! Não houve uma resposta válida da API.")
        return None

# Iterando sobre as descrições das vagas no DataFrame
for idx, description in enumerate(data["DESCRICAO"]):
    print(f"\nProcessando descrição da vaga {idx+1} de {len(data['DESCRICAO'])}.")
    full_prompt = base_prompt + "\n" + description

    max_attempts = 3
    is_list = False
    attempts = 0

    while not is_list and attempts < max_attempts:
        mensagem = fetch_openai_response(full_prompt)
        if mensagem:
            try:
                lista = ast.literal_eval(mensagem)
                if isinstance(lista, list):
                    print(f"Sucesso ao processar a descrição da vaga {idx+1}.")
                    is_list = True
                else:
                    attempts += 1
                    print(f"Tentativa {attempts} falhou. A resposta não estava no formato de lista esperado.")
            except:
                attempts += 1
                print(f"Erro ao tentar converter a resposta em lista na tentativa {attempts}.")
        else:
            attempts += 1
            print(f"Tentativa {attempts} falhou. Não houve resposta da API.")

    if not is_list:
        lista = ["Erro", "Erro", "Erro", "Erro"]
        print(f"Não foi possível processar a descrição da vaga {idx+1} após {max_attempts} tentativas.")

    results.append(lista)

print("\nProcessamento completo. Convertendo resultados em DataFrame...")
# Convertendo os resultados em um DataFrame
results_df = pd.DataFrame(results, columns=["Cargo", "Remoto", "Resumo", "Senioridade"])

# Juntando os DataFrames
final_df = pd.concat([data, results_df], axis=1)
print("DataFrame final criado com sucesso!")

final_df.to_csv("deu_certo.csv") 