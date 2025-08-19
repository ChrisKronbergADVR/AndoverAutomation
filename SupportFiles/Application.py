import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver import FirefoxOptions,FirefoxProfile

from .MultiLog import MultiLog
from .Address import Address
from .File import File
from .Timing import Timing
from .Actions import Actions
from SupportFiles.MenuItems.Billing import Billing
from SupportFiles.MenuItems.CoreCoverages import CoreCoverages
from SupportFiles.MenuItems.Underwriting import Underwriting

class Application:
    TEST = False
    COMPANY = "ADVR"

    def __init__(self) -> None:
        self.billing = None
        self.underwriting = None
        self.core_coverages = None
        self.browser = None
        self.line_of_business = None
        self.state_chosen = None
        self.date_chosen = None
        self.env_used = "Local"
        self.producer_selected = None
        self.doc_types = ["Quote", "Application", "Policy"]
        self.create_type = self.doc_types[1]
        self.browser_chosen = None
        self.multiAdd = None
        self.number_of_addresses = 1
        self.pay_plan = "Direct Bill Full Pay"
        self.dwelling_program = None
        self.first_name = None
        self.mid_name = None
        self.last_name = None
        self.custom_address = False
        self.custom_name = False
        self.address1 = None
        self.address2 = None
        self.city = None
        self.subtype = None

        self.verified = False
        self.user_chosen = None
        self.gw_environment = {"Local": "https://localhost:9443", "QA": "https://qa-advr.iscs.com/", "QA2": "https://qa2-acx-advr.in.guidewire.net/innovation", "UAT3": "https://uat3-advr.in.guidewire.net/innovation?saml=off",
                               "UAT4": "https://uat4-advr.in.guidewire.net/innovation"}
        
    def delete_quote(self):
        # delete created Quote
        Actions.find_Element(self.browser, "Delete").click()
        Actions.find_Element(self.browser, "dialogOK").click()

    # * This function is used to decide whether to use chrome or edge browser
    def load_page(self):
        MultiLog.add_log(f"Browser Used: {self.browser_chosen}", logging.INFO)
        
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
        #Actions.check_for_value(self.browser, "details-button", keys="click")
        #Actions.check_for_value(self.browser, "proceed-link", keys="click")
        Actions.waitPageLoad(self.browser)

        assert "Guidewire InsuranceNow™ Login" in self.browser.title

    def get_password(self, user):
        password = File.env_files_plus_users[self.env_used]["Users"]["Usernames"][user]
        return password

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

    def run_verify_address(self):
        script = "InsuredMailingAddr.verify();"
        self.self.browser.execute_script(script)
        # lambda browser: browser.execute_script(script)

    def copy_to_property(self):
        Actions.find_Element(
            self.browser, "InsuredResidentAddr.Addr1").send_keys(self.address1)
        if self.address2 is not None:
            Actions.find_Element(
                self.browser, "InsuredResidentAddr.Addr1").send_keys(self.address2)
        Actions.find_Element(
            self.browser, "InsuredResidentAddr.City").send_keys(self.city)
        Select(Actions.find_Element(
            self.browser, "InsuredResidentAddr.StateProvCd")).select_by_value(self.state)
        if Actions.find_Element(self.browser, "InsuredResidentAddr.addrVerifyImg").is_displayed():
            script = "InsuredResidentAddr.verify()"
            self.browser.execute_script(script)
            Actions.waitPageLoad(self.browser)

    def copy_to_mailing(self):
        Actions.find_Element(
            self.browser, "InsuredMailingAddr.Addr1").send_keys(self.address1)
        if self.address2 is not None:
            Actions.find_Element(
                self.browser, "InsuredResidentAddr.Addr1").send_keys(self.address2)
        Actions.find_Element(
            self.browser, "InsuredMailingAddr.City").send_keys(self.city)
        Select(Actions.find_Element(
            self.browser, "InsuredMailingAddr.StateProvCd")).select_by_value(self.state)
        if Actions.find_Element(self.browser, "InsuredMailingAddr.addrVerifyImg").is_displayed():
            script = "InsuredMailingAddr.verify()"
            self.browser.execute_script(script)
            Actions.waitPageLoad(self.browser)

    # Start application creation
    def startApplication(self, multiAdd, subType, carrier):
        user_chosen = self.user_chosen
        create_type = self.create_type
        state_chosen = self.state_chosen
        line_of_business = self.line_of_business
        env_used = self.env_used
        date_chosen = self.date_chosen
        producer_selected = self.producer_selected

        if MultiLog.log_data:
            MultiLog.create_log(self.state_chosen, self.line_of_business)

        CARRIER = {"Merrimack Mutual Fire Insurance": "MMFI",
                   "Cambrige Mutual Fire Insurance": "CMFI", "Bay State Insurance Company": "BSIC"}
        password = self.get_password(user_chosen)

        if line_of_business == "Homeowners" or line_of_business == "Personal Umbrella":
            MultiLog.add_log(f"Started {create_type} for {state_chosen} {line_of_business}. Carrier: {carrier} | Subtype: {
                             subType} | in {env_used} Environment with {user_chosen} user where date = {date_chosen}", logging.INFO)
        else:
            MultiLog.add_log(f"Started {create_type} for {state_chosen} {line_of_business} in {
                             env_used} Environment with {user_chosen} user where date = {date_chosen}", logging.INFO)

        self.load_page()

        try:
            self.login(user_chosen, password)
        except:
            raise Exception("Incorrect username and/or password")

        self.billing = Billing(self.browser, self.pay_plan, self.state_chosen)
        self.core_coverages = CoreCoverages(
            self.browser, self.dwelling_program)
        self.underwriting = Underwriting(
            self.browser, self.state_chosen, self.line_of_business, self.number_of_addresses)

        # *Tab to click  for recent quotes, applications, and policies
        Actions.find_Element(self.browser, "Tab_Recent").click()
        self.state, self.city, self.address1 = Address.addresses[str(
            state_chosen)]

        if self.custom_address:
            self.city = Address.custom_address["City"]
            self.address1 = Address.custom_address["Address"]
            if Address.custom_address["Address2"] is not None:
                self.address2 = Address.custom_address["Address2"]

        if not self.first_name:
            first_name = state_chosen + " " + line_of_business
            last_name = "Automation"
        else:
            first_name = self.first_name
            last_name = self.last_name

        self.create_new_quote(date_chosen, producer_selected, first_name,
                              last_name, multiAdd, self.TEST, subType, CARRIER[carrier])

        if self.TEST:
            sleep(5)
            self.browser.quit()

    def submit_policy(self):
        wait = WebDriverWait(self.browser, 30)
        script = "return document.readyState == 'complete'"

        Actions.find_Element(self.browser, "Closeout").click()
        Actions.waitPageLoad(self.browser)
        Select(Actions.find_Element(self.browser, "TransactionInfo.PaymentTypeCd")
               ).select_by_value("None")
        Actions.find_Element(
            self.browser, "TransactionInfo.SignatureDocument").click()
        Actions.find_Element(self.browser, "PrintApplication").click()
        wait.until(EC.number_of_windows_to_be(2))
        self.browser.switch_to.window(self.browser.window_handles[1])
        wait.until(lambda browser: browser.execute_script(script))
        self.browser.switch_to.window(self.browser.window_handles[0])
        Actions.waitPageLoad(self.browser)
        Actions.find_Element(self.browser, "Process").click()
        Actions.waitPageLoad(self.browser)

    def create_new_quote(self, date, producer: str, first_name: str, last_name: str, multiLoc: bool, test: bool, subType: str, carrier: str):

        # New Quote
        Actions.find_Element(
            self.browser, "QuickAction_NewQuote_Holder").click()
        Actions.find_Element(
            self.browser, "QuickAction_EffectiveDt").send_keys(date)

        Actions.waitPageLoad(self.browser)
        # State Select
        self.browser.execute_script(
            "document.getElementById('QuickAction_StateCd').value = '"+self.state_chosen+"';")
        Actions.check_for_value(
            self.browser, "QuickAction_CarrierGroupCd", self.COMPANY)

        self.browser.execute_script(
            "document.getElementById('QuickAction_NewQuote').click()")

        if self.line_of_business == "Personal Umbrella":
            Actions.find_Element(
                self.browser, "Homeowners", By.LINK_TEXT).click()
        elif self.line_of_business == "Commercial Umbrella":
            Actions.find_Element(
                self.browser, "Businessowners", By.LINK_TEXT).click()
        else:
            Actions.find_Element(self.browser, self.line_of_business,
                                 By.LINK_TEXT).click()

        # enter producer here
        Actions.check_for_value(self.browser, "ProviderNumber", keys=producer)

        # select entity type
        if (self.line_of_business == "Dwelling Property" or self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella"):
            Select(Actions.find_Element(self.browser, "Insured.EntityTypeCd")
                   ).select_by_value("Individual")

        Actions.waitPageLoad(self.browser)

        quote_num = Actions.find_Element(
            self.browser, "QuoteAppSummary_QuoteAppNumber")
        MultiLog.add_log(f" ", logging.INFO)
        MultiLog.add_log(
            f" ------------ QUOTE STARTED ---------------- ", logging.INFO)
        MultiLog.add_log(f"Quote Number: {quote_num.text}", logging.INFO)

        Actions.check_for_value(
            self.browser, "InsuredPersonal.OccupationClassCd", "Other")
        Actions.check_for_value(
            self.browser, "InsuredPersonal.OccupationOtherDesc", keys="No")

        if self.state_chosen == "NY" and (self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella"):
            Select(Actions.find_Element(
                self.browser, "BasicPolicy.GeographicTerritory")).select_by_value("Upstate")

        self.browser.execute_script(
            'document.getElementById("InsuredName.GivenName").value = "' + first_name + '"')
        if (self.mid_name is not None) and (self.mid_name != ""):
            self.browser.execute_script(
                'document.getElementById("InsuredName.OtherGivenName").value = "' + self.mid_name + '"')
        self.browser.execute_script(
            'document.getElementById("InsuredName.Surname").value = "' + last_name + '"')

        Actions.check_for_value(
            self.browser, "InsuredNameJoint.GivenName", keys="click")
        Actions.check_for_value(
            self.browser, "InsuredNameJoint.GivenName", keys="Second")
        Actions.check_for_value(
            self.browser, "InsuredNameJoint.Surname", keys="Person")
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(
            self.browser, "InsuredNameJoint.GivenName", keys="Second")
        Actions.check_for_value(
            self.browser, "InsuredNameJoint.Surname", keys="Person")
        Actions.check_for_value(
            self.browser, "InsuredPersonalJoint.BirthDt", keys="01/01/1980")
        Actions.check_for_value(
            self.browser, "InsuredPersonalJoint.OccupationClassCd", "Other")
        Actions.check_for_value(
            self.browser, "InsuredPersonalJoint.OccupationOtherJointDesc", keys="No")

        if (self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella") and subType:
            Actions.check_for_value(
                self.browser, "BasicPolicy.DisplaySubTypeCd", subType)
            if self.state_chosen == "NY":
                Select(Actions.find_Element(
                    self.browser, "BasicPolicy.DisplaySubTypeCd")).select_by_index(1)

        if self.line_of_business != "Businessowners" and self.line_of_business != "Commercial Umbrella":
            Actions.find_Element(
                self.browser, "InsuredPersonal.BirthDt").send_keys("01/01/1980")
            Actions.find_Element(
                self.browser, "InsuredCurrentAddr.Addr1").send_keys(self.address1)
            if self.address2 is not None:
                Actions.find_Element(
                    self.browser, "InsuredCurrentAddr.Addr2").send_keys(self.address2)
            Actions.find_Element(
                self.browser, "InsuredCurrentAddr.City").send_keys(self.city)
            Select(Actions.find_Element(
                self.browser, "InsuredCurrentAddr.StateProvCd")).select_by_value(self.state)

            if Actions.find_Element(self.browser, "InsuredCurrentAddr.addrVerifyImg").is_displayed():
                script = "InsuredCurrentAddr.verify()"
                self.browser.execute_script(script)
                Actions.waitPageLoad(self.browser)

        # *Select state here
        if (self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella"):
            Actions.find_Element(
                self.browser, "InsuredMailingAddr.Addr1").send_keys(self.address1)
            if self.address2 is not None:
                Actions.find_Element(
                    self.browser, "InsuredMailingAddr.Addr1").send_keys(self.address2)
            Actions.find_Element(
                self.browser, "InsuredMailingAddr.City").send_keys(self.city)
            Select(Actions.find_Element(
                self.browser, "InsuredMailingAddr.StateProvCd")).select_by_value(self.state)

        # *Adding geographic territory and policy carrier here
        if (self.state_chosen == "NY" and (self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella")):
            Select(Actions.find_Element(
                self.browser, "BasicPolicy.GeographicTerritory")).select_by_value("Metro")

        Actions.waitPageLoad(self.browser)
        if self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella":
            Actions.find_Element(self.browser, "DefaultAddress").click()

        if self.line_of_business != "Businessowners" and self.line_of_business != "Commercial Umbrella":
            self.copy_to_property()
            Actions.waitPageLoad(self.browser)
            self.copy_to_mailing()
            Actions.waitPageLoad(self.browser)

        # *First and Last names copied to input fields here
        Actions.check_for_value(self.browser, "ResetMailtoName", keys="click")
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(
            self.browser, "ResetCommercialName", keys="click")
        Actions.waitPageLoad(self.browser)

        # *Phone Type, Phone number, and email entered here
        Actions.check_for_value(
            self.browser, "Insured.InspectionContact", keys="None")
        Actions.check_for_value(
            self.browser, "InsuredPhonePrimary.PhoneName", "Mobile")
        # Select(Actions.find_Element(self.browser, "InsuredPhonePrimary.PhoneName")
        #       ).select_by_value("Mobile")
        Actions.find_Element(
            self.browser, "InsuredPhonePrimary.PhoneNumber").send_keys(5558675309)
        Actions.check_for_value(
            self.browser, "Insured.InspectionContactPhoneType", "Mobile")
        Actions.check_for_value(
            self.browser, "Insured.InspectionContactNumber", keys=5558675309)
        Actions.find_Element(self.browser, "InsuredEmail.EmailAddr").send_keys(
            "test@mail.com")
        Actions.waitPageLoad(self.browser)

        # Set insurance score if available
        Actions.check_for_value(
            self.browser, "InsuredInsuranceScore.OverriddenInsuranceScore", keys="999")

        # *click the save button
        Actions.save(self.browser)
        Actions.waitPageLoad(self.browser)

        # Select the second policy carrier
        Actions.check_for_value(
            self.browser, "BasicPolicy.PolicyCarrierCd", carrier)

        # multiple locations here
        if self.line_of_business != "Businessowners" and self.line_of_business != "Commercial Umbrella":

            self.core_coverages.start_coverages()
            if (multiLoc and self.line_of_business == "Dwelling Property"):
                for i in range(self.number_of_addresses-1):
                    Actions.find_Element(self.browser, "CopyRisk").click()
                    Actions.save(self.browser)

        if (self.create_type == "Application" or self.create_type == "Policy"):
            Actions.waitPageLoad(self.browser)
            Actions.check_for_value(
                self.browser, "Wizard_Policy", keys="click")
            Actions.waitPageLoad(self.browser)
            Actions.click_radio(self.browser)
            Actions.waitPageLoad(self.browser)
            Actions.find_Element(self.browser, "Bind").click()

            if self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella":
                self.core_coverages.start_coverages()

            Actions.waitPageLoad(self.browser)
            if (self.state_chosen == "NJ" and (self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella")):
                Actions.find_Element(self.browser, "Wizard_Risks").click()
                Actions.waitPageLoad(self.browser)
                Actions.check_for_value(
                    self.browser, "Building.Inspecti onSurveyReqInd", "No")

                # click the save button
                Actions.save(self.browser)

            application_num = Actions.find_Element(
                self.browser, "QuoteAppSummary_QuoteAppNumber")
            MultiLog.add_log(f" ", logging.INFO)
            MultiLog.add_log(
                f" ------------ APPLICATION STARTED ---------------- ", logging.INFO)
            MultiLog.add_log(f"Application Number: {
                             application_num.text}", logging.INFO)

            # Creating a Timing Object for Underwriting questions
            underwriting_time = Timing()
            underwriting_time.start()
            self.underwriting.underwriting_questions(multiLoc)
            underwriting_time.end()

            MultiLog.add_log(f"Time to Complete Underwriting Questions: {
                             underwriting_time.compute_time()} seconds", logging.INFO)

            self.billing.run_billing()

            if self.line_of_business == "Personal Umbrella":
                Actions.find_Element(self.browser, "GetUmbrellaQuote").click()
                Actions.waitPageLoad(self.browser)
                Actions.find_Element(
                    self.browser, "Wizard_UmbrellaLiability").click()
                Select(Actions.find_Element(
                    self.browser, "Line.PersonalLiabilityLimit")).select_by_value("1000000")
                Actions.find_Element(
                    self.browser, "Line.TotMotOwnLeasBus").send_keys(0)
                Actions.find_Element(
                    self.browser, "Line.NumMotExcUmb").send_keys(0)
                Actions.find_Element(
                    self.browser, "Line.NumHouseAutoRec").send_keys(0)
                Actions.find_Element(
                    self.browser, "Line.NumOfYouthInexp").send_keys(0)
                if self.state_chosen == "NH":
                    Select(Actions.find_Element(
                        self.browser, "Line.RejectExcessUninsuredMotorists")).select_by_value("No")
                    Select(Actions.find_Element(
                        self.browser, "Line.UnderAutLiabPerOcc")).select_by_value("No")
                if self.state_chosen == "NJ" or self.state_chosen == "NY" or self.state_chosen == "RI" or self.state_chosen == "CT" or self.state_chosen == "IL" or self.state_chosen == "ME" or self.state_chosen == "MA":
                    Select(Actions.find_Element(
                        self.browser, "Line.UnderAutLiabPerOcc")).select_by_value("No")
                Actions.find_Element(self.browser, "Bind").click()
                Actions.find_Element(
                    self.browser, "Wizard_Underwriting").click()
                Select(Actions.find_Element(
                    self.browser, "Question_DiscussedWithUnderwriter")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_DUIConvicted")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_ConvictedTraffic")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_WatercraftBusiness")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_DayCarePremises")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_UndergraduateStudents")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_AnimalsCustody")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_PoolPremises")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_TrampolinePremises")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_CancelledRecently")).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_BusinessPolicies")).select_by_value("NO")
                Select(Actions.find_Element(self.browser, "Question_OnlineHome")
                       ).select_by_value("NO")
                Actions.save(self.browser)
                Actions.find_Element(self.browser, "Wizard_Review").click()

                self.billing.run_billing()

                Actions.waitPageLoad(self.browser)
                Actions.save(self.browser)

                if self.create_type == "Policy":
                    Actions.find_Element(self.browser, "Return").click()
                    Actions.find_Element(self.browser, "policyLink0").click()
                    self.submit_policy(self.browser)
                    Actions.find_Element(self.browser, "Return").click()
                    Actions.find_Element(self.browser, "policyLink0").click()
                    self.billing.run_billing()

            if self.line_of_business == "Commercial Umbrella":
                Actions.find_Element(self.browser, "GetUmbrellaQuote").click()
                Actions.waitPageLoad(self.browser)
                Actions.find_Element(
                    self.browser, "Wizard_UmbrellaLiability").click()
                if self.state_chosen == "CT" or self.state_chosen == "NH" or self.state_chosen == "NY" or self.state_chosen == "RI":
                    Select(Actions.find_Element(self.browser, "Line.CoverageTypeCd")).select_by_value(
                        "Businessowners Umbrella Liability")
                Select(Actions.find_Element(
                    self.browser, "Line.CommercialLiabilityLimit")).select_by_value("1000000")
                Select(Actions.find_Element(self.browser, "Line.OwnedAutosInd")
                       ).select_by_value("No")
                Select(Actions.find_Element(
                    self.browser, "Line.EmplLiabCovrInsured")).select_by_value("No")
                Actions.find_Element(self.browser, "Wizard_Policy").click()
                Actions.find_Element(self.browser, "Bind").click()
                Actions.find_Element(
                    self.browser, "Wizard_Underwriting").click()
                Select(Actions.find_Element(self.browser, "Question_OtherLiab")
                       ).select_by_value("NO")
                Select(Actions.find_Element(
                    self.browser, "Question_PriorCovCancelled")).select_by_value("NO")
                Actions.find_Element(
                    self.browser, "Question_PreviousUmbrella").send_keys("ACME")
                Actions.save(self.browser)
                Actions.find_Element(self.browser, "Wizard_Review").click()

                self.billing.run_billing()

                Actions.find_Element(
                    self.browser, "Navigate_Location_2").click()
                Select(Actions.find_Element(
                    self.browser, "Location.UnderlyingEmplLimitConf")).select_by_value("Yes")
                Actions.find_Element(self.browser, "NextPage").click()

                if self.create_type == "Policy":
                    Actions.find_Element(self.browser, "Return").click()
                    Actions.find_Element(self.browser, "policyLink0").click()
                    self.submit_policy(self.browser)
                    Actions.find_Element(self.browser, "Return").click()
                    Actions.find_Element(self.browser, "policyLink0").click()
                    if self.pay_plan.__contains__("Bill To Other"):
                        self.billing.run_billing()

        Actions.check_for_value(self.browser, "Wizard_Policy", keys="click")
        warning_value = Actions.value_exists(self.browser, "WarningIssues")
        error_value = Actions.value_exists(self.browser, "ErrorIssues")
        if warning_value is not None:
            for warning in warning_value:
                MultiLog.add_log(f"Issues: {warning.text}", logging.WARNING)
        if error_value is not None:
            for error in error_value:
                MultiLog.add_log(f"Issues: {error.text}", logging.ERROR)

        if (self.create_type == "Policy" and error_value is None):
            self.submit_policy()

            policy_num = Actions.find_Element(
                self.browser, "PolicySummary_PolicyNumber")
            MultiLog.add_log(f" ", logging.INFO)
            MultiLog.add_log(
                f" ------------ Policy STARTED ---------------- ", logging.INFO)
            MultiLog.add_log(f"Policy Number: {policy_num.text}", logging.INFO)

        elif (error_value is not None):
            MultiLog.add_log(f"Application Could not be submitted due to {
                             error_value.text}", logging.ERROR)

        if (test and self.create_type != "Policy"):
            self.delete_quote(self.browser)

    def get_created_application(self, applicaiton_number: str):
        pass