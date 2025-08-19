from datetime import datetime
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import FirefoxOptions

from .Actions import Actions
from .File import File

class User:
    browser = None
    env_used = "Local"
    gw_environment = "https://localhost:9443"
    user_dict = {"AgentAdmin": "AgentAdmin", "Admin": "Everything",
                          "Underwriter": "PolicyUnderwriter", "Agent": "PolicyAgent"}
    browser_chosen = None
    producer_selected = None

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
            self.browser = webdriver.Firefox(options=firefox_options)

        self.browser.get(self.gw_environment)

        if self.browser_chosen == "Chrome" or self.browser_chosen == None:
            self.browser.execute_script('document.getElementById("details-button").click();')
            self.browser.execute_script('document.getElementById("proceed-link").click();')
            
        Actions.waitPageLoad(self.browser)

        assert "Guidewire InsuranceNow™ Login" in self.browser.title

    def get_password(self, user):
        if self.env_used == None:
            self.env_used = "Local"
        password = File.env_files_plus_users[self.env_used]["Users"]["Usernames"][user]
        return password

    # Create a user
    def create_user(self, user_type, user_name):
        user_dict = self.user_dict
        y = datetime.today()
        default_date = y.strftime("%m/%d/%Y").split("/")
        password = self.get_password(user_name)
        user_xpath = "/html/body/main/form/div[1]/div/div[4]/div/div[2]/div[4]/div/div/div[2]/table/tbody/tr[2]/td[1]/a"
        new_user_password = "pass"
        user_values = File.env_files_plus_users[self.env_used]['Users']['Usernames'].keys(
        )
        user_searched_name = None

        self.load_page()

        try:
            self.login(user_name, password)
        except ValueError:
            sleep(5)
            self.browser.quit()
            raise Exception("Incorrect username and/or password")

        Actions.waitPageLoad(self.browser)

        self.browser.execute_script(
            'document.getElementById("Menu_Admin").click();')
        self.browser.execute_script(
            'document.getElementById("Menu_Admin_UserManagement").click();')
        
        Actions.waitPageLoad(self.browser)

        #################### Searching for a User #########################
        Actions.check_for_value(self.browser, "SearchText", keys=user_type)
        Actions.check_for_value(self.browser, "MatchType", "=")
        Actions.check_for_value(self.browser, "Search", keys="click")

        Actions.waitPageLoad(self.browser)
        try:
            user_searched_name = Actions.find_Element(
                self.browser, user_xpath, By.XPATH)
        except:
            pass

        try:
            if user_searched_name is not None:
                if user_dict not in list(user_values):
                    File.add_user(user_type, new_user_password)
                script = "alert(\"User Already Exists\")"
                self.browser.execute_script(script)
                sleep(5)
                self.browser.quit()
                return False
        except:
            pass

        Actions.check_for_value(self.browser, "AddUser", keys="click")
        Actions.check_for_value(
            self.browser, "UserInfo.LoginId", keys=user_type)
        if (user_type == "Agent" or user_type == "Agent Admin"):
            Actions.check_for_value(
                self.browser, "UserInfo.TypeCd", "Producer")
        else:
            Actions.check_for_value(self.browser, "UserInfo.TypeCd", "Company")

        Actions.check_for_value(
            self.browser, "UserInfo.DefaultLanguageCd", "en_US")
        Actions.check_for_value(
            self.browser, "UserInfo.FirstName", keys=user_type)
        Actions.check_for_value(self.browser, "UserInfo.LastName", keys="User")
        Actions.check_for_value(
            self.browser, "UserInfo.ConcurrentSessions", keys=100)
        Actions.check_for_value(
            self.browser, "PasswordInfo.PasswordRequirementTemplateId", "Exempt")
        Actions.check_for_value(
            self.browser, "ChangePassword", keys=new_user_password)
        Actions.check_for_value(self.browser, "ConfirmPassword",
                                keys=new_user_password)
        
        script = "document.getElementById(\"UserInfo.PasswordMustChangeInd\").checked = false"
        self.browser.execute_script(script)
        Actions.check_for_value(self.browser, "ProviderNumber",
                                keys=self.producer_selected)
        Actions.check_for_value(
            self.browser, "UserInfo.BranchCd", "Home Office")
        
        Actions.save(self.browser)

        Actions.check_for_value(
            self.browser, "AddProviderSecurity", keys="click")
        Actions.check_for_value(
            self.browser, "ProviderSecurity.ProviderSecurityCd", keys=self.producer_selected)
        Actions.save(self.browser)
        Actions.waitPageLoad(self.browser)

        Actions.check_for_value(self.browser, "AddRole", keys="click")
        Actions.check_for_value(
            self.browser, "UserRole.AuthorityRoleIdRef", user_dict[user_type])
        Actions.save(self.browser)
        Actions.waitPageLoad(self.browser)

        if user_type == "Underwriter":
            values_used = ["UWServicesPersonal", "UnderwritingPersonalLines", "UnderwritingCommercialLines",
                           "UWServicesCommercial", "UWServicesPersonal-CLM", "UWServicesCommercial-CLM", "UnderwritingPersonalLines-CLM"]
            for value in values_used:
                Actions.check_for_value(
                    self.browser, "AddTaskGroup", keys="click")
                Actions.check_for_value(
                    self.browser, "UserTaskGroup.TaskGroupCd", value)
                Actions.save(self.browser)

        Actions.waitPageLoad(self.browser)
        Actions.save(self.browser)

        script = "alert(\"User Created Successfully!\")"
        self.browser.execute_script(script)
        sleep(5)
        self.browser.quit()

        if user_type not in list(user_values):
            File.add_user(user_type, new_user_password)