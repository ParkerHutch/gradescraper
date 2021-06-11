import requests
from bs4 import BeautifulSoup
from requests.sessions import session
import json
from util.course import Course
from util.assignment import Assignment
from util import extractor
# Gradescope API Info: https://courses.csail.mit.edu/6.857/2016/files/20.pdf


def main():
    with requests.Session() as session:
        login_soup = extractor.get_login_soup(session)
        login_soup = extractor.get_login_soup(session)
        courses = extractor.extract_courses(login_soup)
        for course in courses:
            course.assignments = extractor.get_course_assignments(session, course.course_num)
            print(course)

if __name__ == '__main__':
    main()
