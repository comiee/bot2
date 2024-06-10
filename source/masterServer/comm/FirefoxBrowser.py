from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import platform


class FirefoxBrowser(Firefox):
    __SERVICE_PATH = 'geckodriver.exe' if platform.system() == 'Windows' else 'geckodriver'

    def __init__(self):
        options = FirefoxOptions()
        options.set_preference('webdriver.timezone', 'Asia/Shanghai')
        options.set_preference('intl.accept_languages', 'zh-CN')
        service = Service(self.__SERVICE_PATH)
        super().__init__(options=options, service=service)
        self.__waiter = WebDriverWait(self, 60)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        try:
            super().close()
        except:
            pass

    def wait_element(self, by, val) -> WebElement:
        return self.__waiter.until(EC.presence_of_element_located((by, val)))

    def wait_elements(self, by, val) -> list[WebElement]:
        return self.__waiter.until(EC.presence_of_all_elements_located((by, val)))
