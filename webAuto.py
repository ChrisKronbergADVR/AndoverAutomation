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
import requests
from threading import Thread
import itertools
import time

#*Constants
TEST = False
THEME = "TanBlue"
TEXTLEN = 25
CARRIER = "ADVR"

#*Global Variables
gw_environment ={"Local":"http://localhost:9090","QA":"https://qa-advr.iscs.com/","UAT3":"https://uat3-advr.in.guidewire.net/innovation?saml=off","UAT4":"https://uat4-advr.in.guidewire.net/innovation","QA2":"https://qa2-acx-advr.in.guidewire.net/innovation"}
#,"Model":"https://login.model.andovercompanies.com","Model 2":"https://login.test.andovercompanies.com","Model 3":"https://login.dev.andovercompanies.com"
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
custom_address = {"Address":"","Address2":"","City":"","Flag":False}
user_chosen = "admin"
verified = False
payment_plan_most = {"Mortgagee Direct Bill Full Pay":"BasicPolicy.PayPlanCd_1","Automated Monthly":"BasicPolicy.PayPlanCd_2","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_3","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_5","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_6","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_7","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_8","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_9","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_10"}
payment_plan_bop = {"Mortgagee Direct Bill Full Pay":"BasicPolicy.PayPlanCd_1","Automated Monthly":"BasicPolicy.PayPlanCd_2","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_3","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_5","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_6","Direct Bill 9 Pay":"BasicPolicy.PayPlanCd_7","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_8","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_9","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_10","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_11"}
payment_plan_bop_wrong = {"Mortgagee Direct Bill Full Pay":"BasicPolicy.PayPlanCd_1","Automated Monthly":"BasicPolicy.PayPlanCd_2","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_3","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_5","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_6","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_7","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_8","Direct Bill 9 Pay":"BasicPolicy.PayPlanCd_9","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_10","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_11"}
payment_plan_pumb = {"Automated Monthly":"BasicPolicy.PayPlanCd_1","Bill To Other Automated Monthly":"BasicPolicy.PayPlanCd_2","Direct Bill 2 Pay":"BasicPolicy.PayPlanCd_3","Direct Bill 4 Pay":"BasicPolicy.PayPlanCd_4","Direct Bill 6 Pay":"BasicPolicy.PayPlanCd_5","Bill To Other 4 Pay":"BasicPolicy.PayPlanCd_6","Bill To Other 6 Pay":"BasicPolicy.PayPlanCd_7","Direct Bill Full Pay":"BasicPolicy.PayPlanCd_8","Bill To Other Full Pay":"BasicPolicy.PayPlanCd_9"}
pay_plan = ""

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
                   "Producers":{"file":"qa2_prod.csv","ProducerNames":[""]}},
            "UAT3":{"Users":{"file":"uat3_user.csv","Usernames":{}},
                   "Producers":{"file":"uat3_prod.csv","ProducerNames":[""]}},
            "UAT4":{"Users":{"file":"uat4_user.csv","Usernames":{}},
                   "Producers":{"file":"uat4_prod.csv","ProducerNames":[""]}},
            "Model":{"Users":{"file":"model_user.csv","Usernames":{}},
                   "Producers":{"file":"model_prod.csv","ProducerNames":[""]}},
            "Model 2":{"Users":{"file":"model2_user.csv","Usernames":{}},
                   "Producers":{"file":"model2_prod.csv","ProducerNames":[""]}},
            "Model 3":{"Users":{"file":"model3_user.csv","Usernames":{}},
                   "Producers":{"file":"model3_prod.csv","ProducerNames":[""]}}       
                   }

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
         
def verify_address(city,state,address1,address2=None):
    global verified
    verified = False

    if(address2 == None):
        address_validaiton_request = requests.post(f"""http://production.shippingapis.com/ShippingAPI.dll?API=Verify
                                                    &XML=<AddressValidateRequest USERID="005FSELF04917"><Address
                                                    ID="0"><Address1>{address1}</Address1>
                                                    <Address2></Address2><City>{city}</City><State>{state}</State>
                                                    <Zip5></Zip5><Zip4></Zip4></Address></AddressValidateRequest>""")
    else:
        address_validaiton_request = requests.post(f"""http://production.shippingapis.com/ShippingAPI.dll?API=Verify
                                                    &XML=<AddressValidateRequest USERID="005FSELF04917"><Address
                                                    ID="0"><Address1>{address1}</Address1>
                                                    <Address2>{address2}</Address2><City>{city}</City><State>{state}</State>
                                                    <Zip5></Zip5><Zip4></Zip4></Address></AddressValidateRequest>""")

    if(not address_validaiton_request.text.__contains__('Error')):
        verified = True

    return verified

