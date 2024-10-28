import json
from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
import os

app = Flask(__name__)

# Nome do arquivo JSON para armazenar os dados
json_file = 'dados_faltas.json'

# Função para capturar dados de faltas, frequência e notas
def capturar_dados():
    driver = webdriver.Chrome()
    dados = {}

    try:
        # Acessa a página de login do SUAP
        driver.get("https://suap.ifrn.edu.br/accounts/login/")
        
        username = 'username'  # Coloque seu username aqui
        password = 'senha'  # Coloque sua senha aqui

        driver.find_element(By.ID, "id_username").send_keys(username)
        driver.find_element(By.ID, "id_password").send_keys(password, Keys.RETURN)
        
        # Acessa a página do boletim
        WebDriverWait(driver, 10).until(EC.url_contains("/"))
        driver.get(f"https://suap.ifrn.edu.br/edu/aluno/{username}/?tab=boletim")
        
        # Localiza a linha com o texto "Total:"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//tr[td[contains(text(), "Total:")]]')))
        total_row = driver.find_element(By.XPATH, '//tr[td[contains(text(), "Total:")]]')
        faltas_element = total_row.find_element(By.CSS_SELECTOR, 'td[headers="th_total_faltas"]')
        frequencia_element = total_row.find_element(By.CSS_SELECTOR, 'td[headers="th_frequencia"]')

        # Extrai os valores de faltas e frequência
        faltas_text = faltas_element.text.strip()
        frequencia_text = frequencia_element.text.strip()

        # Verificando se os valores estão sendo capturados
        print(f"Faltas Capturadas: {faltas_text}")
        print(f"Frequência Capturada: {frequencia_text}")

        # Limpa os valores extraídos para conter apenas números
        faltas = int(re.search(r'\d+', faltas_text).group())
        frequencia = float(re.search(r'\d+,\d+', frequencia_text).group().replace(',', '.'))

        # Função para calcular a nota necessária para atingir a média
        def calcular_nota_necessaria(notas, pesos, media_esperada=60):
            soma_pesos = sum(pesos)
            soma_pesos_usados = 0
            soma_notas_ponderadas = 0
            indices_notas_faltantes = []

            for i, nota in enumerate(notas):
                if nota == "-":
                    indices_notas_faltantes.append(i)
                else:
                    nota_valor = float(nota)
                    soma_notas_ponderadas += nota_valor * pesos[i]
                    soma_pesos_usados += pesos[i]

            # Se não há notas faltantes, não é necessário calcular
            if not indices_notas_faltantes:
                return None

            # Calcula quanto falta para atingir a média
            restante_para_media = media_esperada * soma_pesos - soma_notas_ponderadas
            pesos_restantes = sum(pesos[i] for i in indices_notas_faltantes)

            # Se os pesos restantes são zero, não é possível calcular
            if pesos_restantes == 0:
                return None

            # Nota necessária média nos bimestres faltantes
            nota_necessaria = restante_para_media / pesos_restantes

            # Verifica se a nota necessária é viável (entre 0 e 100)
            if nota_necessaria > 100:
                return "Não é possível atingir a média."
            elif nota_necessaria <= 0:
                return "Média já atingida."
            else:
                return f"Você precisa de uma média de {round(nota_necessaria, 2)} nos próximos bimestres."

        # Captura as notas para cada matéria
        notas = []
        rows = driver.find_elements(By.XPATH, '//tr[@class=""]')  # Pega cada linha de matéria
        for row in rows:
            materia_element = row.find_element(By.CSS_SELECTOR, 'td[headers="th_disciplina"]')
            materia = materia_element.text.strip()

            # Função para verificar se um elemento de nota existe
            def pegar_nota(seletor):
                try:
                    return row.find_element(By.CSS_SELECTOR, f'td[headers="{seletor}"] span').text.strip()
                except:
                    return None  # Retorna None se a nota não existir

            # Pega as notas ou None se não estiver disponível
            nota1 = pegar_nota('th_n1n')
            nota2 = pegar_nota('th_n2n')
            nota3 = pegar_nota('th_n3n')
            nota4 = pegar_nota('th_n4n')

            # Lista de notas e pesos para a matéria atual
            notas_materia = []
            pesos = []

            # Verifica cada nota e adiciona aos pesos se a coluna existir
            if 'th_n1n' in row.get_attribute('innerHTML'):
                notas_materia.append(nota1 if nota1 is not None else "-")
                pesos.append(2)
            if 'th_n2n' in row.get_attribute('innerHTML'):
                notas_materia.append(nota2 if nota2 is not None else "-")
                pesos.append(2)
            if 'th_n3n' in row.get_attribute('innerHTML'):
                notas_materia.append(nota3 if nota3 is not None else "-")
                pesos.append(3)
            if 'th_n4n' in row.get_attribute('innerHTML'):
                notas_materia.append(nota4 if nota4 is not None else "-")
                pesos.append(3)

            # Calcula a nota necessária, considerando os bimestres existentes
            nota_necessaria = calcular_nota_necessaria(notas_materia, pesos)

            # Adiciona a matéria, as notas e a nota necessária à lista de notas
            notas.append({
                "materia": materia,
                "nota1": nota1 if 'th_n1n' in row.get_attribute('innerHTML') else None,
                "nota2": nota2 if 'th_n2n' in row.get_attribute('innerHTML') else None,
                "nota3": nota3 if 'th_n3n' in row.get_attribute('innerHTML') else None,
                "nota4": nota4 if 'th_n4n' in row.get_attribute('innerHTML') else None,
                "nota_necessaria": nota_necessaria  # Quanto falta para passar
            })

        # Calcula quantos dias ainda pode faltar
        total_faltas_permitidas = 300  # Total de 300 faltas permitidas
        aulas_por_dia = 6  # 6 aulas por dia
        faltas_restantes = total_faltas_permitidas - faltas
        dias_restantes = faltas_restantes // aulas_por_dia  # Calcula quantos dias pode faltar

        # Condições para mostrar as imagens e mensagens
        if frequencia >= 80:
            mensagem = "Você não irá reprovar e nem perder o Pé de Meia, pode faltar."
            imagem = "img.jpg"
        elif 70 <= frequencia < 80:
            mensagem = "Cuidado, você pode perder o Pé de Meia, mas não irá reprovar."
            imagem = "img2.jpg"
        else:
            mensagem = "Atenção! Você está perto de reprovar."
            imagem = None

        # Prepara os dados para o front-end
        dados = {
            "faltas": faltas,
            "frequencia": frequencia,
            "faltas_restantes": faltas_restantes,
            "dias_restantes": dias_restantes,
            "mensagem": mensagem,
            "imagem": imagem,
            "notas": notas
        }

        # Verificando se os dados estão sendo gerados corretamente
        print(f"Dados Gerados: {dados}")

        # Salva os dados no arquivo JSON
        with open(json_file, 'w') as f:
            json.dump(dados, f)

    except Exception as e:
        dados = {"erro": str(e)}
        print(f"Erro capturado: {e}")
    
    finally:
        driver.quit()

    return dados

# Função para carregar os dados do arquivo JSON
def carregar_dados():
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            dados = json.load(f)
        print(f"Dados carregados do arquivo: {dados}")
    else:
        # Se o arquivo JSON não existir, captura os dados e cria o arquivo
        dados = capturar_dados()
    
    return dados

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para obter os dados do arquivo JSON
@app.route('/dados', methods=['GET'])
def get_dados():
    dados = carregar_dados()
    return jsonify(dados)

# Rota para atualizar os dados e salvar no arquivo JSON
@app.route('/atualizar', methods=['GET'])
def atualizar_dados():
    dados = capturar_dados()
    return jsonify(dados)

if __name__ == '__main__':
    app.run(debug=True)
