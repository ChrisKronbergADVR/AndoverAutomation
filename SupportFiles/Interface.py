import PySimpleGUI as sg
from datetime import datetime, timedelta
import threading
from SupportFiles.Address import Address
from SupportFiles.Application import Application
from SupportFiles.File import File
from SupportFiles.MultiLog import MultiLog


class Interface:
    VERSION = "0.1.1"
    TEXTLEN = 25
    THEME = "TanBlue"

    def __init__(self) -> None:
        self.gw_environment = {"Local": "https://localhost:9443", "QA": "https://qa-advr.iscs.com/", "GWCP QA": "https://advr-qa.mu-1-andromeda.guidewire.net/",  "QA2": "https://qa2-acx-advr.in.guidewire.net/innovation", "GWCP QA2": "https://advr-qa2.mu-1-andromeda.guidewire.net/", "UAT3": "https://uat3-advr.in.guidewire.net/innovation?saml=off",
                               "UAT4": "https://uat4-advr.in.guidewire.net/innovation"}

        self.payment_plan_most = {"Mortgagee Direct Bill Full Pay": "BasicPolicy.PayPlanCd_1", "Automated Monthly": "BasicPolicy.PayPlanCd_2", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_3", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_4", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_5",
                                  "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_6", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_7", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_8", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_9", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_10"}
        self.payment_plan_bop = {"Mortgagee Direct Bill Full Pay": "BasicPolicy.PayPlanCd_1", "Automated Monthly": "BasicPolicy.PayPlanCd_2", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_3", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_4", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_5",
                                 "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_6", "Direct Bill 9 Pay": "BasicPolicy.PayPlanCd_7", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_8", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_9", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_10", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_11"}
        self.payment_plan_bop_wrong = {"Mortgagee Direct Bill Full Pay": "BasicPolicy.PayPlanCd_1", "Automated Monthly": "BasicPolicy.PayPlanCd_2", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_3", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_4", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_5",
                                       "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_6", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_7", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_8", "Direct Bill 9 Pay": "BasicPolicy.PayPlanCd_9", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_10", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_11"}
        self.payment_plan_pumb = {"Automated Monthly": "BasicPolicy.PayPlanCd_1", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_2", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_3", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_4",
                                  "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_5", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_6", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_7", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_8", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_9"}
        self.user_dict = {"AgentAdmin": "AgentAdmin", "Admin": "Everything",
                          "Underwriter": "PolicyUnderwriter", "Agent": "PolicyAgent"}

        self.env_used = "Local"
        self.state_chosen = None
        self.date_chosen = None
        self.user_name = None
        self.producer_selected = None
        self.create_type = None
        self.browser_chosen = None
        self.line_of_business = None
        self.user_chosen = None
        self.verified = False
        self.number_of_addresses = 1
        self.pay_plan = None
        self.thread_name = None
        self.userList = []
        self.dwelling_program = None
        self.custom_address = False
        self.city = None
        self.state = None
        self.address1 = None
        self.address2 = None
        self.address_validate = False

        self.application = Application()

    def check_for_errors(self, selectedUser, selectedEnviron, producer, browser_chose, date_selected, doc_type, subType):
        if self.address2 == None:
            self.address_validate = Address.verify_address(
                self.city, self.state_chosen, self.address1)
        else:
            self.address_validate = Address.verify_address(
                self.city, self.state_chosen, self.address1, self.address2)

        self.submit_errors = {"User": selectedUser, "Environment": selectedEnviron, "Producer": producer,
                              "Browser": browser_chose, "Date": date_selected, "State": self.state, "Application Type": doc_type, "Subtype": subType, "Address Validation": self.address_validate}
        self.submit_message = []

        err_text = ""
        for error_key, error_value in self.submit_errors.items():
            if error_value == "" or error_value == False:
                err_text += f"{error_key} \n"
                self.submit_message.append(error_value)

        sg.popup_notify("Fields Below must be filled in to Submit \n--------------------------------------------------\n" +
                        err_text, display_duration_in_ms=5000, location=(800, 394))

    # Function for making the GUI
    def make_window(self):

        sg.theme(self.THEME)
        LOB = ["Dwelling Property", "Homeowners", "Businessowners",
               "Personal Umbrella", "Commercial Umbrella"]
        SUBTYPE = {"HO3": "HO3", "HO4": "HO4", "HO5": "HO5T4",
                   "HO5 Superior": "HO5", "HO6": "HO6"}
        STATES = {"Connecticut": "CT", "Illinois": "IL", "Maine": "ME", "Massechusetts": "MA",
                  "New Hampshire": "NH", "New Jersey": "NJ", "New York": "NY", "Rhode Island": "RI"}
        CARRIER = {"Merrimack Mutual Fire Insurance": "MMFI",
                   "Cambrige Mutual Fire Insurance": "CMFI", "Bay State Insurance Company": "BSIC"}
        DWELLING_PROGRAM = ["DP1", "DP2", "DP3"]

        browsers = ["Chrome", "Edge"]
        y = datetime.today()+timedelta(days=65)
        default_date = y.strftime("%m/%d/%Y").split("/")
        default_date = (int(default_date[0]), int(
            default_date[1]), int(default_date[2]))

        top_layout = [
            [sg.Text('Andover Automation', size=(38, 1), justification='center',
                     relief=sg.RELIEF_RIDGE, font=("Helvetica", 16), key='-TEXTHEADING-')]
        ]

        all_tabs_info = [
            [sg.Text('Select Local or QA Environment'), sg.DropDown(
                list(self.gw_environment.keys()), readonly=True, enable_events=True, key="-ENVLIST-")],
            [sg.Text('Select Browser'), sg.DropDown(
                browsers, readonly=True, key="BROWSER")],
            [sg.Text("Select Producer"), sg.DropDown(list(File.env_files_plus_users[self.env_used]["Producers"]["ProducerNames"]), size=(
                self.TEXTLEN, 1), readonly=True, key="-PRODUCER-"), sg.Push(), sg.Button("Delete", size=(10, 1), key="-REMPROD-")],
            [sg.HorizontalSeparator()]
        ]

        new_app_layout = [
            [sg.Text('Enter Information for Creating An Application', border_width=3)],
            [sg.Text('Username'), sg.DropDown(self.userList, readonly=True, key="-ULIST-", size=(20, 1)),
             sg.Push(), sg.Button("Delete User", size=(10, 1), key="-REMU-")],
            [sg.Checkbox(text="Use Custom Name",
                         enable_events=True, key="-NAME_CHECK-")],
            [sg.Text("First Name", visible=False, justification="left",  enable_events=True, key="-FIRST_TEXT-",),
             sg.Text("   "),
             sg.InputText(size=(self.TEXTLEN, 1), visible=False,  enable_events=True, key="-FIRST-")],
            [sg.Text("Mid Name ", visible=False, justification="left",  enable_events=True, key="-MID_TEXT-",),
             sg.Text("   "),
             sg.InputText(size=(self.TEXTLEN, 1), visible=False,  enable_events=True, key="-MID-")],
            [sg.Text("Last Name", visible=False, justification="left",  enable_events=True, key="-LAST_TEXT-"),
             sg.Text("   "), sg.InputText(size=(self.TEXTLEN, 1), visible=False,  enable_events=True, key="-LAST-")],
            [sg.Text("Select State"), sg.DropDown(list(STATES.keys()), key="-STATE-", readonly=True, enable_events=True),
             sg.Checkbox(text="Use Custom Address", enable_events=True, key="ADD_CHECK")],
            [sg.Text("Address 1 (Required)", visible=False, justification="left", key="-AddText1-",),
             sg.Text("   "), sg.InputText(size=(self.TEXTLEN, 1), visible=False, key="-CADD1-")],
            [sg.Text("                      Address 2", visible=False, justification="left",
                     key="-AddText2-"), sg.InputText(size=(self.TEXTLEN, 1), visible=False, key="-CADD2-")],
            [sg.Text("City (Required)", visible=False, justification="left", key="-CityText-"),
             sg.Text("            "), sg.InputText(size=(self.TEXTLEN, 1), visible=False, key="-CITY-")],
            [sg.Button("Verify Address", visible=False, key="BTN_VERIFY"), sg.Push(), sg.Text(
                "Verified", text_color="green", visible=False, key="-VERIFY_BUTTON-")],
            [sg.Text("Select Line of Business"), sg.DropDown(
                LOB, key="-LOB-", enable_events=True, readonly=True)],
            [sg.Text("Select Carrier", key="-CARRIERTEXT-"),
             sg.DropDown(list(CARRIER.keys()), key="-CARRIER-", readonly=True, enable_events=True)],
            [sg.Text("Program", key="-DPTEXT-", enable_events=True, visible=False), sg.DropDown(
                DWELLING_PROGRAM, key="-DP-", default_value="DP1", enable_events=True, readonly=True, visible=False)],
            [sg.Text("Select SubType", visible=False, key="-SUBTYPELABEL-"), sg.DropDown(list(
                SUBTYPE.keys()), key="-SUBTYPE-", default_value="HO5", enable_events=True, readonly=True, visible=False)],
            [sg.Text("Multiple Locations? ", visible=False, key="-MULT-"), sg.DropDown(["Yes",
                                                                                        "No"], visible=False, default_value="No", enable_events=True, readonly=True, key="-MULTI-")],
            [sg.Text("Locations ", justification="left", visible=False, key="-NUMMULT-"),
             sg.DropDown([2, 3, 4, 5], visible=False, default_value="2", readonly=True, key="-NUMLOC-")],
            [sg.Text("Enter Date or Select Date Below")],
            [sg.Input(key='-DATE-', size=(20, 1)), sg.CalendarButton('Date Select', close_when_date_chosen=True,
                                                                     target='-DATE-', format='%m/%d/%Y', default_date_m_d_y=default_date)],
            [sg.Text()],
            [sg.Text("Payment Plan: ", visible=True), sg.DropDown(list(self.payment_plan_most.keys()), visible=True, readonly=True, default_value="Direct Bill Full Pay", enable_events=True, key="-PAYPLAN-"),
             sg.DropDown(list(self.payment_plan_bop.keys()), visible=False,
                         default_value="Direct Bill Full Pay", enable_events=True, readonly=True, key="-PAYPLANBOP-"),
             sg.DropDown(list(self.payment_plan_pumb.keys()), visible=False, default_value="Direct Bill Full Pay", enable_events=True, readonly=True, key="-PAYPLANPUMB-")],
            [sg.Text()],
            [sg.Text("Create Quote, Application or Policy"), sg.DropDown(
                ["Quote", "Application", "Policy"], default_value="Application", readonly=True, key="-CREATE-")],
            [sg.Text()],
            [sg.Button('Submit'), sg.Button('Cancel'), sg.Push(),
             sg.Checkbox("Enable Logging", key="-LOG-")]
        ]

        new_user_layout = [
            [sg.Text()],
            [sg.Text('Add Producer')],
            [sg.Text('Select Login Username'), sg.DropDown(
                self.userList, key="-CREATE_USERLIST-", size=(20, 1), readonly=True, enable_events=True)],
            [sg.Text("Producer Name"), sg.InputText(
                do_not_clear=False, key="-PROD_IN-")],
            [sg.Button("Add Producer", key="-ADD_PROD-")],
            [sg.Text()],
            [sg.HorizontalSeparator()],
            [sg.Text()],
            [sg.Text('Add User')],
            [sg.Text("Username"), sg.InputText(
                do_not_clear=False, size=(self.TEXTLEN, 1), key="USER")],
            [sg.Text("Password"), sg.InputText(
                do_not_clear=False, size=(self.TEXTLEN, 1), key="PASS")],
            [sg.Button("Add", key="-ADDU-")],
            [sg.Text()],
            [sg.HorizontalSeparator()],
            [sg.Text()],
            [sg.Text("Create User in Andover (Local Only)",
                     key="-CREATE_TEXT-", enable_events=True, visible=False)],
            [sg.DropDown(list(self.user_dict.keys()), key="UserDrop",
                         enable_events=True, readonly=True, visible=False)],
            [sg.Button("Create", key="-CREATE_USER-",
                       enable_events=True, visible=False)]
        ]

        exist_app_layout = [
            [sg.Text('Enter Information for An Existing Application')],
            [sg.Text("Application Number"),
             sg.InputText(size=(self.TEXTLEN, 1))]
        ]

        tabs_layout = [
            [sg.TabGroup([
                [sg.Tab('Creating New Applications', new_app_layout),
                 sg.Tab('Add Users and Producers', new_user_layout),
                 ]],
                key="-TABGROUP-", expand_x=True, expand_y=True)]
        ]

        layout = [top_layout]
        layout += [all_tabs_info]
        layout += [tabs_layout]

        # Create the Window
        window = sg.Window(f"Automation for Andover                                  Version: {
                           self.VERSION}", layout)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel or exit
                break

            user_name = values["USER"]
            password = values["PASS"]
            selectedUser = values["-ULIST-"]
            selectedEnviron = values["-ENVLIST-"]
            producer = values["-PRODUCER-"]
            doc_type = values["-CREATE-"]
            self.city = values["-CITY-"]
            self.address1 = values["-CADD1-"]
            self.address2 = values["-CADD2-"]
            browser_chose = values["BROWSER"]
            self.custom_address = values["ADD_CHECK"]
            self.state = values["-STATE-"]
            lob = values["-LOB-"]
            subType = SUBTYPE[values["-SUBTYPE-"]]
            multi = values["-MULTI-"]
            payment_p = values["-PAYPLAN-"]
            payment_p_bop = values["-PAYPLANBOP-"]
            payment_p_pumb = values["-PAYPLANPUMB-"]
            carrier = values["-CARRIER-"]
            producer_name = values["-PROD_IN-"]
            producer_user_name = values["-CREATE_USERLIST-"]
            add_user_value = values["UserDrop"]
            date_selected = values["-DATE-"]
            log_val = values["-LOG-"]
            dwelling_program = values["-DP-"]
            custom_name = values["-NAME_CHECK-"]

            if self.address2 == "":
                self.address2 = None

            if event == "-ADD_PROD-" and producer_name != "" and selectedEnviron and producer_user_name and browser_chose:
                self.browser_chosen = browser_chose
                prod_thread = threading.Thread(target=self.application.create_producer, args=(
                    producer_name, producer_user_name))
                prod_thread.start()

            if event == "-CREATE_USER-" and add_user_value != "" and selectedEnviron and producer_user_name and browser_chose:
                self.browser_chosen = browser_chose
                user_thread = threading.Thread(
                    target=self.application.create_user, args=(add_user_value, producer_user_name))
                user_thread.start()

            if selectedEnviron == "Local":
                window['UserDrop'].update(visible=True)
                window['-CREATE_USER-'].update(visible=True)
                window['-CREATE_TEXT-'].update(visible=True)
                window.refresh()
            else:
                window['UserDrop'].update(visible=False)
                window['-CREATE_USER-'].update(visible=False)
                window['-CREATE_TEXT-'].update(visible=False)
                window.refresh()

            if log_val:
                MultiLog.log_data = True
            else:
                MultiLog.log_data = False

            if (event == "-LOB-" and self.address1 != "") or (event == "-STATE-" and lob != ""):
                if STATES[self.state] == "NY":
                    all_items = list(CARRIER.keys())
                    current_list = []
                    if lob == "Homeowners":
                        current_list = [all_items[0], all_items[1]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()
                    if lob == "Dwelling Property":
                        current_list = [all_items[0]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()

                if STATES[self.state] == "MA":
                    all_items = list(CARRIER.keys())
                    current_list = []
                    if lob == "Homeowners":
                        current_list = all_items
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()
                    if lob == "Dwelling Property":
                        current_list = [all_items[0]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()

                if STATES[self.state] == "CT":
                    all_items = list(CARRIER.keys())
                    current_list = []
                    if lob == "Homeowners":
                        current_list = [all_items[0], all_items[1]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()
                    if lob == "Dwelling Property":
                        current_list = [all_items[0]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()

                if STATES[self.state] == "IL":
                    all_items = list(CARRIER.keys())
                    current_list = []
                    if (lob == "Homeowners" or lob == "Dwelling Property"):
                        current_list = [all_items[0], all_items[1]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()

                if STATES[self.state] == "NH":
                    all_items = list(CARRIER.keys())
                    current_list = []
                    if lob == "Homeowners":
                        current_list = [all_items[0], all_items[1]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()
                    if lob == "Dwelling Property":
                        current_list = [all_items[1]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()

                if STATES[self.state] == "NJ":
                    all_items = list(CARRIER.keys())
                    current_list = []
                    if lob == "Homeowners":
                        current_list = all_items
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()
                    if lob == "Dwelling Property":
                        current_list = [all_items[0]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()

                if STATES[self.state] == "ME":
                    all_items = list(CARRIER.keys())
                    current_list = []
                    if lob == "Homeowners":
                        current_list = [all_items[0], all_items[1]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()
                    if lob == "Dwelling Property":
                        current_list = [all_items[0]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()

                if STATES[self.state] == "RI":
                    all_items = list(CARRIER.keys())
                    current_list = []
                    if (lob == "Homeowners" or lob == "Dwelling Property"):
                        current_list = [all_items[0]]
                        window["-CARRIER-"].update(values=current_list)
                        window["-CARRIER-"].update(value=current_list[0])
                        window.refresh()

            if event == "-ENVLIST-" and selectedEnviron != '' and (selectedEnviron == "QA" or selectedEnviron == "GWCP QA" or selectedEnviron == "GWCP QA2" or selectedEnviron == 'Local' or selectedEnviron == 'UAT3' or selectedEnviron == 'UAT4' or selectedEnviron == 'QA2' or selectedEnviron == 'Model' or selectedEnviron == 'Model 2' or selectedEnviron == 'Model 3'):
                self.env_used = selectedEnviron
                File.env_used = self.env_used
                self.application.env_used = self.env_used
                File.read_username_password()
                File.read_producers()
                prod_user_list = []
                self.userList = list(
                    File.env_files_plus_users[self.env_used]["Users"]["Usernames"].keys())
                for user in self.userList:
                    if user.lower().__contains__("admin") and (not user.lower().__contains__("agent")):
                        prod_user_list.append(user)
                window["-CREATE_USERLIST-"].update(values=prod_user_list)
                window["-ULIST-"].update(values=self.userList)
                window["-PRODUCER-"].update(
                    values=File.env_files_plus_users[self.env_used]["Producers"]["ProducerNames"])
                window.refresh()

            if event == "-ADDU-" and selectedEnviron != '':
                File.env_used = selectedEnviron
                File.add_user(user_name, password)
                self.userList = list(
                    File.env_files_plus_users[self.env_used]["Users"]["Usernames"].keys())
                window["-ULIST-"].update(values=self.userList)
                window.refresh()

            if custom_name:
                window['-FIRST_TEXT-'].update(visible=True)
                window['-FIRST-'].update(visible=True)
                window['-MID_TEXT-'].update(visible=True)
                window['-MID-'].update(visible=True)
                window['-LAST_TEXT-'].update(visible=True)
                window['-LAST-'].update(visible=True)
            else:
                window['-FIRST_TEXT-'].update(visible=False)
                window['-FIRST-'].update(visible=False)
                window['-MID_TEXT-'].update(visible=False)
                window['-MID-'].update(visible=False)
                window['-LAST_TEXT-'].update(visible=False)
                window['-LAST-'].update(visible=False)

            if self.custom_address:
                window["-AddText1-"].update(visible=True)
                window["-CADD1-"].update(visible=True)
                window["-AddText2-"].update(visible=True)
                window["-CADD2-"].update(visible=True)
                window["-CityText-"].update(visible=True)
                window["-CITY-"].update(visible=True)
                # window["BTN_VERIFY"].update(visible=True)
                window.refresh()
            else:
                window["-AddText1-"].update(visible=False)
                window["-CADD1-"].update(visible=False)
                window["-AddText2-"].update(visible=False)
                window["-CADD2-"].update(visible=False)
                window["-CityText-"].update(visible=False)
                window["-CITY-"].update(visible=False)
                window["BTN_VERIFY"].update(visible=False)
                # window["-VERIFY_BUTTON-"].update(visible=False)
                window.refresh()

            if event == "-LOB-":
                if lob == "Businessowners":
                    window["-PAYPLANBOP-"].update(visible=True)
                    window["-PAYPLAN-"].update(visible=False)
                    window["-PAYPLANPUMB-"].update(visible=False)
                    window.refresh()
                elif lob == "Personal Umbrella" or lob == "Commercial Umbrella":
                    window["-PAYPLANPUMB-"].update(visible=True)
                    window["-PAYPLANBOP-"].update(visible=False)
                    window["-PAYPLAN-"].update(visible=False)
                    window.refresh()
                else:
                    window["-PAYPLANBOP-"].update(visible=False)
                    window["-PAYPLAN-"].update(visible=True)
                    window["-PAYPLANPUMB-"].update(visible=False)
                    window.refresh()

            if lob == "Dwelling Property":
                window["-MULT-"].update(visible=True)
                window["-MULTI-"].update(visible=True)
                window["-DPTEXT-"].update(visible=True)
                window["-DP-"].update(visible=True)
                window.refresh()
            else:
                window["-MULT-"].update(visible=False)
                window["-MULTI-"].update(visible=False)
                window["-DPTEXT-"].update(visible=False)
                window["-DP-"].update(visible=False)
                window.refresh()

            if lob == "Homeowners" or lob == "Personal Umbrella":
                window["-SUBTYPELABEL-"].update(visible=True)
                window["-SUBTYPE-"].update(visible=True)
                window["-CARRIERTEXT-"].update(visible=True)
                window["-CARRIER-"].update(visible=True)
                window.refresh()
            else:
                window["-SUBTYPELABEL-"].update(visible=False)
                window["-SUBTYPE-"].update(visible=False)
                window["-CARRIERTEXT-"].update(visible=False)
                window["-CARRIER-"].update(visible=False)
                window.refresh()

            if lob == "Homeowners" or lob == "Personal Umbrella" or lob == "Dwelling Property":
                window["-CARRIERTEXT-"].update(visible=True)
                window["-CARRIER-"].update(visible=True)

                window.refresh()
            else:
                window["-CARRIERTEXT-"].update(visible=False)
                window["-CARRIER-"].update(visible=False)
                window.refresh()

            if multi == "Yes" and lob == "Dwelling Property":
                window["-NUMLOC-"].update(visible=True)
                window["-NUMMULT-"].update(visible=True)
            else:
                window["-NUMLOC-"].update(visible=False)
                window["-NUMMULT-"].update(visible=False)

            if event == "-REMU-" and len(File.env_files_plus_users[self.env_used]["Users"]["Usernames"].keys()) > 0 and selectedUser != "":
                del File.env_files_plus_users[self.env_used]["Users"]["Usernames"][selectedUser]
                self.userList = File.env_files_plus_users[self.env_used]["Users"]["Usernames"]
                File.write_username_password(
                    File.folder+File.env_files_plus_users[self.env_used]["Users"]["file"], self.userList)
                window["-ULIST-"].update(values=list(self.userList.keys()))
                window.refresh()

            if event == "-REMPROD-" and len(File.env_files_plus_users[self.env_used]["Producers"]["ProducerNames"]) > 0 and producer != "":
                File.env_files_plus_users[self.env_used]["Producers"]["ProducerNames"].remove(
                    producer)
                prod_list = File.env_files_plus_users[self.env_used]["Producers"]["ProducerNames"]
                File.write_producer(
                    File.folder+File.env_files_plus_users[self.env_used]["Producers"]["file"], prod_list)
                window["-PRODUCER-"].update(values=prod_list)
                window.refresh()

            if event == "-ADDRESS-":
                Address.custom_address["Address"] = self.address1
                Address.custom_address["Address2"] = self.address2
                Address.custom_address["City"] = self.city
                window["ADD_DISP"].update(value=self.address1)
                window["CITY_DISP"].update(value=self.city)
                window.refresh()

            if event == "Submit" and self.custom_address:
                if self.address1 != "" and self.address2 == None:
                    self.verified = Address.verify_address(
                        self.city, STATES[self.state], self.address1)
                elif self.address1 != "" and self.address2 is not None:
                    self.verified = Address.verify_address(
                        self.city, STATES[self.state], self.address1, address2=self.address2)
                    
            if not self.custom_address:
                self.verified = True

            if event == "Submit" and selectedUser and selectedEnviron and producer and doc_type and browser_chose and lob and self.state and date_selected and self.verified:

                self.application.line_of_business = lob
                self.application.browser_chosen = browser_chose
                self.application.state_chosen = STATES[self.state]
                self.application.date_chosen = date_selected
                self.application.producer_selected = producer
                self.application.create_type = doc_type
                self.application.user_chosen = selectedUser

                if self.custom_address:
                    Address.custom_address["Address"] = self.address1
                    Address.custom_address["City"] = self.city
                    Address.custom_address["Address2"] = self.address2
                    Address.custom_address["Flag"] = True
                
                if custom_name:
                    self.application.first_name = values["-FIRST-"]
                    self.application.mid_name = values["-MID-"]
                    self.application.last_name = values["-LAST-"]
                else:
                    self.application.first_name = self.application.state_chosen
                    self.application.last_name = self.application.line_of_business

                if self.application.line_of_business == "Dwelling Property":
                    self.application.dwelling_program = dwelling_program

                if (self.application.line_of_business != "Businessowners"):
                    # if line_of_business == "Homeowners":
                    # pay_plan = payment_plan + " "+state_chosen
                    if self.application.line_of_business == "Personal Umbrella" or self.application.line_of_business == "Commercial Umbrella":
                        self.application.pay_plan = payment_p_pumb
                    else:
                        self.application.pay_plan = payment_p
                else:
                    self.application.pay_plan = payment_p_bop

                if (multi == "Yes" and lob == "Dwelling Property"):
                    self.application.multiAdd = True
                    self.application.number_of_addresses = values["-NUMLOC-"]
                else:
                    self.application.number_of_addresses = 1
                    self.application.multiAdd = False

                if self.custom_address and self.address_validate:
                    app_thread = threading.Thread(target=self.application.startApplication, args=(
                        self.application.multiAdd, subType, carrier))

                    app_thread.start()
                else:
                    app_thread = threading.Thread(target=self.application.startApplication, args=(
                        self.application.multiAdd, subType, carrier))

                    app_thread.start()

                if not app_thread.is_alive():
                    del self.application

            elif event == "Submit":
                self.check_for_errors(selectedUser, selectedEnviron, producer, browser_chose,
                                      date_selected, doc_type, subType)
                
                sg.popup_auto_close(
                        'This Address Has Not been Verified. Check the address and enter it again.')
    
        window.close()