#Function for making the GUI
def make_window():
    global user_name,date_chosen,env_used,state_chosen,producer_selected,create_type,browser_chosen,line_of_business,user_chosen,verified,number_of_addresses,pay_plan
    sg.theme(THEME)
    userList = []
    browsers = ["Chrome","Edge"]
    y = datetime.today()+timedelta(days=65)
    default_date = y.strftime("%m/%d/%Y").split("/")
    default_date = (int(default_date[0]),int(default_date[1]),int(default_date[2]))
    LOB = ["Dwelling Property","Homeowners","Businessowners","Personal Umbrella","Commercial Umbrella"]
    SUBTYPE = {"HO3":"HO3", "HO4":"HO4", "HO5":"HO5T4", "HO5 Superior": "HO5", "HO6":"HO6"}
    STATES = {"Connecticut":"CT","Illinois":"IL","Maine":"ME","Massechusetts":"MA","New Hampshire":"NH","New Jersey":"NJ","New York":"NY","Rhode Island":"RI"}

    new_app_layout = [  [sg.Text('Enter Information for Creating An Application')],
                        [sg.Text()],
                        [sg.Text('Username'), sg.DropDown(userList,key="-ULIST-",size =(20,1)),sg.Text("                      "),sg.Button("Delete User",size=(10,1),key="-REMU-")],
                        [sg.Text()],
                        [sg.Text("Select Producer"),sg.DropDown(list(env_files_plus_users[env_used]["Producers"]["ProducerNames"]),size=(TEXTLEN,1),key="-PRODUCER-"),sg.Text("     "),sg.Button("Delete Producer",size=(10,2),key="-REMPROD-")],
                        [sg.Text()],
                        [sg.Text("Select State"),sg.DropDown(list(STATES.keys()),key="-STATE-"),sg.Checkbox(text="Use Custom Address",enable_events=True,key="ADD_CHECK")],
                        [sg.Text("Address 1 (Required)",visible=False,justification="left",key = "-AddText1-",),sg.Text("   "),sg.InputText(size = (TEXTLEN,1),visible=False, key = "-CADD1-")],
                        [sg.Text("                      Address 2",visible=False,justification="left", key = "-AddText2-"),sg.InputText(size = (TEXTLEN,1),visible=False, key = "-CADD2-")],
                        [sg.Text("City (Required)",visible=False,justification="left", key = "-CityText-"),sg.Text("            "),sg.InputText(size = (TEXTLEN,1),visible=False, key = "-CITY-")],
                        [sg.Button("Verify Address",visible=False,key="BTN_VERIFY"),sg.Text("                "),sg.Text("Verified",text_color="green",visible=False,key = "-VERIFY_BUTTON-")],
                        [sg.Text()],
                        [sg.Text("Select Line of Business"),sg.DropDown(LOB,key="-LOB-",enable_events=True)],
                        [sg.Text("Select SubType", visible=False, key="-SUBTYPELABEL-"),sg.DropDown(list(SUBTYPE.keys()),key="-SUBTYPE-",default_value="HO5",enable_events=True, visible=False)],
                        [sg.Text("Multiple Locations? ", visible=False,key="-MULT-"),sg.DropDown(["Yes","No"],visible=False,default_value="No",enable_events=True,key="-MULTI-")],[sg.Text("Locations ", justification="left",visible=False,key="-NUMMULT-"),sg.DropDown([2,3,4,5],visible=False,default_value="2",key="-NUMLOC-")],
                        [sg.Text("Enter Date or Select Date Below")],
                        [sg.Input(key='-IN4-', size=(20,1)), sg.CalendarButton('Date Select', close_when_date_chosen=True ,target='-IN4-', format='%m/%d/%Y', default_date_m_d_y=default_date)],
                        [sg.Text()],
                        [sg.Text("Payment Plan: ", visible=True),sg.DropDown(list(payment_plan_most.keys()),visible=True,default_value="Direct Bill Full Pay",enable_events=True,key="-PAYPLAN-"),sg.DropDown(list(payment_plan_bop.keys()),visible=False,default_value="Direct Bill Full Pay",enable_events=True,key="-PAYPLANBOP-"),sg.DropDown(list(payment_plan_pumb.keys()),visible=False,default_value="Direct Bill Full Pay",enable_events=True,key="-PAYPLANPUMB-")],
                        [sg.Text("Insured Name")],
                        [sg.Text('First Name'), sg.InputText(size=(TEXTLEN,1), key = "-FIRST-")],
                        [sg.Text('Last Name'), sg.InputText(size=(TEXTLEN,1), key="-LAST-")],
                        [sg.Text("Create Quote,Application or Policy"), sg.DropDown(["Quote","Application","Policy"],default_value="Application",key="-CREATE-")],
                        [sg.Text()],
                        [sg.Button('Submit'), sg.Button('Cancel')],
                        ]

    add_address_layout= [
                        [sg.Text("")],
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
                        [sg.Text()],
                        ]
    
    create_producer_layout = [ 
                        [sg.Text('Create a Producer')],
                        [sg.Text("Producer Name"),sg.InputText(do_not_clear=False,key="-PROD_IN-")],
                        [sg.Button("Create Producer",key="-ADD_PROD-")]]
                        
    exist_app_layout = [[sg.Text('Enter Information for An Existing Application')],
                        [sg.Text("Application Number"), sg.InputText(size=(TEXTLEN,1))]
                        ]


    layout = [[sg.Text('Andover Automation', size=(38, 1), justification='center', font=("Helvetica", 16), relief=sg.RELIEF_RIDGE, key='-TEXTHEADING-', enable_events=True)]]
    layout += [[sg.Text('Select Local or QA Environment'), sg.DropDown(list(gw_environment.keys()),enable_events=True,key="-ENVLIST-")],
               [sg.Text('Select Browser'), sg.DropDown(browsers, key = "BROWSER")],
               [sg.HorizontalSeparator()]]
    layout+=[[sg.TabGroup([[  sg.Tab('Creating New Applications', new_app_layout),
                               sg.Tab('Add Users and Producers', new_user_layout),
                               sg.Tab('Create Producers', create_producer_layout),
                               #sg.Tab('Create Producer for All States', create_producer_layout),
                               #sg.Tab('Add Custom Address', add_address_layout),
                               ]],key = "-TABGROUP-",expand_x=True, expand_y=True)]]

    # sg.Button("Update", key = "UPDATE")
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
        addr = values["-CADD1-"]
        addr2 = values["-CADD2-"]
        browser = values["BROWSER"]
        cust_addr = values["ADD_CHECK"]
        state = values["-STATE-"]
        lob = values["-LOB-"]
        subType = SUBTYPE[values["-SUBTYPE-"]]
        multi = values["-MULTI-"]
        payment_p = values["-PAYPLAN-"]
        payment_p_bop = values["-PAYPLANBOP-"]
        payment_p_pumb = values["-PAYPLANPUMB-"]

        if event == "-ENVLIST-" and selectedEnviron !='' and (selectedEnviron =="QA" or selectedEnviron == 'Local' or selectedEnviron == 'UAT3' or selectedEnviron == 'UAT4'or selectedEnviron == 'QA2' or selectedEnviron =='Model'or selectedEnviron =='Model 2' or selectedEnviron =='Model 3'):
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

        if event == "BTN_VERIFY" and city and addr and state:
            verified = verify_address(city,STATES[state],addr)

            if verified:
                sg.popup_auto_close('Custom Address Has been Verified Successfully!')
                window["-VERIFY_BUTTON-"].update(visible = True)
                custom_address["Address"] = addr
                custom_address["City"] = city
                custom_address["Address2"] = addr2
                custom_address["Flag"] = True
            else:
                window["-VERIFY_BUTTON-"].update(visible = False)
                sg.popup_auto_close('This Address Has Not been Verified. Check the address and enter it again.')

        if  cust_addr:
            window["-AddText1-"].update(visible = True)
            window["-CADD1-"].update(visible = True)
            window["-AddText2-"].update(visible = True)
            window["-CADD2-"].update(visible = True)
            window["-CityText-"].update(visible = True)
            window["-CITY-"].update(visible = True)
            window["BTN_VERIFY"].update(visible = True)
            window.refresh()

        if  not cust_addr:
            window["-AddText1-"].update(visible = False)
            window["-CADD1-"].update(visible = False)
            window["-AddText2-"].update(visible = False)
            window["-CADD2-"].update(visible = False)
            window["-CityText-"].update(visible = False)
            window["-CITY-"].update(visible = False)
            window["BTN_VERIFY"].update(visible = False)
            window["-VERIFY_BUTTON-"].update(visible = False)
            window.refresh()

        if event == "-LOB-":
            if lob == "Businessowners":
                window["-PAYPLANBOP-"].update(visible = True)
                window["-PAYPLAN-"].update(visible = False)
                window["-PAYPLANPUMB-"].update(visible = False)
                window.refresh()
            elif lob == "Personal Umbrella" or lob == "Commercial Umbrella":
                window["-PAYPLANPUMB-"].update(visible = True)
                window["-PAYPLANBOP-"].update(visible = False)
                window["-PAYPLAN-"].update(visible = False)
                window.refresh()
            else:
                window["-PAYPLANBOP-"].update(visible = False)
                window["-PAYPLAN-"].update(visible = True)
                window["-PAYPLANPUMB-"].update(visible = False)
                window.refresh()

        if lob == "Dwelling Property":
            window["-MULT-"].update(visible = True)
            window["-MULTI-"].update(visible = True)
            window.refresh()
        else:
            window["-MULT-"].update(visible = False)
            window["-MULTI-"].update(visible = False)
            window.refresh()

        if lob == "Homeowners" or lob =="Personal Umbrella":
            window["-SUBTYPELABEL-"].update(visible=True)
            window["-SUBTYPE-"].update(visible=True)
            window.refresh()
        else:
            window["-SUBTYPELABEL-"].update(visible=False)
            window["-SUBTYPE-"].update(visible=False)
            window.refresh()

        if multi == "Yes":
            window["-NUMLOC-"].update(visible = True)
            window["-NUMMULT-"].update(visible=True)
        else:
            window["-NUMLOC-"].update(visible = False)
            window["-NUMMULT-"].update(visible = False)

        if event == "-ADDP-" and selectedEnviron!= '':
            add_producer(add_prod)
            prodList = env_files_plus_users[env_used]["Producers"]["ProducerNames"]
            window["-PRODUCER-"].update(values = prodList)
            window.refresh()
                    
        if event == "-REMU-" and len(env_files_plus_users[env_used]["Users"]["Usernames"].keys()) > 0 and selectedUser != "" :
            del env_files_plus_users[env_used]["Users"]["Usernames"][selectedUser]
            userList = env_files_plus_users[env_used]["Users"]["Usernames"]
            write_username_password(folder+env_files_plus_users[env_used]["Users"]["file"],userList)
            window["-ULIST-"].update(values = list(userList.keys()))
            window.refresh()

        if event == "-REMPROD-" and len(env_files_plus_users[env_used]["Producers"]["ProducerNames"]) > 0 and producer!="":
            env_files_plus_users[env_used]["Producers"]["ProducerNames"].remove(producer)
            prod_list = env_files_plus_users[env_used]["Producers"]["ProducerNames"]
            write_producer(folder+env_files_plus_users[env_used]["Producers"]["file"],prod_list)
            window["-PRODUCER-"].update(values = prod_list)
            window.refresh()
        
        if event == "-ADDRESS-":
            custom_address["Address"] = addr
            custom_address["Address2"] = addr2
            custom_address["City"] = city
            window["ADD_DISP"].update(value = addr)
            window["CITY_DISP"].update(value = city)
            window.refresh()

        if event == "Submit" and first_name and last_name and selectedUser and selectedEnviron and producer and browser and date_chosen and values["-IN4-"] and (custom_address["Flag"] or cust_addr == False):
            line_of_business = values["-LOB-"]         
            browser_chosen = browser
            state_chosen = STATES[values["-STATE-"]]
            date_chosen = values["-IN4-"]
            producer_selected = producer
            create_type = doc_type
            user_chosen = selectedUser
            if(line_of_business != "Businessowners"):
                #if line_of_business == "Homeowners":
                    #pay_plan = payment_plan + " "+state_chosen
                if line_of_business == "Personal Umbrella" or line_of_business == "Commercial Umbrella":
                    #pay_plan = payment_plan_pumb + " "+state_chosen
                    pay_plan = payment_p_pumb
                else:
                    pay_plan = payment_p
            else:
                #pay_plan = payment_plan_bop + " "+state_chosen
                pay_plan = payment_p_bop

            print(pay_plan)
            if(multi == "Yes" and lob == "Dwelling Property"):
                multiAdd = True
                number_of_addresses = values["-NUMLOC-"]
            else:
                number_of_addresses = 1
                multiAdd = False
            window.close()
            return first_name,last_name,selectedUser,multiAdd, subType
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

