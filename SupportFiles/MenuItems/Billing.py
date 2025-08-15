import logging
from selenium.webdriver.support.select import Select
from SupportFiles.MultiLog import MultiLog
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from SupportFiles.Actions import Actions


class Billing:
    browser = None
    pay_plan = None
    state_chosen = None

    def __init__(self, browser, pay_plan, state_chosen):
        self.browser = browser
        self.pay_plan = pay_plan
        self.state_chosen = state_chosen

    def run_billing(self):
        Actions.waitPageLoad(self.browser)
        Actions.find_Element(self.browser, "Wizard_Review").click()
        Actions.waitPageLoad(self.browser)
        state = self.state_chosen
        MultiLog.add_log(f"Pay Plan: {self.pay_plan}", logging.INFO)

        elements = self.browser.find_elements(By.NAME, "BasicPolicy.PayPlanCd")
        for e in elements:
            Actions.remove_javascript(self.browser)
            val1 = e.get_attribute("value")
            id_value = e.get_attribute("id")
            try:
                if val1.index(" "+state):
                    value = val1.index(" "+state)
                    val2 = val1[:value]
                    if (val2 == self.pay_plan):
                        script = f"document.getElementById(\"{id_value}\").checked = true"
                        try:
                            t = Actions.find_Element(
                                self.browser, id_value).is_displayed()
                            if t:
                                self.browser.execute_script(script)
                                break
                        except:
                            pass
                        break
            except:
                if (val1 == self.pay_plan):
                    script = f"document.getElementById(\"{id_value}\").checked = true"
                    try:
                        t = Actions.find_Element(
                            self.browser, id_value).is_displayed()
                        if t:
                            self.browser.execute_script(script)
                            break
                    except:
                        pass

        Actions.waitPageLoad(self.browser)

        if self.pay_plan.__contains__("Automated Monthly"):
            Select(Actions.find_Element(
                self.browser, "InstallmentSource.MethodCd")).select_by_value("ACH")
            self.waitPageLoad(self.browser)
            Select(Actions.find_Element(
                self.browser, "InstallmentSource.ACHStandardEntryClassCd")).select_by_value("PPD")
            Select(Actions.find_Element(
                self.browser, "InstallmentSource.ACHBankAccountTypeCd")).select_by_value("Checking")
            Actions.find_Element(
                self.browser, "InstallmentSource.ACHBankName").send_keys("Bank")
            Actions.find_Element(
                self.browser, "InstallmentSource.ACHBankAccountNumber").send_keys(123456789)
            Actions.find_Element(
                self.browser, "InstallmentSource.ACHRoutingNumber").send_keys("011000015")
            Actions.find_Element(
                self.browser, "BasicPolicy.PaymentDay").send_keys(15)
            Actions.find_Element(
                self.browser, "BasicPolicy.CheckedEFTForm").click()
        if self.pay_plan.__contains__("Bill To Other") or self.pay_plan.__contains__("Mortgagee"):
            Actions.find_Element(self.browser, "UWAINew").click()
            Actions.waitPageLoad(self.browser)
            if self.pay_plan.__contains__("Bill To Other"):
                Select(Actions.find_Element(self.browser, "AI.InterestTypeCd")
                       ).select_by_value("Bill To Other")
                Actions.waitPageLoad(self.browser)
            else:
                Select(Actions.find_Element(self.browser, "AI.InterestTypeCd")
                       ).select_by_value("First Mortgagee")
                Select(Actions.find_Element(self.browser, "AI.EscrowInd")
                       ).select_by_value("Yes")
                Select(Actions.find_Element(self.browser, "AI.BillMortgRnwlInd")
                       ).select_by_value("No")
            Actions.find_Element(
                self.browser, "AI.AccountNumber").send_keys(12345)
            Actions.check_for_value(self.browser, "AI.BTORnwlInd", "No")
            Actions.find_Element(
                self.browser, "AI.InterestName").send_keys("First Last")
            Actions.find_Element(self.browser, "AIMailingAddr.Addr1").send_keys(
                "1595 N Peach Ave")
            Actions.find_Element(
                self.browser, "AIMailingAddr.City").send_keys("Fresno")
            Select(Actions.find_Element(
                self.browser, "AIMailingAddr.StateProvCd")).select_by_value("CA")
            Actions.find_Element(
                self.browser, "AIMailingAddr.PostalCode").send_keys(93727)
            Select(Actions.find_Element(self.browser, "AIMailingAddr.RegionCd")
                   ).select_by_value("United States")

            try:
                Actions.find_Element(
                    self.browser, "LinkReferenceInclude_0").click()
            except:
                try:
                    Actions.find_Element(
                        self.browser, "LinkReferenceInclude_1").click()
                except:
                    pass

            Actions.waitPageLoad(self.browser)
            Actions.save(self.browser)

        Actions.waitPageLoad(self.browser)

        # click the save button
        Actions.save(self.browser)
        Actions.waitPageLoad(self.browser)
