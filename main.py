import requests
from bs4 import BeautifulSoup
from requests.sessions import session
import json
from util.course import Course
from util.assignment import Assignment
from util import extractor
# Gradescope API Info: https://courses.csail.mit.edu/6.857/2016/files/20.pdf
import time
import cchardet # Speeds up BeautifulSoup encoding

account_info_filename = 'data.json'

def main():
    with requests.Session() as session, open(account_info_filename, 'r') as account_file:
        login_soup = extractor.get_login_soup(session, json.load(account_file))
        courses = extractor.extract_courses(login_soup)
        """
        The below loop takes most of the program time due to the multiple
        GET requests made - each course has one GET
        Performance improvements to make:
            - Use the course term to determine if its assignments should be 
            extracted. Courses from past terms should not have their assignments
            extracted, unless explicitly specified by the client
            - Add multithreading/parallel processing. Each GET request takes about
            .3 seconds on average. When requesting ~10 courses, this can add up to 
            3-5 seconds of run time. If each request is run as its own thread, 
            the run time could be cut significantly.
        """
        for course in courses:
            # TODO this is a good candidate for multithreading:
            # make a thread for each course assignments request
            course.assignments = extractor.get_course_assignments(session, course.course_num)
        
if __name__ == '__main__':
    main()