#*Functions for finding or sending values to input fields
def check_for_value(browser,element,value = None,visible_text:bool=False,keys=None):
    try:
        if(find_Element(browser,element).is_displayed()):
            if(keys != None):
                if(keys == "click"):
                    find_Element(browser,element).click()
                else:
                    find_Element(browser,element).send_keys(keys)
            if(visible_text):
                Select(find_Element(browser,element)).select_by_visible_text(value)
            else:
                Select(find_Element(browser,element)).select_by_value(value)
    except:
        pass

def click_radio_button(browser,element):
    try:
        if(find_Element(browser,element).is_displayed()):
            find_Element(browser,element).click()
    except:
        pass

def send_value(browser,element,value):
    try:
        if(find_Element(browser,element).is_displayed()):
            find_Element(browser,element).send_keys(value)
    except:
        pass

#*Removes the errors on webpage
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

def question_update(question,size):
    if(question.__contains__("1")):
        word = question.split("1")
        new_word =  word[0]+str(size)+word[1]
    return new_word

#* Function to add underwriting questions for each location
def gen_dwell_location_questions(browser,num):

    ques_dwell = ["Question_PolicyKnownPersonally","Question_PolicyOtherIns","Question_PolicyArson","Question_RiskNumber1PrevDisc","Question_RiskNumber1Vacant","Question_RiskNumber1OnlineHome"
                       ,"Question_RiskNumber1Isolated","Question_RiskNumber1Island","Question_RiskNumber1Seasonal","Question_RiskNumber1SolarPanels","Question_RiskNumber1Adjacent","Question_RiskNumber1ChildCare",
                       "Question_RiskNumber1OtherBusiness","Question_RiskNumber1Undergrad","Question_RiskNumber1DogsAnimals","Question_RiskNumber1Electrical","Question_RiskNumber1EdisonFuses","Question_RiskNumber1Stove",
                       "Question_RiskNumber1OilHeated","Question_RiskNumber1Pool","Question_RiskNumber1Trampoline","Question_RiskNumber1Outbuildings","Question_RiskNumber1InsDeclined","Question_MAFireRiskNumber1OtherFireInsuranceApp",
                       "Question_MAFireRiskNumber1OtherFireInsuranceActive","Question_MAFireRiskNumber1FireInPast","Question_MAFireRiskNumber1PropertyForSale","Question_MAFireRiskNumber1ApplicantMortgageeCrime",
                       "Question_MAFireRiskNumber1ShareholderTrusteeCrime","Question_MAFireRiskNumber1MortgagePaymentsDelinquent","Question_MAFireRiskNumber1RealEstateTaxesDelinquent","Question_MAFireRiskNumber1CodeViolations"]
    
    newDict = {1:ques_dwell}
    newArr = []

    gen_dewll_location_extra_questions(browser,1)
    if state_chosen == "RI":
        find_Element(browser,"Question_RiskNumber"+str(1)+"InspectorName").send_keys("No")

    if(num > 1):
        for loc in range(num-1):
            number = loc+2
            for question_name in ques_dwell:    
                if(question_name.__contains__("1")):
                    word = question_name.split("1")
                    newArr.append(word[0]+str(number)+word[1])
            newDict[number] = newArr
            if(state_chosen == "RI"):                                                                  
                find_Element(browser,"Question_RiskNumber"+str(number)+"InspectorName").send_keys("No")
            gen_dewll_location_extra_questions(browser,number)
  
            
    return newDict

