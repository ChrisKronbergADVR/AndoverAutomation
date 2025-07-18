import os
#from SupportFiles.Interface import Interface
from SupportFiles.File import File
from SupportFiles.custom_tab import App

LOG_PATH = "Logs/"

def main():
    #interface = Interface()
    if (not os.path.exists(LOG_PATH)):
        os.mkdir(LOG_PATH)
    File.create_folders()
    File.create_files()
    #interface.make_window()
    #del interface
    #App()
  
if __name__ == '__main__':
    main()