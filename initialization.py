def initialize():
    from selenium import webdriver
    from selenium.webdriver.chrome.webdriver import WebDriver

    from random_user_agent.user_agent import UserAgent
    from random_user_agent.params import OperatingSystem, SoftwareName

    from configuration import WEBDRIVER_PATH, HEADLESS

    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    if HEADLESS:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        f'user-agent={UserAgent(software_names=(SoftwareName.CHROME.value,), operating_systems=(OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value), limit=120).get_random_user_agent()}'
    )
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')

    return WebDriver(WEBDRIVER_PATH, options=options)
