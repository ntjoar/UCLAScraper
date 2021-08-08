import os
import json
from datetime import date
from classes import getClasses, getSchedule

##################################################
#                     Helper                     #
##################################################
# Helper function to save settings into pref.json
def saveSettings(data):
    with open('./pref.json', 'w') as outfile:
        json.dump(data, outfile, indent=1)

# If folders don't exist, we need to make them
def initializeFolders():
    if not os.path.isdir('./Results'): 
        os.mkdir('./Results')

    if not os.path.isdir('./Class_Data'): 
        os.mkdir('./Class_Data')

    return

def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

#################################################
#                    Startup                    #
#################################################
# On startup load all values
def startUp(): 
    data = {}
    data['settings'] = []
    
    # Load our setting preferences
    if not os.path.isfile('./pref.json'):
        resetSettings(False)
            
    with open('./pref.json', 'r') as infile:
        data['settings'] = json.load(infile)['settings']

    if data['settings'][0]['disclaimerRead'] == False:
        # Notice agreement so that user knows we need acess
        print("Notice: this will create local folders to store data into. Please ensure the application has the necessary write privileges.\n---")
        inputData = ''
        
        # Agreement
        while inputData != 'y' and inputData != 'n':
            inputData = input("Continue (y/n): ")

            if inputData == 'y':
                # Disclaimer has been read and agreed to
                data['settings'][0]['disclaimerRead'] = True
                saveSettings(data)
                print("===")
            elif inputData == 'n':
                print("Unable to run program, exiting...")
            else: 
                print("=\nPlease enter (y/n)\n=")

    return
    
##################################################
#                      Menu                      #
##################################################
def initialize():
    print("Initializing all requirments...")

    # Load our setting preferences
    if not os.path.isfile('./pref.json'):
        resetSettings(False)

    if os.path.isfile('./Results/classDesc.json'):
        confirm = ''
        while confirm != 'y' and confirm != 'n':
            confirm = input("./Results/classDesc.json already exists. Overwrite (y/n)? ")
            if confirm == 'y':
                os.remove('./Results/classDesc.json')
                getClasses(True, True)
            elif confirm == 'n':
                return
            else:
                print("=\nPlease enter (y/n)\n=")
    else:
        getClasses(True, True)

# Clears Class_Data folder
def clearClassData():
    for filename in os.listdir('./Class_Data'):
        os.remove('./Class_Data/' + filename)

# Clears Results folder
def clearResults():
    for filename in os.listdir('./Results'):
        os.remove('./Results/' + filename)

# Empty just the Class_Data
def clean():
    confirm = ''
    while confirm != 'y' and confirm != 'n':
        confirm = input("All files in ./Class_Data/ will be deleted. Continue (y/n)? ")
        if confirm == 'y':
            clearClassData()
        elif confirm == 'n':
            return
        else:
            print("=\nPlease enter (y/n)\n=")

# Empty results  
def clean_all():
    confirm = ''
    while confirm != 'y' and confirm != 'n':
        confirm = input("All files in ./Class_Data/ and ./Results/ will be deleted. Continue (y/n)? ")
        if confirm == 'y':
            clearClassData()
            clearResults()
        elif confirm == 'n':
            return
        else:
            print("=\nPlease enter (y/n)\n=")

# Print dependencies
def dependencies():
    print("Please install necessary dependencies as listed below\n---")
    print("Regex: https://pypi.org/project/regex/")
    print("DateTime: https://pypi.org/project/DateTime/")
    print("Selenium: https://pypi.org/project/selenium/")
    print("Beautiful Soup: https://pypi.org/project/beautifulsoup4/")

