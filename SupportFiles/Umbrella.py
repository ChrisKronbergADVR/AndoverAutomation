from selenium.webdriver.support.select import Select
from .Actions import Actions
from .MenuItems.Billing import Billing

class Umbrella:
    billing = None
    browser = None
    create_type = None

    def __init__(self):
        pass

    @staticmethod
    def start_umbrella(self,browser,create_type,billing:Billing):
        Actions.find_Element(browser, "GetUmbrellaQuote").click()
        Actions.waitPageLoad(browser)
        Actions.find_Element(browser, "Wizard_UmbrellaLiability").click()
        Select(Actions.find_Element(browser, "Line.PersonalLiabilityLimit")).select_by_value("1000000")
        Actions.find_Element(browser, "Line.TotMotOwnLeasBus").send_keys(0)
        Actions.find_Element(browser, "Line.NumMotExcUmb").send_keys(0)
        Actions.find_Element(browser, "Line.NumHouseAutoRec").send_keys(0)
        Actions.find_Element(browser, "Line.NumOfYouthInexp").send_keys(0)

        if self.state_chosen == "NH":
            Select(Actions.find_Element(browser, "Line.RejectExcessUninsuredMotorists")).select_by_value("No")
            Select(Actions.find_Element(browser, "Line.UnderAutLiabPerOcc")).select_by_value("No")

        if self.state_chosen == "NJ" or self.state_chosen == "NY" or self.state_chosen == "RI" or self.state_chosen == "CT" or self.state_chosen == "IL" or self.state_chosen == "ME" or self.state_chosen == "MA":
            Select(Actions.find_Element(browser, "Line.UnderAutLiabPerOcc")).select_by_value("No")
            Actions.waitPageLoad(browser)
            Actions.save(browser)

        if create_type == "Application":
            Actions.find_Element(browser, "Bind").click()
            Actions.find_Element(browser, "Wizard_Underwriting").click()
            Select(Actions.find_Element(browser, "Question_DUIConvicted")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_ConvictedTraffic")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_WatercraftBusiness")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_DiscussedWithUnderwriter")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_DayCarePremises")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_UndergraduateStudents")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_AnimalsCustody")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_PoolPremises")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_TrampolinePremises")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_CancelledRecently")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_BusinessPolicies")).select_by_value("NO")
            Select(Actions.find_Element(browser, "Question_OnlineHome")).select_by_value("NO")
            Actions.save(browser)
            Actions.find_Element(browser, "Wizard_Review").click()

            billing.run_billing()

            Actions.waitPageLoad(browser)
            Actions.save(browser)

        if create_type == "Policy":
            Actions.find_Element(browser, "Return").click()
            Actions.find_Element(browser, "policyLink0").click()
            self.submit_policy(browser)
            Actions.find_Element(browser, "Return").click()
            Actions.find_Element(browser, "policyLink0").click()
            self.billing.run_billing()
    
    @staticmethod
    def start_commercial_umbrella(self,browser,create_type,billing:Billing):
        Actions.find_Element(browser, "GetUmbrellaQuote").click()
        Actions.waitPageLoad(browser)
        Actions.find_Element(browser, "Wizard_UmbrellaLiability").click()

        if self.state_chosen == "CT" or self.state_chosen == "NH" or self.state_chosen == "NY" or self.state_chosen == "RI":
            Select(Actions.find_Element(browser, "Line.CoverageTypeCd")).select_by_value("Businessowners Umbrella Liability")

        Select(Actions.find_Element(browser, "Line.CommercialLiabilityLimit")).select_by_value("1000000")
        Select(Actions.find_Element(browser, "Line.OwnedAutosInd")).select_by_value("No")
        Select(Actions.find_Element(browser, "Line.EmplLiabCovrInsured")).select_by_value("No")
        Actions.find_Element(browser, "Wizard_Policy").click()
        Actions.find_Element(browser, "Bind").click()
        Actions.find_Element(browser, "Wizard_Underwriting").click()
        Select(Actions.find_Element(browser, "Question_OtherLiab")).select_by_value("NO")
        Select(Actions.find_Element(browser, "Question_PriorCovCancelled")).select_by_value("NO")
        Actions.find_Element(browser, "Question_PreviousUmbrella").send_keys("ACME")
        Actions.save(browser)
        Actions.find_Element(browser, "Wizard_Review").click()
        billing.run_billing()
        Actions.find_Element(browser, "Navigate_Location_2").click()
        Select(Actions.find_Element(browser, "Location.UnderlyingEmplLimitConf")).select_by_value("Yes")
        Actions.find_Element(browser, "NextPage").click()
        if self.create_type == "Policy":
            Actions.find_Element(browser, "Return").click()
            Actions.find_Element(browser, "policyLink0").click()
            self.submit_policy(browser)
            Actions.find_Element(browser, "Return").click()
            Actions.find_Element(browser, "policyLink0").click()
            if self.pay_plan.__contains__("Bill To Other"):
                billing.run_billing()