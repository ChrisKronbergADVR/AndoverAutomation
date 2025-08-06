import os
from csv import DictReader, DictWriter
from datetime import datetime

class File:
    env_used = None
    folder = "csvFiles/"

    gw_environment = {"Local": "https://localhost:9443", "QA": "https://qa-advr.iscs.com/", "QA2": "https://qa2-acx-advr.in.guidewire.net/innovation", "UAT3": "https://uat3-advr.in.guidewire.net/innovation?saml=off","UAT4": "https://uat4-advr.in.guidewire.net/innovation"}

    env_files_plus_users = {
        "QA": {"Users": {"file": "users.csv", "Usernames": {}},
               "Producers": {"file": "producers.csv", "ProducerNames": ["ALLSTATES HO and DW"]}},
        "Local": {"Users": {"file": "local_users.csv", "Usernames": {}},
                  "Producers": {"file": "local_prod.csv", "ProducerNames": ["DEF"]}},
        "QA2": {"Users": {"file": "qa2_user.csv", "Usernames": {}},
                "Producers": {"file": "qa2_prod.csv", "ProducerNames": ["ALLSTATES HO and DW"]}},
        "UAT3": {"Users": {"file": "uat3_user.csv", "Usernames": {}},
                 "Producers": {"file": "uat3_prod.csv", "ProducerNames": [""]}},
        "UAT4": {"Users": {"file": "uat4_user.csv", "Usernames": {}},
                 "Producers": {"file": "uat4_prod.csv", "ProducerNames": [""]}},
    }
    
    filePath = "Logs/"
    log_path = datetime.now()
    year = log_path.year
    month = log_path.month
    day = log_path.day

    day_path = f"{filePath}{year}/{month}/{day}"
    month_path = f"{filePath}{year}/{month}"
    year_path = f"{filePath}{year}"

    @staticmethod
    def create_folders():
        if (not os.path.exists(File.year_path)):
            os.mkdir(File.year_path)
        if (not os.path.exists(File.month_path)):
            os.mkdir(File.month_path)
        if (not os.path.exists(File.day_path)):
            os.mkdir(File.day_path)

    # Functions for creating, reading and writing to file
    @staticmethod
    def create_files():
        folder = File.folder
        if (not os.path.exists(folder)):
            os.mkdir(folder)
        for env_name in File.env_files_plus_users.keys():
            file_user = File.env_files_plus_users[env_name]['Users']['file']
            file_prod = File.env_files_plus_users[env_name]['Producers']['file']
            if not (os.path.exists(folder+file_user)):
                with open(folder+file_user, "w") as file_users:
                    File.write_username_password(
                        folder+file_user, File.env_files_plus_users[env_name]["Users"]["Usernames"])
                with open(folder+file_prod, "w") as file_prods:
                    File.write_producer(
                        folder+file_prod, File.env_files_plus_users[env_name]["Producers"]["ProducerNames"])

    # This function takes a file and user dictionary and writes the username and password to a csv file
    @staticmethod
    def write_username_password(file, user_dict):
        with open(file, 'w', newline='') as csvfile:
            fieldnames = ['Username', 'Password']
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            if os.path.getsize(file) == 0:
                writer.writeheader()
            for user, password in user_dict.items():
                writer.writerow({'Username': user, 'Password': password})

    @staticmethod
    def get_password(user):
        password = File.env_files_plus_users[File.env_used]["Users"]["Usernames"][user]
        return password

    # This function takes a file and user dictionary and writes the username and password to a csv file
    @staticmethod
    def write_username_password(file, user_dict):
        with open(file, 'w', newline='') as csvfile:
            fieldnames = ['Username', 'Password']
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            if os.path.getsize(file) == 0:
                writer.writeheader()
            for user, password in user_dict.items():
                writer.writerow({'Username': user, 'Password': password})

    @staticmethod
    def read_username_password():
        with open(File.folder+File.env_files_plus_users[File.env_used]['Users']['file'], newline='') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                File.env_files_plus_users[File.env_used]['Users']['Usernames'][row['Username']
                                                                               ] = row["Password"]

    # Add a user to the file and GUI
    @staticmethod
    def add_user(user_name, password):
        File.env_files_plus_users[File.env_used]['Users']['Usernames'][user_name] = password
        file_name = File.env_files_plus_users[File.env_used]['Users']['file']
        user_dict = File.env_files_plus_users[File.env_used]['Users']['Usernames']
        File.write_username_password(File.folder+file_name, user_dict)

   # Read producers from file
    @staticmethod
    def read_producers():
        File.env_files_plus_users[File.env_used]['Producers']['ProducerNames'] = [
        ]
        with open(File.folder+File.env_files_plus_users[File.env_used]['Producers']['file'], newline='') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                File.env_files_plus_users[File.env_used]['Producers']['ProducerNames'].append(
                    row["Producer"])

    @staticmethod
    def add_producer(producer_name):
        File.env_files_plus_users[File.env_used]['Producers']['ProducerNames'].append(
            producer_name)
        File.write_producer(File.folder+File.env_files_plus_users[File.env_used]['Producers']
                            ['file'], File.env_files_plus_users[File.env_used]['Producers']['ProducerNames'])

    # Add producer to file
    @staticmethod
    def write_producer(fileName, prod_list):
        with open(fileName, 'w', newline='') as csvfile:
            fieldnames = ['Producer']
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            if os.path.getsize(fileName) == 0:
                writer.writeheader()
            for producer in prod_list:
                writer.writerow({'Producer': producer})