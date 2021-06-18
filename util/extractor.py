from util import course
from util.course import Course
from bs4 import BeautifulSoup, SoupStrainer
from util.assignment import Assignment
from datetime import datetime
import time
import asyncio
import aiohttp

base_url = 'https://www.gradescope.com'


def get_auth_token(session):
    parsed_init_resp = BeautifulSoup(session.get(base_url).text, 'lxml', parse_only=SoupStrainer("input"))
    return (parsed_init_resp.find('input', {'name': 'authenticity_token'})).get("value")


def extract_courses(dashboard_page_soup): # TODO try to make this async, or make the individual course extraction async
    courses = [] 
    course_list_div_children = list(dashboard_page_soup.find('div', {'class': 'courseList'}).children)
    
    for i in [x for x in range(len(course_list_div_children) - 1) if x % 2 == 0]:
        term = course_list_div_children[i].string
        term_courses_div = course_list_div_children[i+1]
        for tag in term_courses_div.find_all('a', class_='courseBox'):
            course_num = tag.get('href').replace('/courses/', '')
            name = tag.find('h4', {'class': 'courseBox--name'}).string
            short_name = tag.find('h3', {'class': 'courseBox--shortname'}).string
            total_assignments = int(tag.find('div', {'class': 'courseBox--assignments'}).string.split(' ')[0])
            courses.append(Course(term, course_num, short_name, name, total_assignments))
        
    return courses

def get_login_soup(session, account_info_json):
    
    if not all(x in account_info_json for x in ['email', 'password']): # TODO try turning this into just two boolean conditions rather than a search
        raise Exception('Insufficient account information provided.')
    
    post_params = {
        "session[email]": account_info_json['email'],
        "session[password]": account_info_json['password'],
        "authenticity_token": get_auth_token(session),
    }
    
    # Login and get the response, or access the base url if the user is already logged in.
    response = session.post(f'{base_url}/login', params=post_params) or session.get(base_url)
    
    soup = BeautifulSoup(response.content, 'lxml')
    if soup.find('title').string  == 'Log In | Gradescope':
        raise Exception('Failed to log in. Please check username and password.')
        
    return soup

def extract_assignment_from_row(row_soup):
    submitted = not row_soup.find('td', {'class': 'submissionStatus submissionStatus-warning'})
    assignment_link_header = row_soup.find('th', {'class': 'table--primaryLink'})
    assignment_link_element = assignment_link_header.find('a')
    assignment_name = (assignment_link_element or assignment_link_header).contents[0] # TODO .string instead of .contents[0]?

    assignment_url = base_url + assignment_link_element['href'].split('/submissions')[0] if assignment_link_element else ''

    release_date = row_soup.find('span', {'class':'submissionTimeChart--releaseDate'}).contents
    # TODO use span.string below instead of span.contents[0]?
    due_dates = [datetime.strptime(span.contents[0].split('Due Date: ')[-1], '%b %d at %I:%M%p') for span in row_soup.find_all('span', {'class': 'submissionTimeChart--dueDate'})]
    due_date = due_dates[0]
    late_due_date = due_dates[1] if len(due_dates) == 2 else None
    return Assignment(assignment_name, assignment_url, submitted, release_date, due_date, late_due_date)

def get_course_assignments(session, course_num):
    course_page_response = session.get(f'{base_url}/courses/{course_num}')
    
    assignments_soup = BeautifulSoup(course_page_response.content, 'lxml', parse_only=SoupStrainer('tr')).find_all('tr')[1:]
    
    return [extract_assignment_from_row(row) for row in assignments_soup]


async def async_get_auth_token(url, session):
    response = await session.get(url)
    # TODO use response.raise_for_status() ?
    response_text = await response.text()
    parsed_init_resp = BeautifulSoup(response_text, 'lxml', parse_only=SoupStrainer("input"))
    return (parsed_init_resp.find('input', {'name': 'authenticity_token'})).get("value")
    

async def async_get_login_soup(session, account_info_json):
    
    if not all(x in account_info_json for x in ['email', 'password']):
        raise Exception('Insufficient account information provided.')
    
    post_params = {
        "session[email]": account_info_json['email'],
        "session[password]": account_info_json['password'],
        "authenticity_token": await async_get_auth_token(base_url, session),
    }
    
    # Login and get the response, or access the base url if the user is already logged in.
    response = await session.post(f'{base_url}/login', params=post_params) or await session.get(base_url)
    
    soup = BeautifulSoup(await response.text(), 'lxml')
    if soup.find('title').string  == 'Log In | Gradescope':
        raise Exception('Failed to log in. Please check username and password.')
        
    return soup

async def async_retrieve_course_assignments(session, course):
    course_page_response = await session.get(f'{base_url}/courses/{course.course_num}')
    
    assignments_soup = BeautifulSoup(await course_page_response.text(), 'lxml', parse_only=SoupStrainer('tr')).find_all('tr')[1:]
    
    course.assignments = [extract_assignment_from_row(row) for row in assignments_soup] # TODO maybe async here