def gen_dewll_location_extra_questions(browser,num):
    extra_dwell_questions = ["Question_RiskNumber1Lapse","Question_RiskNumber1NumClaims","Question_MAFireRiskNumber1PurchaseDate","Question_MAFireRiskNumber1PurchasePrice","Question_MAFireRiskNumber1EstimatedValue","Question_MAFireRiskNumber1ValuationMethod","Question_MAFireRiskNumber1AppraisalMethod"]
    updatedArr = []

    if(num >1):
        for question in extra_dwell_questions:
            updatedArr.append(question_update(question,num))
    else:
        updatedArr = extra_dwell_questions
    Select(find_Element(browser,updatedArr[0])).select_by_value("No-New purchase")
    find_Element(browser,updatedArr[1]).send_keys(0)
    if(state_chosen == 'MA'):
        find_Element(browser,updatedArr[2]).send_keys("01/01/2022")
        find_Element(browser,updatedArr[3]).send_keys("100000")
        find_Element(browser,updatedArr[4]).send_keys("150000")
        Select(find_Element(browser,updatedArr[5])).select_by_value("Replacement Cost")
        Select(find_Element(browser,updatedArr[6])).select_by_value("Professional Appraisal")
        
def underwriting_questions(browser,multi):
    y = datetime.today()+timedelta(days=60)
    producer_inspection_date = y.strftime("%m/%d/%Y")
    find_Element(browser,"Wizard_Underwriting").click()
    waitPageLoad(browser)

    questions_home = ["Question_IslandProperty","Question_IsolatedProperty","Question_IslandHome","Question_PrevKnown",
                 "Question_PrevDiscussed","Question_OtherInsurance","Question_VacantOrOccupied", "Question_OnlineHome", "Question_OnlineHome",
                 "Question_SeasonalHome", "Question_FrameDwellings", "Question_DayCareOnPremises", "Question_UndergraduateStudents","Question_SolarPanels","Question_UndergraduateStudents",
                 "Question_DogsCare", "Question_ElectricalService", "Question_WiringInUse", "Question_StoveOnPremises", "Question_OilHeated", "Question_PoolOnPremises",
                 "Question_TrampolineOnPremises","Question_AnyOutbuildings","Question_CancelledRecently","Question_ArsonConvicted"]

    if line_of_business =="Dwelling Property":
        if multi == True:
            dwell_questions = gen_dwell_location_questions(browser,number_of_addresses)
        else:
            dwell_questions = gen_dwell_location_questions(browser,1)

    if line_of_business == "Homeowners" or line_of_business == "Personal Umbrella":
        send_value(browser,"Question_InspectorName","Gadget")

        for question in questions_home:
            check_for_value(browser,question,"No",True)
        check_for_value(browser,"Question_AnyLapsePast","No-New Purchase",True)
        check_for_value(browser,"Question_ClaimsRecently",None,False,0)
        check_for_value(browser,"Question_PurchasePrice",None,False,500000)

    if(line_of_business == "Dwelling Property"):
        for key in range(len(dwell_questions.keys())):
            for question in dwell_questions[key+1]:
                check_for_value(browser,question,"No",True)

    if(line_of_business == "Businessowners" or line_of_business == "Commercial Umbrella"):
        Select(find_Element(browser,"Question_01CoverageCancellation")).select_by_visible_text("No")
        find_Element(browser,"Question_03PreviousCarrierPropertyLimitsPremium").send_keys("No")
        Select(find_Element(browser,"Question_08NumLosses")).select_by_value("0")
        find_Element(browser,"Question_05ProducerName").send_keys("No")
        find_Element(browser,"Question_06ProducerInspectionDt").send_keys(producer_inspection_date)
        Select(find_Element(browser,"Question_09Broker")).select_by_visible_text("No")
            
     #click the save button
    save(browser)
    waitPageLoad(browser)

