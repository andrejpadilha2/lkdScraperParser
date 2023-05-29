from time import sleep
import http.cookiejar
from selenium import webdriver

def get_cookies():
    cookie_jar = http.cookiejar.CookieJar()
    driver = webdriver.Chrome()
    sleep(1.5)
    driver.maximize_window()
    sleep(2)
    
    websites = [
        'https://www.google.com.br',
        'https://g1.globo.com/',
        'https://lista.mercadolivre.com.br/camera-dslr#D[A:camera%20dslr]',
        'https://www.amazon.com.br/b/ref=dp_bc_aui_C_4?ie=UTF8&node=16244249011',
        'https://ge.globo.com/',
        'https://www.youtube.com/@gaveta',
    ]
    
    for website in websites:
        driver.get(website)
        sleep(10)
        
        for cookie in driver.get_cookies():
            cookie_dict = {
                'version': 0,
                'name': cookie['name'],
                'value': cookie['value'],
                'port': None,
                'port_specified': False,
                'domain': cookie['domain'],
                'domain_specified': True,
                'domain_initial_dot': False,
                'path': cookie['path'],
                'path_specified': True,
                'secure': cookie['secure'] if 'secure' in cookie else False,
                'expires': None,
                'discard': False,
                'comment': None,
                'comment_url': None,
                'rest': {}
            }
            cookie_jar.set_cookie(http.cookiejar.Cookie(**cookie_dict))

    driver.close()

    return cookie_jar