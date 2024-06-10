import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import threading
from datetime import datetime, timedelta
from SupportFiles.MultiLog import MultiLog
from SupportFiles.Address import Address
from SupportFiles.File import File
from SupportFiles.Timing import Timing

class Application:
    TEST = False
    COMPANY = "ADVR"

    #add variable for a logger here to be used within the Application Class
    app_logger = MultiLog()
    thread_name = str(threading.current_thread().name)

    line_of_business = None
    state_chosen = None
    date_chosen = None
    env_used = None
    producer_selected = None
    doc_types = ["Quote","Application","Policy"]
    create_type = doc_types[1]
    browser_chosen = None
    multiAdd = None
    number_of_addresses = 1
    pay_plan = None

    gw_environment ={"Local":"https://localhost:9443","QA":"https://qa-advr.iscs.com/","UAT3":"https://uat3-advr.in.guidewire.net/innovation?saml=off","UAT4":"https://uat4-advr.in.guidewire.net/innovation","QA2":"https://qa2-acx-advr.in.guidewire.net/innovation"}
    
    user_chosen = None
    verified = False
    payment_plan_most = {"Mortgagee Direct Bill Full Pay":"BasicPolicy.PayPlanCd_1","Automated Monthly":"BasicPolicy.PayPlanCd_2","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_3","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_5","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_6","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_7","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_8","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_9","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_10"}
    payment_plan_bop = {"Mortgagee Direct Bill Full Pay":"BasicPolicy.PayPlanCd_1","Automated Monthly":"BasicPolicy.PayPlanCd_2","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_3","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_5","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_6","Direct Bill 9 Pay":"BasicPolicy.PayPlanCd_7","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_8","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_9","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_10","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_11"}
    payment_plan_bop_wrong = {"Mortgagee Direct Bill Full Pay":"BasicPolicy.PayPlanCd_1","Automated Monthly":"BasicPolicy.PayPlanCd_2","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_3","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_5","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_6","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_7","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_8","Direct Bill 9 Pay":"BasicPolicy.PayPlanCd_9","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_10","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_11"}
    payment_plan_pumb = {"Automated Monthly":"BasicPolicy.PayPlanCd_1","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_2","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_3","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_5","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_6","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_7","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_8","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_9"}
    user_dict = {"AgentAdmin":"AgentAdmin","Admin":"Everything","Underwriter":"PolicyUnderwriter","Agent":"PolicyAgent"}

    #*function for finding elements in the browser
    
    def find_Element(self,browser,browser_Element, id = By.ID):
        elem = browser.find_element(id,browser_Element)
        return elem
    
    
    def delete_quote(self,browser):
        #delete created Quote
        self.find_Element(browser,"Delete").click()
        self.find_Element(browser,"dialogOK").click()
    
    #* This function is used to decide whether to use chrome or edge browser
    
    def load_page(self):
        self.app_logger.add_log(f"Browser Used: {self.browser_chosen}",logging.INFO)
        if(self.browser_chosen == "Chrome"):
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            browser = webdriver.Chrome(options = chrome_options)
        else:
            edge_options = webdriver.edge.options.Options()
            edge_options.add_experimental_option("detach", True)
            browser = webdriver.Edge(options = edge_options)
        browser.get(self.gw_environment[self.env_used])
    
        self.check_for_value(browser,"details-button",keys="click")    
        self.check_for_value(browser,"proceed-link",keys="click")    
        self.waitPageLoad(browser)

        assert "Guidewire InsuranceNow™ Login" in browser.title
        return browser

    
    def get_password(self,user):
        password = File.env_files_plus_users[self.env_used]["Users"]["Usernames"][user]
        return password

    #*function for login
    
    def login(self,browser,user = "admin",password = "Not9999!"):
        self.waitPageLoad(browser)
        self.find_Element(browser,"j_username").send_keys(user)
        self.find_Element(browser,"j_password").send_keys(password + Keys.RETURN)

    
    def save(self,browser):
        browser.execute_script('document.getElementById("Save").click();')
        self.remove_javascript(browser)

    
    def click_radio_button(self,browser,element):
        try:
            if(self.find_Element(browser,element).is_displayed()):
                self.find_Element(browser,element).click()
        except:
            pass

    
    def click_radio(self,browser):
        e_name = "QuoteCustomerClearingRef"
        table = browser.find_elements(By.NAME,e_name)
        radio_number = len(table)
        my_value = e_name+"_"+str(radio_number)
        self.click_radio_button(browser,my_value)

    
    def value_exists(self,browser,element_id):
        try:
            element1 = self.find_Element(browser,element_id)
            if element1.is_displayed():
                return element1
        except:
            return None

    #*Functions for finding or sending values to input fields
    
    def check_for_value(self,browser,element,value = None,visible_text:bool=False,keys=None):
        try:
            element1 = self.find_Element(browser,element)
            if element1.is_displayed():
                if(keys != None):
                    if(keys == "click"):
                        if visible_text:
                            self.find_Element(browser,"Producer",id=By.LINK_TEXT).click()
                        else:
                            browser.execute_script('document.getElementById("'+element+'").click();')
                    elif keys == "index":
                        Select(element1).select_by_index(value)
                    else:
                        browser.execute_script('document.getElementById("'+element+'").value = ""')
                        element1.send_keys(keys)
                elif(visible_text):
                    Select(element1).select_by_visible_text(value)
                else:
                    Select(element1).select_by_value(value)
        except:
            self.app_logger.add_log(f"Element Not Found with id {element} value:{value} keys:{keys}",logging.DEBUG)
    
    #*Removes the errors on webpage
    
    def remove_javascript(self,browser):
        element_used = "js_error_list"
        script = """
            const parent = document.getElementById("js_error_list").parentNode;
            if(parent != null)
            {
            parent.delete();  
            }
        """
        
        try:
            t = self.find_Element(browser,element_used).is_displayed()
            if t:
                browser.execute_script(script)
        except:
            pass
        finally:
            pass

    #*function used for waiting for page to load after a button is clicked and the page has to refresh
    
    def waitPageLoad(self,browser):
        self.remove_javascript(browser)
        script = "return window.seleniumPageLoadOutstanding == 0;"
        WebDriverWait(browser, 60).until(lambda browser:browser.execute_script(script)) 

    
    def run_verify_address(self,browser):
        script = "InsuredMailingAddr.verify();"
        lambda browser:browser.execute_script(script)

    
    def copy_to_property(self,browser,addr,city,state):
        self.find_Element(browser,"InsuredResidentAddr.Addr1").send_keys(addr)
        self.find_Element(browser,"InsuredResidentAddr.City").send_keys(city)
        Select(self.find_Element(browser,"InsuredResidentAddr.StateProvCd")).select_by_value(state)

    
    def copy_to_mailing(self,browser,addr,city,state):
        self.find_Element(browser,"InsuredMailingAddr.Addr1").send_keys(addr)
        self.find_Element(browser,"InsuredMailingAddr.City").send_keys(city)
        Select(self.find_Element(browser,"InsuredMailingAddr.StateProvCd")).select_by_value(state)

    
    def core_coverages(self,browser):
        
        core_coverages_time = Timing()
        core_coverages_time.start()
        coverage_a =  300000
        coverage_c = coverage_a
        self.app_logger.add_log(f"Starting Core Coverages",logging.INFO)
        
        core_values = ["Risk.ListOfTenantsAndOccupancy","Risk.BasementInd","Risk.BldgCentralHeatInd","Risk.CircuitBreakerProtInd","Risk.UndergradResidentInd",
                    "Risk.SpaceHeatersInd","Risk.FrameClearance15ftInd","Risk.ShortTermRent","Risk.MercantileOfficeOccupantsInd","Risk.ExcessLinesInd"]
        
        core_values_after = ["Risk.RoofUpdatedIn15YrsInd","Risk.AdequateSmokeDetInd","Risk.BldgOccGt75PctInd","Risk.EgressFromAllUnitsInd","Risk.MaintProgramInd"]

        browser.execute_script("document.getElementById('Wizard_Risks').click();")

        self.waitPageLoad(browser)
        self.check_for_value(browser,"Building.ConstructionCd","Frame")
        self.check_for_value(browser,"Building.YearBuilt",keys=2020)
        self.check_for_value(browser,"Building.OccupancyCd","Owner occupied dwelling")
        self.check_for_value(browser,"Building.Seasonal","No")
        self.check_for_value(browser,"Risk.TypeCd","DP2")
        self.check_for_value(browser,"Building.BuildingLimit",keys=300000)
        self.check_for_value(browser,"Building.StandardDed","500")
        self.check_for_value(browser,"Building.NumOfFamilies","1")
        self.check_for_value(browser,"Building.DistanceToHydrant","1000")
        self.check_for_value(browser,"Building.OccupancyCd","Primary Residence")
        self.check_for_value(browser,"Building.CovALimit",keys=coverage_a)
        self.check_for_value(browser,"Building.NumOfFamiliesSameFire","Less Than 5",False,None)
        self.check_for_value(browser,"Building.DistanceToHydrant","1000")
        self.check_for_value(browser,"Building.FuelLiability","300000")
        self.check_for_value(browser,"Building.OilTankLocation","none")
        self.check_for_value(browser,"Building.CovELimit","300000")
        self.check_for_value(browser,"Building.CovFLimit","2000")
        self.check_for_value(browser,"Building.CovFLimit","100000")
        self.check_for_value(browser,"Building.CovCLimit",keys=coverage_c)
        self.check_for_value(browser,"Building.StandardDed","1000")
        self.check_for_value(browser,"Building.NumOfFamilies","1")
        self.check_for_value(browser,"Building.DistanceToHydrant","1000")
        self.check_for_value(browser,"Building.TerritoryCd",keys="1")
        self.check_for_value(browser,"Risk.WorkersCompInd","100000")
        self.check_for_value(browser,"Risk.WorkersCompEmployees","none")
        self.check_for_value(browser,"Building.HurricaneMitigation","No Action")
                
        self.check_for_value(browser,"Building.BuildingClassDescription","75% or more Apartments")
        self.check_for_value(browser,"Building.BuildingClassDescription","67% or more Apartments")
        self.check_for_value(browser,"Building.DistanceToHydrant","1000")
        self.check_for_value(browser,"Building.ContentClassDescription","None - Building Owner only")
        self.check_for_value(browser,"Building.BuildingLimit",keys=900000)
        self.check_for_value(browser,"Building.DistanceToHydrant","1000")
        self.check_for_value(browser,"Risk.SqFtArea",keys=2000)
        self.check_for_value(browser,"Risk.PremisesAlarm","None",True)
        self.check_for_value(browser,"Risk.YrsInBusinessInd","1",True)
        self.check_for_value(browser,"Building.NumOfApartmentCondoBuilding",keys=5)
        self.check_for_value(browser,"Building.MaxNumOfAptCondoBetweenBrickWalls",keys=5)
        self.check_for_value(browser,"Building.NumOfStories",keys=5)
        self.check_for_value(browser,"Risk.ListOfTenantsAndOccupancy",keys="None")
        self.check_for_value(browser,"Risk.NumOfStories",keys=3)
        self.check_for_value(browser,"Building.ProtectionClass",keys=3)
        
        #if line_of_business == "Businessowners" or line_of_business == "Commercial Umbrella":
        for value in core_values:
            self.check_for_value(browser,value,"No",False)

        #save(browser)
        self.save(browser)
        self.waitPageLoad(browser)
        
        for value in core_values_after:
            self.check_for_value(browser,value,"No",False)

        try:
            t = self.find_Element(browser,"MissingFieldError").is_displayed()
            if t:
                self.app_logger.add_log(f"Core Coverages Was not able to Complete",logging.ERROR)
        except:
            self.app_logger.add_log(f"Finishing Core Coverages without Errors",logging.INFO)
            core_coverages_time.end()
            self.app_logger.add_log(f"Time to complete Core Coverages: {core_coverages_time.compute_time()} seconds",logging.INFO)

        #click the save button
        self.save(browser)
        

    
    def question_update(self,question,size):
        if(question.__contains__("1")):
            word = question.split("1")
            new_word =  word[0]+str(size)+word[1]
        return new_word

    #* Function to add underwriting questions for each location
    
    def gen_dwell_location_questions(self,browser,num):
        
        self.app_logger.add_log(f"Starting questions for Dwelling",logging.INFO)

        ques_dwell = ["Question_PolicyKnownPersonally","Question_PolicyOtherIns","Question_PolicyArson","Question_RiskNumber1PrevDisc","Question_RiskNumber1Vacant","Question_RiskNumber1OnlineHome"
                        ,"Question_RiskNumber1Isolated","Question_RiskNumber1Island","Question_RiskNumber1Seasonal","Question_RiskNumber1SolarPanels","Question_RiskNumber1Adjacent","Question_RiskNumber1ChildCare",
                        "Question_RiskNumber1OtherBusiness","Question_RiskNumber1Undergrad","Question_RiskNumber1DogsAnimals","Question_RiskNumber1Electrical","Question_RiskNumber1EdisonFuses","Question_RiskNumber1Stove",
                        "Question_RiskNumber1OilHeated","Question_RiskNumber1Pool","Question_RiskNumber1Trampoline","Question_RiskNumber1Outbuildings","Question_RiskNumber1InsDeclined","Question_MAFireRiskNumber1OtherFireInsuranceApp",
                        "Question_MAFireRiskNumber1OtherFireInsuranceActive","Question_MAFireRiskNumber1FireInPast","Question_MAFireRiskNumber1PropertyForSale","Question_MAFireRiskNumber1ApplicantMortgageeCrime",
                        "Question_MAFireRiskNumber1ShareholderTrusteeCrime","Question_MAFireRiskNumber1MortgagePaymentsDelinquent","Question_MAFireRiskNumber1RealEstateTaxesDelinquent","Question_MAFireRiskNumber1CodeViolations"]
        
        newDict = {1:ques_dwell}
        newArr = []

        self.gen_dewll_location_extra_questions(browser,1)
        if self.state_chosen == "RI":
            self.find_Element(browser,"Question_RiskNumber"+str(1)+"InspectorName").send_keys("No")

        if(num > 1):
            for loc in range(num-1):
                number = loc+2
                for question_name in ques_dwell:    
                    if(question_name.__contains__("1")):
                        word = question_name.split("1")
                        newArr.append(word[0]+str(number)+word[1])
                newDict[number] = newArr
                if self.state_chosen == "RI":                                                                  
                    self.find_Element(browser,"Question_RiskNumber"+str(number)+"InspectorName").send_keys("No")
                self.gen_dewll_location_extra_questions(browser,number)
                
        return newDict

    
    def gen_dewll_location_extra_questions(self,browser,num):
        extra_dwell_questions = ["Question_RiskNumber1Lapse","Question_RiskNumber1NumClaims","Question_MAFireRiskNumber1PurchaseDate","Question_MAFireRiskNumber1PurchasePrice","Question_MAFireRiskNumber1EstimatedValue","Question_MAFireRiskNumber1ValuationMethod","Question_MAFireRiskNumber1AppraisalMethod"]
        updatedArr = []

        if(num >1):
            for question in extra_dwell_questions:
                updatedArr.append(self.question_update(question,num))
        else:
            updatedArr = extra_dwell_questions
        Select(self.find_Element(browser,updatedArr[0])).select_by_value("No-New purchase")
        self.find_Element(browser,updatedArr[1]).send_keys(0)
        if(self.state_chosen == 'MA'):
            self.find_Element(browser,updatedArr[2]).send_keys("01/01/2022")
            self.find_Element(browser,updatedArr[3]).send_keys("100000")
            self.find_Element(browser,updatedArr[4]).send_keys("150000")
            Select(self.find_Element(browser,updatedArr[5])).select_by_value("Replacement Cost")
            Select(self.find_Element(browser,updatedArr[6])).select_by_value("Professional Appraisal")

    
    def underwriting_questions(self,browser,multi):
        
        y = datetime.today()+timedelta(days=60)
        producer_inspection_date = y.strftime("%m/%d/%Y")
        self.find_Element(browser,"Wizard_Underwriting").click()
        self.app_logger.add_log(f"Starting Underwriting Questions for {self.state_chosen} {self.line_of_business}",logging.INFO)
        self.waitPageLoad(browser)
        lob = self.line_of_business

        questions_home = ["Question_PermanentFoundation","Question_IslandProperty","Question_IsolatedProperty","Question_IslandHome","Question_PrevKnown",
                    "Question_PrevDiscussed","Question_OtherInsurance","Question_VacantOrOccupied", "Question_OnlineHome", "Question_OnlineHome",
                    "Question_SeasonalHome", "Question_FrameDwellings", "Question_DayCareOnPremises", "Question_UndergraduateStudents","Question_SolarPanels","Question_UndergraduateStudents",
                    "Question_DogsCare", "Question_ElectricalService", "Question_WiringInUse", "Question_StoveOnPremises", "Question_OilHeated", "Question_PoolOnPremises",
                    "Question_TrampolineOnPremises","Question_AnyOutbuildings","Question_CancelledRecently","Question_ArsonConvicted"]

        if self.line_of_business =="Dwelling Property":
            if multi:
                dwell_questions = self.gen_dwell_location_questions(browser,self.number_of_addresses)
            else:
                dwell_questions = self.gen_dwell_location_questions(browser,1)

        if self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella":
            self.check_for_value(browser,"Question_InspectorName",keys="Gadget")

            for question in questions_home:
                self.check_for_value(browser,question,"No",True)
            self.check_for_value(browser,"Question_AnyLapsePast","No-New Purchase",True)
            self.check_for_value(browser,"Question_ClaimsRecently",keys=0)
            self.check_for_value(browser,"Question_PurchasePrice",keys=500000)

        if(lob == "Dwelling Property"):
            for key in range(len(dwell_questions.keys())):
                for question in dwell_questions[key+1]:
                    self.check_for_value(browser,question,"No",True)

        if(lob == "Businessowners" or lob == "Commercial Umbrella"):
            Select(self.find_Element(browser,"Question_01CoverageCancellation")).select_by_visible_text("No")
            self.find_Element(browser,"Question_03PreviousCarrierPropertyLimitsPremium").send_keys("No")
            Select(self.find_Element(browser,"Question_08NumLosses")).select_by_value("0")
            self.find_Element(browser,"Question_05ProducerName").send_keys("No")
            self.find_Element(browser,"Question_06ProducerInspectionDt").send_keys(producer_inspection_date)
            Select(self.find_Element(browser,"Question_09Broker")).select_by_visible_text("No")
                
        #click the save button
        self.save(browser)
        self.waitPageLoad(browser)

        try:
            t = self.find_Element(browser,"MissingFieldError").is_displayed()
            if t:
                self.app_logger.add_log(f"Underwriting Questions Were not able to Complete because of Missing Field",logging.ERROR)
        except:
            self.app_logger.add_log(f"Finishing Underwriting Questions without Errors",logging.INFO)

    
    def billing(self,browser):
        self.waitPageLoad(browser)
        self.find_Element(browser,"Wizard_Review").click()
        self.waitPageLoad(browser)
        state = self.state_chosen
        pay_plan = self.pay_plan
        self.app_logger.add_log(f"Pay Plan: {pay_plan}",logging.INFO)

        elements = browser.find_elements(By.NAME,"BasicPolicy.PayPlanCd")
        for e in elements:
            self.remove_javascript(browser)
            val1 = e.get_attribute("value")
            id_value = e.get_attribute("id")
            try: 
                if val1.index(" "+state):
                    value = val1.index(" "+state)
                    val2 = val1[:value]
                    if(val2 == pay_plan):
                        script = f"document.getElementById(\"{id_value}\").checked = true"
                        try:
                            t = self.find_Element(browser,id_value).is_displayed()
                            if t:
                                browser.execute_script(script)
                                break
                        except:
                            pass
                        break
            except:
                if(val1 == pay_plan):
                    script = f"document.getElementById(\"{id_value}\").checked = true"
                    try:
                        t = self.find_Element(browser,id_value).is_displayed()
                        if t:
                            browser.execute_script(script)
                            break
                    except:
                        pass
                
        self.waitPageLoad(browser)

        if pay_plan.__contains__("Automated Monthly"):
            Select(self.find_Element(browser,"InstallmentSource.MethodCd")).select_by_value("ACH")
            self.waitPageLoad(browser)
            Select(self.find_Element(browser,"InstallmentSource.ACHStandardEntryClassCd")).select_by_value("PPD")
            Select(self.find_Element(browser,"InstallmentSource.ACHBankAccountTypeCd")).select_by_value("Checking")
            self.find_Element(browser,"InstallmentSource.ACHBankName").send_keys("Bank")
            self.find_Element(browser,"InstallmentSource.ACHBankAccountNumber").send_keys(123456789)
            self.find_Element(browser,"InstallmentSource.ACHRoutingNumber").send_keys("011000015")
            self.find_Element(browser,"BasicPolicy.PaymentDay").send_keys(15)
            self.find_Element(browser,"BasicPolicy.CheckedEFTForm").click()
        if pay_plan.__contains__("Bill To Other") or pay_plan.__contains__("Mortgagee"):
            self.find_Element(browser,"UWAINew").click()
            self.waitPageLoad(browser)
            if pay_plan.__contains__("Bill To Other"):
                Select(self.find_Element(browser,"AI.InterestTypeCd")).select_by_value("Bill To Other")
                self.waitPageLoad(browser)
            else:
                Select(self.find_Element(browser,"AI.InterestTypeCd")).select_by_value("First Mortgagee")
                Select(self.find_Element(browser,"AI.EscrowInd")).select_by_value("Yes")
                Select(self.find_Element(browser,"AI.BillMortgRnwlInd")).select_by_value("No")
            self.find_Element(browser,"AI.AccountNumber").send_keys(12345)
            self.check_for_value(browser,"AI.BTORnwlInd","No")
            self.find_Element(browser,"AI.InterestName").send_keys("First Last")
            self.find_Element(browser,"AIMailingAddr.Addr1").send_keys("1595 N Peach Ave")
            self.find_Element(browser,"AIMailingAddr.City").send_keys("Fresno")
            Select(self.find_Element(browser,"AIMailingAddr.StateProvCd")).select_by_value("CA")
            self.find_Element(browser,"AIMailingAddr.PostalCode").send_keys(93727)
            Select(self.find_Element(browser,"AIMailingAddr.RegionCd")).select_by_value("United States")

            try:
                self.find_Element(browser,"LinkReferenceInclude_0").click()
            except:
                try: 
                    self.find_Element(browser,"LinkReferenceInclude_1").click()
                except:
                    pass

            self.waitPageLoad(browser)
            self.save(browser)

        self.waitPageLoad(browser)

        #click the save button
        self.save(browser)
        self.waitPageLoad(browser)

    #Start application creation
    
    def startApplication(self,multiAdd,subType,carrier):
        user_chosen = self.user_chosen
        create_type = self.create_type
        state_chosen = self.state_chosen
        line_of_business = self.line_of_business
        env_used = self.env_used
        date_chosen = self.date_chosen
        producer_selected = self.producer_selected

        

        if MultiLog.log_data:
            self.app_logger.createLog(self.state_chosen,self.line_of_business,self.thread_name)

        CARRIER = {"Merrimack Mutual Fire Insurance":"MMFI","Cambrige Mutual Fire Insurance":"CMFI","Bay State Insurance Company":"BSIC"}
        password = self.get_password(user_chosen)

        if line_of_business == "Homeowners" or line_of_business == "Personal Umbrella":
            self.app_logger.add_log(f"Started {create_type} for {state_chosen} {line_of_business}. Carrier: {carrier} | Subtype: {subType} | in {env_used} Environment with {user_chosen} user where date = {date_chosen}",logging.INFO)
        else:
            self.app_logger.add_log(f"Started {create_type} for {state_chosen} {line_of_business} in {env_used} Environment with {user_chosen} user where date = {date_chosen}",logging.INFO)

        browser = self.load_page()
        
        try:
            self.login(browser,user_chosen,password)
        except:
            raise Exception("Incorrect username and/or password")

        #*Tab to click  for recent quotes, applications, and policies
        self.find_Element(browser,"Tab_Recent").click()
        state1,CITY,ADDRESS = Address.addresses[str(state_chosen+"1")]
        custom_city = Address.custom_address["City"]
        custom_add = Address.custom_address["Address"]
        first_name = state_chosen + " " + line_of_business
        last_name = "Automation"

        if Address.custom_address["Flag"]:
            self.create_new_quote(browser,date_chosen,state1,producer_selected,first_name,last_name,custom_add,custom_city,multiAdd,self.TEST, subType,CARRIER[carrier])
        else:
            self.create_new_quote(browser,date_chosen,state1,producer_selected,first_name,last_name,ADDRESS,CITY,multiAdd,self.TEST,subType,CARRIER[carrier])

        if self.TEST:
            sleep(5)
            browser.quit()

    
    def submit_policy(self,browser):
        self.find_Element(browser,"Closeout").click()
        self.waitPageLoad(browser)
        Select(self.find_Element(browser,"TransactionInfo.PaymentTypeCd")).select_by_value("None")
        self.find_Element(browser,"TransactionInfo.SignatureDocument").click()
        self.find_Element(browser,"Printself").click()
        sleep(30)
        self.find_Element(browser,"Process").click()
        self.waitPageLoad(browser)

    
    def create_new_quote(self,browser,date,state:str,producer:str,first_name:str,last_name:str,address:str,city:str,multiLoc:bool,test:bool,subType:str,carrier:str):
        
        #New Quote
        self.find_Element(browser,"QuickAction_NewQuote_Holder").click()
        self.find_Element(browser,"QuickAction_EffectiveDt").send_keys(date)

        self.waitPageLoad(browser)
        #State Select
        browser.execute_script("document.getElementById('QuickAction_StateCd').value = '"+state+"';")
        self.check_for_value(browser,"QuickAction_CarrierGroupCd",self.COMPANY)

        browser.execute_script("document.getElementById('QuickAction_NewQuote').click()")

        if self.line_of_business == "Personal Umbrella":
            self.find_Element(browser,"Homeowners",By.LINK_TEXT).click()
        elif self.line_of_business == "Commercial Umbrella":
            self.find_Element(browser,"Businessowners",By.LINK_TEXT).click()
        else:
            self.find_Element(browser,self.line_of_business,By.LINK_TEXT).click()

        #enter producer here
        self.check_for_value(browser,"ProviderNumber",keys=producer)
        
        #select entity type
        if(self.line_of_business == "Dwelling Property" or self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella"):
            Select(self.find_Element(browser,"Insured.EntityTypeCd")).select_by_value("Individual")
        
        self.waitPageLoad(browser)

        quote_num = self.find_Element(browser,"QuoteAppSummary_QuoteAppNumber")
        self.app_logger.add_log(f" ",logging.INFO)
        self.app_logger.add_log(f" ------------ QUOTE STARTED ---------------- ",logging.INFO)
        self.app_logger.add_log(f"Quote Number: {quote_num.text}",logging.INFO)

        self.check_for_value(browser,"InsuredPersonal.OccupationClassCd","Other")
        self.check_for_value(browser,"InsuredPersonal.OccupationOtherDesc",keys="No")

        if self.state_chosen == "NY" and (self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella"):
            Select(self.find_Element(browser,"BasicPolicy.GeographicTerritory")).select_by_value("Upstate")

        browser.execute_script('document.getElementById("InsuredName.GivenName").value = "' + first_name + '"')
        browser.execute_script('document.getElementById("InsuredName.Surname").value = "' + last_name + '"')

        self.check_for_value(browser,"InsuredNameJoint.GivenName",keys="click")
        self.check_for_value(browser,"InsuredNameJoint.GivenName",keys="Second")
        self.check_for_value(browser,"InsuredNameJoint.Surname",keys="Person")
        self.waitPageLoad(browser)
        self.check_for_value(browser,"InsuredNameJoint.GivenName",keys="Second")
        self.check_for_value(browser,"InsuredNameJoint.Surname",keys="Person")
        self.check_for_value(browser,"InsuredPersonalJoint.BirthDt",keys="01/01/1980")
        self.check_for_value(browser,"InsuredPersonalJoint.OccupationClassCd","Other")
        self.check_for_value(browser,"InsuredPersonalJoint.OccupationOtherJointDesc",keys="No")

        if (self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella") and subType:
            self.check_for_value(browser,"BasicPolicy.DisplaySubTypeCd",subType)
            if self.state_chosen == "NY":
                Select(self.find_Element(browser,"BasicPolicy.DisplaySubTypeCd")).select_by_index(1)
        
        
        if self.line_of_business != "Businessowners" and self.line_of_business != "Commercial Umbrella":
            self.find_Element(browser,"InsuredPersonal.BirthDt").send_keys("01/01/1980")
            self.find_Element(browser,"InsuredCurrentAddr.Addr1").send_keys(address)
            self.find_Element(browser,"InsuredCurrentAddr.City").send_keys(city)
            Select(self.find_Element(browser,"InsuredCurrentAddr.StateProvCd")).select_by_value(state)

        #*Select state here
        if(self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella"): 
            self.find_Element(browser,"InsuredMailingAddr.Addr1").send_keys(address)
            self.find_Element(browser,"InsuredMailingAddr.City").send_keys(city)
            Select(self.find_Element(browser,"InsuredMailingAddr.StateProvCd")).select_by_value(state)

        #*Adding geographic territory and policy carrier here
        if(self.state_chosen == "NY" and (self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella")):
            Select(self.find_Element(browser,"BasicPolicy.GeographicTerritory")).select_by_value("Metro")

        self.waitPageLoad(browser)
        if self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella":
            self.find_Element(browser,"DefaultAddress").click()

        if self.line_of_business != "Businessowners" and self.line_of_business != "Commercial Umbrella":
            self.copy_to_property(browser,address,city,state)
            self.copy_to_mailing(browser,address,city,state)
            self.waitPageLoad(browser)

        #*First and Last names copied to input fields here
        self.find_Element(browser,"InsuredName.MailtoName").send_keys(f"{first_name} {last_name}")
        self.find_Element(browser,"Insured.InspectionContact").send_keys(f"{first_name} {last_name}")

        #*Phone Type, Phone number, and email entered here
        Select(self.find_Element(browser,"InsuredPhonePrimary.PhoneName")).select_by_value("Mobile")
        self.find_Element(browser,"InsuredPhonePrimary.PhoneNumber").send_keys(5558675309)
        self.check_for_value(browser,"Insured.InspectionContactPhoneType","Mobile")
        self.check_for_value(browser,"Insured.InspectionContactNumber",keys=5558675309)
        self.find_Element(browser,"InsuredEmail.EmailAddr").send_keys("test@mail.com")
        self.waitPageLoad(browser)

        #Set insurance score if available
        self.check_for_value(browser,"InsuredInsuranceScore.OverriddenInsuranceScore",keys="999")

        #*click the save button
        self.save(browser)
        self.waitPageLoad(browser)

        #Select the second policy carrier
        self.check_for_value(browser,"BasicPolicy.PolicyCarrierCd",carrier)

        #multiple locations here
        if self.line_of_business != "Businessowners" and self.line_of_business != "Commercial Umbrella":
            
            self.core_coverages(browser)
            if(multiLoc and self.line_of_business == "Dwelling Property"):
                for i in range(self.number_of_addresses-1):
                    self.find_Element(browser,"CopyRisk").click()
                    self.save(browser)

        if(self.create_type == "Application" or self.create_type == "Policy"):
            self.waitPageLoad(browser)
            self.check_for_value(browser,"Wizard_Policy",keys="click")
            self.waitPageLoad(browser)
            self.click_radio(browser)
            self.waitPageLoad(browser)
            self.find_Element(browser,"Bind").click()
            
            if self.line_of_business == "Businessowners" or self.line_of_business == "Commercial Umbrella":
                self.core_coverages(browser)
        
            self.waitPageLoad(browser)
            if(self.state_chosen == "NJ" and (self.line_of_business == "Homeowners" or self.line_of_business == "Personal Umbrella")):
                self.find_Element(browser,"Wizard_Risks").click()
                self.waitPageLoad(browser)
                self.check_for_value(browser,"Building.Inspecti onSurveyReqInd","No")

                #click the save button
                self.save(browser)
            
            application_num = self.find_Element(browser,"QuoteAppSummary_QuoteAppNumber")
            self.app_logger.add_log(f" ",logging.INFO)
            self.app_logger.add_log(f" ------------ APPLICATION STARTED ---------------- ",logging.INFO)
            self.app_logger.add_log(f"Application Number: {application_num.text}",logging.INFO)

            #Creating a Timing Object for Underwriting questions
            underwriting_time = Timing()
            underwriting_time.start()
            self.underwriting_questions(browser,multiLoc)
            underwriting_time.end()

            self.app_logger.add_log(f"Time to Complete Underwriting Questions: {underwriting_time.compute_time()} seconds",logging.INFO)
            
            self.billing(browser)

            if self.line_of_business == "Personal Umbrella":
                self.find_Element(browser,"GetUmbrellaQuote").click()
                self.waitPageLoad(browser)
                self.find_Element(browser,"Wizard_UmbrellaLiability").click()
                Select(self.find_Element(browser,"Line.PersonalLiabilityLimit")).select_by_value("1000000")
                self.find_Element(browser,"Line.TotMotOwnLeasBus").send_keys(0)
                self.find_Element(browser,"Line.NumMotExcUmb").send_keys(0)
                self.find_Element(browser,"Line.NumHouseAutoRec").send_keys(0)
                self.find_Element(browser,"Line.NumOfYouthInexp").send_keys(0)
                if self.state_chosen == "NH":
                    Select(self.find_Element(browser,"Line.RejectExcessUninsuredMotorists")).select_by_value("No")
                    Select(self.find_Element(browser,"Line.UnderAutLiabPerOcc")).select_by_value("No")
                if self.state_chosen == "NJ" or self.state_chosen == "NY" or self.state_chosen == "RI" or self.state_chosen == "CT" or self.state_chosen == "IL" or self.state_chosen == "ME" or self.state_chosen == "MA":
                    Select(self.find_Element(browser,"Line.UnderAutLiabPerOcc")).select_by_value("No")
                self.find_Element(browser,"Bind").click()
                self.find_Element(browser,"Wizard_Underwriting").click()
                Select(self.find_Element(browser,"Question_DiscussedWithUnderwriter")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_DUIConvicted")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_ConvictedTraffic")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_WatercraftBusiness")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_DayCarePremises")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_UndergraduateStudents")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_AnimalsCustody")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_PoolPremises")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_TrampolinePremises")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_CancelledRecently")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_BusinessPolicies")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_OnlineHome")).select_by_value("NO")
                self.save(browser)
                self.find_Element(browser,"Wizard_Review").click()
                self.billing(browser)
                self.waitPageLoad(browser)
                self.save(browser)

                if self.create_type == "Policy":
                    self.find_Element(browser,"Return").click()
                    self.find_Element(browser,"policyLink0").click()
                    self.submit_policy(browser)
                    self.find_Element(browser,"Return").click()
                    self.find_Element(browser,"policyLink0").click()
                    self.billing(browser)
            
            if self.line_of_business == "Commercial Umbrella":
                self.find_Element(browser,"GetUmbrellaQuote").click()
                self.waitPageLoad(browser)
                self.find_Element(browser,"Wizard_UmbrellaLiability").click()
                if self.state_chosen == "CT" or self.state_chosen == "NH" or self.state_chosen=="NY" or self.state_chosen == "RI":
                    Select(self.find_Element(browser,"Line.CoverageTypeCd")).select_by_value("Businessowners Umbrella Liability")
                Select(self.find_Element(browser,"Line.CommercialLiabilityLimit")).select_by_value("1000000")
                Select(self.find_Element(browser,"Line.OwnedAutosInd")).select_by_value("No")
                Select(self.find_Element(browser,"Line.EmplLiabCovrInsured")).select_by_value("No")
                self.find_Element(browser,"Wizard_Policy").click()
                self.find_Element(browser,"Bind").click()
                self.find_Element(browser,"Wizard_Underwriting").click()
                Select(self.find_Element(browser,"Question_OtherLiab")).select_by_value("NO")
                Select(self.find_Element(browser,"Question_PriorCovCancelled")).select_by_value("NO")
                self.find_Element(browser,"Question_PreviousUmbrella").send_keys("ACME")
                self.save(browser)
                self.find_Element(browser,"Wizard_Review").click()
                self.billing(browser)
                self.find_Element(browser,"Navigate_Location_2").click()
                Select(self.find_Element(browser,"Location.UnderlyingEmplLimitConf")).select_by_value("Yes")
                self.find_Element(browser,"NextPage").click()
            
                if self.create_type == "Policy":
                    self.find_Element(browser,"Return").click()
                    self.find_Element(browser,"policyLink0").click()
                    self.submit_policy(browser)
                    self.find_Element(browser,"Return").click()
                    self.find_Element(browser,"policyLink0").click()
                    if self.pay_plan.__contains__("Bill To Other"):
                        self.billing(browser)
        
        self.check_for_value(browser,"Wizard_Policy",keys="click")
        warning_value = self.value_exists(browser,"WarningIssues")
        error_value = self.value_exists(browser,"ErrorIssues")
        if warning_value is not None:
            self.app_logger.add_log(f"Issues: {warning_value.text}",logging.WARNING)
        if error_value is not None:
            self.app_logger.add_log(f"Issues: {error_value.text}",logging.ERROR)

        if(self.create_type == "Policy" and error_value is None):
            self.submit_policy(browser)

            policy_num = self.find_Element(browser,"PolicySummary_PolicyNumber")
            self.app_logger.add_log(f" ",logging.INFO)
            self.app_logger.add_log(f" ------------ Policy STARTED ---------------- ",logging.INFO)
            self.app_logger.add_log(f"Policy Number: {policy_num.text}",logging.INFO)

        elif(error_value is not None):
            self.app_logger.add_log(f"Application Could not be submitted due to {error_value.text}",logging.ERROR)

        sleep(5)

        if(test and self.create_type != "Policy"):
            self.delete_quote(browser)

    
    def get_created_application(self,applicaiton_number:str):
        pass

    #Create a producer
    
    def create_producer(self,producerName,user_name):
        agency_name = "All_States_All_LOB"
        agent_name = None
        prod_name = None
        y = datetime.today()
        default_date = y.strftime("%m/%d/%Y").split("/")
        password = self.get_password(user_name)
        states = ["CT","IL","MA","ME","NH","NJ","NY","RI"]
        LOB = ["PUL","HO","DP","BOP-UMB","BOP"]
        prod_values = File.env_files_plus_users[self.env_used]['Producers']['ProducerNames']

        browser = self.load_page()

        try:
            self.login(browser,user_name,password)
        except ValueError:
            #logger.error(f"Username or Password is not correct. username: {user_name} password: {password}")
            sleep(5)
            browser.quit()
            raise Exception("Incorrect username and/or password")
        self.waitPageLoad(browser)    

        #################### Searching for a Producer #########################
        browser.execute_script('document.getElementById("Menu_Policy").click();')
        browser.execute_script('document.getElementById("Menu_Policy_UnderwritingMaintenance").click();')

        self.find_Element(browser,"Producer",id=By.LINK_TEXT).click()
        self.check_for_value(browser,"SearchText",keys=producerName)
        self.check_for_value(browser,"SearchBy","ProviderNumber")
        self.check_for_value(browser,"SearchFor","Producer")
        self.check_for_value(browser,"SearchOperator","=")
        self.check_for_value(browser,"Search",keys = "click")
        self.waitPageLoad(browser)

        try:
            prod_name = self.find_Element(browser,"//div[id='Agency/Producer List']/*/*/tr[2]/td[2]",By.XPATH)
        except:
            pass

        #################### Searching for an Agency #########################
        self.check_for_value(browser,"SearchText",keys=agency_name)
        self.check_for_value(browser,"SearchBy","ProviderNumber")
        self.check_for_value(browser,"SearchFor","Agency")
        self.check_for_value(browser,"SearchOperator","=")
        self.check_for_value(browser,"Search",keys = "click")
        self.waitPageLoad(browser)

        try:
            agent_name = self.find_Element(browser,"//div[id='Agency/Producer List']/*/*/tr[2]/td[2]",By.XPATH)

        except:
            pass

        try: 
            if prod_name is not None:
                if producerName not in prod_values:
                    File.add_producer(producerName)
                script = "alert('Producer Already Exists')"
                browser.execute_script(script)
                sleep(5)
                browser.quit()
                return False
        except:
            pass
        
        if agent_name is None:
            ################ Create Agency #################################
            self.check_for_value(browser,"NewProducer",keys="click")
            self.check_for_value(browser,"Provider.ProviderNumber",keys=agency_name)
            self.check_for_value(browser,"ProducerTypeCd",value="Agency")
            self.check_for_value(browser,"Provider.StatusDt",keys=default_date)
            self.check_for_value(browser,"AppointedDt",keys="01/01/1900")
            self.check_for_value(browser,"CombinedGroup",value="No")
            self.check_for_value(browser,"ProviderName.CommercialName",keys="The White House")
            self.check_for_value(browser,"ProviderStreetAddr.Addr1",keys="1600 Pennsylvania Ave NW")
            self.check_for_value(browser,"ProviderStreetAddr.City",keys="Washington")
            self.check_for_value(browser,"ProviderStreetAddr.StateProvCd",value="DC")
            self.waitPageLoad(browser)
            self.check_for_value(browser,"CopyAddress",keys="click")
            self.waitPageLoad(browser)
            self.check_for_value(browser,"ProviderEmail.EmailAddr",keys="testmail.com")
            self.check_for_value(browser,"AcctName.CommercialName",keys="White House")
            self.check_for_value(browser,"PayToCd",value="Agency")
            self.check_for_value(browser,"Provider.CombinePaymentInd",value="No")
            self.check_for_value(browser,"Provider.PaymentPreferenceCd",value="Check")
            self.check_for_value(browser,"CopyBillingAddress",keys="click")
            self.waitPageLoad(browser)
            self.save(browser)
            self.check_for_value(browser,"Return",keys="click")
            self.waitPageLoad(browser)

        self.check_for_value(browser,"NewProducer",keys="click")
        self.check_for_value(browser,"Provider.ProviderNumber",keys=producerName)
        self.check_for_value(browser,"ProducerTypeCd",value="Producer")
        self.check_for_value(browser,"ProducerAgency",keys=agency_name)
        self.check_for_value(browser,"Provider.StatusDt",keys=default_date)
        self.check_for_value(browser,"AppointedDt",keys="01/01/1900")
        self.check_for_value(browser,"CombinedGroup",value="No")
        self.check_for_value(browser,"ProviderName.CommercialName",keys="Starbucks")
        self.check_for_value(browser,"ProviderStreetAddr.Addr1",keys="43 Crossing Way")
        self.check_for_value(browser,"ProviderStreetAddr.City",keys="Augusta")
        self.check_for_value(browser,"ProviderStreetAddr.StateProvCd",value="ME")
        self.waitPageLoad(browser)
        self.check_for_value(browser,"CopyAddress",keys="click")
        self.waitPageLoad(browser)
        self.check_for_value(browser,"ProviderEmail.EmailAddr",keys="testmail.com")
        self.check_for_value(browser,"AcctName.CommercialName",keys="White House")
        self.check_for_value(browser,"PayToCd",value="Agency")
        self.check_for_value(browser,"Provider.CombinePaymentInd",value="No")
        self.check_for_value(browser,"Provider.PaymentPreferenceCd",value="Check")
        self.check_for_value(browser,"CopyBillingAddress",keys="click")
        self.waitPageLoad(browser)
        self.save(browser)
        self.waitPageLoad(browser)
        self.check_for_value(browser,"IvansCommissionInd",value="No")

        #########################  Add States ############################

        for state in states:
            self.check_for_value(browser,"AddState",keys="click")
            self.check_for_value(browser,"StateInfo.StateCd",value=state)
            self.check_for_value(browser,"StateInfo.AppointedDt",keys="01/01/1900")
            self.check_for_value(browser,"StateInfo.MerrimackAppointedDt",keys="01/01/1900")
            self.check_for_value(browser,"StateInfo.CambridgeAppointedDt",keys="01/01/1900")
            self.check_for_value(browser,"StateInfo.BayStateAppointedDt",keys="01/01/1900")
            self.check_for_value(browser,"StateInfo.MerrimackLicensedDt",keys="01/01/2999")
            self.check_for_value(browser,"StateInfo.CambridgeLicensedDt",keys="01/01/2999")
            self.check_for_value(browser,"StateInfo.BayStateLicensedDt",keys="01/01/2999")
            self.save(browser)
            self.waitPageLoad(browser)

        ############################ Add Products ################################

        for state in states:
            for bus in LOB:
                self.check_for_value(browser,"AddProduct",keys="click")
                self.check_for_value(browser,"LicensedProduct.LicenseClassCd",value=bus)
                self.check_for_value(browser,"LicensedProduct.StateProvCd",value=state)
                self.check_for_value(browser,"LicensedProduct.EffectiveDt",keys="01/01/1900")
                self.check_for_value(browser,"LicensedProduct.CommissionNewPct",keys="5")
                self.check_for_value(browser,"LicensedProduct.CommissionRenewalPct",keys="5")
                self.save(browser)
                self.waitPageLoad(browser)
        self.check_for_value(browser,"IvansCommissionInd",value="No")
        self.check_for_value(browser,"FCRAEmail.EmailAddr",keys="test2mail.com")
        self.save(browser)

        script = "alert(\"Producer Created Successfully!\")"
        browser.execute_script(script)
        sleep(5)
        browser.quit()

        if producerName not in prod_values:
            File.add_producer(producerName)


    #Create a user
    
    def create_user(self,user_type,user_name):
        user_dict = self.user_dict
        y = datetime.today()
        default_date = y.strftime("%m/%d/%Y").split("/")
        password = self.get_password(user_name)
        user_xpath = "//div[id='System User List']/div[2]/*/*/tr[2]/td[1]/a"
        new_user_password = "pass"
        user_values = File.env_files_plus_users[self.env_used]['Users']['Usernames'].keys()
        user_searched_name = None
        browser = self.load_page()

        try:
            self.login(browser,user_name,password)
        except ValueError:
            sleep(5)
            browser.quit()
            raise Exception("Incorrect username and/or password")
        self.waitPageLoad(browser)    

        browser.execute_script('document.getElementById("Menu_Admin").click();')
        browser.execute_script('document.getElementById("Menu_Admin_UserManagement").click();')

        #################### Searching for a User #########################
        self.check_for_value(browser,"SearchText",keys=user_type)
        self.check_for_value(browser,"MatchType","=")
        self.check_for_value(browser,"Search",keys="click")

        try:
            user_searched_name = self.find_Element(browser,user_xpath,By.XPATH)
        except:
            pass

        try: 
            if user_searched_name is not None:
                if user_dict not in list(user_values):
                    File.add_user(user_type,new_user_password)
                script = "alert(\"User Already Exists\")"
                browser.execute_script(script)
                sleep(5)
                browser.quit()
                return False
        except:
            pass

        self.check_for_value(browser,"AddUser",keys="click") 
        self.check_for_value(browser,"UserInfo.LoginId",keys=user_type)
        if(user_type == "Agent" or user_type == "Agent Admin"):
            self.check_for_value(browser,"UserInfo.TypeCd","Producer")
        else:
            self.check_for_value(browser,"UserInfo.TypeCd","Company")

        self.check_for_value(browser,"UserInfo.DefaultLanguageCd","en_US")
        self.check_for_value(browser,"UserInfo.FirstName",keys=user_type)
        self.check_for_value(browser,"UserInfo.LastName",keys="User")
        self.check_for_value(browser,"UserInfo.ConcurrentSessions",keys=100)
        self.check_for_value(browser,"PasswordInfo.PasswordRequirementTemplateId","Exempt")
        self.check_for_value(browser,"ChangePassword",keys=new_user_password)
        self.check_for_value(browser,"ConfirmPassword",keys=new_user_password)
        script = "document.getElementById(\"UserInfo.PasswordMustChangeInd\").checked = false"
        browser.execute_script(script)
        self.check_for_value(browser,"ProviderNumber",keys=self.producer_selected)
        self.check_for_value(browser,"UserInfo.BranchCd","Home Office")
        self.save(browser)

        self.check_for_value(browser,"AddProviderSecurity",keys="click")
        self.check_for_value(browser,"ProviderSecurity.ProviderSecurityCd",keys=self.producer_selected)
        self.save(browser)
        self.waitPageLoad(browser)

        self.check_for_value(browser,"AddRole",keys="click")
        self.check_for_value(browser,"UserRole.AuthorityRoleIdRef",user_dict[user_type])
        self.save(browser)
        self.waitPageLoad(browser)

        if user_type == "Underwriter":
            values_used = ["UWServicesPersonal","UnderwritingPersonalLines","UnderwritingCommercialLines","UWServicesCommercial","UWServicesPersonal-CLM","UWServicesCommercial-CLM","UnderwritingPersonalLines-CLM"]
            for value in values_used:
                self.check_for_value(browser,"AddTaskGroup",keys="click")
                self.check_for_value(browser,"UserTaskGroup.TaskGroupCd",value)
                self.save(browser)

        self.waitPageLoad(browser)
        self.save(browser)

        script = "alert(\"User Created Successfully!\")"
        browser.execute_script(script)
        sleep(5)
        browser.quit()
        del self.app_logger
        if user_type not in list(user_values):
            File.add_user(user_type,new_user_password)