# Help main menu print
def helpMain():
    print("Help\n---")
    print("1: Initialize (If you just want to get the courses - i.e. COM SCI, MECH&AE")
    print("2: Run (Runs the entire program and checks for dependency")
    print("3: Run all (Runs everything, even inialization, will take a little longer)")
    print("4: Clean (Cleans out the folder we are writing all our course data in)")
    print("5: Clean all (Clears out Course data and the results of running the program)")
    print("6: Settings")
    print("7: List Dependencies (List of dependencies to install)")
    print("8: Help (Get a summary of each option)")
    print("9: Quit (Quit the program)")

def menu():
    # Store vars
    inputMenu = '0'
    data = {}
    data['settings'] = []

    # Introduction
    print("Welcome to the UCLA scraper menu\n===")
    print("Notice: this application has some necessary dependencies. For a list, please select option 7.")

    while inputMenu != '9':
        # In case we accidentally delete pref.json 
        if not os.path.isfile('./pref.json'):
            print("ERROR: pref.json not found. Reinitializing...")
            resetSettings(True)

        with open('./pref.json', 'r') as infile:
            data['settings'] = json.load(infile)['settings']

        verbose = data['settings'][0]['verbose']
        quarter = data['settings'][0]['quarter']
        year = data['settings'][0]['year']
        headless = data['settings'][0]['headless']
        overwrite = data['settings'][0]['overwrite']
        toClean = data['settings'][0]['cleanAfterRun']
        if data['settings'][0]['developer']:
            verbose = True
            headless = False
            overwrite = True
            toClean = False

        print("Main menu\n-")
        print("1: Initialize\n2: Run\n3: Run all\n4: Clean\n5: Clean all\n6: Settings\n7: List Dependencies\n8: Help\n9: Quit\n-")
        inputMenu = input("Please enter a number: ")
        print("=")

        if inputMenu == '1': 
            initialize()
        elif inputMenu == '2':
            if not os.path.exists('./Results/classDesc.json'):
                print("Getting list of courses")
                getClasses(headless, verbose)
            print("Getting schedule of courses")
            getSchedule(year, quarter, verbose, headless, overwrite)
            if toClean:
                print("Clearing Class_Data")
                clearClassData()
        elif inputMenu == '3':
            print("Getting list of courses")
            getClasses(headless, verbose)
            print("Getting schedule of courses")
            getSchedule(year, quarter, verbose, headless, overwrite)
            if toClean:
                print("Clearing Class_Data")
                clearClassData()
        elif inputMenu == '4':
            clean()
        elif inputMenu == '5':
            clean_all()
        elif inputMenu == '6':
            settings()
        elif inputMenu == '7':
            dependencies()
        elif inputMenu == '8':
            helpMain()
        elif inputMenu == '9':
            print("===\nExiting application...")
        else:
            print("Unknown Command, please choose an available option")

        print("=")

##################################################
#                    Settings                    #
##################################################
# Toggle verbose
def toggle(data, setting):
    cur = data['settings'][0][setting]
    challenge = ''
    if setting == 'cleanAfterRun':
        challenge = 'Clean after run'
    else:
        challenge = setting.capitalize()

    if cur == True:
        challenge = challenge + ' mode will be toggled to false. Continue (y/n)? '
    else:
        challenge = challenge + ' mode will be toggled to true. Continue (y/n)? '

    confirm = ''
    while confirm != 'y' and confirm != 'n':
        confirm = input(challenge)
        if confirm == 'y':
            data['settings'][0][setting] = not cur
            saveSettings(data)
        elif confirm == 'n':
            return
        else:
            print("=\nPlease enter (y/n)\n=")

