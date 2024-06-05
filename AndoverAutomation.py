import os
from SupportFiles.Interface import Interface
from SupportFiles.File import File

def main():
    interface = Interface()
    if(not os.path.exists("Logs")):
        os.mkdir("Logs")

    File.create_files()
    interface.make_window()

if __name__ == '__main__':
    main()