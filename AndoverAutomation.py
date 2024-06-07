import os
from SupportFiles.Interface import Interface
from SupportFiles.File import File

LOG_PATH = "Logs/"

def main():
    interface = Interface()
    if(not os.path.exists(LOG_PATH)):
        os.mkdir(LOG_PATH)
    File.create_files()
    interface.make_window()

if __name__ == '__main__':
    main()