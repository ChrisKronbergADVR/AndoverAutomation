from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge import options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxOptions,FirefoxProfile

from .Actions import Actions
from .File import File

class Producer:
    browser = None
    browser_chosen = "Chrome"
    env_used = "Local"
    File.env_used = env_used
    gw_environment = {"Local": "https://localhost:9443", 
                      "QA": "https://qa-advr.iscs.com/", 
                      "QA2": "https://qa2-acx-advr.in.guidewire.net/innovation", 
                      "UAT3": "https://uat3-advr.in.guidewire.net/innovation?saml=off",
                      "UAT4": "https://uat4-advr.in.guidewire.net/innovation"}
    
    def __init__(self):
        pass

    # *function for login
    def login(self, user="admin", password="Not9999!"):
        Actions.waitPageLoad(self.browser)
        Actions.find_Element(self.browser, "j_username").send_keys(user)
        Actions.find_Element(self.browser, "j_password").send_keys(
            password + Keys.RETURN)

        Actions.remove_javascript(self.browser)
        script = "return window.seleniumPageLoadOutstanding == 0;"

        WebDriverWait(self.browser, 60).until(
            lambda browser: browser.execute_script(script))
        
    # * This function is used to decide whether to use chrome or edge browser
    def load_page(self):
        if (self.browser_chosen == "Chrome" or self.browser_chosen == None):
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            self.browser = webdriver.Chrome(options=chrome_options)
        else:
            firefox_options = FirefoxOptions()
            firefox_profile = FirefoxProfile()
            firefox_profile.set_preference("javascript.enabled", True)
            self.browser = webdriver.Firefox(options=firefox_options)
        
        self.browser.get(self.gw_environment[self.env_used])
        if self.browser_chosen == "Chrome" or self.browser_chosen == None:
            self.browser.execute_script('document.getElementById("details-button").click();')
            self.browser.execute_script('document.getElementById("proceed-link").click();')
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "proceed-link", keys="click")

        assert "Guidewire InsuranceNow™ Login" in self.browser.title

    def get_password(self, user):
        if self.env_used == None:
            self.env_used = "Local"
        password = File.env_files_plus_users[self.env_used]["Users"]["Usernames"][user]
        return password

    def create_producer(self, producerName, user_name):
        agency_name = "All_States_All_LOB"
        agent_name = None
        prod_name = None
        y = datetime.today()
        default_date = y.strftime("%m/%d/%Y").split("/")
        password = self.get_password(user_name)
        states = ["CT", "IL", "MA", "ME", "NH", "NJ", "NY", "RI"]
        LOB = ["PUL", "HO", "DP", "BOP-UMB", "BOP"]
        prod_values = File.env_files_plus_users[self.env_used]['Producers']['ProducerNames']

        self.load_page()

        try:
            self.login(user_name, password)
        except ValueError:
            sleep(5)
            self.browser.quit()
            raise Exception("Incorrect username and/or password")
        Actions.waitPageLoad(self.browser)

        #################### Searching for a Producer #########################
        self.browser.execute_script(
            'document.getElementById("Menu_Policy").click();')
        self.browser.execute_script(
            'document.getElementById("Menu_Policy_UnderwritingMaintenance").click();')

        Actions.waitPageLoad(self.browser)
        Actions.find_Element(self.browser, "Producer", id=By.LINK_TEXT).click()
        Actions.check_for_value(self.browser, "SearchText", keys=producerName)
        Actions.check_for_value(self.browser, "SearchBy", "ProviderNumber")
        Actions.check_for_value(self.browser, "SearchFor", "Producer")
        Actions.check_for_value(self.browser, "SearchOperator", "=")
        Actions.check_for_value(self.browser, "Search", keys="click")
        Actions.waitPageLoad(self.browser)

        try:
            prod_name = Actions.find_Element(
                self.browser, "//*[@id=\"Agency/Producer List\"]/table/tbody/tr[2]/td[2]", By.XPATH)

        except:
            pass

        #################### Searching for an Agency #########################
        Actions.check_for_value(self.browser, "SearchText", keys=agency_name)
        Actions.check_for_value(self.browser, "SearchBy", "ProviderNumber")
        Actions.check_for_value(self.browser, "SearchFor", "Agency")
        Actions.check_for_value(self.browser, "SearchOperator", "=")
        Actions.check_for_value(self.browser, "Search", keys="click")
        Actions.waitPageLoad(self.browser)

        try:
            agent_name = Actions.find_Element(
                self.browser, "//*[@id=\"Agency/Producer List\"]/table/tbody/tr[2]/td[2]", By.XPATH)

        except:
            pass

        try:
            if prod_name is not None:
                if producerName not in prod_values:
                    File.add_producer(producerName)
                script = "alert('Producer Already Exists')"
                self.browser.execute_script(script)
                sleep(5)
                self.browser.quit()
                return False
        except:
            pass

        #Actions.waitPageLoad(self.browser)

        if agent_name is None:
            ################ Create Agency #################################
            browser_handles = self.browser.window_handles
            Actions.check_for_value(self.browser, "NewProducer", keys="click")
            Actions.waitPageLoad(self.browser)
            Actions.check_for_value(self.browser, "Provider.ProviderNumber", keys=agency_name)
            Actions.check_for_value(self.browser, "ProducerTypeCd", value="Agency")
            Actions.check_for_value(self.browser, "Provider.StatusDt", keys=default_date)
            Actions.check_for_value(self.browser, "AppointedDt", keys="01/01/1900")
            Actions.check_for_value(self.browser, "CombinedGroup", value="No")
            Actions.check_for_value(self.browser, "ProviderName.CommercialName", keys="The White House")
            Actions.check_for_value(self.browser, "ProviderStreetAddr.Addr1", keys="1600 Pennsylvania Ave NW")
            Actions.check_for_value(self.browser, "ProviderStreetAddr.City", keys="Washington")
            Actions.check_for_value(self.browser, "ProviderStreetAddr.StateProvCd", value="DC")
            Actions.waitPageLoad(self.browser)
            if EC.new_window_is_opened(browser_handles):
                self.browser.switch_to.window(self.browser.window_handles[1])
                Actions.check_for_value(self.browser, "addressGroupValue_0", keys="click")
                Actions.check_for_value(self.browser, "Select", keys="click")
                self.browser.switch_to.window(self.browser.window_handles[0])
            Actions.waitPageLoad(self.browser)
            Actions.check_for_value(self.browser, "CopyAddress", keys="click")
            Actions.check_for_value(self.browser, "ProviderEmail.EmailAddr", keys="test@mail.com")
            Actions.check_for_value(self.browser, "AcctName.CommercialName", keys="White House")
            Actions.check_for_value(self.browser, "PayToCd", value="Agency")
            Actions.check_for_value(self.browser, "Provider.CombinePaymentInd", value="No")
            Actions.check_for_value(self.browser, "Provider.PaymentPreferenceCd", value="Check")
            Actions.check_for_value(self.browser, "CopyBillingAddress", keys="click")
            Actions.save(self.browser)
            Actions.check_for_value(self.browser, "Return", keys="click")

        Actions.check_for_value(self.browser, "NewProducer", keys="click")
        Actions.check_for_value(self.browser, "Provider.ProviderNumber", keys=producerName)
        Actions.check_for_value(self.browser, "ProducerTypeCd", value="Producer")
        Actions.check_for_value(self.browser, "ProducerAgency", keys=agency_name)
        Actions.check_for_value(self.browser, "Provider.StatusDt", keys=default_date)
        Actions.check_for_value(self.browser, "AppointedDt", keys="01/01/1900")
        Actions.check_for_value(self.browser, "CombinedGroup", value="No")
        Actions.check_for_value(self.browser, "ProviderName.CommercialName", keys="Starbucks")
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "ProviderStreetAddr.Addr1", keys="43 Crossing Way")
        Actions.check_for_value(self.browser, "ProviderStreetAddr.City", keys="Augusta")
        Actions.check_for_value(self.browser, "ProviderStreetAddr.StateProvCd", value="ME")
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "ProviderStreetAddr.addrVerifyImg", keys="click")
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "CopyAddress", keys="click")
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "ProviderEmail.EmailAddr", keys="test@mail.com")
        Actions.check_for_value(self.browser, "AcctName.CommercialName", keys="White House")
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "PayToCd", value="Agency")
        Actions.check_for_value(self.browser, "Provider.CombinePaymentInd", value="No")
        Actions.check_for_value(self.browser, "Provider.PaymentPreferenceCd", value="Check")
        Actions.check_for_value(self.browser, "CopyBillingAddress", keys="click")
        Actions.waitPageLoad(self.browser)
        Actions.save(self.browser)
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "IvansCommissionInd", value="No")

        #########################  Add States ############################
        Actions.waitPageLoad(self.browser)
        for state in states:
            Actions.check_for_value(self.browser, "AddState", keys="click")
            Actions.check_for_value(self.browser, "StateInfo.StateCd", value=state)
            Actions.check_for_value(self.browser, "StateInfo.AppointedDt", keys="01/01/1900")
            Actions.check_for_value(self.browser, "StateInfo.MerrimackAppointedDt", keys="01/01/1900")
            Actions.check_for_value(self.browser, "StateInfo.CambridgeAppointedDt", keys="01/01/1900")
            Actions.check_for_value(self.browser, "StateInfo.BayStateAppointedDt", keys="01/01/1900")
            Actions.check_for_value(self.browser, "StateInfo.MerrimackLicensedDt", keys="01/01/2999")
            Actions.check_for_value(self.browser, "StateInfo.CambridgeLicensedDt", keys="01/01/2999")
            Actions.check_for_value(self.browser, "StateInfo.BayStateLicensedDt", keys="01/01/2999")
            Actions.save(self.browser)
            Actions.waitPageLoad(self.browser)

        ############################ Add Products ################################
        Actions.waitPageLoad(self.browser)
        for state in states:
            for bus in LOB:
                Actions.check_for_value(self.browser, "AddProduct", keys="click")
                Actions.check_for_value(self.browser, "LicensedProduct.LicenseClassCd", value=bus)
                Actions.check_for_value(self.browser, "LicensedProduct.StateProvCd", value=state)
                Actions.check_for_value(self.browser, "LicensedProduct.EffectiveDt", keys="01/01/1900")
                Actions.check_for_value(self.browser, "LicensedProduct.CommissionNewPct", keys="5")
                Actions.check_for_value(self.browser, "LicensedProduct.CommissionRenewalPct", keys="5")
                Actions.save(self.browser)
                Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "IvansCommissionInd", value="No")
        Actions.check_for_value(
            self.browser, "FCRAEmail.EmailAddr", keys="test2@mail.com")
        Actions.save(self.browser)

        script = "alert(\"Producer Created Successfully!\")"
        self.browser.execute_script(script)
        sleep(5)
        self.browser.quit()

        if producerName not in prod_values:
            File.add_producer(producerName)