def core_coverages(browser):
    
    core_values = ["Risk.ListOfTenantsAndOccupancy","Risk.BasementInd","Risk.BldgCentralHeatInd","Risk.CircuitBreakerProtInd","Risk.UndergradResidentInd",
                   "Risk.SpaceHeatersInd","Risk.FrameClearance15ftInd","Risk.ShortTermRent","Risk.MercantileOfficeOccupantsInd","Risk.ExcessLinesInd"]
    
    core_values_after = ["Risk.RoofUpdatedIn15YrsInd","Risk.AdequateSmokeDetInd","Risk.BldgOccGt75PctInd","Risk.EgressFromAllUnitsInd","Risk.MaintProgramInd"]

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

    if line_of_business == "Homeowners" or line_of_business == "Personal Umbrella":
        check_for_value(browser,"Building.OccupancyCd","Primary Residence")
        check_for_value(browser,"Building.CovALimit",None,False,300000)
        check_for_value(browser,"Building.CovCLimit",None,False,300000)
        check_for_value(browser,"Building.NumOfFamiliesSameFire","Less Than 5",False,None)
        check_for_value(browser,"Building.DistanceToHydrant","1000")
        #Select(find_Element(browser,"Building.OccupancyCd")).select_by_value("Primary Residence")
        #find_Element(browser,"Building.CovALimit").send_keys(300000)
        if(state_chosen == "CT"):
            Select(find_Element(browser,"Building.FuelLiability")).select_by_value("300000")
            Select(find_Element(browser,"Building.OilTankLocation")).select_by_value("none")
        #if(state_chosen != "NY"):
        #     find_Element(browser,"Building.CovCLimit").send_keys(250000)
        Select(find_Element(browser,"Building.CovELimit")).select_by_value("300000")
        Select(find_Element(browser,"Building.CovFLimit")).select_by_value("2000")
        Select(find_Element(browser,"Building.StandardDed")).select_by_value("1000")
        Select(find_Element(browser,"Building.NumOfFamilies")).select_by_value("1")
        if(state_chosen == "NJ"):
            Select(find_Element(browser,"Building.DistanceToHydrant")).select_by_value("1000")
            find_Element(browser,"Building.TerritoryCd").send_keys("1")
            Select(find_Element(browser,"Risk.WorkersCompInd")).select_by_value("100000")
            Select(find_Element(browser,"Risk.WorkersCompEmployees")).select_by_value("none")
            
            
    if line_of_business == "Businessowners" or line_of_business == "Commercial Umbrella":
        if(state_chosen == "NJ" or state_chosen == "NY"):
            Select(find_Element(browser,"Building.BuildingClassDescription")).select_by_value("75% or more Apartments")
            if state_chosen == "NJ":
                Select(find_Element(browser,"Building.DistanceToHydrant")).select_by_value("1000")
        else:
            Select(find_Element(browser,"Building.BuildingClassDescription")).select_by_value("67% or more Apartments")
        Select(find_Element(browser,"Building.ContentClassDescription")).select_by_value("None - Building Owner only")
        find_Element(browser,"Building.BuildingLimit").send_keys(900000)
        find_Element(browser,"Risk.SqFtArea").send_keys(2000)

        for value in core_values:
            check_for_value(browser,value,"No",False)

        check_for_value(browser,"Risk.PremisesAlarm","None",True)
        check_for_value(browser,"Risk.YrsInBusinessInd","1",True)
        
        if(state_chosen == "ME" or state_chosen == "MA" or state_chosen == "NH" or state_chosen=="CT"):
            find_Element(browser,"Building.NumOfApartmentCondoBuilding").send_keys(5)
            find_Element(browser,"Building.MaxNumOfAptCondoBetweenBrickWalls").send_keys(5)

        send_value(browser,"Risk.NumOfStories",3)
        send_value(browser,"Risk.ListOfTenantsAndOccupancy","None")

        save(browser)
        save(browser)
        waitPageLoad(browser)
        for value in core_values_after:
            check_for_value(browser,value,"No",False)
        
     #click the save button
    save(browser)

