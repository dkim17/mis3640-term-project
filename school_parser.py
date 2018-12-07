from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import bs4
import csv
from lxml import etree
import re

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(chrome_options=chrome_options)

base_url = "https://fusionmx.babson.edu/CourseListing/"

driver.get("https://fusionmx.babson.edu")

inputElement = driver.find_element_by_name("babsonauth_user")
#USERNAME
inputElement.send_keys('dkim17')


inputElement = driver.find_element_by_name("babsonauth_pass")
#PASSWORD
inputElement.send_keys('Pogba2018!')


inputElement = driver.find_element_by_name("formGetCredentials")
inputElement.submit()

driver.get("https://fusionmx.babson.edu/CourseListing/index.cfm?fuseaction=CourseListing.DisplayCourseListing&blnShowHeader=false&program=Undergraduate&semester=All&sort_by=course_level&btnSubmit=Display+Courses")

# open("courses.html", 'w').write(driver.page_source)


def get_details(link):
    driver.get(base_url+link)
    popup_page = bs4.BeautifulSoup(driver.page_source)
    popup_page.findAll('tr', {'valign': 'top'})[1].findAll(
        'td', {'class': 'boldText'})[0].findNext('td')
    attrs = {}
    for srow in popup_page.findAll('tr', {'valign': 'top'}):
        for attr in srow.findAll('td', {'class': 'boldText'}):
            attrs[attr.text.strip().replace(':',"")] = attr.findNext('td').text
    return attrs


page = bs4.BeautifulSoup(driver.page_source)
# htmlparser = etree.HTMLParser()
source = driver.page_source
# page = etree.parse(source, htmlparser)

headers = [
    'Capacity',
    'Course Level',
    'Course No',
    'Course Title',
    'Credits',
    'Days Time',
    'Days',
    'Description',
    'Division',
    'End Date',
    'Enroll/Cap',
    'Enrolled',
    'Instructor(s)',
    'Location',
    'Program',
    'Section',
    'Semister',
    'Session',
    'Start Date',
    "Year",
    "Times",
    "Term",
    "Title"
]
with open("courses.csv", 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

    for semister in page.select("table[border='1']"):
        semister_name = re.sub(
            r'[\n\t]', '', semister.select_one("tr.tableheader").text)
        for semister_course in semister.select("tr[bgcolor='#efeff5']"):
            course_name = re.sub(r'[\n\t]', '', semister_course.text)
            for section in semister_course.findNextSibling().findAll('tr', {'valign': 'top'}):
                section_info = [re.sub(r'[\n\t]', '', info.text.strip())
                                for info in section.findChildren("td")]
                details_link = section.find('a')['href']
                details_link = re.search(r"\('(.*?)?',", details_link).group(1)
                row = {
                    "Semister": semister_name,
                    "Course Title": course_name,
                    "Course No": section_info[1],
                    "Title": section_info[2],
                    "Days Time": section_info[3],
                    "Instructor(s)": section_info[4],
                    "Location": section_info[5],
                    "Enroll/Cap": section_info[6],
                    "Credits": section_info[7],
                    "Session": section_info[8],
                    # "Trackit":
                }
                additional_details = get_details(details_link)
                row.update(additional_details)
                writer.writerow(row)
driver.quit()
