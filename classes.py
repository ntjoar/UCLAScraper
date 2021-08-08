from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path
import re
import time
import json
import os

# Helper function to instantiate chrome driver
def drive(headless):
    # Set Headless
    chromeOpt = Options()
    chromeOpt.add_argument('--headless')
    chromeOpt.add_argument('--disable-gpu')

    if headless:
        return webdriver.Chrome(options=chromeOpt, executable_path=binary_path)
    else:
        return webdriver.Chrome(executable_path=binary_path)
        
# Script only gets the classes that we have available on the registrar site
def getClasses(headless, verbose): 
    # JSON storage
    data = {}
    data['courses'] = []

    # URL list (CHANGE ONLY THIS LINK TO ADJUST FOR DNS CHANGES)
    baseURL = "https://registrar.ucla.edu/faculty-staff/courses-and-programs/department-and-subject-area-codes"

    # Class Name list (No formatting handled yet)
    classList = []
    abbrevList = []

    # Create a new Chrome Session
    driver = drive(headless)
    driver.implicitly_wait(30)
    driver.get(baseURL)

    # Selenium hands the page source to Beautiful Soup
    soup_classes = BeautifulSoup(driver.page_source, 'lxml')

    # Parse the table in the document
    for row in soup_classes.find('table', attrs={'class':'js-sortable'}).find('tbody').find_all('tr'):
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        classList.append(cols[2])
        abbrevList.append(cols[3])

    # Error checking of list lengths
    if len(classList) != len(abbrevList) or len(classList) == 0 or len(abbrevList) == 0:
        if verbose: 
            print("Error: Class list length and abbreviation list length vary.")
        driver.quit()
        return

    # Convert data to json
    for i in range(len(classList)):
        data['courses'].append({
            'class' : classList[i], 
            'abbrev' : abbrevList[i]
        })

    # Write to json
    with open('./Results/classDesc.json', 'w') as outfile:
        json.dump(data, outfile, indent=1)

    driver.quit()
    return

