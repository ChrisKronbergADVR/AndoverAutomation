# Pysimplegui has updated and no longer has version 4.6. I will work on getting a gui added before the 30 day trial is up for version 5 as it costs $99. 
                                                     
                                                     # AndoverAutomation
Python Automation with GUI for Andover Local and QA Environments

### **** If you find any bugs or features you would like to be added. click on the issues Tab on Github - New Issue Button then either bug report Button or feature request Button and fill out the Information. ****

### If you already have Python installed, you can skip the Python install

### A new .bat file was added to help run the python program from a shortcut. Copy the runAutomation.bat file and paste the shortcut to the desktop. After this is done, you can rename the file to whatever you want and it will launch the automation software.
---

## 1. Installing Python
- click  [here](https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe) to download python version 3.12.3


&emsp; <a href="https://www.python.org/downloads/"><img src = "https://www.python.org/static/img/python-logo.png" height="50rem"></a>
<br>
<br>

&emsp;&emsp;&emsp;&emsp;- Make sure the pip selection is checked like it is  in the image below.
<br>
<br>
<p align="center" width="100%"><img src = "docImages\first.png" height="300rem"></p>
<br>
<br>
&emsp;&emsp;&emsp;&emsp;- Make sure to add the environment variable checkbox when installing Python also.
<br>
<br>
<p align="center" width="100%"><img src = "docImages\secondPic.png" height="300rem"></p>
<br>
<br>
<br>
<br>

<h4>&ensp; 1. Check the Python version to make sure it is installed with the command below in a command prompt or terminal. This can be done from vs code as well</h4>

&emsp;&emsp;&emsp;&emsp;```python --version```

&emsp;&emsp;&emsp;&emsp;- if it returns a version number for Python, it is working correctly. It should return =>  Python 3.12.3 or the python version that is installed

&emsp;&emsp;&emsp;&emsp;- if it does not return Python with a version number try the suggestions below in a terminal or command prompt: 

&emsp;&emsp;&emsp;&emsp;&emsp;```py --version```

&emsp;&emsp;&emsp;&emsp;&emsp;```python3 --version```

<br>
<h4>&ensp; 2. Check the pip version to make sure it is installed with the commands below</h4>

&emsp;&emsp;&emsp;&emsp;&emsp;```pip --version```

&emsp;&emsp;&emsp;&emsp;&emsp;```pip3 --version```

&emsp;&emsp;&emsp;&emsp;&emsp;```pip3.12 --version``` 

<br>
<h4>&ensp; 3. Click the code button</h4>

<p align="center" width="100%"><img src = "docImages\codeButton.png" height="300rem"></p>

- You can click the copy button to copy the code and then add git clone to the beginning of it in a terminal or command prompt. I have already copied and added git clone so you do not have to do that with the text below. you can just copy what is below and paste it  into a terminal or command prompt.

&emsp;&emsp;&emsp;&emsp;&emsp;```git clone https://github.com/ChrisKronbergADVR/AndoverAutomation.git```


- If you would like to download the zip file, you can do that also by clicking Download ZIP.
<hr>
<br>

### 2. After you have completed all of the above steps, the packages needed to run this script are in the file requirements.txt
- first, make sure you are in the directory with the requirements.txt file
- The command to enter into a command prompt is: ```pip install -r requirements.txt```
- If the command above does not work then try: ```pip3 install -r requirements.txt```

### 3. To run the file you can navigate to the directory in command prompt by opening command prompt and using cd (change directory) or copying the file path from the file explorer.
<br>
<p align="center" width="100%"><img src = "docImages\file_in_exporer.jpg" height="300rem"></p>

<br>

 - To run the program: open the command prompt and paste the file path
 - The program should run after pressing the enter key

<br>
<p align="center" width="100%"><img src = "docImages\cmd_prompt.jpg" height="300rem"></p>
<br>

<hr>

## 2. How to use the GUI

### There are pictures below of the GUI with numbers letting you know each function of this application
<br>
<p align="center" width="100%"><img src = "docImages\DetailedGUI1.jpg" height="700rem"></p>
<p align="center">GUI Image 1</p>

#### 1. This is where the Environment is selected. This is either one of the many QA environments or local development environment.
#### 2. Select the web browser you would like to use. This can be either the google chrome or Edge browser
#### 3. Select the Add users and producers tab to add users and producers or to change the password of a current user.
#### 4. Select the username that you would like to test with here
#### 5. Delete the user that has been selected in 4
#### 6. Select the producer to use in testing here
#### 7. Delete the prducer that has been selected in 6
#### 8. Select the state to be used for the quote, application, or policy
#### 9. Select the checkbox for the next
#### 10. Add Address and Select Verify Address in GUI 2
#### 11. Select the line of business to use here
#### 12. Select the date from clicking the date select button or entering the date in the input box to the left of the button
#### 13. Enter the Insured's first and last name here
#### 14. Click on the dropdown box for selecting a quote, application or policy
#### 15. Click submit if everything has been entered and looks good. Otherwise, you can go back and change information or click cancel to exit the application.

<br>
<p align="center" width="100%">
<img src = "docImages\DetailedGUI2.jpg" height="700rem"></p>
<p align="center">GUI Image 2</p>
<br>
<hr>

### Adding users and Producers
<p align="center" width="100%"><img  src = "docImages\DetailedGUI3.jpg" height="700rem"></p>
<p align="center">GUI Image 3</p>


#### 1. Select the environment in either QA or development environment
#### 2. If adding a user or changing the password, enter the username and password and click the add user button
#### 3. If adding a producer to the environment, enter the producer name and click the add producer button
