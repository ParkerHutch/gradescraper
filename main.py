#import urllib.request
import requests
from bs4 import BeautifulSoup
from requests.sessions import session
import json

base_url = 'https://www.gradescope.com'
account_info_filename = 'data.json'

def get_auth_token(session):
    init_response = session.get(base_url)
    auth_token = ""
    parsed_init_resp = BeautifulSoup(init_response.text, 'html.parser')
    for form in parsed_init_resp.find_all('form'): # this method of finding the token is from https://github.com/apozharski/gradescope-api/blob/master/pyscope/pyscope.py
        if form.get("action") == "/login":
            for inp in form.find_all('input'):
                if inp.get('name') == "authenticity_token":
                    auth_token = inp.get('value')
    return auth_token # TODO raise exception if empty

def get_post_parameters(session):
    login_data = {}
    with open(account_info_filename, 'r') as account_file:
        account_data = json.load(account_file)

        login_data = {
            #"utf8": "✓",
            #"session[remember_me]": 0,
            #"commit": "Log In",
            #"session[remember_me_sso]": 0,
            "session[email]": account_data['email'],
            "session[password]": account_data['password'],
            "authenticity_token": get_auth_token(session),
        }
    return login_data

def main():
    with requests.Session() as session:
        #p = session.post(login_url, params=get_post_parameters(session))
        print(f'{get_auth_token(session)=}')
        login_resp = session.post(f'{base_url}/login', params=get_post_parameters(session))

        soup = BeautifulSoup(login_resp.content, 'html.parser')
        #print(soup.prettify())
        for tag in soup.find_all('a', class_='courseBox'):
            print(tag)


if __name__ == '__main__':
    main()
