import requests
from bs4 import BeautifulSoup
from requests.sessions import session
import json
from util.course import Course

base_url = 'https://www.gradescope.com'
account_info_filename = 'data.json'

def get_auth_token(session):
    init_response = session.get(base_url)
    auth_token = ""
    parsed_init_resp = BeautifulSoup(init_response.text, 'html.parser')
    #print(parsed_init_resp.find_all('form', {'action': '/login'}))

    #print('big search: \n')
    inp = parsed_init_resp.find('input', {'name': 'authenticity_token'})
    #print(inp, '\n')
    #print('small search:\n')
    #for form in parsed_init_resp.find_all('form', {'action': '/login'}): # this method of finding the token is from https://github.com/apozharski/gradescope-api/blob/master/pyscope/pyscope.py
        #if form.get("action") == "/login":
        #for inp in form.find_all('input', {'name': 'authenticity_token'}):
            #if inp.get('name') == "authenticity_token":
            #print(inp, '\n')
            #auth_token = inp.get('value')
    
    #print(f'{inp.get("value")=}\n{auth_token=}')
    return inp.get("value") # TODO why can't I do get("value") properly?

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

def main():
    with requests.Session() as session:
        login_resp = session.post(f'{base_url}/login', params=get_post_parameters(session))

        soup = BeautifulSoup(login_resp.content, 'html.parser')
        courses = extract_courses(soup)
        for course in courses:
            print(course)

if __name__ == '__main__':
    main()
