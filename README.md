# Verificador de Faltas e Notas-Flask
 Esse é o meu primeiro projeto com Flask, criado pra quem, como eu, quer acompanhar as faltas e notas do SUAP sem ter que ficar entrando lá toda hora. Aqui você consegue ver como está sua frequência, se dá pra faltar mais um pouco, e até o que precisa tirar pra passar.

- **Resumo de Faltas**: Traz o total de faltas, quantos dias ainda dá pra faltar.
- **Notas por Matéria**: Mostra suas notas por bimestre e o quanto ainda precisa pra passar.
- **Feedback Visual**: Tem ícones e mensagens que representam sua situação – algo simples

## Tecnologias

- **Flask**: Estrutura backend da aplicação.
- **Selenium**: Para puxar os dados direto do SUAP (é preciso colocar o login e a senha no código).
- **Tailwind CSS**: Deixa o frontend bonitinho.
- **JSON**: Armazena os dados de faltas e notas.


## Como rodar o projeto

1. **Clone o repositório**:

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuração do login**: Abra o `app.py` e insira seu usuário e senha do SUAP

4. **Execute o projeto**:
   - **Modo Manual**:
     ```bash
     .venv\Scripts\activate.bat  # Ativa o ambiente virtual
     python app.py  # Roda o Flask
     ```
     Abra [http://127.0.0.1:5000](http://127.0.0.1:5000) no navegador.

   - **Modo Com Um Clique** (para Windows):
     - no arquivo `start_flask_app.bat`:
       ```batch
       cd "caminho para onde esta a pasta do projeto"
       call .venv\Scripts\Activate.bat
       start "" "http://127.0.0.1:5000"
       python app.py
       ```
     - altere esse arquivo e com um clique o projeto é executado 


## Observações

- **Login Seguro**: Lembre-se de proteger o login e senha caso compartilhe o código.
- **Selenium e ChromeDriver**: Certifique-se de ter o `chromedriver` compatível com a versão do seu Chrome.
- **Uso Local**: O projeto é para uso pessoal/local; evite compartilhar o servidor sem ajustes de segurança.
