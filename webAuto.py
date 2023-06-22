#* Authors: Chris Kronberg
#* Andover Autmoation Software

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from csv import DictReader,DictWriter
import PySimpleGUI as sg
from os import path
import os
from time import sleep
from datetime import datetime,timedelta

#*Constants
TEST = False
THEME = "TanBlue"
TEXTLEN = 25
CARRIER = "ADVR"

#*Global Variables
gw_environment ={"Local":"http://localhost:9090","QA":"https://qa-advr.iscs.com/","UAT3":"https://uat3-advr.in.guidewire.net/innovation?saml=off","UAT4":"https://uat4-advr.in.guidewire.net/innovation","QA2":"https://qa2-acx-advr.in.guidewire.net/innovation"}
browser_chosen = "Chrome"
line_of_business = "Dwelling Property"
state_chosen = "RI"
number_of_addresses = 1
date_chosen = "07/10/2023"
env_used = "Local"
producer_selected = "DEF"
doc_types = ["Quote","Application","Policy"]
create_type = doc_types[1]
folder = "csvFiles/"
custom_address = {"Address":"","City":"","Flag":False}
user_chosen = "admin"
agent_list = ["qaagent02", "qaagent01","agent04","agent","agent05","testagent4058","testagent0827","testagent4188","testagent9749","agent6578","agentuser7737","agentuser7791","testagent6131","testagent9679","kaylaagent","QAPolicyAgent1"]

addresses = {
            "CT1":["CT","Waterbury","1250 W Main St"],
            "CT2":["CT","Milddletown","871 Washington St"],
            "IL1":["IL","Urbana","1401 W Green St"],
            "IL2":["IL","Fairview Heights","4701 N Illinois St"],
            "ME1":["ME","South Portland","364 Maine Mall Rd"],
            "ME2":["ME","Portland","1080 Forest Ave"],
            "MA1":["MA","Cambridge","1662 Massechusetts AVe"],
            "MA2":["MA","Arlington","1465 Massachusetts Ave"],
            "NH1":["NH","Manchester","1111 S Willow St"],
            "NH2":["NH","Salem","203 S Broadway"],
            "NJ1":["NJ","Jackson","50 Hannah Hill Rd"],
            "NJ2":["NJ","Jackson","426 Chandler Rd"],
            "NY1":["NY","New York","1500 Broadway"],
            "NY2":["NY","New York","424 Park Ave S"],
            "RI1":["RI","Providence","468 Angell St"],
            "RI2":["RI","Warwick","25 Pace Blvd"]
            }

env_files_plus_users= {
            "QA":{"Users":{"file":"users.csv","Usernames":{}},
                  "Producers":{"file":"producers.csv","ProducerNames":["ALLSTATES HO and DW"]}},
            "Local":{"Users":{"file":"local_users.csv","Usernames":{}},
                   "Producers":{"file":"local_prod.csv","ProducerNames":["DEF"]}},
            "QA2":{"Users":{"file":"qa2_user.csv","Usernames":{}},
                   "Producers":{"file":"qa2_prod.csv","ProducerNames":["ALLSTATES HO and DW"]}},
            "UAT3":{"Users":{"file":"uat3_user.csv","Usernames":{}},
                   "Producers":{"file":"uat3_prod.csv","ProducerNames":["ALLSTATES HO and DW"]}},
            "UAT4":{"Users":{"file":"uat4_user.csv","Usernames":{}},
                   "Producers":{"file":"uat4_prod.csv","ProducerNames":["ALLSTATES HO and DW"]}}}


#Functions for creating, reading and writing to files 
def create_files():
    if(not path.exists("csvFiles")):
        os.mkdir("csvFiles")
    for env_name in env_files_plus_users.keys():    
        file_user = env_files_plus_users[env_name]['Users']['file']
        file_prod = env_files_plus_users[env_name]['Producers']['file']
        if not(path.exists(folder+file_user)):
            file_users= open(folder+file_user,"w")
            write_username_password(folder+file_user,env_files_plus_users[env_name]["Users"]["Usernames"])
            file_prods = open(folder+file_prod,"w")
            write_producer(folder+file_prod,env_files_plus_users[env_name]["Producers"]["ProducerNames"])
            file_prods.close()
            file_users.close()

