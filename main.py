import requests
from bs4 import BeautifulSoup
from requests.sessions import session
import json
from util.course import Course
from util.assignment import Assignment

base_url = 'https://www.gradescope.com'
account_info_filename = 'data.json'
# Gradescope API Info: https://courses.csail.mit.edu/6.857/2016/files/20.pdf

def get_auth_token(session):
    init_response = session.get(base_url)
    parsed_init_resp = BeautifulSoup(init_response.text, 'html.parser')
    return (parsed_init_resp.find('input', {'name': 'authenticity_token'})).get("value")

def get_post_parameters(session):
    with open(account_info_filename, 'r') as account_file:
        account_data = json.load(account_file)

    return {
        "session[email]": account_data['email'],
        "session[password]": account_data['password'],
        "authenticity_token": get_auth_token(session),
    }

def extract_courses(login_page_html):
    courses = []
    for tag in login_page_html.find_all('a', class_='courseBox'):
        course_num = tag.get('href').replace('/courses/', '')
        name = tag.find('h4', {'class': 'courseBox--name'}).string
        short_name = tag.find('h3', {'class': 'courseBox--shortname'}).string
        total_assignments = int(tag.find('div', {'class': 'courseBox--assignments'}).string.split(' ')[0])
        courses.append(Course(course_num, short_name, name, total_assignments))
    return courses

def get_login_soup(session):
    response = session.post(f'{base_url}/login', params=get_post_parameters(session))
    if not response:
        # TODO better handling here; this could happen because the user is already logged in.
        raise Exception('User may already be logged in.')
    soup = BeautifulSoup(response.content, 'html.parser') # TODO switch to lxml parser
    if soup.find('title').string  == 'Log In | Gradescope':
        raise Exception('Failed to log in, or the user is already logged in. please check username and password.')
        
    return soup

def extract_assignment_from_row(row):
    submission_status = 'incomplete' if 'submissionStatus-warning' in row.select('td[class*="submissionStatus"]')[0].get('class') else 'complete'

    assignment_link_header = row.find('th', {'class': 'table--primaryLink'})
    assignment_name = (assignment_link_header.find('a') or assignment_link_header).contents[0]

    assignment_url = base_url + assignment_link_header.find('a')['href'].split('/submissions')[0] if assignment_link_header.find('a') else ''

    release_date = row.find('span', {'class':'submissionTimeChart--releaseDate'}).contents
    due_dates = [span.contents[0] for span in row.find_all('span', {'class': 'submissionTimeChart--dueDate'})]
    due_date = due_dates[0]
    late_due_date = due_dates[1] if len(due_dates) == 2 else ''
    return Assignment(assignment_name, assignment_url, submission_status, release_date, due_date, late_due_date)

def get_course_assignments(session, course_num):
    course_page_response = session.get(f'{base_url}/courses/{course_num}')
    soup = BeautifulSoup(course_page_response.content, 'html.parser')
    assignments_table = soup.find('table', {'id': 'assignments-student-table'}).find('tbody')
    
    assignments = [extract_assignment_from_row(row) for row in assignments_table]
    return assignments

def main():
    with requests.Session() as session:
        login_soup = get_login_soup(session)
        courses = extract_courses(login_soup)
        for course in courses:
            course.assignments = get_course_assignments(session, course.course_num)
            print(course)

if __name__ == '__main__':
    main()
