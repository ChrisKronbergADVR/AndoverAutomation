import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from SupportFiles.MultiLog import MultiLog
from SupportFiles.Address import Address
from SupportFiles.File import File
from SupportFiles.Timing import Timing
from selenium.webdriver.support import expected_conditions as EC

from SupportFiles.Actions import Actions
from SupportFiles.MenuItems.Billing import Billing
from SupportFiles.MenuItems.CoreCoverages import CoreCoverages
from SupportFiles.MenuItems.Underwriting import Underwriting


class Application:
    TEST = False
    COMPANY = "ADVR"

    billing = None
    underwriting = None
    core_coverages = None
    browser = None
    line_of_business = None
    state_chosen = None
    date_chosen = None
    env_used = None
    producer_selected = None
    doc_types = ["Quote", "Application", "Policy"]
    create_type = doc_types[1]
    browser_chosen = None
    multiAdd = None
    number_of_addresses = 1
    pay_plan = None
    dwelling_program = None
    first_name = None
    last_name = None

    gw_environment = {"Local": "https://localhost:9443", "QA": "https://qa-advr.iscs.com/", "QWCP QA": "https://advr-qa.mu-1-andromeda.guidewire.net/", "UAT3": "https://uat3-advr.in.guidewire.net/innovation?saml=off",
                      "UAT4": "https://uat4-advr.in.guidewire.net/innovation", "QA2": "https://qa2-acx-advr.in.guidewire.net/innovation"}

    user_chosen = None
    verified = False
    payment_plan_most = {"Mortgagee Direct Bill Full Pay": "BasicPolicy.PayPlanCd_1", "Automated Monthly": "BasicPolicy.PayPlanCd_2", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_3", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_4", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_5",
                         "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_6", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_7", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_8", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_9", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_10"}
    payment_plan_bop = {"Mortgagee Direct Bill Full Pay": "BasicPolicy.PayPlanCd_1", "Automated Monthly": "BasicPolicy.PayPlanCd_2", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_3", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_4", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_5",
                        "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_6", "Direct Bill 9 Pay": "BasicPolicy.PayPlanCd_7", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_8", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_9", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_10", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_11"}
    payment_plan_bop_wrong = {"Mortgagee Direct Bill Full Pay": "BasicPolicy.PayPlanCd_1", "Automated Monthly": "BasicPolicy.PayPlanCd_2", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_3", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_4", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_5",
                              "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_6", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_7", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_8", "Direct Bill 9 Pay": "BasicPolicy.PayPlanCd_9", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_10", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_11"}
    payment_plan_pumb = {"Automated Monthly": "BasicPolicy.PayPlanCd_1", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_2", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_3", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_4",
                         "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_5", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_6", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_7", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_8", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_9"}
    user_dict = {"AgentAdmin": "AgentAdmin", "Admin": "Everything",
                 "Underwriter": "PolicyUnderwriter", "Agent": "PolicyAgent"}

    def __init__(self):
        pass

    def delete_quote(self):
        # delete created Quote
        Actions.find_Element(self.browser, "Delete").click()
        Actions.find_Element(self.browser, "dialogOK").click()

    # * This function is used to decide whether to use chrome or edge browser

    def load_page(self):
        MultiLog.add_log(f"Browser Used: {self.browser_chosen}", logging.INFO)
        if (self.browser_chosen == "Chrome"):
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            self.browser = webdriver.Chrome(options=chrome_options)
        else:
            edge_options = webdriver.edge.options.Options()
            edge_options.add_experimental_option("detach", True)
            self.browser = webdriver.Edge(options=edge_options)
        self.browser.get(self.gw_environment[self.env_used])

        Actions.check_for_value(self.browser, "details-button", keys="click")
        Actions.check_for_value(self.browser, "proceed-link", keys="click")
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

    def run_verify_address(self, browser):
        script = "InsuredMailingAddr.verify();"
        lambda browser: browser.execute_script(script)

    def copy_to_property(self, browser, addr, city, state):
        Actions.find_Element(
            browser, "InsuredResidentAddr.Addr1").send_keys(addr)
        Actions.find_Element(
            browser, "InsuredResidentAddr.City").send_keys(city)
        Select(Actions.find_Element(
            browser, "InsuredResidentAddr.StateProvCd")).select_by_value(state)
        if Actions.find_Element(browser, "InsuredResidentAddr.addrVerifyImg").is_displayed():
            script = "InsuredResidentAddr.verify()"
            browser.execute_script(script)
            Actions.waitPageLoad(browser)

    def copy_to_mailing(self, browser, addr, city, state):
        Actions.find_Element(
            browser, "InsuredMailingAddr.Addr1").send_keys(addr)
        Actions.find_Element(
            browser, "InsuredMailingAddr.City").send_keys(city)
        Select(Actions.find_Element(
            browser, "InsuredMailingAddr.StateProvCd")).select_by_value(state)
        if Actions.find_Element(browser, "InsuredMailingAddr.addrVerifyImg").is_displayed():
            script = "InsuredMailingAddr.verify()"
            browser.execute_script(script)
            Actions.waitPageLoad(browser)

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
        state1, CITY, ADDRESS = Address.addresses[str(state_chosen+"1")]
        custom_city = Address.custom_address["City"]
        custom_add = Address.custom_address["Address"]

        if not self.first_name:
            first_name = state_chosen + " " + line_of_business
            last_name = "Automation"
        else:
            first_name = self.first_name
            last_name = self.last_name

        if Address.custom_address["Flag"]:
            self.create_new_quote(date_chosen, state1, producer_selected, first_name,
                                  last_name, custom_add, custom_city, multiAdd, self.TEST, subType, CARRIER[carrier])
        else:
            self.create_new_quote(date_chosen, state1, producer_selected, first_name,
                                  last_name, ADDRESS, CITY, multiAdd, self.TEST, subType, CARRIER[carrier])

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

    def create_new_quote(self, date, state: str, producer: str, first_name: str, last_name: str, address: str, city: str, multiLoc: bool, test: bool, subType: str, carrier: str):

        # New Quote
        Actions.find_Element(
            self.browser, "QuickAction_NewQuote_Holder").click()
        Actions.find_Element(
            self.browser, "QuickAction_EffectiveDt").send_keys(date)

        Actions.waitPageLoad(self.browser)
        # State Select
        self.browser.execute_script(
            "document.getElementById('QuickAction_StateCd').value = '"+state+"';")
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
                self.browser, "InsuredCurrentAddr.Addr1").send_keys(address)
            Actions.find_Element(
                self.browser, "InsuredCurrentAddr.City").send_keys(city)
            Select(Actions.find_Element(
                self.browser, "InsuredCurrentAddr.StateProvCd")).select_by_value(state)

            if Actions.find_Element(self.browser, "InsuredCurrentAddr.addrVerifyImg").is_displayed():
                script = "InsuredCurrentAddr.verify()"
                self.browser.execute_script(script)
                Actions.waitPageLoad(self.browser)

        # *Select state here
        if (self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella"):
            Actions.find_Element(
                self.browser, "InsuredMailingAddr.Addr1").send_keys(address)
            Actions.find_Element(
                self.browser, "InsuredMailingAddr.City").send_keys(city)
            Select(Actions.find_Element(
                self.browser, "InsuredMailingAddr.StateProvCd")).select_by_value(state)

        # *Adding geographic territory and policy carrier here
        if (self.state_chosen == "NY" and (self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella")):
            Select(Actions.find_Element(
                self.browser, "BasicPolicy.GeographicTerritory")).select_by_value("Metro")

        Actions.waitPageLoad(self.browser)
        if self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella":
            Actions.find_Element(self.browser, "DefaultAddress").click()

        if self.line_of_business != "Businessowners" and self.line_of_business != "Commercial Umbrella":
            self.copy_to_property(self.browser, address, city, state)
            self.copy_to_mailing(self.browser, address, city, state)
            Actions.waitPageLoad(self.browser)

        # *First and Last names copied to input fields here
        Actions.find_Element(self.browser, "InsuredName.MailtoName").send_keys(
            f"{first_name} {last_name}")
        Actions.find_Element(self.browser, "Insured.InspectionContact").send_keys(
            f"{first_name} {last_name}")

        # *Phone Type, Phone number, and email entered here
        Select(Actions.find_Element(self.browser, "InsuredPhonePrimary.PhoneName")
               ).select_by_value("Mobile")
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
                self.core_coverages(self.browser)

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

    # Create a producer

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
            # logger.error(f"Username or Password is not correct. username: {user_name} password: {password}")
            sleep(5)
            self.browser.quit()
            raise Exception("Incorrect username and/or password")
        Actions.waitPageLoad(self.browser)

        #################### Searching for a Producer #########################
        self.browser.execute_script(
            'document.getElementById("Menu_Policy").click();')
        self.browser.execute_script(
            'document.getElementById("Menu_Policy_UnderwritingMaintenance").click();')

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

        if agent_name is None:
            ################ Create Agency #################################
            Actions.check_for_value(self.browser, "NewProducer", keys="click")
            Actions.check_for_value(
                self.browser, "Provider.ProviderNumber", keys=agency_name)
            Actions.check_for_value(
                self.browser, "ProducerTypeCd", value="Agency")
            Actions.check_for_value(
                self.browser, "Provider.StatusDt", keys=default_date)
            Actions.check_for_value(
                self.browser, "AppointedDt", keys="01/01/1900")
            Actions.check_for_value(self.browser, "CombinedGroup", value="No")
            Actions.check_for_value(
                self.browser, "ProviderName.CommercialName", keys="The White House")
            Actions.check_for_value(
                self.browser, "ProviderStreetAddr.Addr1", keys="1600 Pennsylvania Ave NW")
            Actions.check_for_value(
                self.browser, "ProviderStreetAddr.City", keys="Washington")
            Actions.check_for_value(
                self.browser, "ProviderStreetAddr.StateProvCd", value="DC")
            Actions.waitPageLoad(self.browser)
            Actions.check_for_value(self.browser, "CopyAddress", keys="click")
            Actions.waitPageLoad(self.browser)
            Actions.check_for_value(
                self.browser, "ProviderEmail.EmailAddr", keys="test@mail.com")
            Actions.check_for_value(
                self.browser, "AcctName.CommercialName", keys="White House")
            Actions.check_for_value(self.browser, "PayToCd", value="Agency")
            Actions.check_for_value(
                self.browser, "Provider.CombinePaymentInd", value="No")
            Actions.check_for_value(
                self.browser, "Provider.PaymentPreferenceCd", value="Check")
            Actions.check_for_value(
                self.browser, "CopyBillingAddress", keys="click")
            Actions.waitPageLoad(self.browser)
            Actions.save(self.browser)
            Actions.check_for_value(self.browser, "Return", keys="click")
            Actions.waitPageLoad(self.browser)

        Actions.check_for_value(self.browser, "NewProducer", keys="click")
        Actions.check_for_value(
            self.browser, "Provider.ProviderNumber", keys=producerName)
        Actions.check_for_value(
            self.browser, "ProducerTypeCd", value="Producer")
        Actions.check_for_value(
            self.browser, "ProducerAgency", keys=agency_name)
        Actions.check_for_value(
            self.browser, "Provider.StatusDt", keys=default_date)
        Actions.check_for_value(self.browser, "AppointedDt", keys="01/01/1900")
        Actions.check_for_value(self.browser, "CombinedGroup", value="No")
        Actions.check_for_value(
            self.browser, "ProviderName.CommercialName", keys="Starbucks")
        Actions.check_for_value(
            self.browser, "ProviderStreetAddr.Addr1", keys="43 Crossing Way")
        Actions.check_for_value(
            self.browser, "ProviderStreetAddr.City", keys="Augusta")
        Actions.check_for_value(
            self.browser, "ProviderStreetAddr.StateProvCd", value="ME")
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "CopyAddress", keys="click")
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(
            self.browser, "ProviderEmail.EmailAddr", keys="test@mail.com")
        Actions.check_for_value(
            self.browser, "AcctName.CommercialName", keys="White House")
        Actions.check_for_value(self.browser, "PayToCd", value="Agency")
        Actions.check_for_value(
            self.browser, "Provider.CombinePaymentInd", value="No")
        Actions.check_for_value(
            self.browser, "Provider.PaymentPreferenceCd", value="Check")
        Actions.check_for_value(
            self.browser, "CopyBillingAddress", keys="click")
        Actions.waitPageLoad(self.browser)
        Actions.save(self.browser)
        Actions.waitPageLoad(self.browser)
        Actions.check_for_value(self.browser, "IvansCommissionInd", value="No")

        #########################  Add States ############################

        for state in states:
            Actions.check_for_value(self.browser, "AddState", keys="click")
            Actions.check_for_value(
                self.browser, "StateInfo.StateCd", value=state)
            Actions.check_for_value(
                self.browser, "StateInfo.AppointedDt", keys="01/01/1900")
            Actions.check_for_value(
                self.browser, "StateInfo.MerrimackAppointedDt", keys="01/01/1900")
            Actions.check_for_value(
                self.browser, "StateInfo.CambridgeAppointedDt", keys="01/01/1900")
            Actions.check_for_value(
                self.browser, "StateInfo.BayStateAppointedDt", keys="01/01/1900")
            Actions.check_for_value(
                self.browser, "StateInfo.MerrimackLicensedDt", keys="01/01/2999")
            Actions.check_for_value(
                self.browser, "StateInfo.CambridgeLicensedDt", keys="01/01/2999")
            Actions.check_for_value(
                self.browser, "StateInfo.BayStateLicensedDt", keys="01/01/2999")
            Actions.save(self.browser)
            Actions.waitPageLoad(self.browser)

        ############################ Add Products ################################

        for state in states:
            for bus in LOB:
                Actions.check_for_value(
                    self.browser, "AddProduct", keys="click")
                Actions.check_for_value(
                    self.browser, "LicensedProduct.LicenseClassCd", value=bus)
                Actions.check_for_value(
                    self.browser, "LicensedProduct.StateProvCd", value=state)
                Actions.check_for_value(
                    self.browser, "LicensedProduct.EffectiveDt", keys="01/01/1900")
                Actions.check_for_value(
                    self.browser, "LicensedProduct.CommissionNewPct", keys="5")
                Actions.check_for_value(
                    self.browser, "LicensedProduct.CommissionRenewalPct", keys="5")
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

        #################### Searching for a User #########################
        Actions.check_for_value(self.browser, "SearchText", keys=user_type)
        Actions.check_for_value(self.browser, "MatchType", "=")
        Actions.check_for_value(self.browser, "Search", keys="click")

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
