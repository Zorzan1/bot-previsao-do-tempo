import os
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as condicao_esperada
from selenium.webdriver.chrome.service import Service as ChromeService
from dotenv import load_dotenv
from time import sleep

load_dotenv()

def iniciar_driver():
    chrome_options = Options()
    arguments = ['--lang=en-US', '--window-size=1300,1000', '--incognito']
    
    for argument in arguments:
        chrome_options.add_argument(argument)

    chrome_options.add_experimental_option('prefs', {
        'download.prompt_for_download': False,
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_setting_values.automatic_downloads': 1
    })

    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), options=chrome_options)
    
    wait = WebDriverWait(driver, 10, poll_frequency=1, ignored_exceptions=[
        NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException,
    ])
    return driver, wait

def extrair_dados_do_site():
    driver, wait = iniciar_driver()
    driver.get('https://www.accuweather.com/pt/br/rio-de-janeiro/45449/weather-forecast/45449')

    botao_entendo = wait.until(
        condicao_esperada.element_to_be_clickable((By.XPATH, '//div[@class="banner-button policy-accept"]'))
    )
    sleep(3)
    botao_entendo.click()
    sleep(3)

    driver.execute_script("window.scrollTo(0,1450);")

    dias = []
    temperaturas = []
    temperaturas_max = []
    temperaturas_min = []
    status_tempo = []

    elementos_dia = wait.until(condicao_esperada.presence_of_all_elements_located((By.XPATH, '//p[@class="day"]')))
    elementos_dia_continuacao = wait.until(condicao_esperada.presence_of_all_elements_located((By.XPATH, '//p[@class="day"]/following-sibling::*[1]')))
    elementos_temp_max = wait.until(condicao_esperada.presence_of_all_elements_located((By.XPATH, '//span[@class="temp-hi"]')))
    elementos_temp_min = wait.until(condicao_esperada.presence_of_all_elements_located((By.XPATH, '//span[@class="temp-lo"]')))
    elementos_status = wait.until(condicao_esperada.presence_of_all_elements_located((By.XPATH, '//p[@class="no-wrap"]')))

    for i in range(len(elementos_dia)):
        temperaturas.append(elementos_dia[i].text)
        dias.append(elementos_dia_continuacao[i].text)
        temperaturas_max.append(elementos_temp_max[i].text)
        temperaturas_min.append(elementos_temp_min[i].text)
        status_tempo.append(elementos_status[i].text)


    driver.close()
    
    return dias, temperaturas, temperaturas_max, temperaturas_min, status_tempo

def formatar_html_para_email(dias, temperaturas, temperaturas_max, temperaturas_min, status_tempo):
    html = f"""
    <html>
        <head></head>
        <body>
            <h2>Previsão do Tempo para os Próximos Dias</h2>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr>
                    <th>Dia</th>
                    <th>Período</th>
                    <th>Temperatura Máxima</th>
                    <th>Temperatura Mínima</th>
                    <th>Status do Tempo</th>
                </tr>
                {''.join(
                    f"<tr><td>{dias[i]}</td><td>{temperaturas[i]}</td>"
                    f"<td>{temperaturas_max[i]}</td><td>{temperaturas_min[i]}</td>"
                    f"<td>{status_tempo[i]}</td></tr>"
                    for i in range(len(dias))
                )}
            </table>
        </body>
    </html>
    """
    return html

def enviar_email():
    # Configurações de login
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    # Extrair dados
    dias, temperaturas, temperaturas_max, temperaturas_min, status_tempo = extrair_dados_do_site()
    
    # Formatar HTML
    mensagem = formatar_html_para_email(dias, temperaturas, temperaturas_max, temperaturas_min, status_tempo)
    
    # Criar e enviar um email
    destinatario = input('Qual e-mail enviar? ')
    mail = EmailMessage()
    mail['Subject'] = 'Previsão do Tempo'
    mail['From'] = EMAIL_ADDRESS
    mail['To'] = destinatario
    mail.set_content(mensagem, subtype='html')  # define o conteúdo como HTML e mantém o UTF-8 automaticamente

    # Enviar o email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as email:
        email.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        email.send_message(mail)

if __name__ == "__main__":
    enviar_email()

    








