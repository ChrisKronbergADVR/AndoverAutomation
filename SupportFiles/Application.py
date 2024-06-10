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

    gw_environment ={"Local":"https://localhost:9443","QA":"https://qa-advr.iscs.com/","UAT3":"https://uat3-advr.in.guidewire.net/innovation?saml=off","UAT4":"https://uat4-advr.in.guidewire.net/innovation","QA2":"https://qa2-acx-advr.in.guidewire.net/innovation"}
    
    user_chosen = None
    verified = False
    payment_plan_most = {"Mortgagee Direct Bill Full Pay":"BasicPolicy.PayPlanCd_1","Automated Monthly":"BasicPolicy.PayPlanCd_2","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_3","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_5","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_6","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_7","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_8","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_9","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_10"}
    payment_plan_bop = {"Mortgagee Direct Bill Full Pay":"BasicPolicy.PayPlanCd_1","Automated Monthly":"BasicPolicy.PayPlanCd_2","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_3","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_5","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_6","Direct Bill 9 Pay":"BasicPolicy.PayPlanCd_7","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_8","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_9","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_10","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_11"}
    payment_plan_bop_wrong = {"Mortgagee Direct Bill Full Pay":"BasicPolicy.PayPlanCd_1","Automated Monthly":"BasicPolicy.PayPlanCd_2","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_3","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_5","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_6","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_7","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_8","Direct Bill 9 Pay":"BasicPolicy.PayPlanCd_9","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_10","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_11"}
    payment_plan_pumb = {"Automated Monthly":"BasicPolicy.PayPlanCd_1","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_2","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_3","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_5","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_6","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_7","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_8","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_9"}
    pay_plan = ""
    user_dict = {"AgentAdmin":"AgentAdmin","Admin":"Everything","Underwriter":"PolicyUnderwriter","Agent":"PolicyAgent"}

    #*function for finding elements in the browser
    @staticmethod
    def find_Element(browser,browser_Element, id = By.ID):
        elem = browser.find_element(id,browser_Element)
        return elem
    
    @staticmethod
    def delete_quote(browser):
        #delete created Quote
        Application.find_Element(browser,"Delete").click()
        Application.find_Element(browser,"dialogOK").click()
    
    #* This function is used to decide whether to use chrome or edge browser
    @staticmethod
    def load_page():
        Application.app_logger.add_log(f"Browser Used: {Application.browser_chosen}",logging.INFO)
        if(Application.browser_chosen == "Chrome"):
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            browser = webdriver.Chrome(options = chrome_options)
        else:
            edge_options = webdriver.edge.options.Options()
            edge_options.add_experimental_option("detach", True)
            browser = webdriver.Edge(options = edge_options)
        browser.get(Application.gw_environment[Application.env_used])
    
        Application.check_for_value(browser,"details-button",keys="click")    
        Application.check_for_value(browser,"proceed-link",keys="click")    
        Application.waitPageLoad(browser)

        assert "Guidewire InsuranceNow™ Login" in browser.title
        return browser

    @staticmethod
    def get_password(user):
        password = File.env_files_plus_users[Application.env_used]["Users"]["Usernames"][user]
        return password

    #*function for login
    @staticmethod
    def login(browser,user = "admin",password = "Not9999!"):
        Application.waitPageLoad(browser)
        Application.find_Element(browser,"j_username").send_keys(user)
        Application.find_Element(browser,"j_password").send_keys(password + Keys.RETURN)

    @staticmethod
    def save(browser):
        browser.execute_script('document.getElementById("Save").click();')
        Application.remove_javascript(browser)

    @staticmethod
    def click_radio_button(browser,element):
        try:
            if(Application.find_Element(browser,element).is_displayed() == True):
                Application.find_Element(browser,element).click()
        except:
            pass

    @staticmethod
    def click_radio(browser):
        e_name = "QuoteCustomerClearingRef"
        table = browser.find_elements(By.NAME,e_name)
        radio_number = len(table)
        my_value = e_name+"_"+str(radio_number)
        Application.click_radio_button(browser,my_value)

    @staticmethod
    def value_exists(browser,element_id):
        try:
            element1 = Application.find_Element(browser,element_id)
            if element1.is_displayed():
                return element1
        except:
            return None

    #*Functions for finding or sending values to input fields
    @staticmethod
    def check_for_value(browser,element,value = None,visible_text:bool=False,keys=None):
        try:
            element1 = Application.find_Element(browser,element)
            if element1.is_displayed():
                if(keys != None):
                    if(keys == "click"):
                        if visible_text == True:
                            Application.find_Element(browser,"Producer",id=By.LINK_TEXT).click()
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
            Application.app_logger.add_log(f"Element Not Found with id {element} value:{value} keys:{keys}",logging.DEBUG)
    
    #*Removes the errors on webpage
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
            t = Application.find_Element(browser,element_used).is_displayed()
            if(t == True):
                browser.execute_script(script)
        except:
            pass
        finally:
            pass

    #*function used for waiting for page to load after a button is clicked and the page has to refresh
    @staticmethod
    def waitPageLoad(browser):
        Application.remove_javascript(browser)
        script = "return window.seleniumPageLoadOutstanding == 0;"
        WebDriverWait(browser, 60).until(lambda browser:browser.execute_script(script)) 

    @staticmethod
    def run_verify_address(browser):
        script = "InsuredMailingAddr.verify();"
        lambda browser:browser.execute_script(script)

    @staticmethod
    def copy_to_property(browser,addr,city,state):
        Application.find_Element(browser,"InsuredResidentAddr.Addr1").send_keys(addr)
        Application.find_Element(browser,"InsuredResidentAddr.City").send_keys(city)
        Select(Application.find_Element(browser,"InsuredResidentAddr.StateProvCd")).select_by_value(state)

    @staticmethod
    def copy_to_mailing(browser,addr,city,state):
        Application.find_Element(browser,"InsuredMailingAddr.Addr1").send_keys(addr)
        Application.find_Element(browser,"InsuredMailingAddr.City").send_keys(city)
        Select(Application.find_Element(browser,"InsuredMailingAddr.StateProvCd")).select_by_value(state)

    @staticmethod
    def core_coverages(browser):
        core_coverages_time = Timing()
        core_coverages_time.start()
        coverage_a =  300000
        coverage_c = coverage_a
        Application.app_logger.add_log(f"Starting Core Coverages",logging.INFO)
        
        core_values = ["Risk.ListOfTenantsAndOccupancy","Risk.BasementInd","Risk.BldgCentralHeatInd","Risk.CircuitBreakerProtInd","Risk.UndergradResidentInd",
                    "Risk.SpaceHeatersInd","Risk.FrameClearance15ftInd","Risk.ShortTermRent","Risk.MercantileOfficeOccupantsInd","Risk.ExcessLinesInd"]
        
        core_values_after = ["Risk.RoofUpdatedIn15YrsInd","Risk.AdequateSmokeDetInd","Risk.BldgOccGt75PctInd","Risk.EgressFromAllUnitsInd","Risk.MaintProgramInd"]

        browser.execute_script("document.getElementById('Wizard_Risks').click();")

        Application.waitPageLoad(browser)
        Application.check_for_value(browser,"Building.ConstructionCd","Frame")
        Application.check_for_value(browser,"Building.YearBuilt",keys=2020)
        Application.check_for_value(browser,"Building.OccupancyCd","Owner occupied dwelling")
        Application.check_for_value(browser,"Building.Seasonal","No")
        Application.check_for_value(browser,"Risk.TypeCd","DP2")
        Application.check_for_value(browser,"Building.BuildingLimit",keys=300000)
        Application.check_for_value(browser,"Building.StandardDed","500")
        Application.check_for_value(browser,"Building.NumOfFamilies","1")
        Application.check_for_value(browser,"Building.DistanceToHydrant","1000")
        Application.check_for_value(browser,"Building.OccupancyCd","Primary Residence")
        Application.check_for_value(browser,"Building.CovALimit",keys=coverage_a)
        Application.check_for_value(browser,"Building.NumOfFamiliesSameFire","Less Than 5",False,None)
        Application.check_for_value(browser,"Building.DistanceToHydrant","1000")
        Application.check_for_value(browser,"Building.FuelLiability","300000")
        Application.check_for_value(browser,"Building.OilTankLocation","none")
        Application.check_for_value(browser,"Building.CovELimit","300000")
        Application.check_for_value(browser,"Building.CovFLimit","2000")
        Application.check_for_value(browser,"Building.CovFLimit","100000")
        Application.check_for_value(browser,"Building.CovCLimit",keys=coverage_c)
        Application.check_for_value(browser,"Building.StandardDed","1000")
        Application.check_for_value(browser,"Building.NumOfFamilies","1")
        Application.check_for_value(browser,"Building.DistanceToHydrant","1000")
        Application.check_for_value(browser,"Building.TerritoryCd",keys="1")
        Application.check_for_value(browser,"Risk.WorkersCompInd","100000")
        Application.check_for_value(browser,"Risk.WorkersCompEmployees","none")
        Application.check_for_value(browser,"Building.HurricaneMitigation","No Action")
                
        Application.check_for_value(browser,"Building.BuildingClassDescription","75% or more Apartments")
        Application.check_for_value(browser,"Building.BuildingClassDescription","67% or more Apartments")
        Application.check_for_value(browser,"Building.DistanceToHydrant","1000")
        Application.check_for_value(browser,"Building.ContentClassDescription","None - Building Owner only")
        Application.check_for_value(browser,"Building.BuildingLimit",keys=900000)
        Application.check_for_value(browser,"Building.DistanceToHydrant","1000")
        Application.check_for_value(browser,"Risk.SqFtArea",keys=2000)
        Application.check_for_value(browser,"Risk.PremisesAlarm","None",True)
        Application.check_for_value(browser,"Risk.YrsInBusinessInd","1",True)
        Application.check_for_value(browser,"Building.NumOfApartmentCondoBuilding",keys=5)
        Application.check_for_value(browser,"Building.MaxNumOfAptCondoBetweenBrickWalls",keys=5)
        Application.check_for_value(browser,"Building.NumOfStories",keys=5)
        Application.check_for_value(browser,"Risk.ListOfTenantsAndOccupancy",keys="None")
        Application.check_for_value(browser,"Risk.NumOfStories",keys=3)
        Application.check_for_value(browser,"Building.ProtectionClass",keys=3)
        
        #if line_of_business == "Businessowners" or line_of_business == "Commercial Umbrella":
        for value in core_values:
            Application.check_for_value(browser,value,"No",False)

        #save(browser)
        Application.save(browser)
        Application.waitPageLoad(browser)
        
        for value in core_values_after:
            Application.check_for_value(browser,value,"No",False)

        try:
            t = Application.find_Element(browser,"MissingFieldError").is_displayed()
            if t:
                Application.app_logger.add_log(f"Core Coverages Was not able to Complete",logging.ERROR)
        except:
            Application.app_logger.add_log(f"Finishing Core Coverages without Errors",logging.INFO)
            core_coverages_time.end()
            Application.app_logger.add_log(f"Time to complete Core Coverages: {core_coverages_time.compute_time()} seconds",logging.INFO)

        #click the save button
        Application.save(browser)
        

    @staticmethod
    def question_update(question,size):
        if(question.__contains__("1")):
            word = question.split("1")
            new_word =  word[0]+str(size)+word[1]
        return new_word

    #* Function to add underwriting questions for each location
    @staticmethod
    def gen_dwell_location_questions(browser,num):
        Application.app_logger.add_log(f"Starting questions for Dwelling",logging.INFO)

        ques_dwell = ["Question_PolicyKnownPersonally","Question_PolicyOtherIns","Question_PolicyArson","Question_RiskNumber1PrevDisc","Question_RiskNumber1Vacant","Question_RiskNumber1OnlineHome"
                        ,"Question_RiskNumber1Isolated","Question_RiskNumber1Island","Question_RiskNumber1Seasonal","Question_RiskNumber1SolarPanels","Question_RiskNumber1Adjacent","Question_RiskNumber1ChildCare",
                        "Question_RiskNumber1OtherBusiness","Question_RiskNumber1Undergrad","Question_RiskNumber1DogsAnimals","Question_RiskNumber1Electrical","Question_RiskNumber1EdisonFuses","Question_RiskNumber1Stove",
                        "Question_RiskNumber1OilHeated","Question_RiskNumber1Pool","Question_RiskNumber1Trampoline","Question_RiskNumber1Outbuildings","Question_RiskNumber1InsDeclined","Question_MAFireRiskNumber1OtherFireInsuranceApp",
                        "Question_MAFireRiskNumber1OtherFireInsuranceActive","Question_MAFireRiskNumber1FireInPast","Question_MAFireRiskNumber1PropertyForSale","Question_MAFireRiskNumber1ApplicantMortgageeCrime",
                        "Question_MAFireRiskNumber1ShareholderTrusteeCrime","Question_MAFireRiskNumber1MortgagePaymentsDelinquent","Question_MAFireRiskNumber1RealEstateTaxesDelinquent","Question_MAFireRiskNumber1CodeViolations"]
        
        newDict = {1:ques_dwell}
        newArr = []

        Application.gen_dewll_location_extra_questions(browser,1)
        if Application.state_chosen == "RI":
            Application.find_Element(browser,"Question_RiskNumber"+str(1)+"InspectorName").send_keys("No")

        if(num > 1):
            for loc in range(num-1):
                number = loc+2
                for question_name in ques_dwell:    
                    if(question_name.__contains__("1")):
                        word = question_name.split("1")
                        newArr.append(word[0]+str(number)+word[1])
                newDict[number] = newArr
                if Application.state_chosen == "RI":                                                                  
                    Application.find_Element(browser,"Question_RiskNumber"+str(number)+"InspectorName").send_keys("No")
                Application.gen_dewll_location_extra_questions(browser,number)
                
        return newDict

    @staticmethod
    def gen_dewll_location_extra_questions(browser,num):
        extra_dwell_questions = ["Question_RiskNumber1Lapse","Question_RiskNumber1NumClaims","Question_MAFireRiskNumber1PurchaseDate","Question_MAFireRiskNumber1PurchasePrice","Question_MAFireRiskNumber1EstimatedValue","Question_MAFireRiskNumber1ValuationMethod","Question_MAFireRiskNumber1AppraisalMethod"]
        updatedArr = []

        if(num >1):
            for question in extra_dwell_questions:
                updatedArr.append(Application.question_update(question,num))
        else:
            updatedArr = extra_dwell_questions
        Select(Application.find_Element(browser,updatedArr[0])).select_by_value("No-New purchase")
        Application.find_Element(browser,updatedArr[1]).send_keys(0)
        if(Application.state_chosen == 'MA'):
            Application.find_Element(browser,updatedArr[2]).send_keys("01/01/2022")
            Application.find_Element(browser,updatedArr[3]).send_keys("100000")
            Application.find_Element(browser,updatedArr[4]).send_keys("150000")
            Select(Application.find_Element(browser,updatedArr[5])).select_by_value("Replacement Cost")
            Select(Application.find_Element(browser,updatedArr[6])).select_by_value("Professional Appraisal")

    @staticmethod
    def underwriting_questions(browser,multi):
        y = datetime.today()+timedelta(days=60)
        producer_inspection_date = y.strftime("%m/%d/%Y")
        Application.find_Element(browser,"Wizard_Underwriting").click()
        Application.app_logger.add_log(f"Starting Underwriting Questions for {Application.state_chosen} {Application.line_of_business}",logging.INFO)
        Application.waitPageLoad(browser)
        lob = Application.line_of_business

        questions_home = ["Question_PermanentFoundation","Question_IslandProperty","Question_IsolatedProperty","Question_IslandHome","Question_PrevKnown",
                    "Question_PrevDiscussed","Question_OtherInsurance","Question_VacantOrOccupied", "Question_OnlineHome", "Question_OnlineHome",
                    "Question_SeasonalHome", "Question_FrameDwellings", "Question_DayCareOnPremises", "Question_UndergraduateStudents","Question_SolarPanels","Question_UndergraduateStudents",
                    "Question_DogsCare", "Question_ElectricalService", "Question_WiringInUse", "Question_StoveOnPremises", "Question_OilHeated", "Question_PoolOnPremises",
                    "Question_TrampolineOnPremises","Question_AnyOutbuildings","Question_CancelledRecently","Question_ArsonConvicted"]

        if Application.line_of_business =="Dwelling Property":
            if multi == True:
                dwell_questions = Application.gen_dwell_location_questions(browser,Application.number_of_addresses)
            else:
                dwell_questions = Application.gen_dwell_location_questions(browser,1)

        if Application.line_of_business == "Homeowners" or Application.line_of_business == "Personal Umbrella":
            Application.check_for_value(browser,"Question_InspectorName",keys="Gadget")

            for question in questions_home:
                Application.check_for_value(browser,question,"No",True)
            Application.check_for_value(browser,"Question_AnyLapsePast","No-New Purchase",True)
            Application.check_for_value(browser,"Question_ClaimsRecently",keys=0)
            Application.check_for_value(browser,"Question_PurchasePrice",keys=500000)

        if(lob == "Dwelling Property"):
            for key in range(len(dwell_questions.keys())):
                for question in dwell_questions[key+1]:
                    Application.check_for_value(browser,question,"No",True)

        if(lob == "Businessowners" or lob == "Commercial Umbrella"):
            Select(Application.find_Element(browser,"Question_01CoverageCancellation")).select_by_visible_text("No")
            Application.find_Element(browser,"Question_03PreviousCarrierPropertyLimitsPremium").send_keys("No")
            Select(Application.find_Element(browser,"Question_08NumLosses")).select_by_value("0")
            Application.find_Element(browser,"Question_05ProducerName").send_keys("No")
            Application.find_Element(browser,"Question_06ProducerInspectionDt").send_keys(producer_inspection_date)
            Select(Application.find_Element(browser,"Question_09Broker")).select_by_visible_text("No")
                
        #click the save button
        Application.save(browser)
        Application.waitPageLoad(browser)

        try:
            t = Application.find_Element(browser,"MissingFieldError").is_displayed()
            if t:
                Application.app_logger.add_log(f"Underwriting Questions Were not able to Complete because of Missing Field",logging.ERROR)
        except:
            Application.app_logger.add_log(f"Finishing Underwriting Questions without Errors",logging.INFO)

    @staticmethod
    def billing(browser):

        Application.waitPageLoad(browser)
        Application.find_Element(browser,"Wizard_Review").click()
        Application.waitPageLoad(browser)
        state = Application.state_chosen
        pay_plan = Application.pay_plan
        Application.app_logger.add_log(f"Pay Plan: {pay_plan}",logging.INFO)

        elements = browser.find_elements(By.NAME,"BasicPolicy.PayPlanCd")
        for e in elements:
            val1 = e.get_attribute("value")
            try: 
                if val1.index(" "+state):
                    value = val1.index(" "+state)
                    val2 = val1[:value]
                    if(val2 == pay_plan):
                        val = "//input[@value='"+val1+"' and @type='radio']"
                        Application.find_Element(browser,val,By.XPATH).click()
                        break
            except:
                if(val1 == pay_plan):
                        val = "//input[@value='"+pay_plan+"' and @type='radio']"
                        Application.find_Element(browser,val,By.XPATH).click()
                        break
                
        Application.waitPageLoad(browser)

        if pay_plan.__contains__("Automated Monthly"):
            Select(Application.find_Element(browser,"InstallmentSource.MethodCd")).select_by_value("ACH")
            Application.waitPageLoad(browser)
            Select(Application.find_Element(browser,"InstallmentSource.ACHStandardEntryClassCd")).select_by_value("PPD")
            Select(Application.find_Element(browser,"InstallmentSource.ACHBankAccountTypeCd")).select_by_value("Checking")
            Application.find_Element(browser,"InstallmentSource.ACHBankName").send_keys("Bank")
            Application.find_Element(browser,"InstallmentSource.ACHBankAccountNumber").send_keys(123456789)
            Application.find_Element(browser,"InstallmentSource.ACHRoutingNumber").send_keys("011000015")
            Application.find_Element(browser,"BasicPolicy.PaymentDay").send_keys(15)
            Application.find_Element(browser,"BasicPolicy.CheckedEFTForm").click()
        if pay_plan.__contains__("Bill To Other") or pay_plan.__contains__("Mortgagee"):
            Application.find_Element(browser,"UWAINew").click()
            Application.waitPageLoad(browser)
            if pay_plan.__contains__("Bill To Other"):
                Select(Application.find_Element(browser,"AI.InterestTypeCd")).select_by_value("Bill To Other")
                Application.waitPageLoad(browser)
            else:
                Select(Application.find_Element(browser,"AI.InterestTypeCd")).select_by_value("First Mortgagee")
                Select(Application.find_Element(browser,"AI.EscrowInd")).select_by_value("Yes")
                Select(Application.find_Element(browser,"AI.BillMortgRnwlInd")).select_by_value("No")
            Application.find_Element(browser,"AI.AccountNumber").send_keys(12345)
            Application.find_Element(browser,"AI.InterestName").send_keys("First Last")
            Application.find_Element(browser,"AIMailingAddr.Addr1").send_keys("1595 N Peach Ave")
            Application.find_Element(browser,"AIMailingAddr.City").send_keys("Fresno")
            Select(Application.find_Element(browser,"AIMailingAddr.StateProvCd")).select_by_value("CA")
            Application.find_Element(browser,"AIMailingAddr.PostalCode").send_keys(93727)
            Select(Application.find_Element(browser,"AIMailingAddr.RegionCd")).select_by_value("United States")

            try:
                Application.find_Element(browser,"LinkReferenceInclude_0").click()
            except:
                try: 
                    Application.find_Element(browser,"LinkReferenceInclude_1").click()
                except:
                    pass

            Application.waitPageLoad(browser)
            Application.save(browser)

        Application.waitPageLoad(browser)

        #click the save button
        Application.save(browser)
        Application.waitPageLoad(browser)

    #Start application creation
    @staticmethod
    def startApplication(multiAdd,subType,carrier):
        user_chosen = Application.user_chosen
        create_type = Application.create_type
        state_chosen = Application.state_chosen
        line_of_business = Application.line_of_business
        env_used = Application.env_used
        date_chosen = Application.date_chosen
        producer_selected = Application.producer_selected

        thread_name = str(threading.current_thread().name)

        if MultiLog.log_data:
            Application.app_logger.createLog(Application.state_chosen,Application.line_of_business,thread_name)

        CARRIER = {"Merrimack Mutual Fire Insurance":"MMFI","Cambrige Mutual Fire Insurance":"CMFI","Bay State Insurance Company":"BSIC"}
        password = Application.get_password(user_chosen)

        Application.app_logger.add_log(f"Started {create_type} for {state_chosen} {line_of_business} in {env_used} Environment with {user_chosen} user where date = {date_chosen}",logging.INFO)

        browser = Application.load_page()
        
        try:
            Application.login(browser,user_chosen,password)
        except:
            raise Exception("Incorrect username and/or password")

        #*Tab to click  for recent quotes, applications, and policies
        Application.find_Element(browser,"Tab_Recent").click()
        state1,CITY,ADDRESS = Address.addresses[str(state_chosen+"1")]
        custom_city = Address.custom_address["City"]
        custom_add = Address.custom_address["Address"]
        first_name = state_chosen + " " + line_of_business
        last_name = "Automation"

        if Address.custom_address["Flag"]:
            Application.create_new_quote(browser,date_chosen,state1,producer_selected,first_name,last_name,custom_add,custom_city,multiAdd,Application.TEST, subType,CARRIER[carrier])
        else:
            Application.create_new_quote(browser,date_chosen,state1,producer_selected,first_name,last_name,ADDRESS,CITY,multiAdd,Application.TEST,subType,CARRIER[carrier])

        if Application.TEST:
            sleep(5)
            browser.quit()

    @staticmethod
    def submit_policy(browser):
        Application.find_Element(browser,"Closeout").click()
        Application.waitPageLoad(browser)
        Select(Application.find_Element(browser,"TransactionInfo.PaymentTypeCd")).select_by_value("None")
        Application.find_Element(browser,"TransactionInfo.SignatureDocument").click()
        Application.find_Element(browser,"PrintApplication").click()
        sleep(30)
        Application.find_Element(browser,"Process").click()
        Application.waitPageLoad(browser)

    @staticmethod
    def create_new_quote(browser,date,state:str,producer:str,first_name:str,last_name:str,address:str,city:str,multiLoc:bool,test:bool,subType:str,carrier:str):
        #New Quote
        Application.find_Element(browser,"QuickAction_NewQuote_Holder").click()
        Application.find_Element(browser,"QuickAction_EffectiveDt").send_keys(date)

        Application.waitPageLoad(browser)
        #State Select
        browser.execute_script("document.getElementById('QuickAction_StateCd').value = '"+state+"';")
        Application.check_for_value(browser,"QuickAction_CarrierGroupCd",Application.COMPANY)

        browser.execute_script("document.getElementById('QuickAction_NewQuote').click()")

        if Application.line_of_business == "Personal Umbrella":
            Application.find_Element(browser,"Homeowners",By.LINK_TEXT).click()
        elif Application.line_of_business == "Commercial Umbrella":
            Application.find_Element(browser,"Businessowners",By.LINK_TEXT).click()
        else:
            Application.find_Element(browser,Application.line_of_business,By.LINK_TEXT).click()

        #enter producer here
        Application.check_for_value(browser,"ProviderNumber",keys=producer)
        
        #select entity type
        if(Application.line_of_business == "Dwelling Property" or Application.line_of_business == "Businessowners" or Application.line_of_business == "Commercial Umbrella"):
            Select(Application.find_Element(browser,"Insured.EntityTypeCd")).select_by_value("Individual")
        
        Application.waitPageLoad(browser)

        quote_num = Application.find_Element(browser,"QuoteAppSummary_QuoteAppNumber")
        Application.app_logger.add_log(f" ",logging.INFO)
        Application.app_logger.add_log(f" ------------ QUOTE STARTED ---------------- ",logging.INFO)
        Application.app_logger.add_log(f"Quote Number: {quote_num.text}",logging.INFO)

        Application.check_for_value(browser,"InsuredPersonal.OccupationClassCd","Other")
        Application.check_for_value(browser,"InsuredPersonal.OccupationOtherDesc",keys="No")

        if Application.state_chosen == "NY" and (Application.line_of_business == "Homeowners" or Application.line_of_business == "Personal Umbrella"):
            Select(Application.find_Element(browser,"BasicPolicy.GeographicTerritory")).select_by_value("Upstate")

        browser.execute_script('document.getElementById("InsuredName.GivenName").value = "' + first_name + '"')
        browser.execute_script('document.getElementById("InsuredName.Surname").value = "' + last_name + '"')

        Application.check_for_value(browser,"InsuredNameJoint.GivenName",keys="click")
        Application.check_for_value(browser,"InsuredNameJoint.GivenName",keys="Second")
        Application.check_for_value(browser,"InsuredNameJoint.Surname",keys="Person")
        Application.waitPageLoad(browser)
        Application.check_for_value(browser,"InsuredNameJoint.GivenName",keys="Second")
        Application.check_for_value(browser,"InsuredNameJoint.Surname",keys="Person")
        Application.check_for_value(browser,"InsuredPersonalJoint.BirthDt",keys="01/01/1980")
        Application.check_for_value(browser,"InsuredPersonalJoint.OccupationClassCd","Other")
        Application.check_for_value(browser,"InsuredPersonalJoint.OccupationOtherJointDesc",keys="No")

        if (Application.line_of_business == "Homeowners" or Application.line_of_business == "Personal Umbrella") and subType:
            Application.check_for_value(browser,"BasicPolicy.DisplaySubTypeCd",subType)
            if Application.state_chosen == "NY":
                Select(Application.find_Element(browser,"BasicPolicy.DisplaySubTypeCd")).select_by_index(1)
        
        
        if Application.line_of_business != "Businessowners" and Application.line_of_business != "Commercial Umbrella":
            Application.find_Element(browser,"InsuredPersonal.BirthDt").send_keys("01/01/1980")
            Application.find_Element(browser,"InsuredCurrentAddr.Addr1").send_keys(address)
            Application.find_Element(browser,"InsuredCurrentAddr.City").send_keys(city)
            Select(Application.find_Element(browser,"InsuredCurrentAddr.StateProvCd")).select_by_value(state)

        #*Select state here
        if(Application.line_of_business == "Businessowners" or Application.line_of_business == "Commercial Umbrella"): 
            Application.find_Element(browser,"InsuredMailingAddr.Addr1").send_keys(address)
            Application.find_Element(browser,"InsuredMailingAddr.City").send_keys(city)
            Select(Application.find_Element(browser,"InsuredMailingAddr.StateProvCd")).select_by_value(state)

        #*Adding geographic territory and policy carrier here
        if(Application.state_chosen == "NY" and (Application.line_of_business == "Homeowners" or Application.line_of_business == "Personal Umbrella")):
            Select(Application.find_Element(browser,"BasicPolicy.GeographicTerritory")).select_by_value("Metro")

        Application.waitPageLoad(browser)
        if Application.line_of_business == "Businessowners" or Application.line_of_business == "Commercial Umbrella":
            Application.find_Element(browser,"DefaultAddress").click()

        if Application.line_of_business != "Businessowners" and Application.line_of_business != "Commercial Umbrella":
            Application.copy_to_property(browser,address,city,state)
            Application.copy_to_mailing(browser,address,city,state)
            Application.waitPageLoad(browser)

        #*First and Last names copied to input fields here
        Application.find_Element(browser,"InsuredName.MailtoName").send_keys(f"{first_name} {last_name}")
        Application.find_Element(browser,"Insured.InspectionContact").send_keys(f"{first_name} {last_name}")

        #*Phone Type, Phone number, and email entered here
        Select(Application.find_Element(browser,"InsuredPhonePrimary.PhoneName")).select_by_value("Mobile")
        Application.find_Element(browser,"InsuredPhonePrimary.PhoneNumber").send_keys(5558675309)
        Application.check_for_value(browser,"Insured.InspectionContactPhoneType","Mobile")
        Application.check_for_value(browser,"Insured.InspectionContactNumber",keys=5558675309)
        Application.find_Element(browser,"InsuredEmail.EmailAddr").send_keys("test@mail.com")
        Application.waitPageLoad(browser)

        #Set insurance score if available
        Application.check_for_value(browser,"InsuredInsuranceScore.OverriddenInsuranceScore",keys="999")

        #*click the save button
        Application.save(browser)
        Application.waitPageLoad(browser)

        #Select the second policy carrier
        Application.check_for_value(browser,"BasicPolicy.PolicyCarrierCd",carrier)

        #multiple locations here
        if Application.line_of_business != "Businessowners" and Application.line_of_business != "Commercial Umbrella":
            
            Application.core_coverages(browser)
            if(multiLoc == True and Application.line_of_business == "Dwelling Property"):
                for i in range(Application.number_of_addresses-1):
                    Application.find_Element(browser,"CopyRisk").click()
                    Application.save(browser)

        if(Application.create_type == "Application" or Application.create_type == "Policy"):
            Application.waitPageLoad(browser)
            Application.check_for_value(browser,"Wizard_Policy",keys="click")
            Application.waitPageLoad(browser)
            Application.click_radio(browser)
            Application.waitPageLoad(browser)
            Application.find_Element(browser,"Bind").click()
            
            if Application.line_of_business == "Businessowners" or Application.line_of_business == "Commercial Umbrella":
                Application.core_coverages(browser)
        
            Application.waitPageLoad(browser)
            if(Application.state_chosen == "NJ" and (Application.line_of_business == "Homeowners" or Application.line_of_business == "Personal Umbrella")):
                Application.find_Element(browser,"Wizard_Risks").click()
                Application.waitPageLoad(browser)
                Application.check_for_value(browser,"Building.Inspecti onSurveyReqInd","No")

                #click the save button
                Application.save(browser)
            
            application_num = Application.find_Element(browser,"QuoteAppSummary_QuoteAppNumber")
            Application.app_logger.add_log(f" ",logging.INFO)
            Application.app_logger.add_log(f" ------------ APPLICATION STARTED ---------------- ",logging.INFO)
            Application.app_logger.add_log(f"Application Number: {application_num.text}",logging.INFO)

            #Creating a Timing Object for Underwriting questions
            underwriting_time = Timing()
            underwriting_time.start()
            Application.underwriting_questions(browser,multiLoc)
            underwriting_time.end()

            Application.app_logger.add_log(f"Time to Complete Underwriting Questions: {underwriting_time.compute_time()} seconds",logging.INFO)
            
            Application.billing(browser)

            if Application.line_of_business == "Personal Umbrella":
                Application.find_Element(browser,"GetUmbrellaQuote").click()
                Application.waitPageLoad(browser)
                Application.find_Element(browser,"Wizard_UmbrellaLiability").click()
                Select(Application.find_Element(browser,"Line.PersonalLiabilityLimit")).select_by_value("1000000")
                Application.find_Element(browser,"Line.TotMotOwnLeasBus").send_keys(0)
                Application.find_Element(browser,"Line.NumMotExcUmb").send_keys(0)
                Application.find_Element(browser,"Line.NumHouseAutoRec").send_keys(0)
                Application.find_Element(browser,"Line.NumOfYouthInexp").send_keys(0)
                if Application.state_chosen == "NH":
                    Select(Application.find_Element(browser,"Line.RejectExcessUninsuredMotorists")).select_by_value("No")
                    Select(Application.find_Element(browser,"Line.UnderAutLiabPerOcc")).select_by_value("No")
                if Application.state_chosen == "NJ" or Application.state_chosen == "NY" or Application.state_chosen == "RI" or Application.state_chosen == "CT" or Application.state_chosen == "IL" or Application.state_chosen == "ME" or Application.state_chosen == "MA":
                    Select(Application.find_Element(browser,"Line.UnderAutLiabPerOcc")).select_by_value("No")
                Application.find_Element(browser,"Bind").click()
                Application.find_Element(browser,"Wizard_Underwriting").click()
                Select(Application.find_Element(browser,"Question_DiscussedWithUnderwriter")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_DUIConvicted")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_ConvictedTraffic")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_WatercraftBusiness")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_DayCarePremises")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_UndergraduateStudents")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_AnimalsCustody")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_PoolPremises")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_TrampolinePremises")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_CancelledRecently")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_BusinessPolicies")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_OnlineHome")).select_by_value("NO")
                Application.save(browser)
                Application.find_Element(browser,"Wizard_Review").click()
                Application.billing(browser)
                Application.waitPageLoad(browser)
                Application.save(browser)

                if Application.create_type == "Policy":
                    Application.find_Element(browser,"Return").click()
                    Application.find_Element(browser,"policyLink0").click()
                    Application.submit_policy(browser)
                    Application.find_Element(browser,"Return").click()
                    Application.find_Element(browser,"policyLink0").click()
                    Application.billing(browser)
            
            if Application.line_of_business == "Commercial Umbrella":
                Application.find_Element(browser,"GetUmbrellaQuote").click()
                Application.waitPageLoad(browser)
                Application.find_Element(browser,"Wizard_UmbrellaLiability").click()
                if Application.state_chosen == "CT" or Application.state_chosen == "NH" or Application.state_chosen=="NY" or Application.state_chosen == "RI":
                    Select(Application.find_Element(browser,"Line.CoverageTypeCd")).select_by_value("Businessowners Umbrella Liability")
                Select(Application.find_Element(browser,"Line.CommercialLiabilityLimit")).select_by_value("1000000")
                Select(Application.find_Element(browser,"Line.OwnedAutosInd")).select_by_value("No")
                Select(Application.find_Element(browser,"Line.EmplLiabCovrInsured")).select_by_value("No")
                Application.find_Element(browser,"Wizard_Policy").click()
                Application.find_Element(browser,"Bind").click()
                Application.find_Element(browser,"Wizard_Underwriting").click()
                Select(Application.find_Element(browser,"Question_OtherLiab")).select_by_value("NO")
                Select(Application.find_Element(browser,"Question_PriorCovCancelled")).select_by_value("NO")
                Application.find_Element(browser,"Question_PreviousUmbrella").send_keys("ACME")
                Application.save(browser)
                Application.find_Element(browser,"Wizard_Review").click()
                Application.billing(browser)
                Application.find_Element(browser,"Navigate_Location_2").click()
                Select(Application.find_Element(browser,"Location.UnderlyingEmplLimitConf")).select_by_value("Yes")
                Application.find_Element(browser,"NextPage").click()
            
                if Application.create_type == "Policy":
                    Application.find_Element(browser,"Return").click()
                    Application.find_Element(browser,"policyLink0").click()
                    Application.submit_policy(browser)
                    Application.find_Element(browser,"Return").click()
                    Application.find_Element(browser,"policyLink0").click()
                    if Application.pay_plan.__contains__("Bill To Other"):
                        Application.billing(browser)
        
        Application.check_for_value(browser,"Wizard_Policy",keys="click")
        warning_value = Application.value_exists(browser,"WarningIssues")
        error_value = Application.value_exists(browser,"ErrorIssues")
        if warning_value is not None:
            Application.app_logger.add_log(f"Issues: {warning_value.text}",logging.WARNING)
        if error_value is not None:
            Application.app_logger.add_log(f"Issues: {error_value.text}",logging.ERROR)

        if(Application.create_type == "Policy" and error_value is None):
            Application.submit_policy(browser)

            policy_num = Application.find_Element(browser,"PolicySummary_PolicyNumber")
            Application.app_logger.add_log(f" ",logging.INFO)
            Application.app_logger.add_log(f" ------------ Policy STARTED ---------------- ",logging.INFO)
            Application.app_logger.add_log(f"Policy Number: {policy_num.text}",logging.INFO)

        elif(error_value is not None):
            Application.app_logger.add_log(f"Application Could not be submitted due to {error_value.text}",logging.ERROR)

        sleep(5)

        if(test == True and Application.create_type != "Policy"):
            Application.delete_quote(browser)

    @staticmethod
    def get_created_application(applicaiton_number:str):
        pass


    #Create a producer
    @staticmethod
    def create_producer(producerName,user_name):
        agency_name = "All_States_All_LOB"
        agent_name = None
        prod_name = None
        y = datetime.today()
        default_date = y.strftime("%m/%d/%Y").split("/")
        password = Application.get_password(user_name)
        states = ["CT","IL","MA","ME","NH","NJ","NY","RI"]
        LOB = ["PUL","HO","DP","BOP-UMB","BOP"]
        prod_values = File.env_files_plus_users[Application.env_used]['Producers']['ProducerNames']

        browser = Application.load_page()

        try:
            Application.login(browser,user_name,password)
        except ValueError:
            #logger.error(f"Username or Password is not correct. username: {user_name} password: {password}")
            sleep(5)
            browser.quit()
            raise Exception("Incorrect username and/or password")
        Application.waitPageLoad(browser)    

        #################### Searching for a Producer #########################
        browser.execute_script('document.getElementById("Menu_Policy").click();')
        browser.execute_script('document.getElementById("Menu_Policy_UnderwritingMaintenance").click();')

        Application.find_Element(browser,"Producer",id=By.LINK_TEXT).click()
        Application.check_for_value(browser,"SearchText",keys=producerName)
        Application.check_for_value(browser,"SearchBy","ProviderNumber")
        Application.check_for_value(browser,"SearchFor","Producer")
        Application.check_for_value(browser,"SearchOperator","=")
        Application.check_for_value(browser,"Search",keys = "click")
        Application.waitPageLoad(browser)

        try:
            prod_name = Application.find_Element(browser,"//div[@id='Agency/Producer List']/*/*/tr[2]/td[2]",By.XPATH)
        except:
            pass

        #################### Searching for an Agency #########################
        Application.check_for_value(browser,"SearchText",keys=agency_name)
        Application.check_for_value(browser,"SearchBy","ProviderNumber")
        Application.check_for_value(browser,"SearchFor","Agency")
        Application.check_for_value(browser,"SearchOperator","=")
        Application.check_for_value(browser,"Search",keys = "click")
        Application.waitPageLoad(browser)

        try:
            agent_name = Application.find_Element(browser,"//div[@id='Agency/Producer List']/*/*/tr[2]/td[2]",By.XPATH)

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
            Application.check_for_value(browser,"NewProducer",keys="click")
            Application.check_for_value(browser,"Provider.ProviderNumber",keys=agency_name)
            Application.check_for_value(browser,"ProducerTypeCd",value="Agency")
            Application.check_for_value(browser,"Provider.StatusDt",keys=default_date)
            Application.check_for_value(browser,"AppointedDt",keys="01/01/1900")
            Application.check_for_value(browser,"CombinedGroup",value="No")
            Application.check_for_value(browser,"ProviderName.CommercialName",keys="The White House")
            Application.check_for_value(browser,"ProviderStreetAddr.Addr1",keys="1600 Pennsylvania Ave NW")
            Application.check_for_value(browser,"ProviderStreetAddr.City",keys="Washington")
            Application.check_for_value(browser,"ProviderStreetAddr.StateProvCd",value="DC")
            Application.waitPageLoad(browser)
            Application.check_for_value(browser,"CopyAddress",keys="click")
            Application.waitPageLoad(browser)
            Application.check_for_value(browser,"ProviderEmail.EmailAddr",keys="test@mail.com")
            Application.check_for_value(browser,"AcctName.CommercialName",keys="White House")
            Application.check_for_value(browser,"PayToCd",value="Agency")
            Application.check_for_value(browser,"Provider.CombinePaymentInd",value="No")
            Application.check_for_value(browser,"Provider.PaymentPreferenceCd",value="Check")
            Application.check_for_value(browser,"CopyBillingAddress",keys="click")
            Application.waitPageLoad(browser)
            Application.save(browser)
            Application.check_for_value(browser,"Return",keys="click")
            Application.waitPageLoad(browser)

        Application.check_for_value(browser,"NewProducer",keys="click")
        Application.check_for_value(browser,"Provider.ProviderNumber",keys=producerName)
        Application.check_for_value(browser,"ProducerTypeCd",value="Producer")
        Application.check_for_value(browser,"ProducerAgency",keys=agency_name)
        Application.check_for_value(browser,"Provider.StatusDt",keys=default_date)
        Application.check_for_value(browser,"AppointedDt",keys="01/01/1900")
        Application.check_for_value(browser,"CombinedGroup",value="No")
        Application.check_for_value(browser,"ProviderName.CommercialName",keys="Starbucks")
        Application.check_for_value(browser,"ProviderStreetAddr.Addr1",keys="43 Crossing Way")
        Application.check_for_value(browser,"ProviderStreetAddr.City",keys="Augusta")
        Application.check_for_value(browser,"ProviderStreetAddr.StateProvCd",value="ME")
        Application.waitPageLoad(browser)
        Application.check_for_value(browser,"CopyAddress",keys="click")
        Application.waitPageLoad(browser)
        Application.check_for_value(browser,"ProviderEmail.EmailAddr",keys="test@mail.com")
        Application.check_for_value(browser,"AcctName.CommercialName",keys="White House")
        Application.check_for_value(browser,"PayToCd",value="Agency")
        Application.check_for_value(browser,"Provider.CombinePaymentInd",value="No")
        Application.check_for_value(browser,"Provider.PaymentPreferenceCd",value="Check")
        Application.check_for_value(browser,"CopyBillingAddress",keys="click")
        Application.waitPageLoad(browser)
        Application.save(browser)
        Application.waitPageLoad(browser)
        Application.check_for_value(browser,"IvansCommissionInd",value="No")

        #########################  Add States ############################

        for state in states:
            Application.check_for_value(browser,"AddState",keys="click")
            Application.check_for_value(browser,"StateInfo.StateCd",value=state)
            Application.check_for_value(browser,"StateInfo.AppointedDt",keys="01/01/1900")
            Application.check_for_value(browser,"StateInfo.MerrimackAppointedDt",keys="01/01/1900")
            Application.check_for_value(browser,"StateInfo.CambridgeAppointedDt",keys="01/01/1900")
            Application.check_for_value(browser,"StateInfo.BayStateAppointedDt",keys="01/01/1900")
            Application.check_for_value(browser,"StateInfo.MerrimackLicensedDt",keys="01/01/2999")
            Application.check_for_value(browser,"StateInfo.CambridgeLicensedDt",keys="01/01/2999")
            Application.check_for_value(browser,"StateInfo.BayStateLicensedDt",keys="01/01/2999")
            Application.save(browser)
            Application.waitPageLoad(browser)

        ############################ Add Products ################################

        for state in states:
            for bus in LOB:
                Application.check_for_value(browser,"AddProduct",keys="click")
                Application.check_for_value(browser,"LicensedProduct.LicenseClassCd",value=bus)
                Application.check_for_value(browser,"LicensedProduct.StateProvCd",value=state)
                Application.check_for_value(browser,"LicensedProduct.EffectiveDt",keys="01/01/1900")
                Application.check_for_value(browser,"LicensedProduct.CommissionNewPct",keys="5")
                Application.check_for_value(browser,"LicensedProduct.CommissionRenewalPct",keys="5")
                Application.save(browser)
                Application.waitPageLoad(browser)
        Application.check_for_value(browser,"IvansCommissionInd",value="No")
        Application.check_for_value(browser,"FCRAEmail.EmailAddr",keys="test2@mail.com")
        Application.save(browser)

        script = "alert(\"Producer Created Successfully!\")"
        browser.execute_script(script)
        sleep(5)
        browser.quit()

        if producerName not in prod_values:
            File.add_producer(producerName)


    #Create a user
    @staticmethod
    def create_user(user_type,user_name):
        user_dict = Application.user_dict
        y = datetime.today()
        default_date = y.strftime("%m/%d/%Y").split("/")
        password = Application.get_password(user_name)
        user_xpath = "//div[@id='System User List']/div[2]/*/*/tr[2]/td[1]/a"
        new_user_password = "pass"
        user_values = File.env_files_plus_users[Application.env_used]['Users']['Usernames'].keys()
        user_searched_name = None
        browser = Application.load_page()

        try:
            Application.login(browser,user_name,password)
        except ValueError:
            sleep(5)
            browser.quit()
            raise Exception("Incorrect username and/or password")
        Application.waitPageLoad(browser)    

        browser.execute_script('document.getElementById("Menu_Admin").click();')
        browser.execute_script('document.getElementById("Menu_Admin_UserManagement").click();')

        #################### Searching for a User #########################
        Application.check_for_value(browser,"SearchText",keys=user_type)
        Application.check_for_value(browser,"MatchType","=")
        Application.check_for_value(browser,"Search",keys="click")

        try:
            user_searched_name = Application.find_Element(browser,user_xpath,By.XPATH)
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

        Application.check_for_value(browser,"AddUser",keys="click") 
        Application.check_for_value(browser,"UserInfo.LoginId",keys=user_type)
        if(user_type == "Agent" or user_type == "Agent Admin"):
            Application.check_for_value(browser,"UserInfo.TypeCd","Producer")
        else:
            Application.check_for_value(browser,"UserInfo.TypeCd","Company")

        Application.check_for_value(browser,"UserInfo.DefaultLanguageCd","en_US")
        Application.check_for_value(browser,"UserInfo.FirstName",keys=user_type)
        Application.check_for_value(browser,"UserInfo.LastName",keys="User")
        Application.check_for_value(browser,"UserInfo.ConcurrentSessions",keys=100)
        Application.check_for_value(browser,"PasswordInfo.PasswordRequirementTemplateId","Exempt")
        Application.check_for_value(browser,"ChangePassword",keys=new_user_password)
        Application.check_for_value(browser,"ConfirmPassword",keys=new_user_password)
        script = "document.getElementById(\"UserInfo.PasswordMustChangeInd\").checked = false"
        browser.execute_script(script)
        Application.check_for_value(browser,"ProviderNumber",keys=Application.producer_selected)
        Application.check_for_value(browser,"UserInfo.BranchCd","Home Office")
        Application.save(browser)

        Application.check_for_value(browser,"AddProviderSecurity",keys="click")
        Application.check_for_value(browser,"ProviderSecurity.ProviderSecurityCd",keys=Application.producer_selected)
        Application.save(browser)
        Application.waitPageLoad(browser)

        Application.check_for_value(browser,"AddRole",keys="click")
        Application.check_for_value(browser,"UserRole.AuthorityRoleIdRef",user_dict[user_type])
        Application.save(browser)
        Application.waitPageLoad(browser)

        if user_type == "Underwriter":
            values_used = ["UWServicesPersonal","UnderwritingPersonalLines","UnderwritingCommercialLines","UWServicesCommercial","UWServicesPersonal-CLM","UWServicesCommercial-CLM","UnderwritingPersonalLines-CLM"]
            for value in values_used:
                Application.check_for_value(browser,"AddTaskGroup",keys="click")
                Application.check_for_value(browser,"UserTaskGroup.TaskGroupCd",value)
                Application.save(browser)

        Application.waitPageLoad(browser)
        Application.save(browser)

        script = "alert(\"User Created Successfully!\")"
        browser.execute_script(script)
        sleep(5)
        browser.quit()

        if user_type not in list(user_values):
            File.add_user(user_type,new_user_password)