def setQuarterandYear(data):
    year = data['settings'][0]['year']
    quarter = data['settings'][0]['quarter']
    curYear = date.today().strftime("%Y")

    # Get new year
    yearIn = ''
    yearInt = 0
    while yearInt > int(curYear) + 1 or yearInt < int(curYear) - 2:
        yearIn = input('Please specify a year to parse from (or leave empty to skip): ')
        if yearIn == '':
            break

        if representsInt(yearIn):
            yearInt = int(yearIn)
            if yearInt > int(curYear) + 1 or yearInt < int(curYear) - 2:
                print("=\nPlease enter a valid year from " + str(int(curYear) - 2) + " to " + str(int(curYear) + 1) + "\n=")
            else:
                year = yearIn
        else:
            print("=\nPlease enter a valid year from " + str(int(curYear) - 2) + " to " + str(int(curYear) + 1) + "\n=")

    # Get new quarter
    quarterIn = 'ABC'
    while quarterIn != 'Fall' and quarterIn != 'Spring' and quarterIn != 'Summer' and quarterIn != 'Winter' and quarterIn != '':
        quarterIn = input('Please specify a quarter to parse from (or leave empty to skip): ')

        if quarterIn != 'Fall' and quarterIn != 'Spring' and quarterIn != 'Summer' and quarterIn != 'Winter' and quarterIn != '':
            print("=\nPlease enter Fall, Winter, Spring, Summer, or leave blank\n=")
        else: 
            quarter = quarterIn

    data['settings'][0]['year'] = year
    data['settings'][0]['quarter'] = quarter

    saveSettings(data)

# Reset Settings
def resetSettings(reinit):
    data = {}
    data['settings'] = []
    data['settings'].append({
        'disclaimerRead': reinit,
        'verbose': False,
        'quarter': 'Fall',
        'year': date.today().strftime("%Y"),
        'headless': True,
        'developer': False,
        'overwrite': False,
        'cleanAfterRun': True,
    })
    saveSettings(data)

# Settings help menu
def settingsHelp():
    print("Help\n---")
    print("1: Verbose (Set verbose logging - on by default)")
    print("2: Quarter and Year (Set the quarter and year to scrape)")
    print("3: Headless mode (Set headless mode - off by default)")
    print("4: Developer mode (Set verbose flag, nonheadless running, no deletion of Class_Data, and overwrite flags)")
    print("5: Overwrite mode (Set if you want the script to overwrite your currently saved data)")
    print("6: Run Cleanly (Set if you want your script to run and clear the Class_Data folder afterwards - on by default)")
    print("7: Reset settings (Set all settings to default)")
    print("8: Help (Get a summary of each option)")
    print("9: Back to main menu (Return to main menu)")

# Print settings
def settings():
    # Store vars
    inputMenu = '0'
    data = {}
    data['settings'] = []

    while inputMenu != '9':
        # In case we accidentally delete pref.json 
        if not os.path.isfile('./pref.json'):
            print("ERROR: pref.json not found. Reinitializing...")
            resetSettings(True)

        print("Settings\n-")
        print("1: Toggle verbose\n2: Set Quarter and year\n3: Toggle headless mode\n4: Toggle Developer mode\n5: Toggle Overwrite mode\n6: Toggle run cleanly\n7: Reset settings\n8: Help\n9: Back to main menu\n-")
        inputMenu = input("Please enter a number: ")
        print("=")

        if inputMenu == '1': 
            toggle(data, 'verbose')
        elif inputMenu == '2':
            setQuarterandYear(data)
        elif inputMenu == '3':
            toggle(data, 'headless')
        elif inputMenu == '4':
            toggle(data, 'developer')
        elif inputMenu == '5':
            toggle(data, 'overwrite')
        elif inputMenu == '6':
            toggle(data, 'cleanAfterRun')
        elif inputMenu == '7':
            print("Resetting settings...")
            resetSettings(False)
        elif inputMenu == '8':
            settingsHelp()
        elif inputMenu == '9':
            return
        else:
            print("Unknown Command, please choose an available option")

        # print("\nVerbose: " + verbose)
        # print("Headless: " + headless)
        # print("Dev Mode: " + devMode)
        # print("Overwrite: " + overwrite)
        print("=")
    
    return 


##################################################
#                  Main Program                  #
##################################################
# Main running program
def main(): 
    startUp()
    initializeFolders()
    menu()
    
main()