#This function takes a file and user dictionary and writes the username and password to a csv file 
def write_username_password(file,user_dict):
    with open(file,'w',newline='') as csvfile:
        fieldnames = ['Username', 'Password']
        writer = DictWriter(csvfile,fieldnames=fieldnames)  
        if path.getsize(file) == 0:
            writer.writeheader()
        for user,password in user_dict.items():
            writer.writerow({'Username':user,'Password':password})

def add_user(user_name,password):
    global env_files_plus_users, file_name
    env_files_plus_users[env_used]['Users']['Usernames'][user_name] = password
    file_name = env_files_plus_users[env_used]['Users']['file']
    user_dict = env_files_plus_users[env_used]['Users']['Usernames']
    write_username_password(folder+file_name,user_dict)

def read_username_password():
        with open(folder+env_files_plus_users[env_used]['Users']['file'], newline='') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                env_files_plus_users[env_used]['Users']['Usernames'][row['Username']] = row["Password"]

def write_producer(fileName,prod_list):
    with open(fileName,'w',newline='') as csvfile:
        fieldnames = ['Producer']
        writer = DictWriter(csvfile,fieldnames=fieldnames)
        if path.getsize(fileName) == 0:
            writer.writeheader()
        for producer in prod_list:
            writer.writerow({'Producer':producer})

def add_producer(producer_name):
    global env_files_plus_users
    env_files_plus_users[env_used]['Producers']['ProducerNames'].append(producer_name)
    write_producer(folder+env_files_plus_users[env_used]['Producers']['file'],env_files_plus_users[env_used]['Producers']['ProducerNames'])

def read_producers():
    env_files_plus_users[env_used]['Producers']['ProducerNames'] = []
    with open(folder+env_files_plus_users[env_used]['Producers']['file'], newline='') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                env_files_plus_users[env_used]['Producers']['ProducerNames'].append(row["Producer"])
         
