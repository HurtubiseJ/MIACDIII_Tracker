from selenium import webdriver
import selenium 
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import random


URL = "https://miacathletics.com/sports/baseball"

def main():

    # create a new Service instance and specify path to Chromedriver executable
    service = ChromeService(executable_path=ChromeDriverManager().install())

    # Step 2: Change browser properties
    # create a ChromeOptions object
    options = webdriver.ChromeOptions()

    #run in headless mode
    options.add_argument("--headless")

    # disable the AutomationControlled feature of Blink rendering engine
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # disable pop-up blocking
    options.add_argument('--disable-popup-blocking')
    
    # start the browser window in maximized mode
    options.add_argument('--start-maximized')
    
    # disable extensions
    options.add_argument('--disable-extensions')
    
    # disable sandbox mode
    options.add_argument('--no-sandbox')
    
    # disable shared memory usage
    options.add_argument('--disable-dev-shm-usage')


    # Set navigator.webdriver to undefined
    # create a driver instance
    driver = webdriver.Chrome(service=service, options=options)

    # Change the property value of the navigator for webdriver to undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")



    # Step 3: Rotate user agents 
    user_agents = [
        # Add your list of user agents here
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]

    # select random user agent
    user_agent = random.choice(user_agents)

    # pass in selected user agent as an argument
    options.add_argument(f'user-agent={user_agent}')


    # Step 4: Scrape using Stealth
    #enable stealth mode
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    # navigate to opensea
    driver.get(URL)
    
    # Wait for page to load
    while driver.execute_script("return document.readyState") != "complete":
        pass

    s
    
    # Take screenshot
    # driver.save_screenshot("opensea.png")
    
    # Close browser
    # driver.quit()

if __name__ == "__main__":
    main()