import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from SupportFiles.MultiLog import MultiLog


class Actions:

    @staticmethod
    def save(browser):
        browser.execute_script('document.getElementById("Save").click();')
        Actions.remove_javascript(browser)

    @staticmethod
    def click_radio_button(browser, element):
        try:
            if (Actions.find_Element(browser, element).is_displayed()):
                Actions.find_Element(browser, element).click()
        except:
            return None

    @staticmethod
    def click_radio(browser):
        e_name = "QuoteCustomerClearingRef"
        table = browser.find_elements(By.NAME, e_name)
        radio_number = len(table)
        my_value = e_name+"_"+str(radio_number)
        Actions.click_radio_button(browser, my_value)

    def value_exists(browser, element_id):
        try:
            element1 = browser.find_elements(By.ID, element_id)
            if len(element1) > 0:
                return element1
        except:
            return None

    # *function for finding elements in the browser
    @staticmethod
    def find_Element(browser, browser_Element, id=By.ID):
        elem = browser.find_element(id, browser_Element)
        return elem

    # *Functions for finding or sending values to input fields

    @staticmethod
    def check_for_value(browser, element, value=None, visible_text: bool = False, keys=None):
        try:
            element1 = Actions.find_Element(browser, element)
            if element1.is_displayed():
                if (keys != None):
                    if (keys == "click"):
                        if visible_text:
                            Actions.find_Element(
                                browser, "Producer", id=By.LINK_TEXT).click()
                        else:
                            browser.execute_script(
                                'document.getElementById("'+element+'").click();')
                    elif keys == "index":
                        Select(element1).select_by_index(value)
                    else:
                        browser.execute_script(
                            'document.getElementById("'+element+'").value = ""')
                        element1.send_keys(keys)
                elif (visible_text):
                    Select(element1).select_by_visible_text(value)
                else:
                    Select(element1).select_by_value(value)
        except:
            MultiLog.add_log(f"Element Not Found with id {element} value:{
                             value} keys:{keys}", logging.DEBUG)

    # *Removes the errors on webpage
    @staticmethod
    def remove_javascript(browser):
        element_used = "js_error_list"
        script = """
            const parent = document.getElementById("js_error_list").parentNode;
            if(parent != null)
            {
            parent.delete();  
            }
        """

        try:
            t = Actions.find_Element(browser, element_used).is_displayed()
            if t:
                browser.execute_script(script)
        except:
            pass
        finally:
            pass

    # *function used for waiting for page to load after a button is clicked and the page has to refresh
    @staticmethod
    def waitPageLoad(browser):
        Actions.remove_javascript(browser)
        script = "return window.seleniumPageLoadOutstanding == 0;"
        WebDriverWait(browser, 60).until(
            lambda browser: browser.execute_script(script))