#Function for making the GUI
def make_window():
    global user_name,date_chosen,env_used,state_chosen,producer_selected,create_type,browser_chosen,line_of_business,add_custom,user_chosen
    sg.theme(THEME)
    userList = []
    browsers = ["Chrome","Edge"]
    y = datetime.today()+timedelta(days=65)
    default_date = y.strftime("%m/%d/%Y").split("/")
    default_date = (int(default_date[0]),int(default_date[1]),int(default_date[2]))
    LOB = ["Dwelling Property","Homeowners"]
    STATES = {"Connecticut":"CT","Illinois":"IL","Maine":"ME","Massechusetts":"MA","New Hampshire":"NH","New Jersey":"NJ","New York":"NY","Rhode Island":"RI"}

    new_app_layout = [  [sg.Text('Enter Information for Creating An Application')],
                        [sg.Text()],
                        [sg.Text('Username'), sg.DropDown(userList,key="-ULIST-",size =(20,1))],
                        [sg.Button("Delete User",key="-REMU-")],
                        [sg.Text()],
                        [sg.Text("Select Producer"),sg.DropDown(list(env_files_plus_users[env_used]["Producers"]["ProducerNames"]),size=(TEXTLEN,1),key="-PRODUCER-")],
                        [sg.Button("Delete Producer",key="-REMPROD-")],
                        [sg.Text()],
                        [sg.Text("Select State"),sg.DropDown(list(STATES.keys()),key="-STATE-"),sg.Checkbox(text="Use Custom Address",key="ADD_CHECK")],
                        [sg.Text("Select Line of Business"),sg.DropDown(LOB,key="-LOB-")],
                        [sg.Text()],
                        [sg.Text("Enter Date or Select Date Below")],
                        [sg.Input(key='-IN4-', size=(20,1)), sg.CalendarButton('Date Select', close_when_date_chosen=True ,target='-IN4-', format='%m/%d/%Y', default_date_m_d_y=default_date)],
                        [sg.Text()],
                        [sg.Text("Insured Name")],
                        [sg.Text('First Name'), sg.InputText(size=(TEXTLEN,1), key = "-FIRST-")],
                        [sg.Text('Last Name'), sg.InputText(size=(TEXTLEN,1), key="-LAST-")],
                        [sg.Text("Create Quote,Applicaiton or Policy"), sg.DropDown(["Quote","Application","Policy"],default_value="Application",key="-CREATE-")],
                        [sg.Text()],
                        [sg.Button('Submit'), sg.Button('Cancel')],
                        ]
    
    add_address_layout= [
                        [sg.Text("")],
                        [sg.Text("Address"),sg.InputText(size = (TEXTLEN,1), key = "-CADD-")],
                        [sg.Text("City"),sg.InputText(size = (TEXTLEN,1), key = "-CITY-")],
                        [sg.Button("Add Address",key="-ADDRESS-")],
                        [sg.Text()],
                        [sg.Text("Address: "),sg.Text(key = "ADD_DISP")],
                        [sg.Text("City: "),sg.Text(key = "CITY_DISP")],
                        ]
    
    create_producer_layout = [
                        [sg.Text()],
                        [sg.Text("Add Producer Name")],
                        [sg.InputText(size = (TEXTLEN,1))],
                        ]
    
    new_user_layout = [
                        [sg.Text()],
                        [sg.Text('Add User')],
                        [sg.Text("Username"),sg.InputText(do_not_clear=False,size=(TEXTLEN,1),key="USER")],
                        [sg.Text("Password"),sg.InputText(do_not_clear=False,size=(TEXTLEN,1),key="PASS")],
                        [sg.Button("Add User",key="-ADDU-")],
                        [sg.Text()],
                        [sg.Text('Add Producer')],
                        [sg.Text("Producer Name"),sg.InputText(do_not_clear=False,size=(TEXTLEN,1),key="-PROD-")],
                        [sg.Button("Add Producer",key="-ADDP-")],
                        ]
                        
    exist_app_layout = [[sg.Text('Enter Information for An Existing Application')],
                        [sg.Text("Application Number"), sg.InputText(size=(TEXTLEN,1))]
                        ]


    layout = [[sg.Text('Andover Automation', size=(38, 1), justification='center', font=("Helvetica", 16), relief=sg.RELIEF_RIDGE, key='-TEXTHEADING-', enable_events=True)]]
    layout += [[sg.Text('Select Local or QA Environment'), sg.DropDown(list(gw_environment.keys()),key="-ENVLIST-"), sg.Button("Update", key = "UPDATE")],
               [sg.Text('Select Browser'), sg.DropDown(browsers, key = "BROWSER")],
               [sg.HorizontalSeparator()]]
    layout+=[[sg.TabGroup([[  sg.Tab('Creating New Applications', new_app_layout),
                               sg.Tab('Add Users and Producers', new_user_layout),
                               #sg.Tab('Create Producer for All States', create_producer_layout),
                               sg.Tab('Add Custom Address', add_address_layout),
                               ]],key = "-TABGROUP-",expand_x=True, expand_y=True)]]

    # Create the Window
    window = sg.Window('Automation for Andover', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel or exit
            break

        for value in values:
            print(values[value])

        first_name= values["-FIRST-"]
        last_name = values["-LAST-"]
        user_name = values["USER"]
        password = values["PASS"]
        selectedUser = values["-ULIST-"]
        selectedEnviron = values["-ENVLIST-"]
        add_prod = values['-PROD-']
        producer = values["-PRODUCER-"]
        doc_type = values["-CREATE-"]
        city = values["-CITY-"]
        addr = values["-CADD-"]
        browser = values["BROWSER"]
        cust_addr = values["ADD_CHECK"]

        if event == "UPDATE" and selectedEnviron !='' and (selectedEnviron =="QA" or selectedEnviron == 'Local' or selectedEnviron == 'UAT3' or selectedEnviron == 'UAT4'or selectedEnviron == 'QA2'):
            env_used = selectedEnviron
            read_username_password()
            read_producers()
            userList = list(env_files_plus_users[env_used]["Users"]["Usernames"].keys())
            window["-ULIST-"].update(values = userList)
            window["-PRODUCER-"].update(values = env_files_plus_users[env_used]["Producers"]["ProducerNames"])
            window.refresh()
   
        if event == "-ADDU-" and selectedEnviron!= '':
            add_user(user_name,password)
            userList = list(env_files_plus_users[env_used]["Users"]["Usernames"].keys())
            window["-ULIST-"].update(values = userList)
            window.refresh()

        if event == "-ADDP-" and selectedEnviron!= '':
            add_producer(add_prod)
            prodList = env_files_plus_users[env_used]["Producers"]["ProducerNames"]
            window["-PRODUCER-"].update(values = prodList)
            window.refresh()
                    
        if event == "-REMU-" and len(env_files_plus_users[env_used]["Users"]["Usernames"].keys()) > 0:
            del env_files_plus_users[env_used]["Users"]["Usernames"][selectedUser]
            userList = env_files_plus_users[env_used]["Users"]["Usernames"]
            write_username_password(folder+env_files_plus_users[env_used]["Users"]["file"],userList)
            window["-ULIST-"].update(values = list(userList.keys()))
            window.refresh()

        if event == "-REMPROD-" and len(env_files_plus_users[env_used]["Producers"]["ProducerNames"]) > 0:
            env_files_plus_users[env_used]["Producers"]["ProducerNames"].remove(producer)
            prod_list = env_files_plus_users[env_used]["Producers"]["ProducerNames"]
            write_producer(folder+env_files_plus_users[env_used]["Producers"]["file"],prod_list)
            window["-PRODUCER-"].update(values = prod_list)
            window.refresh()
        
        if event == "-ADDRESS-":
            custom_address["Address"] = addr
            custom_address["City"] = city
            window["ADD_DISP"].update(value = addr)
            window["CITY_DISP"].update(value = city)
            window.refresh()

        if event == "Submit" and first_name and last_name and selectedUser and selectedEnviron and producer and browser and date_chosen and values["-IN4-"]:
            line_of_business = values["-LOB-"]
            browser_chosen = browser
            state_chosen = STATES[values["-STATE-"]]
            date_chosen = values["-IN4-"]
            producer_selected = producer
            create_type = doc_type
            user_chosen = selectedUser
            if(cust_addr):
                custom_address["Flag"] = True
            window.close()
            return first_name,last_name,selectedUser
    window.close()

#*function for login
def login(browser,user = "admin",password = "Not9999!"):
    waitPageLoad(browser)
    find_Element(browser,"j_username").send_keys(user)
    find_Element(browser,"j_password").send_keys(password + Keys.RETURN)    

#*function for finding elements in the browser
def find_Element(browser,browser_Element, id = By.ID):
    elem = browser.find_element(id,browser_Element)
    return elem
  
def delete_quote(browser):
    #delete created Quote
    find_Element(browser,"Delete").click()
    find_Element(browser,"dialogOK").click()
    
def remove_javascript(browser):
    element_used = "js_error_list"
    script = """
        const parent = document.getElementById("js_error_list");
        if(parent != null)
        {
            parent.style.display = "none";
        }
    """
    try:
        t = find_Element(browser,element_used).is_displayed()
        if(t == True):
            print("executed javascript to remove errors")
            browser.execute_script(script)
    except:
        pass
    finally:
        pass

#*function used for waiting for page to load after a button is clicked and the page has to refresh
def waitPageLoad(browser):
    remove_javascript(browser)
    script = "return window.seleniumPageLoadOutstanding == 0;"
    WebDriverWait(browser, 60).until(lambda browser:browser.execute_script(script)) 
    
def run_verify_address(browser):
    script = "InsuredMailingAddr.verify();"
    lambda browser:browser.execute_script(script)

def copy_to_property(browser,addr,city,state):
    find_Element(browser,"InsuredResidentAddr.Addr1").send_keys(addr)
    find_Element(browser,"InsuredResidentAddr.City").send_keys(city)
    Select(find_Element(browser,"InsuredResidentAddr.StateProvCd")).select_by_value(state)

def copy_to_mailing(browser,addr,city,state):
    find_Element(browser,"InsuredMailingAddr.Addr1").send_keys(addr)
    find_Element(browser,"InsuredMailingAddr.City").send_keys(city)
    Select(find_Element(browser,"InsuredMailingAddr.StateProvCd")).select_by_value(state)

def underwriting_questions(browser):
    no_value = "NO"
    y = datetime.today()+timedelta(days=60)
    producer_inspection_date = y.strftime("%m/%d/%Y")
    find_Element(browser,"Wizard_Underwriting").click()
    waitPageLoad(browser)
    
    if(line_of_business == "Homeowners"):
        if not(state_chosen == 'IL' or state_chosen == 'ME' or state_chosen == 'MA' or state_chosen == "NH" or state_chosen == 'NJ' or state_chosen == "NY" or state_chosen == "CT"):
            find_Element(browser,"Question_InspectorName").send_keys("No")
            Select(find_Element(browser,"Question_IslandHome")).select_by_visible_text("No")
        if not(state_chosen == 'IL'):
            Select(find_Element(browser,"Question_IsolatedProperty")).select_by_visible_text("No")
        if not(state_chosen == 'IL' or state_chosen == "NH" or state_chosen == "MA" or state_chosen == "NY" or state_chosen == "CT" or state_chosen == "RI"):
            Select(find_Element(browser,"Question_IslandProperty")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_PrevKnown")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_PrevDiscussed")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_OtherInsurance")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_VacantOrOccupied")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_OnlineHome")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_SeasonalHome")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_SolarPanels")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_FrameDwellings")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_DayCareOnPremises")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_UndergraduateStudents")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_DogsCare")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_ElectricalService")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_WiringInUse")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_StoveOnPremises")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_OilHeated")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_PoolOnPremises")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_TrampolineOnPremises")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_AnyOutbuildings")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_CancelledRecently")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_ArsonConvicted")).select_by_visible_text("No")
        Select(find_Element(browser,"Question_AnyLapsePast")).select_by_value("No-New Purchase")
        find_Element(browser,"Question_PurchasePrice").send_keys(500000)
        #find_Element(browser,"Question_PriorCarrier").send_keys("No")
        find_Element(browser,"Question_ClaimsRecently").send_keys(0)

    if(line_of_business == "Dwelling Property"):
        Select(find_Element(browser,"Question_PolicyKnownPersonally")).select_by_value(no_value)
        Select(find_Element(browser,"Question_PolicyOtherIns")).select_by_value(no_value)
        Select(find_Element(browser,"Question_PolicyArson")).select_by_value(no_value )
        Select(find_Element(browser,"Question_RiskNumber1PrevDisc")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1Vacant")).select_by_value(no_value)
        if not(state_chosen == 'IL'):
            Select(find_Element(browser,"Question_RiskNumber1OnlineHome")).select_by_value(no_value)
            Select(find_Element(browser,"Question_RiskNumber1Isolated")).select_by_value(no_value)
            Select(find_Element(browser,"Question_RiskNumber1Island")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1Seasonal")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1SolarPanels")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1Adjacent")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1ChildCare")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1OtherBusiness")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1Undergrad")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1DogsAnimals")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1Electrical")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1EdisonFuses")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1Stove")).select_by_value("No")
        Select(find_Element(browser,"Question_RiskNumber1OilHeated")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1Pool")).select_by_value("No")
        Select(find_Element(browser,"Question_RiskNumber1Trampoline")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1Outbuildings")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1InsDeclined")).select_by_value(no_value)
        Select(find_Element(browser,"Question_RiskNumber1Lapse")).select_by_value("No-New purchase")
        find_Element(browser,"Question_RiskNumber1NumClaims").send_keys(0)
        if(state_chosen == 'MA'):
            find_Element(browser,"Question_MAFireRiskNumber1PurchaseDate").send_keys("01/01/2022")
            find_Element(browser,"Question_MAFireRiskNumber1PurchasePrice").send_keys("100000")
            find_Element(browser,"Question_MAFireRiskNumber1EstimatedValue").send_keys("150000")
            Select(find_Element(browser,"Question_MAFireRiskNumber1ValuationMethod")).select_by_value("Replacement Cost")
            Select(find_Element(browser,"Question_MAFireRiskNumber1AppraisalMethod")).select_by_value("Professional Appraisal")
            Select(find_Element(browser,"Question_MAFireRiskNumber1OtherFireInsuranceApp")).select_by_value(no_value)
            Select(find_Element(browser,"Question_MAFireRiskNumber1OtherFireInsuranceActive")).select_by_value(no_value)
            Select(find_Element(browser,"Question_MAFireRiskNumber1FireInPast")).select_by_value(no_value)
            Select(find_Element(browser,"Question_MAFireRiskNumber1PropertyForSale")).select_by_value(no_value)
            Select(find_Element(browser,"Question_MAFireRiskNumber1ApplicantMortgageeCrime")).select_by_value(no_value)
            Select(find_Element(browser,"Question_MAFireRiskNumber1ShareholderTrusteeCrime")).select_by_value(no_value)
            Select(find_Element(browser,"Question_MAFireRiskNumber1MortgagePaymentsDelinquent")).select_by_value(no_value)
            Select(find_Element(browser,"Question_MAFireRiskNumber1RealEstateTaxesDelinquent")).select_by_value(no_value)
            Select(find_Element(browser,"Question_MAFireRiskNumber1CodeViolations")).select_by_value(no_value)

        if(line_of_business == "Businessowners"):
            Select(find_Element(browser,"Question_01CoverageCancellation")).select_by_value("No")
            find_Element(browser,"Question_03PreviousCarrierPropertyLimitsPremium").send_keys("No")
            Select(find_Element(browser,"Question_08NumLosses")).select_by_value("0")
            find_Element(browser,"Question_05ProducerName").send_keys("No")
            find_Element(browser,"Question_06ProducerInspectionDt").send_keys(producer_inspection_date)
            Select(find_Element(browser,"Question_09Broker")).select_by_value("No")
            
     #click the save button
    find_Element(browser,"Save").click()
    waitPageLoad(browser)

    if line_of_business == "Dwelling Property" and state_chosen == "RI":
        find_Element(browser,"Question_RiskNumber1InspectorName").send_keys("No")
        find_Element(browser,"Save").click()