def billing(browser):
    waitPageLoad(browser)
    find_Element(browser,"Wizard_Review").click()
    waitPageLoad(browser)
    print(pay_plan)

    elements = browser.find_elements(By.NAME,"BasicPolicy.PayPlanCd")
    print(f"The number of payment plans is: {len(elements)}")
    for e in elements:
        val1 = e.get_attribute("value")
        try: 
            if val1.index(" "+state_chosen):
                value = val1.index(" "+state_chosen)
                val2 = val1[:value]
                if(val2 == pay_plan):
                    val = "//input[@value='"+val1+"' and @type='radio']"
                    find_Element(browser,val,By.XPATH).click()
                    break
        except:
            if(val1 == pay_plan):
                    val = "//input[@value='"+pay_plan+"' and @type='radio']"
                    find_Element(browser,val,By.XPATH).click()
                    break
    waitPageLoad(browser)
    if pay_plan.__contains__("Automated Monthly"):
        Select(find_Element(browser,"InstallmentSource.MethodCd")).select_by_value("ACH")
        waitPageLoad(browser)
        Select(find_Element(browser,"InstallmentSource.ACHStandardEntryClassCd")).select_by_value("PPD")
        Select(find_Element(browser,"InstallmentSource.ACHBankAccountTypeCd")).select_by_value("Checking")
        find_Element(browser,"InstallmentSource.ACHBankName").send_keys("Bank")
        find_Element(browser,"InstallmentSource.ACHBankAccountNumber").send_keys(123456789)
        find_Element(browser,"InstallmentSource.ACHRoutingNumber").send_keys("011000015")
        find_Element(browser,"BasicPolicy.PaymentDay").send_keys(15)
        find_Element(browser,"BasicPolicy.CheckedEFTForm").click()
    if pay_plan.__contains__("Bill To Other") or pay_plan.__contains__("Mortgagee"):
        find_Element(browser,"UWAINew").click()
        waitPageLoad(browser)
        if pay_plan.__contains__("Bill To Other"):
            Select(find_Element(browser,"AI.InterestTypeCd")).select_by_value("Bill To Other")
            waitPageLoad(browser)
        else:
            Select(find_Element(browser,"AI.InterestTypeCd")).select_by_value("First Mortgagee")
            Select(find_Element(browser,"AI.EscrowInd")).select_by_value("Yes")
            Select(find_Element(browser,"AI.BillMortgRnwlInd")).select_by_value("No")
        find_Element(browser,"AI.AccountNumber").send_keys(12345)
        find_Element(browser,"AI.InterestName").send_keys("First Last")
        find_Element(browser,"AIMailingAddr.Addr1").send_keys("1595 N Peach Ave")
        find_Element(browser,"AIMailingAddr.City").send_keys("Fresno")
        Select(find_Element(browser,"AIMailingAddr.StateProvCd")).select_by_value("CA")
        find_Element(browser,"AIMailingAddr.PostalCode").send_keys(93727)
        Select(find_Element(browser,"AIMailingAddr.RegionCd")).select_by_value("United States")

        try:
            find_Element(browser,"LinkReferenceInclude_0").click()
        except:
            try: 
                find_Element(browser,"LinkReferenceInclude_1").click()
            except:
                pass

        waitPageLoad(browser)
        save(browser)

    waitPageLoad(browser)

    #click the save button
    save(browser)
    waitPageLoad(browser)

def save(browser):
    find_Element(browser,"Save").click()

def click_radio(browser):
    e_name = "QuoteCustomerClearingRef"
    table = browser.find_elements(By.NAME,e_name)
    radio_number = len(table)
    my_value = e_name+"_"+str(radio_number)
    click_radio_button(browser,my_value)

def create_producer(browser):
    find_Element(browser,"Menu_Policy").click()

def submit_policy(browser):
    find_Element(browser,"Closeout").click()
    waitPageLoad(browser)
    Select(find_Element(browser,"TransactionInfo.PaymentTypeCd")).select_by_value("None")
    find_Element(browser,"TransactionInfo.SignatureDocument").click()
    find_Element(browser,"PrintApplication").click()
    sleep(30)
    find_Element(browser,"Process").click()
    waitPageLoad(browser)

