import requests
from bs4 import BeautifulSoup
from requests.sessions import session
from main import get_auth_token, get_post_parameters, extract_courses

base_url = 'https://www.gradescope.com'

with requests.Session() as session:
    login_resp = session.post(f'{base_url}/login', params=get_post_parameters(session))
    soup = BeautifulSoup(login_resp.content, 'html.parser')
        
def test_get_auth_token():
    assert get_auth_token(session).strip() is not ''

def test_extract_courses():
    assert extract_courses(soup)