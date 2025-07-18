import os
from SupportFiles.File import File
from SupportFiles.custom_tab import App

LOG_PATH = "Logs/"

def main():
    if (not os.path.exists(LOG_PATH)):
        os.mkdir(LOG_PATH)
    File.create_folders()
    File.create_files()
  
if __name__ == '__main__':
    main()