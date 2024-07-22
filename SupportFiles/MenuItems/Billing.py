import logging
from selenium.webdriver.support.select import Select
from SupportFiles.MultiLog import MultiLog
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class Billing:

    # *function for finding elements in the browser

    def find_Element(self, browser, browser_Element, id=By.ID):
        elem = browser.find_element(id, browser_Element)
        return elem

    def save(self, browser):
        browser.execute_script('document.getElementById("Save").click();')
        self.remove_javascript(browser)

    def remove_javascript(self, browser):
        element_used = "js_error_list"
        script = """
            const parent = document.getElementById("js_error_list").parentNode;
            if(parent != null)
            {
            parent.delete();  
            }
        """

        try:
            t = self.find_Element(browser, element_used).is_displayed()
            if t:
                browser.execute_script(script)
        except:
            pass
        finally:
            pass

    def waitPageLoad(self, browser):
        self.remove_javascript(browser)
        script = "return window.seleniumPageLoadOutstanding == 0;"
        WebDriverWait(browser, 60).until(
            lambda browser: browser.execute_script(script))

    def __init__(self, browser, pay_plan, state_chosen):
        self.waitPageLoad(browser)
        self.find_Element(browser, "Wizard_Review").click()
        self.waitPageLoad(browser)
        state = state_chosen
        pay_plan = pay_plan
        MultiLog.add_log(f"Pay Plan: {pay_plan}", logging.INFO)

        elements = browser.find_elements(By.NAME, "BasicPolicy.PayPlanCd")
        for e in elements:
            self.remove_javascript(browser)
            val1 = e.get_attribute("value")
            id_value = e.get_attribute("id")
            try:
                if val1.index(" "+state):
                    value = val1.index(" "+state)
                    val2 = val1[:value]
                    if (val2 == pay_plan):
                        script = f"document.getElementById(\"{
                            id_value}\").checked = true"
                        try:
                            t = self.find_Element(
                                browser, id_value).is_displayed()
                            if t:
                                browser.execute_script(script)
                                break
                        except:
                            pass
                        break
            except:
                if (val1 == pay_plan):
                    script = f"document.getElementById(\"{
                        id_value}\").checked = true"
                    try:
                        t = self.find_Element(browser, id_value).is_displayed()
                        if t:
                            browser.execute_script(script)
                            break
                    except:
                        pass

        self.waitPageLoad(browser)

        if pay_plan.__contains__("Automated Monthly"):
            Select(self.find_Element(
                browser, "InstallmentSource.MethodCd")).select_by_value("ACH")
            self.waitPageLoad(browser)
            Select(self.find_Element(
                browser, "InstallmentSource.ACHStandardEntryClassCd")).select_by_value("PPD")
            Select(self.find_Element(
                browser, "InstallmentSource.ACHBankAccountTypeCd")).select_by_value("Checking")
            self.find_Element(
                browser, "InstallmentSource.ACHBankName").send_keys("Bank")
            self.find_Element(
                browser, "InstallmentSource.ACHBankAccountNumber").send_keys(123456789)
            self.find_Element(
                browser, "InstallmentSource.ACHRoutingNumber").send_keys("011000015")
            self.find_Element(browser, "BasicPolicy.PaymentDay").send_keys(15)
            self.find_Element(browser, "BasicPolicy.CheckedEFTForm").click()
        if pay_plan.__contains__("Bill To Other") or pay_plan.__contains__("Mortgagee"):
            self.find_Element(browser, "UWAINew").click()
            self.waitPageLoad(browser)
            if pay_plan.__contains__("Bill To Other"):
                Select(self.find_Element(browser, "AI.InterestTypeCd")
                       ).select_by_value("Bill To Other")
                self.waitPageLoad(browser)
            else:
                Select(self.find_Element(browser, "AI.InterestTypeCd")
                       ).select_by_value("First Mortgagee")
                Select(self.find_Element(browser, "AI.EscrowInd")
                       ).select_by_value("Yes")
                Select(self.find_Element(browser, "AI.BillMortgRnwlInd")
                       ).select_by_value("No")
            self.find_Element(browser, "AI.AccountNumber").send_keys(12345)
            self.check_for_value(browser, "AI.BTORnwlInd", "No")
            self.find_Element(
                browser, "AI.InterestName").send_keys("First Last")
            self.find_Element(browser, "AIMailingAddr.Addr1").send_keys(
                "1595 N Peach Ave")
            self.find_Element(
                browser, "AIMailingAddr.City").send_keys("Fresno")
            Select(self.find_Element(
                browser, "AIMailingAddr.StateProvCd")).select_by_value("CA")
            self.find_Element(
                browser, "AIMailingAddr.PostalCode").send_keys(93727)
            Select(self.find_Element(browser, "AIMailingAddr.RegionCd")
                   ).select_by_value("United States")

            try:
                self.find_Element(browser, "LinkReferenceInclude_0").click()
            except:
                try:
                    self.find_Element(
                        browser, "LinkReferenceInclude_1").click()
                except:
                    pass

            self.waitPageLoad(browser)
            self.save(browser)

        self.waitPageLoad(browser)

        # click the save button
        self.save(browser)
        self.waitPageLoad(browser)