def core_coverages(browser):
    find_Element(browser,"Wizard_Risks").click()
    waitPageLoad(browser)

    Select(find_Element(browser,"Building.ConstructionCd")).select_by_value("Frame")
    find_Element(browser,"Building.YearBuilt").send_keys(2020)

    #select entity type
    if(line_of_business == "Dwelling Property"):
        Select(find_Element(browser,"Building.OccupancyCd")).select_by_value("Owner occupied dwelling")
        Select(find_Element(browser,"Building.Seasonal")).select_by_value("No")
        Select(find_Element(browser,"Risk.TypeCd")).select_by_value("DP2")
        find_Element(browser,"Building.BuildingLimit").send_keys(300000)
        Select(find_Element(browser,"Building.StandardDed")).select_by_value("500")
        Select(find_Element(browser,"Building.NumOfFamilies")).select_by_value("1")
        if(state_chosen == "NJ"):
            Select(find_Element(browser,"Building.DistanceToHydrant")).select_by_value("1000")

    if(line_of_business == "Homeowners"):
        Select(find_Element(browser,"Building.OccupancyCd")).select_by_value("Primary Residence")
        find_Element(browser,"Building.CovALimit").send_keys(300000)
        if(state_chosen != "NY"):
            find_Element(browser,"Building.CovCLimit").send_keys(250000)
        Select(find_Element(browser,"Building.CovELimit")).select_by_value("300000")
        Select(find_Element(browser,"Building.CovFLimit")).select_by_value("2000")
        Select(find_Element(browser,"Building.StandardDed")).select_by_value("1000")
        Select(find_Element(browser,"Building.NumOfFamilies")).select_by_value("1")
        if(state_chosen == "NJ"):
            Select(find_Element(browser,"Building.DistanceToHydrant")).select_by_value("1000")
            find_Element(browser,"Building.TerritoryCd").send_keys("1")
            Select(find_Element(browser,"Risk.WorkersCompInd")).select_by_value("100000")
            Select(find_Element(browser,"Risk.WorkersCompEmployees")).select_by_value("none")
            
            
    if(line_of_business == "Businessowners"):
        Select(find_Element(browser,"Building.BuildingClassDescription")).select_by_value("More than 33% Office")
        Select(find_Element(browser,"Building.ContentClassDescription")).select_by_value("None - Building Owner only")
        Select(find_Element(browser,"Risk.PremisesAlarm")).select_by_value("None")
        find_Element(browser,"Risk.ListOfTenantsAndOccupancy").send_keys("No")
        find_Element(browser,"Building.BuildingLimit").send_keys(500000)
        find_Element(browser,"Risk.SqFtArea").send_keys(2000)
        find_Element(browser,"Risk.NumOfStories").send_keys(3)
        Select(find_Element(browser,"Risk.BasementInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.BldgCentralHeatInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.RoofUpdatedIn15YrsInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.AdequateSmokeDetInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.BldgOccGt75PctInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.EgressFromAllUnitsInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.FrameClearance15ftInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.MaintProgramInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.CircuitBreakerProtectionInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.StabLokCircuitInd")).select_by_value("No")
        Select(find_Element(browser,"Risk.SpaceHeatersInd")).select_by_value("No")
    
     #click the save button
    find_Element(browser,"Save").click()

