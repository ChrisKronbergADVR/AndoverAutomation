import customtkinter as ctk
from datetime import date
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import threading
import os

from .MultiLog import MultiLog
from .Address import Address
from .Application import Application
from .File import File
from .Producer import Producer
from .User import User

class ScrollableTabView(ctk.CTkScrollableFrame):
    states = {"Connecticut": "CT", "Illinois":"IL","Maine": "ME","Massachusetts": "MA", "New Hampshire": "NH", "New Jersey": "NJ","New York": "NY", "Rhode Island": "RI"}
    line_of_business = ["Dwelling Property", "Homeowners", "Businessowners","Personal Umbrella", "Commercial Umbrella"]
    carriers = {"Merrimack Mutual Fire Insurance": "MMFI",
                   "Cambrige Mutual Fire Insurance": "CMFI", "Bay State Insurance Company": "BSIC"}
    payment_methods = ["Credit Card", "Check", "ACH"]

    payment_plan_most = {"Mortgagee Direct Bill Full Pay": "BasicPolicy.PayPlanCd_1", "Automated Monthly": "BasicPolicy.PayPlanCd_2", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_3", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_4", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_5",
                                  "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_6", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_7", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_8", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_9", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_10"}
    payment_plan_bop = {"Mortgagee Direct Bill Full Pay": "BasicPolicy.PayPlanCd_1", "Automated Monthly": "BasicPolicy.PayPlanCd_2", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_3", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_4", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_5",
                                 "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_6", "Direct Bill 9 Pay": "BasicPolicy.PayPlanCd_7", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_8", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_9", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_10", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_11"}
    payment_plan_pumb = {"Automated Monthly": "BasicPolicy.PayPlanCd_1", "Bill To Other Automated Monthly": "BasicPolicy.PayPlanCd_2", "Direct Bill 2 Pay": "BasicPolicy.PayPlanCd_3", "Direct Bill 4 Pay": "BasicPolicy.PayPlanCd_4",
                                  "Direct Bill 6 Pay": "BasicPolicy.PayPlanCd_5", "Bill To Other 4 Pay": "BasicPolicy.PayPlanCd_6", "Bill To Other 6 Pay": "BasicPolicy.PayPlanCd_7", "Direct Bill Full Pay": "BasicPolicy.PayPlanCd_8", "Bill To Other Full Pay": "BasicPolicy.PayPlanCd_9"}
    submit_error = 0
    custom_name = 0
    custom_address = 0
    usernames = []
    browser = None
    producer = None
    application = Application()
    address = Address()

    carrier_keys = list(carriers.keys())
    carrier_list = {"Dwelling Property":{"CT":[carrier_keys[0]],
                                "IL":[carrier_keys[0],carrier_keys[1]],
                                "ME":[carrier_keys[0]],
                                "MA":[carrier_keys[0]],
                                "NH":[carrier_keys[1]],
                                "NJ":[carrier_keys[0]],
                                "NY":[carrier_keys[0]],
                                "RI":[carrier_keys[0]]
                                },
                    "Homeowners":{"CT":[carrier_keys[0],carrier_keys[1]],
                                  "IL":[carrier_keys[0],carrier_keys[1]],
                                  "ME":[carrier_keys[0],carrier_keys[1]],
                                  "MA":[carrier_keys[0],carrier_keys[1],carrier_keys[2]],
                                  "NH":[carrier_keys[0],carrier_keys[1]],
                                  "NJ":[carrier_keys[0],carrier_keys[1],carrier_keys[2]],
                                  "NY":[carrier_keys[0],carrier_keys[1]],
                                  "RI":[carrier_keys[0]]
                                  },
                    "Businessowners":{"CT":[carrier_keys[0]],
                                      "IL":[carrier_keys[0],carrier_keys[1]],
                                      "ME":[carrier_keys[0]],
                                      "MA":[carrier_keys[0],carrier_keys[1],carrier_keys[2]],
                                      "NH":[carrier_keys[0],carrier_keys[1]],
                                      "NJ":[carrier_keys[0]],
                                      "NY":[carrier_keys[0],carrier_keys[2]],
                                      "RI":[carrier_keys[0]]
                                      },
                    "Personal Umbrella":{"CT":[carrier_keys[0]],
                                         "IL":[carrier_keys[0]],
                                         "ME":[carrier_keys[0]],
                                         "MA":[carrier_keys[0]],
                                         "NH":[carrier_keys[0]],
                                         "NJ":[carrier_keys[0]],
                                         "NY":[carrier_keys[0]],
                                         "RI":[carrier_keys[0]]
                                         }
                    }

    check_width = 17
    check_height = 17

    # Used to track if clicked multiple times
    repeat = False # Used to track if the program label and option menu have been created
    program_repeat = False # Used to track if the subtype label and option menu have been created
    loc_repeat = False # Used to track if the multiple locations label and option menu have been created

    # Custom Name and Address Variables
    first_name = None
    mid_name = None
    last_name = None
    address1 = None
    address2 = None
    city = None

    # Text for showing required fields still needed when clicking submit
    required_info_text = "* Required Information"

    #dropdown menu background and hover colors
    drop_back_color = "#144870"
    drop_hover_color = "#073972"

    def __init__(self, master,title,**kwargs):
        super().__init__(master, label_text=title,**kwargs)
        self.grid_columnconfigure(0, weight=1)  # Make the first column expandable
        self.grid_rowconfigure(0, weight=1)     # Make the first row expandable
        self.configure(fg_color="transparent")  # Set background color to transparent

        ################### First Tab Start ###################
        # Username Label
        ctk.CTkLabel(master=self,text=f"Username").grid(row=0, column=0, padx=10, pady=20)

        self.user_val = ctk.CTkOptionMenu(master=self,values=list(File.get_users()) if len(list(File.get_users())) > 0 else ["Add User"], command=lambda x: print(f"Selected user: {x}"),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.user_val.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=1)
    
        # User Delete Button
        self.producer_delete_button = ctk.CTkButton(master=self, text="Delete", command=lambda: self.delete_user(),width=50)
        self.producer_delete_button.grid(row=0, column=2, padx=60, pady=5, sticky="ew")

        self.custom_name = ctk.CTkCheckBox(master=self, text="Use Custom Name", command=lambda:self.toggle_custom_name(),checkbox_width=self.check_width,checkbox_height=self.check_height)
        self.custom_name.grid(row=1, column=0, padx=(40,0), pady=5, sticky="w", columnspan=3)

        # Username Label
        ctk.CTkLabel(master=self,text="State").grid(row=5, column=0, padx=10, pady=20)
                     
        # Username Value Selection
        self.state_val = ctk.CTkOptionMenu(master=self,values=list(self.states.keys()), command=lambda state: self.state_selected(state),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.state_val.grid(row=5, column=1, padx=5, pady=5, sticky="ew", columnspan=1)

        # Custom Address Checkbox
        self.custom_address = ctk.CTkCheckBox(master=self, text="Custom Address", command=lambda:self.toggle_custom_address(),checkbox_width=self.check_width,checkbox_height=self.check_height)
        self.custom_address.grid(row=5, column=2, padx=10, pady=5, sticky="w", columnspan=3)

        # Line of Business Label
        ctk.CTkLabel(master=self, text="Line of Business").grid(row=9, column=0, padx=10, pady=10)
        # Line of Business Value Selection
        self.lob_val = ctk.CTkOptionMenu(master=self, values=self.line_of_business, command=lambda x: self.toggle_program(x), dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.lob_val.grid(row=9, column=1, padx=5, pady=5, sticky="ew", columnspan=1)
        self.lob_val.set("Select Value")  # Set default value

        # Line of Business Label
        ctk.CTkLabel(master=self, text="Carrier").grid(row=14, column=0, padx=10, pady=10)
        # Line of Business Value Selection
        self.carrier_val = ctk.CTkOptionMenu(master=self, values=list(self.carriers.keys()), command=lambda x: print(f"Selected Carrier: {x}"),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.carrier_val.grid(row=14, column=1, padx=5, pady=5, sticky="ew", columnspan=1)

        # Date Label
        ctk.CTkLabel(master=self, text="Date",width=80).grid(row=15, column=0, padx=10, pady=10)

        # Date Input in MM/DD/YYYY format
        self.dateInput = DateEntry(master=self, background='darkblue', foreground='white', borderwidth=1,date_pattern='MM/dd/yyyy')
        self.dateInput.grid(row=15, column=1, padx=10, pady=5, sticky="ew", columnspan=1)

        # `Payment` Method Label and Option Menu
        ctk.CTkLabel(master=self, text="Payment Method").grid(row=16, column=0, padx=10, pady=10)
        self.payment_method = ctk.CTkOptionMenu(master=self, values=list(self.payment_plan_most.keys()), command=lambda x: self.set_payment_value(x),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.payment_method.grid(row=16, column=1, padx=5, pady=5, sticky="ew", columnspan=1)
        
        # Create Quote, Application, or Policy Label and Option Menu
        ctk.CTkLabel(master=self, text="Product").grid(row=17, column=0, padx=10, pady=10)
        self.application_type = ctk.CTkOptionMenu(master=self, values=["Quote", "Application", "Policy"], command=lambda x: print(f"Selected Application Type: {x}"),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.application_type.grid(row=17, column=1, padx=5, pady=5, sticky="ew", columnspan=1)

        ## Logging Checkbox
        self.logging_checkbox = ctk.CTkCheckBox(master=self, text="Enable Logging", checkbox_width=self.check_width, checkbox_height=self.check_height)
        self.logging_checkbox.grid(row=18, column=0, padx=(40,0), pady=(20,0), sticky="w", columnspan=2)

        self.submit = ctk.CTkButton(self, text="Submit", command=lambda: self.submit_values(),width=100)
        self.submit.grid(row=19, column=2, padx=30, pady=(20,0), sticky="w")

        self.required_info = ctk.CTkLabel(master=self, text="", text_color="red")
        self.required_info.grid(row=19, column=1, padx=10, pady=(10,0), sticky="w", columnspan=1)

    def submit_values(self):
        submit_values = {"Cust_Name":False,"Cust_Address":False}
        self.application.producer_selected = self.producer
        self.application.state_chosen = self.states[self.state_val.get()]
        self.application.line_of_business = self.lob_val.get()
        self.application.date_chosen = self.dateInput.get()
        self.application.user_chosen = self.user_val.get()

        #Address Check
        if self.custom_address.get() == 1:
            self.application.custom_address = True
            if self.address1.get() and self.city.get():
                self.application.address1 = self.address1.get()
                self.application.city = self.city.get()
                if self.address2.get() != "":
                    self.application.address2 = self.address2.get()
                    submit_values["Cust_Address"] = self.address.verify_address(self.city.get(),self.state_val.get(),self.address1.get(),self.address2.get())
                    self.address.custom_address["City"] = self.city.get()
                    self.address.custom_address["State"] = self.state_val.get()
                    self.address.custom_address["Address"] = self.address1.get()
                    self.address.custom_address["Address2"] = self.address2.get()
                
                else:
                    submit_values["Cust_Address"] = self.address.verify_address(self.city.get(),self.state_val.get(),self.address1.get())
                    self.address.custom_address["City"] = self.city.get()
                    self.address.custom_address["State"] = self.state_val.get()
                    self.address.custom_address["Address"] = self.address1.get()
          
        else:
            self.application.custom_address = False
            address_vals = self.address.addresses[self.states[self.state_val.get()]]
            self.application.state_chosen = address_vals[0]
            self.application.address1 = address_vals[2]
        
        # Change custom name to red if not filled out when checked
        if self.custom_name.get() == 1:
            if self.first_name.get() and self.last_name.get():
                submit_values["Cust_Name"] = 1
                self.application.first_name = self.first_name.get()
                self.application.last_name = self.last_name.get()
            if not self.first_name.get():
                self.first_name.configure(placeholder_text_color ="red")
                submit_values["Cust_Name"] = 0
            else:
                self.first_name.configure(placeholder_text_color ="white")
            if not self.last_name.get():
                self.last_name.configure(placeholder_text_color ="red")
                submit_values["Cust_Name"] = 0
            else:
                self.last_name.configure(placeholder_text_color ="white")

            if self.mid_name.get() != "":
                    self.application.mid_name = self.mid_name.get()
        else:
            self.application.first_name = self.states[self.state_val.get()]
            self.application.last_name = self.lob_val.get()
        
        
        print(f"State: {self.state_val.get()}")
        print(f"Date: {self.dateInput.get()}")
        print(f"Payment Method: {self.payment_method.get()}")
        print(f"Product Type: {self.application_type.get()}")

        if self.logging_checkbox.get() == 1:
            print("Logging is enabled")
            MultiLog.log_data = True
        else:
            print("Logging is disabled")
            MultiLog.log_data = False

        if self.custom_name.get() == 1:
            if submit_values["Cust_Name"] == False:
                self.submit_error += 1
        if self.custom_address.get() == 1:
            if submit_values["Cust_Address"] == False:
                self.submit_error += 1

        # if required fields are not filled, show an error message
        if self.submit_error != 0:
            self.required_info.configure(text=self.required_info_text)  # Reset the required info text
        else:
            if self.lob_val.get() == self.line_of_business[1]:

                self.application.startApplication(None,self.subtype.get(),self.carrier_val.get())
            else:
                if self.lob_val.get() == self.line_of_business[0]:
                    print(f"Multiple Locations {self.multiple_locations.get()}")
                    self.application.startApplication(self.multiple_locations.get(),None,self.carrier_val.get())
                else:
                    self.application.startApplication(None,None,self.carrier_val.get())

    def toggle_custom_name(self):
        # Checking to see if custom name is selected, and if it is add entries for first, middle, and last name Otherwise remove these entries
        if self.custom_name.get() == 1:
            self.first_name = ctk.CTkEntry(master=self, placeholder_text="First Name (Required)", width=200)
            self.first_name.grid(row=2, column=0, padx=10, pady=5, sticky="ew", columnspan=2)
            self.mid_name = ctk.CTkEntry(master=self, placeholder_text="Middle Name", width=200)
            self.mid_name.grid(row=3, column=0, padx=10, pady=5, sticky="ew", columnspan=2)
            self.last_name = ctk.CTkEntry(master=self, placeholder_text="Last Name (Required)", width=200)
            self.last_name.grid(row=4, column=0, padx=10, pady=5, sticky="ew", columnspan=2)
        else:
            try:
                self.first_name.destroy()
                self.mid_name.destroy()
                self.last_name.destroy()
            except AttributeError:
                pass        

    def toggle_custom_address(self):
        # Checking to see if custom name is selected, and if it is add entries for first, middle, and last name Otherwise remove these entries
        if self.custom_address.get() == 1:
            self.address1 = ctk.CTkEntry(master=self, placeholder_text="Address1 (Required)", width=200)
            self.address1.grid(row=6, column=0, padx=10, pady=5, sticky="ew", columnspan=3)
            self.address2 = ctk.CTkEntry(master=self, placeholder_text="Address 2", width=200)
            self.address2.grid(row=7, column=0, padx=10, pady=5, sticky="ew", columnspan=2)
            self.city = ctk.CTkEntry(master=self, placeholder_text="City (Required)", width=200)
            self.city.grid(row=8, column=0, padx=10, pady=5, sticky="ew", columnspan=2)
        else:
            try:
                self.address1.destroy()
                self.address2.destroy()
                self.city.destroy()
            except AttributeError:
                pass        

    def toggle_program(self,lob_val):
        self.lob_val.set(lob_val)
        if lob_val == self.line_of_business[0]:  # If Dwelling Property is selected
            if not self.program_repeat:
                    self.program_label = ctk.CTkLabel(master=self, text="Program")
                    self.program_label.grid(row=10, column=0, padx=5, pady=5, sticky="ew", columnspan=1)
                    self.program = ctk.CTkOptionMenu(master=self, values=["DP1", "DP2", "DP3"], command=lambda x: print(f"Selected Program: {x}"),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
                    self.program.grid(row=10, column=1, padx=5, pady=5, sticky="ew", columnspan=1)
                    self.multiple_locations = ctk.CTkCheckBox(master=self, text="Multiple Locations", checkbox_width=self.check_width, checkbox_height=self.check_height,command=lambda: self.toggle_multiple_locations(self.multiple_locations.get()))
                    self.multiple_locations.grid(row=11, column=2, padx=5, pady=5, sticky="w", columnspan=1)
                    self.program_repeat = True
        else:
            try:
                self.program.destroy()
                self.program_label.destroy()
                self.multiple_locations.destroy()
                self.num_locations.destroy()
                self.num_locations_label.destroy()
                self.program_repeat = False
            except AttributeError:
                pass

        if lob_val == self.line_of_business[1] or lob_val == self.line_of_business[3]:  # If Homeowners or Personal Umbrella is selected
            if not self.repeat:
                    self.subtype_label = ctk.CTkLabel(master=self, text="Subtype")
                    self.subtype_label.grid(row=12, column=0, padx=5, pady=5, sticky="ew", columnspan=1)
                    self.subtype = ctk.CTkOptionMenu(master=self, values=["HO3", "HO4", "HO5","HO5 Superior","HO6"], command=lambda x:print(f"Subtype Selected: {x}"),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
                    self.subtype.grid(row=12, column=1, padx=5, pady=5, sticky="ew", columnspan=1)
                    self.repeat = True
        else:
            try:
                self.subtype.destroy()
                self.subtype_label.destroy()
                self.repeat = False
            except AttributeError:
                pass

        if lob_val == self.line_of_business[2]:  # If Businessowners is selected
            self.payment_method.configure(values=list(self.payment_plan_bop.keys()))
        if lob_val == self.line_of_business[4]:  # If Personal Umbrella is selected
            self.payment_method.configure(values=list(self.payment_plan_pumb.keys()))
        else:
            self.payment_method.configure(values=list(self.payment_plan_most.keys()))

        if self.lob_val.get() != self.line_of_business[2]:  # If Dwelling Property is selected
            self.carrier_val.configure(values=list(self.carrier_list[self.lob_val.get()][self.states[self.state_val.get()]]))

        self.state_selected(self.state_val.get())  # Update the carrier options based on the selected state

    def set_payment_value(self, payment_method):
        if self.lob_val.get() == self.line_of_business[2]:
            self.application.payment_method = self.payment_plan_bop[payment_method]
        elif self.lob_val.get() == self.line_of_business[4]:
            self.application.payment_method = self.payment_plan_pumb[payment_method]
        else:
            self.application.payment_method = self.payment_plan_most[payment_method]

    def toggle_multiple_locations(self, loc_val):
        if loc_val == True:
            self.num_locations_label = ctk.CTkLabel(master=self, text="Locations")
            self.num_locations_label.grid(row=11, column=0, padx=5, pady=5, sticky="ew", columnspan=1)
            self.num_locations = ctk.CTkOptionMenu(master=self, values=["2", "3", "4", "5"], command=lambda x: print(f"Selected Number of Locations: {x}"), dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
            self.num_locations.grid(row=11, column=1, padx=5, pady=5, sticky="ew", columnspan=1)
        else:
            try:
                self.num_locations.destroy()
                self.num_locations_label.destroy()
            except AttributeError:
                pass

    def set_date_to_today(self):
        self.dateInput.delete(0, 'end')  # Clear the current input
        # Set the date input to today's date in MM/DD/YYYY format
        self.dateInput.insert(0,date.today().strftime("%m/%d/%Y"))

    def delete_user(self):
        print(self.user_val.get())
        users = File.remove_users(self.user_val.get())

        if len(users) > 0:
            self.user_val.configure(values=users)
            self.user_val.set(users[0])
        else:
            self.user_val.configure(values=["Add User"])
            self.user_val.set("Add User")

    def state_selected(self,state):
        # Update the carrier options based on the selected state and line of business
        if self.lob_val in self.line_of_business and self.states[state] in list(self.states.values()):
            carriers = self.carrier_list[self.lob_val][self.states[state]]
            self.carrier_val.configure(values=carriers)
            if carriers:
                self.carrier_val.set(carriers[0])

    def set_users(self):
        users = File.get_users()
        if len(users) > 0:
            self.user_val.configure(values=list(users))
            self.user_val.set(list(users)[0])
        else:
            self.user_val.configure(values=["Add User"])
            self.user_val.set("Add User")

class MyTabView(ctk.CTkTabview):
    tabs = ["Creating New Applications", "Add Users and Producers"]
    browser= None
    producer = None
    environment = None
    producers = None

    # Font settings
    producer_font_size = 15
    font_family = "TimesNewRoman"
    user = User()
    producer = Producer()
    user_dict = {"AgentAdmin": "AgentAdmin", "Admin": "Everything",
                          "Underwriter": "PolicyUnderwriter", "Agent": "PolicyAgent"}
    
    #dropdown menu background and hover colors
    drop_back_color = "#144870"
    drop_hover_color = "#2C4664"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        File.__init__()

        # Create Tabs
        for tab in self.tabs:
            self.add(tab)
    
        ################### First Tab Start ###################
        #Add Scrollable Frame to the first tab 
        self.scrollable_checkbox_frame = ScrollableTabView(master=self.tab(self.tabs[0]), title="Application Options", width=550, height=500)
        self.scrollable_checkbox_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", columnspan=3)

        ################### Second Tab Start ###################
        # Add Font to second tab that says Add Producer
        ctk.CTkLabel(master=self.tab(self.tabs[1]),text="Add Producer",font=ctk.CTkFont(family=self.font_family, size=self.producer_font_size, weight="bold")).grid(padx=0, pady=10,sticky="ew",columnspan=3)

        # Label and Entry for User Name To Create a Producer
        ctk.CTkLabel(master=self.tab(self.tabs[1]),text="Select Login User").grid(row=1, column=0, padx=10, pady=5)
        self.user_value = ctk.CTkOptionMenu(master=self.tab(self.tabs[1]), values=list(File.get_admin_users()), command=lambda x: print(f"Selected user: {x}"),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.user_value.grid(row=1, column=1, padx=10, pady=5, sticky="ew", columnspan=1)

        # Label and Entry for Producer Name
        ctk.CTkLabel(master=self.tab(self.tabs[1]),text="Producer Name").grid(row=2, column=0, padx=10, pady=5)
        self.producer_value =ctk.CTkEntry(master=self.tab(self.tabs[1]), placeholder_text="Producer Name", width=200)
        self.producer_value.grid(row=2, column=1, padx=10, pady=5, sticky="ew", columnspan=1)

        #Button to Add Producer
        self.add_producer_button = ctk.CTkButton(master=self.tab(self.tabs[1]), text="Add Producer", command=lambda:  self.start_producer_create(self.producer_value.get()), width=100)
        self.add_producer_button.grid(row=2, column=2, padx=10, pady=5, sticky="ew", columnspan=1)

        # Label and Entry for Producer Name)
        ctk.CTkLabel(master=self.tab(self.tabs[1]), text="Add User To List of Users", font=ctk.CTkFont(family=self.font_family, size=self.producer_font_size, weight="bold")).grid(row=4, column=0, padx=10, pady=(40,5), sticky="ew", columnspan=3)
  
        # Label and Entry for User Name
        self.username_add_label = ctk.CTkLabel(master=self.tab(self.tabs[1]), text="Username")
        self.username_add_label.grid(row=5, column=0, padx=10, pady=5)
        self.user_name_value = ctk.CTkEntry(master=self.tab(self.tabs[1]), placeholder_text="Username", width=200)
        self.user_name_value.grid(row=5, column=1, padx=10, pady=5, sticky="ew", columnspan=1)

        # Label and Entry for User Password
        self.password_add_label = ctk.CTkLabel(master=self.tab(self.tabs[1]), text="User Password")
        self.password_add_label.grid(row=6, column=0, padx=10, pady=5)
        self.user_password_value = ctk.CTkEntry(master=self.tab(self.tabs[1]), placeholder_text="User Password", width=200)
        self.user_password_value.grid(row=6, column=1, padx=10, pady=5, sticky="ew", columnspan=1)

        # Button to add user
        self.add_user_button = ctk.CTkButton(master=self.tab(self.tabs[1]), text="Add User", command= lambda: self.add_user(), width=100)
        self.add_user_button.grid(row=6, column=2, padx=10, pady=5, sticky="ew", columnspan=1)

        # Create a label for the users to create
        self.users_to_create_label = ctk.CTkLabel(master=self.tab(self.tabs[1]), text="Create User in Andover (Local ONLY)", font=ctk.CTkFont(family=self.font_family, size=self.producer_font_size, weight="bold")).grid(row=7, column=0, padx=10, pady=(40,5), sticky="ew", columnspan=3)
        
        # Create combo box for users to create
        self.users_to_create_value = ctk.CTkOptionMenu(master=self.tab(self.tabs[1]), values=list(self.user_dict.keys()), command=lambda x: print(f"Selected user to create: {x}"),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.users_to_create_value.grid(row=8, column=1, padx=10, pady=5, sticky="ew", columnspan=1)
        self.create_user_button = ctk.CTkButton(master=self.tab(self.tabs[1]), text="Create User",command=lambda: self.start_user_create(self.users_to_create_value.get()), width=100)
        self.create_user_button.grid(row=8, column=2, padx=10, pady=5, sticky="ew", columnspan=1)
        
        ################### Third Tab Start ###################
        #ctk.CTkLabel(master=self.tab(self.tabs[2]),text="Core Coverages Feature Will be added soon").grid(row=0, column=0, padx=10, pady=20)

    def start_user_create(self,user_selected):
        if self.user_value != "Add Admin User":
            self.user.browser_chosen = self.browser
            self.user.producer_selected = self.producer
            user_thread = threading.Thread(target=self.user.create_user, args=(user_selected,self.user_value.get()))
            user_thread.start()
        else:
            print("Please add an admin user first before creating other users.")

    def start_producer_create(self,producer_name):
        self.producer.env_used = self.environment
        if self.user_value != "Add Admin User" and self.producer_value.get() != "" and self.producer_value.get() != None:
            self.producer.browser_chosen = self.browser
            prod_thread = threading.Thread(target=self.producer.create_producer, args=(
                producer_name, self.user_value.get()))
            prod_thread.start()
           
        else:
            print("Please add an admin user first before creating other users.")

    def add_user(self):
        if len(self.user_name_value.get()) != 0 and len(self.user_password_value.get()) != 0:
            self.username_add_label.configure(text="Username", text_color="white")
            self.password_add_label.configure(text="User Password", text_color="white")
            File.env_used = app.environment.get()
            File.add_user(self.user_name_value.get(), self.user_password_value.get())
            File.read_username_password()
            usernames = File.env_files_plus_users[File.env_used]["Users"]["Usernames"]
            self.scrollable_checkbox_frame.user_val.set(list(usernames.keys())[0])
            self.scrollable_checkbox_frame.user_val.configure(values=usernames.keys())
            admin_usernames = File.get_admin_users()
            if len(admin_usernames) > 0:
                self.user_value.configure(values=admin_usernames)
                self.user_value.set(admin_usernames[0])
            else:
                self.user_value.set("Add Admin User")
        else:
            if len(self.user_name_value.get()) == 0:
                self.username_add_label.configure(text="*Username", text_color="red")
                print("Username is required") # replace with making the text red for username label
            else:
                self.username_add_label.configure(text="Username", text_color="white")
            if len(self.user_password_value.get()) == 0:
                self.password_add_label.configure(text="*User Password",text_color="red")
                print("Password is required") #replace with making the text red for password label
            else:
                self.password_add_label.configure(text="User Password", text_color="white")
    
    def check_admin_users(self):
        admin_users = File.get_admin_users()
        if len(admin_users) > 0:
            self.user_value.configure(values=admin_users)
            self.user_value.set(admin_users[0])
        else:
            self.user_value.set("Add Admin User")

    def env_change(self):
    
        admin_users = File.get_admin_users()

        self.user_value.configure(values=list(admin_users))
        self.user_value.set(list(admin_users)[0])

        try:
            if self.environment != "Local":
                self.users_to_create_label = ctk.CTkLabel(master=self.tab(self.tabs[1]), text="")
                self.users_to_create_label.grid(row=7, column=0, padx=10, pady=(40,5), sticky="ew", columnspan=3)
                self.users_to_create_value.destroy()
                self.create_user_button.destroy()
            else:
                self.users_to_create_label = ctk.CTkLabel(master=self.tab(self.tabs[1]), text="Create User in Andover (Local ONLY)", font=ctk.CTkFont(family=self.font_family, size=self.producer_font_size, weight="bold"))
                self.users_to_create_label.grid(row=7, column=0, padx=10, pady=(40,5), sticky="ew", columnspan=3)
                self.users_to_create_value = ctk.CTkOptionMenu(master=self.tab(self.tabs[1]), values=list(self.user_dict.keys()), command=lambda x: print(f"Selected user to create: {x}"),dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
                self.users_to_create_value.grid(row=8, column=1, padx=10, pady=5, sticky="ew", columnspan=1)
                self.create_user_button = ctk.CTkButton(master=self.tab(self.tabs[1]), text="Create User", command=lambda: self.start_user_create(self.users_to_create_value.get()), width=100)
                self.create_user_button.grid(row=8, column=2, padx=10, pady=5, sticky="ew", columnspan=1)
        except AttributeError:
            pass    

class App(ctk.CTk):
    VERSION = "0.5.0"
    LOG_PATH = "Logs/"
    browser = None
    environment = "Local"
    producers = None
    browsers = ["Chrome", "Firefox"]
    gw_environment = {"Local": "https://localhost:9443", "QA": "https://qa-advr.iscs.com/", "QA2": "https://qa2-acx-advr.in.guidewire.net/innovation", 
                               "UAT3": "https://uat3-advr.in.guidewire.net/innovation?saml=off", "UAT4": "https://uat4-advr.in.guidewire.net/innovation"}
    selected_producer = None

    #dropdown menu background and hover colors
    drop_back_color = "#144870"
    drop_hover_color = "#073972"

    def __init__(self):
        super().__init__()

        if (not os.path.exists(self.LOG_PATH)):
            os.mkdir(self.LOG_PATH)
        File.create_folders()
        File.create_files()

        self.title("Andover Automation")
        self.geometry("630x750")
        File.read_producers()

        #default to local environment
        File.env_used = self.environment
    
        #Select Local or QA Environment Here 
        ctk.CTkLabel(self, text="Select Local or QA Environment: ", corner_radius=10).grid(row=0, column=0, padx=5, pady=5, sticky="ew", columnspan=1)
        self.environment = ctk.CTkOptionMenu(self,values=list(self.gw_environment.keys()), command=lambda x: self.set_environment(x),corner_radius=10,dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.environment.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=1)
      
        #Select Browser Here
        ctk.CTkLabel(self, text="Select Browser: ", corner_radius=10).grid(row=1, column=0, padx=5, pady=5, sticky="ew",columnspan=1)
        self.browser = ctk.CTkOptionMenu(self, values=self.browsers, command=lambda x: self.set_browser(x),corner_radius=10,dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.browser.grid(row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=1)

        #Select Producer Here
        ctk.CTkLabel(self, text="Select Producer: ", text_color="white", corner_radius=10).grid(row=2, column=0, padx=5, pady=5, sticky="ew", columnspan=1)
        self.producer = ctk.CTkOptionMenu(self, values=File.get_producers("Local"), command=lambda x: self.set_producer(x),corner_radius=10,dropdown_fg_color=self.drop_back_color,dropdown_hover_color=self.drop_hover_color)
        self.producer.grid(row=2, column=1, padx=5, pady=5, sticky="ew", columnspan=1)

        #Producer Delete Button
        self.producer_delete_button = ctk.CTkButton(self, text="Delete", command=lambda: self.delete_producer(), width=50)
        self.producer_delete_button.grid(row=2, column=2, padx=50, pady=5, sticky="ew")

        #Tabs setup here
        self.tab_view = MyTabView(master=self,width=600)
        self.tab_view.grid(row=3, column=0, padx=10, pady=5,columnspan=3, sticky="nsew")

        my_font = ctk.CTkFont(family="TimesNewRoman",size=15, weight="bold")

        # Configure the segmented button's font
        for button in self.tab_view._segmented_button._buttons_dict.values():
            button.configure(font=my_font)

        self.tab_view.scrollable_checkbox_frame.producer = self.producer._values[0]

    def delete_producer(self):
        print(self.producer.get())
        self.producers = File.remove_producer(self.selected_producer)
        self.producer.configure(values=self.producers)
        self.producer.set(self.producers[0] if len(self.producers) > 0 else "Add Producer")
        if len(self.producers) > 0:
            self.producer.set("Select Producer")
        else:
            self.producer.set("Add Producer")
    
    def set_environment(self, env):
            File.env_used = env
            self.environment = env
            self.tab_view.environment = env
            self.tab_view.scrollable_checkbox_frame.environment = env
            self.producers = File.get_producers(env)
            self.producer.configure(values=self.producers)
            self.tab_view.scrollable_checkbox_frame.producer = self.producer._values[0]
        
            if len(self.producers) != 0:
                self.producer.set(self.producers[0])
            else:
                self.producer.set("Add Producer")

            self.tab_view.scrollable_checkbox_frame.set_users()
            self.tab_view.env_change()  # Update the environment in the tab view
            self.tab_view.scrollable_checkbox_frame.application.env_used = env

    def set_browser(self, browser):
        self.browser = browser
        self.tab_view.browser = browser
        self.tab_view.scrollable_checkbox_frame.browser = browser
        self.tab_view.scrollable_checkbox_frame.application.browser_chosen = browser
    
    def set_producer(self, producer):
        self.selected_producer = producer
        self.tab_view.producer = producer
        self.tab_view.scrollable_checkbox_frame.producer = producer
        self.tab_view.scrollable_checkbox_frame.application.producer_selected = producer

app = App()
app.wm_protocol(func = app.destroy) 

#Added Andover Image as Icon
advr_image1 = ImageTk.PhotoImage(Image.open("SupportFiles/Andover-Cambridge-Mutual.png").resize((64, 64)))  # Resize the image to fit the icon size
app.iconphoto(False, advr_image1)  # Set the icon for the application
app.after(100, lambda: app.iconphoto(False, advr_image1))  # Ensure the icon is set after the main loop starts

app.mainloop()
del app