def create_new_quote(browser,date,state:str,producer:str,first_name:str,last_name:str,address:str,city:str,multiLoc:bool,test:bool,subType:str):
    #New Quote
    find_Element(browser,"QuickAction_NewQuote_Holder").click()
    find_Element(browser,"QuickAction_EffectiveDt").send_keys(date)

    waitPageLoad(browser)
    #State Select
    browser.execute_script("document.getElementById('QuickAction_StateCd').value = '"+state+"';")
    #Select(find_Element(browser,"QuickAction_StateCd")).select_by_value(state)
    Select(find_Element(browser,"QuickAction_CarrierGroupCd")).select_by_value(CARRIER)
    browser.execute_script("document.getElementById('QuickAction_NewQuote').click()")
    #find_Element(browser,"QuickAction_NewQuote").click()

    if line_of_business == "Personal Umbrella":
        find_Element(browser,"Homeowners",By.LINK_TEXT).click()
    elif line_of_business == "Commercial Umbrella":
        find_Element(browser,"Businessowners",By.LINK_TEXT).click()
    else:
        find_Element(browser,line_of_business,By.LINK_TEXT).click()

    selectedAgent = user_chosen.lower()
    if(not(selectedAgent.__contains__("agent"))):
        find_Element(browser,"ProviderNumber").send_keys(producer)

    #select entity type
    if(line_of_business == "Dwelling Property" or line_of_business == "Businessowners" or line_of_business == "Commercial Umbrella"):
        Select(find_Element(browser,"Insured.EntityTypeCd")).select_by_value("Individual")
    
    waitPageLoad(browser)

    try:
        if(find_Element(browser,"InsuredPersonal.OccupationClassCd").is_displayed() == True):
            Select(find_Element(browser,"InsuredPersonal.OccupationClassCd")).select_by_value("Other")
            Select(find_Element(browser,"InsuredPersonal.OccupationClassCd")).select_by_value("Other")
            find_Element(browser,"InsuredPersonal.OccupationOtherDesc").send_keys("No")
    except:
        pass

    if state_chosen == "NY" and (line_of_business == "Homeowners" or line_of_business == "Personal Umbrella"):
        Select(find_Element(browser,"BasicPolicy.GeographicTerritory")).select_by_value("Upstate")

    find_Element(browser,"InsuredName.GivenName").click()
    find_Element(browser,"InsuredName.GivenName").send_keys(first_name)
    find_Element(browser,"InsuredName.Surname").send_keys(last_name)

    if (line_of_business == "Homeowners" or line_of_business == "Personal Umbrella") and subType:
        Select(find_Element(browser,"BasicPolicy.DisplaySubTypeCd")).select_by_value(subType)
    
    if line_of_business != "Businessowners" and line_of_business != "Commercial Umbrella":
        find_Element(browser,"InsuredPersonal.BirthDt").send_keys("01/01/1980")
        find_Element(browser,"InsuredCurrentAddr.Addr1").send_keys(address)
        find_Element(browser,"InsuredCurrentAddr.City").send_keys(city)
        Select(find_Element(browser,"InsuredCurrentAddr.StateProvCd")).select_by_value(state)

    #*Select state here
    if(line_of_business == "Businessowners" or line_of_business == "Commercial Umbrella"): 
        find_Element(browser,"InsuredMailingAddr.Addr1").send_keys(address)
        find_Element(browser,"InsuredMailingAddr.City").send_keys(city)
        Select(find_Element(browser,"InsuredMailingAddr.StateProvCd")).select_by_value(state)

    #*Adding geographic territory and policy carrier here
    if(state_chosen == "NY" and (line_of_business == "Homeowners" or line_of_business == "Personal Umbrella")):
        Select(find_Element(browser,"BasicPolicy.GeographicTerritory")).select_by_value("Metro")
        Select(find_Element(browser,"BasicPolicy.PolicyCarrierCd")).select_by_value("MMFI")

    waitPageLoad(browser)
    if line_of_business == "Businessowners" or line_of_business == "Commercial Umbrella":
        find_Element(browser,"DefaultAddress").click()

    if line_of_business != "Businessowners" and line_of_business != "Commercial Umbrella":
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
    if(user_chosen == "admin" and (line_of_business != "Businessowners" and line_of_business != "Commercial Umbrella")):
        find_Element(browser,"InsuredInsuranceScore.OverriddenInsuranceScore").send_keys("950")

    #*click the save button
    save(browser)
    waitPageLoad(browser)

    #multiple locations here
    
    if line_of_business != "Businessowners" and line_of_business != "Commercial Umbrella":
        core_coverages(browser)
        if(multiLoc == True and line_of_business == "Dwelling Property"):
            for i in range(number_of_addresses-1):
                find_Element(browser,"CopyRisk").click()
                save(browser)

    if(create_type == "Application" or create_type == "Policy"):
        waitPageLoad(browser)
        click_radio(browser)
        find_Element(browser,"Bind").click()
        
        if line_of_business == "Businessowners" or line_of_business == "Commercial Umbrella":
            core_coverages(browser)
      
        waitPageLoad(browser)
        if(state_chosen == "NJ" and (line_of_business == "Homeowners" or line_of_business == "Personal Umbrella")):
            find_Element(browser,"Wizard_Risks").click()
            waitPageLoad(browser)
            Select(find_Element(browser,"Building.InspectionSurveyReqInd")).select_by_value("No")
            #click the save button
            save(browser)

        start = time.perf_counter()
        underwriting_questions(browser,multiLoc)
        end = time.perf_counter()
        print("\n\n\n\n Time to complete: " + str(end-start) + " seconds \n\n\n\n\n")
        
        billing(browser)

        if line_of_business == "Personal Umbrella":
            find_Element(browser,"GetUmbrellaQuote").click()
            waitPageLoad(browser)
            find_Element(browser,"Wizard_UmbrellaLiability").click()
            Select(find_Element(browser,"Line.PersonalLiabilityLimit")).select_by_value("1000000")
            find_Element(browser,"Line.TotMotOwnLeasBus").send_keys(0)
            find_Element(browser,"Line.NumMotExcUmb").send_keys(0)
            find_Element(browser,"Line.NumHouseAutoRec").send_keys(0)
            find_Element(browser,"Line.NumOfYouthInexp").send_keys(0)
            if state_chosen == "NH":
                Select(find_Element(browser,"Line.RejectExcessUninsuredMotorists")).select_by_value("No")
                Select(find_Element(browser,"Line.UnderAutLiabPerOcc")).select_by_value("No")
            if state_chosen == "NJ" or state_chosen == "NY" or state_chosen == "RI" or state_chosen == "CT" or state_chosen == "IL" or state_chosen == "ME" or state_chosen == "MA":
                Select(find_Element(browser,"Line.UnderAutLiabPerOcc")).select_by_value("No")
            find_Element(browser,"Bind").click()
            find_Element(browser,"Wizard_Underwriting").click()
            Select(find_Element(browser,"Question_DiscussedWithUnderwriter")).select_by_value("NO")
            Select(find_Element(browser,"Question_DUIConvicted")).select_by_value("NO")
            Select(find_Element(browser,"Question_ConvictedTraffic")).select_by_value("NO")
            Select(find_Element(browser,"Question_WatercraftBusiness")).select_by_value("NO")
            Select(find_Element(browser,"Question_DayCarePremises")).select_by_value("NO")
            Select(find_Element(browser,"Question_UndergraduateStudents")).select_by_value("NO")
            Select(find_Element(browser,"Question_AnimalsCustody")).select_by_value("NO")
            Select(find_Element(browser,"Question_PoolPremises")).select_by_value("NO")
            Select(find_Element(browser,"Question_TrampolinePremises")).select_by_value("NO")
            Select(find_Element(browser,"Question_CancelledRecently")).select_by_value("NO")
            Select(find_Element(browser,"Question_BusinessPolicies")).select_by_value("NO")
            Select(find_Element(browser,"Question_OnlineHome")).select_by_value("NO")
            save(browser)
            find_Element(browser,"Wizard_Review").click()
            billing(browser)
            waitPageLoad(browser)
            save(browser)

            if create_type == "Policy":
                find_Element(browser,"Return").click()
                find_Element(browser,"policyLink0").click()
                submit_policy(browser)
                find_Element(browser,"Return").click()
                find_Element(browser,"policyLink0").click()
                billing(browser)
                #find_Element(browser,"Closeout").click()

        if line_of_business == "Commercial Umbrella":
            find_Element(browser,"GetUmbrellaQuote").click()
            waitPageLoad(browser)
            find_Element(browser,"Wizard_UmbrellaLiability").click()
            if state_chosen == "CT" or state_chosen == "NH" or state_chosen=="NY" or state_chosen == "RI":
                Select(find_Element(browser,"Line.CoverageTypeCd")).select_by_value("Businessowners Umbrella Liability")
            Select(find_Element(browser,"Line.CommercialLiabilityLimit")).select_by_value("1000000")
            Select(find_Element(browser,"Line.OwnedAutosInd")).select_by_value("No")
            Select(find_Element(browser,"Line.EmplLiabCovrInsured")).select_by_value("No")
            find_Element(browser,"Wizard_Policy").click()
            find_Element(browser,"Bind").click()
            find_Element(browser,"Wizard_Underwriting").click()
            Select(find_Element(browser,"Question_OtherLiab")).select_by_value("NO")
            Select(find_Element(browser,"Question_PriorCovCancelled")).select_by_value("NO")
            find_Element(browser,"Question_PreviousUmbrella").send_keys("ACME")
            save(browser)
            find_Element(browser,"Wizard_Review").click()
            billing(browser)
            find_Element(browser,"Navigate_Location_2").click()
            Select(find_Element(browser,"Location.UnderlyingEmplLimitConf")).select_by_value("Yes")
            find_Element(browser,"NextPage").click()
           
            if create_type == "Policy":
                find_Element(browser,"Return").click()
                find_Element(browser,"policyLink0").click()
                submit_policy(browser)
                find_Element(browser,"Return").click()
                find_Element(browser,"policyLink0").click()
                if pay_plan.__contains__("Bill To Other"):
                    billing(browser)
                #find_Element(browser,"Closeout").click()
            
    if(create_type == "Policy"):
        submit_policy(browser)

    sleep(5)

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

    check_for_value(browser,"details-button",keys="click")    
    check_for_value(browser,"proceed-link",keys="click")    
    waitPageLoad(browser)

    assert "Guidewire InsuranceNow™ Login" in browser.title
    return browser

def get_password(user):
    password = env_files_plus_users[env_used]["Users"]["Usernames"][user]
    return password

def main():
    create_files()

    first_name, last_name, user_name, multi, subType = make_window()

    password = get_password(user_name)
    print("Username: "+user_name + "  Password: " + password)

    browser = load_page()
    
    try:
        login(browser,user_name,password)
    except:
        raise Exception("Incorrect username and/or password")

    #*Tab to click  for recent quotes, applications, and policies
    find_Element(browser,"Tab_Recent").click()
    state1,CITY,ADDRESS = addresses[str(state_chosen+"1")]
    custom_city = custom_address["City"]
    custom_add = custom_address["Address"]
    if(custom_address["Flag"]):
        create_new_quote(browser,date_chosen,state1,producer_selected,first_name,last_name,custom_add,custom_city,multi,TEST, subType)
    else:
        create_new_quote(browser,date_chosen,state1,producer_selected,first_name,last_name,ADDRESS,CITY,multi,TEST, subType)

    if(TEST == True):
        sleep(5)
        browser.quit()

if __name__ == '__main__':
    main()