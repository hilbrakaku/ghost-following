from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from openpyxl import Workbook
import time

# ==== CONFIGURACIÓN ====
USERNAME = 'user'
PASSWORD = 'password'

# ==== OPCIONES SELENIUM ====
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

def login(username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)

    user_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    pass_input = driver.find_element(By.NAME, "password")
    user_input.send_keys(username)
    pass_input.send_keys(password)
    
    pass_input.submit()
    time.sleep(5)

    try:
        not_now = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ahora no')]")))
        not_now.click()
    except:
        pass

    try:
        not_now = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ahora no')]")))
        not_now.click()
    except:
        pass

def get_user_list(link_text, wait, driver):
    try:
        print(f"📥 Abriendo lista de {link_text.lower()}...")
        link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, link_text)))
        link.click()
        time.sleep(2)

        dialog = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//ul")))
        scroll_box = driver.find_element(By.XPATH, "//div[@role='dialog']//div[@class='_aano']")

        last_ht = 0
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
            time.sleep(1.5)
            new_ht = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
            if new_ht == last_ht:
                break
            last_ht = new_ht

        users = scroll_box.find_elements(By.XPATH, ".//span[@class='x1lliihq']/a")
        user_list = [u.text for u in users if u.text.strip() != '']

        close_btn = driver.find_element(By.XPATH, "//div[@role='dialog']//button")
        close_btn.click()
        return set(user_list)

    except Exception as e:
        print(f"❌ Error obteniendo {link_text.lower()}: {e}")
        return set()

def export_to_excel(followers, following, not_following_back):
    wb = Workbook()
    ws = wb.active
    ws.title = "Instagram Check"

    ws.append(["Seguidores"])
    for user in sorted(followers):
        ws.append([user])
    
    ws.append([])
    ws.append(["Seguidos"])
    for user in sorted(following):
        ws.append([user])
    
    ws.append([])
    ws.append(["No me siguen de vuelta"])
    for user in sorted(not_following_back):
        ws.append([user])

    wb.save("seguimiento_instagram.xlsx")
    print("📄 Archivo 'seguimiento_instagram.xlsx' guardado.")

# ==== EJECUCIÓN ====
login(USERNAME, PASSWORD)

time.sleep(5)
driver.get(f"https://www.instagram.com/{USERNAME}/")

seguidores = get_user_list("seguidores", wait, driver)
seguidos = get_user_list("seguidos", wait, driver)

no_me_siguen = seguidos - seguidores

print(f"\n✅ Total seguidores: {len(seguidores)}")
print(f"✅ Total seguidos: {len(seguidos)}")
print(f"❌ No me siguen de vuelta: {len(no_me_siguen)}")

export_to_excel(seguidores, seguidos, no_me_siguen)

driver.quit()
