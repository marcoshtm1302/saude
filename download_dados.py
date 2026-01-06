```{python}
import os
import time
import shutil
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAÇÕES ---
URL_ALVO = "https://realezapr.equiplano.com.br:7049/transparencia/despesaOrcamentaria/listaEmpenhos?formulario.codEntidade=49&formulario.exercicio=2025&formulario.codOrgao=6&formulario.codUnidade=1"

BASE_DIR = os.getcwd()
DIR_DOWNLOAD = os.path.join(BASE_DIR, "downloads_temp")
DIR_FINAL = os.path.join(BASE_DIR, "dados")
ARQUIVO_FINAL = "dados_saude_realeza.csv"

# Inicializa driver para segurança
driver = None

try:
    # 1. PREPARAÇÃO DE PASTAS
    os.makedirs(DIR_DOWNLOAD, exist_ok=True)
    os.makedirs(DIR_FINAL, exist_ok=True)
    
    # Limpa pasta temporária
    for f in os.listdir(DIR_DOWNLOAD):
        try: os.remove(os.path.join(DIR_DOWNLOAD, f))
        except: pass

    # 2. CONFIGURAÇÃO DO BROWSER
    print(">>> Iniciando configuração do Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1920,1080")
    
    prefs = {
        "download.default_directory": DIR_DOWNLOAD,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    # 3. LANÇAR NAVEGADOR
    print(">>> Abrindo navegador...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 4. ACESSAR SITE
    print(f">>> Acessando URL: {URL_ALVO}")
    driver.get(URL_ALVO)

    # 5. AGUARDAR E CLICAR (Wait Explícito)
    print(">>> Aguardando botão CSV...")
    wait = WebDriverWait(driver, 60)
    
    # Tenta encontrar o botão por texto ou valor
    botao = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(., 'CSV')] | //a[contains(., 'CSV')] | //input[@value='CSV']")
    ))
    
    print(">>> Clicando no botão via JS...")
    driver.execute_script("arguments[0].click();", botao)

    # 6. ESPERAR DOWNLOAD CONCLUIR
    print(">>> Aguardando arquivo...")
    timeout = 60
    start = time.time()
    arquivo_baixado = None

    while time.time() - start < timeout:
        arquivos = [f for f in os.listdir(DIR_DOWNLOAD) if f.endswith(".csv")]
        if arquivos:
            path = os.path.join(DIR_DOWNLOAD, arquivos[0])
            # Verifica integridade (arquivo existe, > 0 bytes e não é .crdownload)
            if os.path.exists(path) and os.path.getsize(path) > 0 and "crdownload" not in path:
                arquivo_baixado = path
                break
        time.sleep(1)

    # 7. FINALIZAR (Mover arquivo)
    if arquivo_baixado:
        destino = os.path.join(DIR_FINAL, ARQUIVO_FINAL)
        if os.path.exists(destino):
            os.remove(destino) # Substituir antigo
            
        shutil.move(arquivo_baixado, destino)
        print("="*50)
        print(f"SUCESSO! Arquivo salvo em:\n{destino}")
        print("="*50)
    else:
        raise Exception("Download falhou (tempo limite esgotado).")

except Exception as e:
    print(f"\n>>> ERRO: {e}")
    if driver:
        try: driver.save_screenshot("erro_snapshot.png")
        except: pass

finally:
    if driver:
        print(">>> Fechando navegador...")
        driver.quit()
```