def getSchedule(year, quarter, verbose, headless, overwrite):
    # Constants
    classSearchURL = "https://sa.ucla.edu/ro/public/soc/"

    # JSON storage
    data = {}
    data['courses'] = []

    # Temp variables
    i = 0

    # Lists
    classList = []
    abbrevList = []
    formattedAbbrevList = []

    # Parse term
    term = ""
    if quarter == "Spring":
        term = "S"
    elif quarter == "Fall":
        term = "F"
    elif quarter == "Winter":
        term = "W"
    else:
        term = "1"
    urlFormatTerm = year[len(year)-2:len(year)] + term

    # Load our class Data
    classJson = []
    with open('./Results/classDesc.json', 'r') as infile:
        classJson = json.load(infile)['courses']
    for c in classJson: 
        classList.append(c['class'])
        abbrevList.append(c['abbrev'])

    # For every subject we got from the master course list, run a search
    for subjectName in classList:
        data['courses'] = []

        # Format strings as below
        # " " = "+"
        # "/" = "%2F"
        # "," = "%2C"
        # "&" = "%26"
        formattedSubjName = subjectName
        formattedAbbrev = abbrevList[i]

        urlAbbrev = abbrevList[i].replace("/", "%2" + "F")
        urlAbbrev = urlAbbrev.replace(",", "%2C")
        urlAbbrev = urlAbbrev.replace("&", "%26")
        urlAbbrev = urlAbbrev.replace(" ", "+")
        formattedAbbrevList.append(formattedAbbrev)
        formattedFullName = subjectName + ' (' + formattedAbbrev + ')'

        # Format Strings into url appendages
        urlSubjName = formattedSubjName.replace("/", "%2" + "F")
        urlSubjName = urlSubjName.replace(",", "%2C")
        urlSubjName = urlSubjName.replace("&", "%26")
        urlSubjName = urlSubjName.replace(" ", "+")
        urlClassFull = urlSubjName + '+(' + urlAbbrev + ')'

        # Regex abbreviation
        regexAbbrev = urlAbbrev.replace("+", "")
        regexAbbrev = regexAbbrev.replace("%2" + "F", "")
        regexAbbrev = regexAbbrev.replace("%2C", "")
        regexAbbrev = regexAbbrev.replace("%26", "")

        # Format url
        urlAppend = "Results?SubjectAreaName=" + urlClassFull + "&t=" + urlFormatTerm + "&sBy=subject&subj=" + urlAbbrev + "&catlg=&cls_no=&undefined=Go&btnIsInIndex=btn_inIndex"
        url = classSearchURL + urlAppend
        
        # Increment i
        i = i+1

        # If file for this already exists, skip
        if os.path.isfile('./Class_Data/' + formattedAbbrev + "_" +  year + "_" +  quarter +  '.json') and not overwrite:
            continue

        # Create a new Chrome Session
        driver = drive(headless)
        driver.implicitly_wait(30)
        driver.get(url)
        time.sleep(3)

        # Selenium hands the page source to Beautiful Soup
        classExists = BeautifulSoup(driver.page_source, 'lxml')
        if not classExists.find('a', id=re.compile(r"^expandAll$")):
            # Write our data 
            with open("./Class_Data/"+ formattedAbbrev + "_" +  year + "_" +  quarter +  '.json', 'w') as outfile:
                json.dump(data, outfile, indent=1)
            if verbose:
                print("No class exists for " + formattedFullName + "\nWriting empty file...")
                print("---")
            continue

        # Check for extra pages
        # Bypass UCLA's shadow root
        element = driver.find_element_by_tag_name('ucla-sa-soc-app')
        pages_shadow = driver.execute_script('return arguments[0].shadowRoot', element)
        pages_shadow_html = BeautifulSoup(driver.execute_script('return arguments[0].shadowRoot.innerHTML', element), 'lxml')
        extraPages = pages_shadow_html.find('ul', class_=re.compile(r'jPag-pages'))
        if extraPages == None:
             # Bypass UCLA's shadow root
            lenPages = 1
        else: 
            python_button_pages = pages_shadow.find_element_by_class_name('jPag-pages').find_elements_by_tag_name('a')
            lenPages = len(extraPages.find_all('li'))

        # Reset which page we are on
        page_id = 0

        # Keep searching through pages
        while page_id < lenPages:
            # Bypass UCLA's shadow root
            element = driver.find_element_by_tag_name('ucla-sa-soc-app')
            shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
            python_button = shadow_root.find_element_by_id('expandAll')
            python_button.click()
            time.sleep(5)

            # Selenium hands the page source to Beautiful Soup
            driver.switch_to.window(driver.window_handles[0])
            element = driver.find_element_by_tag_name('ucla-sa-soc-app')
            shadow_root_html = driver.execute_script('return arguments[0].shadowRoot.innerHTML', element)
            soup = BeautifulSoup(shadow_root_html, 'lxml')

            for course in soup.find_all('div', class_=re.compile(r"class-title")):
                fullCourse = course.find('h3').text
                courseName = fullCourse[fullCourse.find('-')+2:len(fullCourse)]
                courseNumber = fullCourse[0:fullCourse.find('-')-1]
                
                for lec in course.find_all('div', id=re.compile(r"^[0-9]{9}_" + course.get('id') + r"$")):
                    professor = lec.find('div', id=re.compile(r"^" + lec.get('id') + r"-instructor_data")).text
                    
                    if lec.find('div', class_=re.compile(r"toggle")): # Get discussions or if just lecture parse
                        for dis in course.find_all('div', id=re.compile(r"^[0-9]{9}_" + lec.get('id') + r"$")):
                            courseID = dis.get('id')[0:9]
                            no = dis.find('div', id=re.compile(r"^" + dis.get('id') + r"-section$")).find('p').text.strip()
                            section = no[no.find(' ')+1:len(no)]

                            # Print data
                            if verbose:
                                print("courseID: " + courseID)
                                print("courseName: " + courseName)
                                print("subjectArea: " + formattedFullName)
                                print("courseNumber: " + courseNumber)
                                print("professor: " + professor)
                                print("Section: " + section)
                                print("quarter: " + quarter)
                                print("year: " + year)
                                print("---")


                            # Add data to json array
                            data['courses'].append({
                                'courseID' : courseID,
                                'courseName' : courseName,
                                'subjectArea' : formattedFullName,
                                'courseNumber' : courseNumber,
                                'professor' : professor,
                                'section' : section,
                                'quarter' : quarter,
                                'year' : year
                            })
                    else:
                        courseID = lec.get('id')[0:9]
                        no = lec.find('div', id=re.compile(r"^" + lec.get('id') + r"-section$")).find('p').text.strip()
                        section = no[no.find(' ')+1:len(no)]

                        # Print data
                        if verbose:
                            print("courseID: " + courseID)
                            print("courseName: " + courseName)
                            print("subjectArea: " + formattedFullName)
                            print("courseNumber: " + courseNumber)
                            print("professor: " + professor)
                            print("Section: " + section)
                            print("quarter: " + quarter)
                            print("year: " + year)
                            print("---")

                        # Add data to json array
                        data['courses'].append({
                            'courseID' : courseID,
                            'courseName' : courseName,
                            'subjectArea' : formattedFullName,
                            'courseNumber' : courseNumber,
                            'professor' : professor,
                            'section' : section,
                            'quarter' : quarter,
                            'year' : year
                        })

            # Paginate if needed
            if lenPages - 1 != page_id:
                python_button_pages[page_id].click()
                time.sleep(2)

                # Reload elements
                element = driver.find_element_by_tag_name('ucla-sa-soc-app')
                pages_shadow = driver.execute_script('return arguments[0].shadowRoot', element)
                pages_shadow_html = BeautifulSoup(driver.execute_script('return arguments[0].shadowRoot.innerHTML', element), 'lxml')
                python_button_pages = pages_shadow.find_element_by_class_name('jPag-pages').find_elements_by_tag_name('a')

            page_id = page_id+1

        driver.quit()

        # Write our data 
        with open("./Class_Data/" + formattedAbbrev + "_" +  year + "_" +  quarter +  '.json', 'w') as outfile:
            json.dump(data, outfile, indent=1)

    # Clear data so we can put in the final formatted data
    data['courses'] = []

    formattedAbbrevList.sort()

    # Iterate through and get the list
    for subjectName in formattedAbbrevList:
        tempArr = []

        with open("./Class_Data/" + subjectName + "_" +  year + "_" +  quarter + ".json", 'r') as infile:
            tempArr = json.load(infile)['courses']

        for cl in tempArr:
            data['courses'].append(cl)

    # Write results
    with open("./Results/" + "classes" + "_" +  year + "_" +  quarter + ".json", 'w') as outfile:
        json.dump(data, outfile, indent=1)