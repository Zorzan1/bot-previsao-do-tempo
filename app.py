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
    
    return dias, temperaturas_max, temperaturas_min, temperaturas, status_tempo

def gerar_html(dias, temperaturas_max, temperaturas_min, temperaturas, status_tempo):
    linhas = ""
    for i in range(len(dias)):
        linhas += f"<tr><td>{dias[i]}</td><td>{temperaturas[i]}</td><td>{temperaturas_max[i]}</td><td>{temperaturas_min[i]}</td><td>{status_tempo[i]}</td></tr>\n"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Previsão do Tempo</title>
        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <h2>Previsão do Tempo</h2>
        <table>
            <tr>
                <th>Dia</th>
                <th>Temperatura</th>
                <th>Máxima</th>
                <th>Mínima</th>
                <th>Status</th>
            </tr>
            {linhas}
        </table>
    </body>
    </html>
    """
    return html_content

def enviar_email(html_content):
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise ValueError("Credenciais de e-mail não definidas nas variáveis de ambiente.")

    mail = EmailMessage()
    mail['Subject'] = 'Previsão do Tempo Atualizada'
    mail['From'] = EMAIL_ADDRESS
    mail['To'] = 'zbalcassabaptista@gmail.com'
    mail.set_content(html_content, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as email:
        email.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        email.send_message(mail)


if __name__ == "__main__":
    dias, temperaturas_max, temperaturas_min, temperaturas, status_tempo = extrair_dados_do_site()
    html_content = gerar_html(dias, temperaturas_max, temperaturas_min, temperaturas, status_tempo)
    enviar_email(html_content)



