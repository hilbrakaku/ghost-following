from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class InstagramBot:
    FOLLOWERS_XPATH = '//section/main/div/header/section[3]/ul/li[2]/div/a/span/span/span'
    FOLLOWING_XPATH = '//section/main/div/header/section[3]/ul/li[3]/div/a/span/span/span'
    POPUP_XPATH = '//html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]'
    USERNAME_CLASS = '_ap3a._aaco._aacw._aacx._aad7._aade'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = self._init_driver()

    def _init_driver(self):
        options = Options()
        # options.add_argument('--headless')
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def login(self):
        self.driver.get("https://www.instagram.com")
        print("[🔐] Iniciando sesión...")
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys(self.username)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)
        print("[✅] Sesión iniciada.")

    def go_to_profile(self):
        url = f"https://www.instagram.com/{self.username}/"
        self.driver.get(url)
        print(f"[📂] Abriendo perfil: {url}")
        time.sleep(3)

    def _get_count(self, xpath):
        return int(WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        ).text.replace(',', '').replace('.', ''))

    def _open_list_popup(self, xpath):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        time.sleep(2)
        return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.POPUP_XPATH)))

    def _scroll_and_collect(self, container, expected_count):
        collected = set()
        attempts = 0

        while True:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(1)
            elements = self.driver.find_elements(By.CLASS_NAME, self.USERNAME_CLASS)
            current_users = {el.text for el in elements if el.text}
            new_users = current_users - collected
            collected.update(new_users)

            print(f"[🌀] Cargados: {len(collected)} usuarios")

            if len(collected) >= expected_count or attempts >= 5:
                break

            if not new_users:
                attempts += 1
            else:
                attempts = 0

        print("[✅] Scroll completado.\n")
        return list(collected)

    def extract_users(self):
        followers_total = self._get_count(self.FOLLOWERS_XPATH)
        following_total = self._get_count(self.FOLLOWING_XPATH)
        print(f"[📊] Seguidores: {followers_total}, Seguidos: {following_total}")

        followers_popup = self._open_list_popup(self.FOLLOWERS_XPATH)
        followers = self._scroll_and_collect(followers_popup, followers_total)

        self.go_to_profile()
        following_popup = self._open_list_popup(self.FOLLOWING_XPATH)
        following = self._scroll_and_collect(following_popup, following_total)

        return followers, following

    def show_non_followers(self, followers, following):
        non_followers = sorted(set(following) - set(followers))
        print(f"🚫 No te siguen ({len(non_followers)}):")
        for user in non_followers:
            print(f" - {user}")

    def close(self):
        self.driver.quit()
        print("[🔚] Sesión cerrada.")

# ------------------- USO -------------------
if __name__ == "__main__":
    USERNAME = "user"
    PASSWORD = "password"

    bot = InstagramBot(USERNAME, PASSWORD)
    try:
        bot.login()
        bot.go_to_profile()
        followers, following = bot.extract_users()
        bot.show_non_followers(followers, following)
    finally:
        bot.close()
