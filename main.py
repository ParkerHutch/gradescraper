import requests
from bs4 import BeautifulSoup
from requests.sessions import session
import json
from util.course import Course
from util.assignment import Assignment
from util import extractor
# Gradescope API Info: https://courses.csail.mit.edu/6.857/2016/files/20.pdf

account_info_filename = 'data.json'

def main():
    with requests.Session() as session, open(account_info_filename, 'r') as account_file:

        login_soup = extractor.get_login_soup(session, json.load(account_file))
        courses = extractor.extract_courses(login_soup)
        for course in courses:
            course.assignments = extractor.get_course_assignments(session, course.course_num)
        
if __name__ == '__main__':
    main()
