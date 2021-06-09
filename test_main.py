import requests
from main import get_auth_token, get_login_soup, get_post_parameters, extract_courses
import pytest # make sure to pip install pytest-dependency

def test_get_auth_token():
    with requests.session() as session:
        assert get_auth_token(session).strip() is not ''

@pytest.mark.dependency(name='login')
def test_get_login_soup():
    with requests.session() as session:
        assert get_login_soup(session)
        with pytest.raises(Exception): # Exception expected if user already logged in.
            # TODO maybe soup should just be empty if the user is already logged in
            get_login_soup(session)
    # TODO test for when bad username/password combo is used

def test_get_post_parameters():
    with requests.session() as session:
        params = get_post_parameters(session)
        for _, val in params.items():
            assert val


@pytest.mark.dependency(depends=['login'])
def test_extract_courses():
    with requests.session() as session:
        soup = get_login_soup(session)
        assert extract_courses(soup)