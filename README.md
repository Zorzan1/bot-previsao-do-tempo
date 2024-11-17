# bot-previsao-do-tempo

Uma aplicação automatizada desenvolvida em Python que utiliza Selenium para buscar a previsão do tempo no site AccuWeather e enviar essas informações diretamente para o seu e-mail. Ideal para quem deseja receber atualizações diárias sobre as condições meteorológicas de uma cidade específica de forma conveniente e sem esforço manual.

## Funcionalidades

- Obtenção de Dados: Utiliza Selenium para acessar o site do AccuWeather, e pega os dados de 10 dias.

- Envio por E-mail: Formata os dados obtidos em um e-mail HTML e envia para um destinatário configurado.

## Requisitos

- Python 3 

## Configuração

1. Instale as dependências necessárias:

pip install -r requirements.txt

2. Execute o script para testar o envio de e-mails:

python app.py
