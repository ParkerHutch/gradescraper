import requests
from bs4 import BeautifulSoup
from requests.sessions import session
import json
from util.course import Course

base_url = 'https://www.gradescope.com'
account_info_filename = 'data.json'

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
    soup = BeautifulSoup(response.content, 'html.parser')
    if soup.find('title').string  == 'Log In | Gradescope':
        raise Exception('Failed to log in, or the user is already logged in. please check username and password.')
        
    return soup
    
def main():
    with requests.Session() as session:
        soup = get_login_soup(session)
        courses = extract_courses(soup)
        for course in courses:
            print(course)

if __name__ == '__main__':
    main()
