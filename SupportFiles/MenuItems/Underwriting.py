from datetime import datetime, timedelta
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

from SupportFiles.Actions import Actions
from SupportFiles.MultiLog import MultiLog


class Underwriting:

    state_chosen = ""
    line_of_business = ""
    number_of_addresses = 1
    browser = None

    def __init__(self, browser, state, lob, num_of_addr):
        self.state_chosen = state
        self.line_of_business = lob
        self.number_of_addresses = num_of_addr
        self.browser = browser

    # * Function to add underwriting questions for each location
    def question_update(self, question, size):
        if (question.__contains__("1")):
            word = question.split("1")
            new_word = word[0]+str(size)+word[1]
        return new_word

    def gen_dwell_location_questions(self, num):

        MultiLog.add_log(f"Starting questions for Dwelling", logging.INFO)

        ques_dwell = ["Question_PolicyKnownPersonally", "Question_PolicyOtherIns", "Question_PolicyArson", "Question_RiskNumber1PrevDisc", "Question_RiskNumber1Vacant", "Question_RiskNumber1OnlineHome", "Question_RiskNumber1Isolated", "Question_RiskNumber1Island", "Question_RiskNumber1Seasonal", "Question_RiskNumber1SolarPanels", "Question_RiskNumber1Adjacent", "Question_RiskNumber1ChildCare",
                      "Question_RiskNumber1OtherBusiness", "Question_RiskNumber1Undergrad", "Question_RiskNumber1DogsAnimals", "Question_RiskNumber1Electrical", "Question_RiskNumber1EdisonFuses", "Question_RiskNumber1Stove",
                      "Question_RiskNumber1OilHeated", "Question_RiskNumber1Pool", "Question_RiskNumber1Trampoline", "Question_RiskNumber1Outbuildings", "Question_RiskNumber1InsDeclined", "Question_MAFireRiskNumber1OtherFireInsuranceApp",
                      "Question_MAFireRiskNumber1OtherFireInsuranceActive", "Question_MAFireRiskNumber1FireInPast", "Question_MAFireRiskNumber1PropertyForSale", "Question_MAFireRiskNumber1ApplicantMortgageeCrime",
                      "Question_MAFireRiskNumber1ShareholderTrusteeCrime", "Question_MAFireRiskNumber1MortgagePaymentsDelinquent", "Question_MAFireRiskNumber1RealEstateTaxesDelinquent", "Question_MAFireRiskNumber1CodeViolations"]

        newDict = {1: ques_dwell}
        newArr = []

        self.gen_dewll_location_extra_questions(1)
        if self.state_chosen == "RI":
            Actions.find_Element(self.browser, "Question_RiskNumber" +
                                 str(1)+"InspectorName").send_keys("No")

        if (num > 1):
            for loc in range(num-1):
                number = loc+2
                for question_name in ques_dwell:
                    if (question_name.__contains__("1")):
                        word = question_name.split("1")
                        newArr.append(word[0]+str(number)+word[1])
                newDict[number] = newArr
                if self.state_chosen == "RI":
                    Actions.find_Element(self.browser,
                                         "Question_RiskNumber"+str(number)+"InspectorName").send_keys("No")
                self.gen_dewll_location_extra_questions(number)

        return newDict

    def gen_dewll_location_extra_questions(self, num):
        extra_dwell_questions = ["Question_RiskNumber1Lapse", "Question_RiskNumber1NumClaims", "Question_MAFireRiskNumber1PurchaseDate", "Question_MAFireRiskNumber1PurchasePrice",
                                 "Question_MAFireRiskNumber1EstimatedValue", "Question_MAFireRiskNumber1ValuationMethod", "Question_MAFireRiskNumber1AppraisalMethod"]
        updatedArr = []

        if (num > 1):
            for question in extra_dwell_questions:
                updatedArr.append(self.question_update(question, num))
        else:
            updatedArr = extra_dwell_questions
        Select(Actions.find_Element(self.browser, updatedArr[0])).select_by_value(
            "No-New purchase")
        Actions.find_Element(self.browser, updatedArr[1]).send_keys(0)
        if (self.state_chosen == 'MA'):
            Actions.find_Element(
                self.browser, updatedArr[2]).send_keys("01/01/2022")
            Actions.find_Element(
                self.browser, updatedArr[3]).send_keys("100000")
            Actions.find_Element(
                self.browser, updatedArr[4]).send_keys("150000")
            Select(Actions.find_Element(self.browser, updatedArr[5])).select_by_value(
                "Replacement Cost")
            Select(Actions.find_Element(self.browser, updatedArr[6])).select_by_value(
                "Professional Appraisal")

    def underwriting_questions(self, multi):

        y = datetime.today()+timedelta(days=60)
        producer_inspection_date = y.strftime("%m/%d/%Y")
        Actions.find_Element(self.browser, "Wizard_Underwriting").click()
        MultiLog.add_log(f"Starting Underwriting Questions for {
                         self.state_chosen} {self.line_of_business}", logging.INFO)
        Actions.waitPageLoad(self.browser)
        lob = self.line_of_business

        questions_home = ["Question_PermanentFoundation", "Question_IslandProperty", "Question_IsolatedProperty", "Question_IslandHome", "Question_PrevKnown",
                          "Question_PrevDiscussed", "Question_OtherInsurance", "Question_VacantOrOccupied", "Question_OnlineHome", "Question_OnlineHome",
                          "Question_SeasonalHome", "Question_FrameDwellings", "Question_DayCareOnPremises", "Question_UndergraduateStudents", "Question_SolarPanels", "Question_UndergraduateStudents",
                          "Question_DogsCare", "Question_ElectricalService", "Question_WiringInUse", "Question_StoveOnPremises", "Question_OilHeated", "Question_PoolOnPremises",
                          "Question_TrampolineOnPremises", "Question_AnyOutbuildings", "Question_CancelledRecently", "Question_ArsonConvicted"]

        if self.line_of_business == "Dwelling Property":
            if multi:
                dwell_questions = self.gen_dwell_location_questions(
                    self.number_of_addresses)
            else:
                dwell_questions = self.gen_dwell_location_questions(1)

        if self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella":
            Actions.check_for_value(
                self.browser, "Question_InspectorName", keys="Gadget")

            for question in questions_home:
                Actions.check_for_value(self.browser, question, "No", True)
            Actions.check_for_value(
                self.browser, "Question_AnyLapsePast", "No-New Purchase", True)
            Actions.check_for_value(
                self.browser, "Question_ClaimsRecently", keys=0)
            Actions.check_for_value(
                self.browser, "Question_PurchasePrice", keys=500000)

        if (lob == "Dwelling Property"):
            for key in range(len(dwell_questions.keys())):
                for question in dwell_questions[key+1]:
                    Actions.check_for_value(self.browser, question, "No", True)

        if (lob == "Businessowners" or lob == "Commercial Umbrella"):
            Select(Actions.find_Element(
                self.browser, "Question_01CoverageCancellation")).select_by_visible_text("No")
            Actions.find_Element(
                self.browser, "Question_03PreviousCarrierPropertyLimitsPremium").send_keys("No")
            Select(Actions.find_Element(self.browser, "Question_08NumLosses")
                   ).select_by_value("0")
            Actions.find_Element(
                self.browser, "Question_05ProducerName").send_keys("No")
            Actions.find_Element(self.browser, "Question_06ProducerInspectionDt").send_keys(
                producer_inspection_date)
            Select(Actions.find_Element(self.browser, "Question_09Broker")
                   ).select_by_visible_text("No")

        # click the save button
        Actions.save(self.browser)
        Actions.waitPageLoad(self.browser)

        try:
            t = Actions.find_Element(
                self.browser, "MissingFieldError").is_displayed()
            if t:
                MultiLog.add_log(
                    f"Underwriting Questions Were not able to Complete because of Missing Field", logging.ERROR)
        except:
            MultiLog.add_log(
                f"Finishing Underwriting Questions without Errors", logging.INFO)