def billing(browser):
    waitPageLoad(browser)
    find_Element(browser,"Wizard_Review").click()
    
    script1 = "document.getElementById('BasicPolicy.PayPlanCd_9').checked = true;"
    browser.execute_script(script1)
    waitPageLoad(browser) 
    #!find_Element(browser,"BasicPolicy.PayPlanCd_9").click()
    #click the save button
    find_Element(browser,"Save").click()
    waitPageLoad(browser)

def save(browser):
    find_Element(browser,"Save").click()

def click_radio(browser):
    e_name = "QuoteCustomerClearingRef"
    table = browser.find_elements(By.NAME,e_name)
    radio_number = len(table)
    my_value = e_name+"_"+str(radio_number)
    find_Element(browser,my_value).click()
 
def create_new_quote(browser,date,state,producer,first_name,last_name,address,city,test:bool):
    #New Quote
    find_Element(browser,"QuickAction_NewQuote_Holder").click()
    find_Element(browser,"QuickAction_EffectiveDt").send_keys(date)

    #sleep needed to enter value 
    waitPageLoad(browser)
    #State Select
    #!find_Element(browser,"NEW QUOTE",By.LINK_TEXT).send_keys(state)
    Select(find_Element(browser,"QuickAction_StateCd")).select_by_value(state)
    Select(find_Element(browser,"QuickAction_CarrierGroupCd")).select_by_value(CARRIER)
    find_Element(browser,"QuickAction_NewQuote").click()

    find_Element(browser,line_of_business,By.LINK_TEXT).click()

    selectedAgent = [user_chosen for user in agent_list if user_chosen == user]

    if(len(selectedAgent) == 0):
        find_Element(browser,"ProviderNumber").send_keys(producer)

    #select entity type
    if(line_of_business == "Dwelling Property" or line_of_business == "Businessowners"):
        Select(find_Element(browser,"Insured.EntityTypeCd")).select_by_value("Individual")
    
    if not(state_chosen == "NJ" or state == "MA" or state_chosen == "NY" or state_chosen == "CT" or state_chosen == "RI"):
        Select(find_Element(browser,"InsuredPersonal.OccupationClassCd")).select_by_value("Other")
        find_Element(browser,"InsuredPersonal.OccupationOtherDesc").send_keys("No")

    if state_chosen == "NY" and line_of_business == "Homeowners":
        Select(find_Element(browser,"BasicPolicy.GeographicTerritory")).select_by_value("Upstate")

    find_Element(browser,"InsuredName.GivenName").click()
    find_Element(browser,"InsuredName.GivenName").send_keys(first_name)
    find_Element(browser,"InsuredName.Surname").send_keys(last_name)

    if(line_of_business != "Businessowners"):
        find_Element(browser,"InsuredPersonal.BirthDt").send_keys("01/01/1980")
        find_Element(browser,"InsuredCurrentAddr.Addr1").send_keys(address)
        find_Element(browser,"InsuredCurrentAddr.City").send_keys(city)
        Select(find_Element(browser,"InsuredCurrentAddr.StateProvCd")).select_by_value(state)

    #*Select state here
    if(line_of_business == "Businessowners"): 
        find_Element(browser,"InsuredMailingAddr.Addr1").send_keys(address)
        find_Element(browser,"InsuredMailingAddr.City").send_keys(city)
        Select(find_Element(browser,"InsuredMailingAddr.StateProvCd")).select_by_value(state)

    #*Adding geographic territory and policy carrier here
    if(state_chosen == "NY" and line_of_business == "Homeowners"):
        Select(find_Element(browser,"BasicPolicy.GeographicTerritory")).select_by_value("Metro")
        Select(find_Element(browser,"BasicPolicy.PolicyCarrierCd")).select_by_value("MMFI")

    #!Select by
    waitPageLoad(browser)
    if(line_of_business == "Businessowners"):
        find_Element(browser,"DefaultAddress").click()

    if(line_of_business != "Businessowners"):
        copy_to_property(browser,address,city,state)
        copy_to_mailing(browser,address,city,state)
        waitPageLoad(browser)

    #*First and Last names copied to input fields here
    find_Element(browser,"InsuredName.MailtoName").send_keys(f"{first_name} {last_name}")
    find_Element(browser,"Insured.InspectionContact").send_keys(f"{first_name} {last_name}")

    #*Phone Type, Phone number, and email entered here
    Select(find_Element(browser,"InsuredPhonePrimary.PhoneName")).select_by_value("Mobile")
    find_Element(browser,"InsuredPhonePrimary.PhoneNumber").send_keys(5555555555)
    find_Element(browser,"InsuredEmail.EmailAddr").send_keys("test@mail.com")
    waitPageLoad(browser)
    if(user_chosen == "admin"):
        find_Element(browser,"InsuredInsuranceScore.OverriddenInsuranceScore").send_keys("950")

    #*click the save button
    find_Element(browser,"Save").click()
    waitPageLoad(browser)
    core_coverages(browser)
    waitPageLoad(browser)
    #!find_Element(browser,"Closeout").click()
    if(create_type == "Application" or create_type == "Policy"):
        if user_chosen != 'admin':
            click_radio(browser)
        find_Element(browser,"Bind").click()

        if(state_chosen == "NJ" and line_of_business == "Homeowners"):
            find_Element(browser,"Wizard_Risks").click()
            waitPageLoad(browser)
            Select(find_Element(browser,"Building.InspectionSurveyReqInd")).select_by_value("No")
            #click the save button
            find_Element(browser,"Save").click()

        underwriting_questions(browser)
        billing(browser)
    print("Create Type: " + create_type)

    if(create_type == "Policy"):
        find_Element(browser,"Closeout").click()
        waitPageLoad(browser)
        Select(find_Element(browser,"TransactionInfo.PaymentTypeCd")).select_by_value("None")
        find_Element(browser,"TransactionInfo.SignatureDocument").click()
        find_Element(browser,"PrintApplication").click()
        sleep(30)
        find_Element(browser,"Process").click()
        waitPageLoad(browser)

    sleep(10)

    if(test == True and create_type != "Policy"):
        delete_quote(browser)

#TODO - make a function for using applications that have already been created
def get_created_application(applicaiton_number:str):
    pass

#* This function is used to decide whether to use chrome or edge browser
def load_page():
    if(browser_chosen == "Chrome"):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        browser = webdriver.Chrome(options = chrome_options)
    else:
        edge_options = webdriver.edge.options.Options()
        edge_options.add_experimental_option("detach", True)
        browser = webdriver.Edge(options = edge_options)
    browser.get(gw_environment[env_used])
    assert "Guidewire InsuranceNow™ Login" in browser.title
    return browser

def get_password(user):
    password = env_files_plus_users[env_used]["Users"]["Usernames"][user]
    return password

def main():
    create_files()

    first_name, last_name, user_name = make_window()

    password = get_password(user_name)
    print("Username: "+user_name + "  Password: " + password)

    browser = load_page()
   
    try:
        login(browser,user_name,password)
    except:
        raise Exception("Incorrect username and/or password")

    #*Tab to click  for recent quotes, applicaitons, and policies
    find_Element(browser,"Tab_Recent").click()
    state1,CITY,ADDRESS = addresses[str(state_chosen+"1")]
    custom_city = custom_address["City"]
    custom_add = custom_address["Address"]
    if(custom_address["Flag"]):
        create_new_quote(browser,date_chosen,state1,producer_selected,first_name,last_name,custom_add,custom_city,TEST)
    else:
        create_new_quote(browser,date_chosen,state1,producer_selected,first_name,last_name,ADDRESS,CITY,TEST)

    if(TEST == True):
        sleep(5)
        browser.quit()

if __name__ == '__main__':
    main()