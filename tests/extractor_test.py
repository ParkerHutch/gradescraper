import requests
from util import course, extractor
import pytest  # make sure to pip install pytest-dependency
from bs4 import BeautifulSoup

@pytest.mark.dependency(name='auth_token')
def test_get_auth_token():
    with requests.session() as session:
        assert extractor.get_auth_token(session).strip() is not ''

@pytest.mark.dependency(name='post_params', depends=['auth_token'])
def test_get_post_parameters():
    with requests.session() as session:
        params = extractor.get_post_parameters(session)
        for _, val in params.items():
            assert val


@pytest.mark.dependency(depends=['post_params', 'auth_token'])
def test_get_login_soup():
    with requests.session() as session:
        assert extractor.get_login_soup(session)
        # Exception expected if user already logged in.
        with pytest.raises(Exception):
            # TODO maybe soup should just be empty if the user is already logged in
            extractor.get_login_soup(session)
    # TODO test for when bad username/password combo is used


def test_extract_courses():
    with open('tests/courses_dashboard.html', 'r') as courses_html:
        soup = BeautifulSoup(courses_html, 'html.parser')
        assert extractor.extract_courses(soup)

def test_extract_submitted_assignment():
    row_input_html = """
    <tr role="row" class="odd">
        <th class="table--primaryLink" role="rowheader" scope="row">
            <a
                aria-label="View Final Exam"
                href="/courses/123456/assignments/1230900/submissions/12345678">Final Exam</a></th>
        <td class="submissionStatus submissionStatus-complete">
            <div aria-hidden="true" class="submissionStatus--bullet"
                role="presentation"></div>
            <div class="submissionStatus--text">Submitted</div>
        </td>
        <td class="sorting_1 sorting_2">
            <div class="submissionTimeChart">
                <div class="progressBar--caption"><span aria-label="Released at May 10"
                        class="submissionTimeChart--releaseDate">May 10</span><span
                        aria-label="Due at May 10 at 11:59PM"
                        class="submissionTimeChart--dueDate">May 10 at 11:59PM</span>
                </div>
            </div>
        </td>
    </tr>
    """
    row_input_soup = BeautifulSoup(row_input_html, 'html.parser')
    extracted_assignment = extractor.extract_assignment_from_row(row_input_soup)
    assert extracted_assignment.name == 'Final Exam'
    assert extracted_assignment.submitted == True

def test_extract_unsubmitted_assignment():
    row_input_html = """
    <tr role="row" class="even">
        <th class="table--primaryLink" role="rowheader" scope="row">Incomplete Assignment</th>
        <td class="submissionStatus submissionStatus-warning">
            <div aria-hidden="true" class="submissionStatus--bullet"
                role="presentation"></div>
            <div class="submissionStatus--text">No Submission</div>
        </td>
        <td class="sorting_1 sorting_2">
            <div class="submissionTimeChart">
                <div class="progressBar--caption"><span
                        aria-label="Released at March 17"
                        class="submissionTimeChart--releaseDate">Mar 17</span><span
                        aria-label="Due at March 17 at  5:00PM"
                        class="submissionTimeChart--dueDate">Mar 17 at 5:00PM</span>
                </div>
            </div>
        </td>
    </tr>
    """
    row_input_soup = BeautifulSoup(row_input_html, 'html.parser')
    extracted_assignment = extractor.extract_assignment_from_row(row_input_soup)
    assert extracted_assignment.name == 'Incomplete Assignment'
    assert extracted_assignment.submitted == False

def test_extract_scored_assignment():
    row_input_html = """
    <tr role="row" class="even">
        <th class="table--primaryLink" role="rowheader" scope="row"><a
                aria-label="View Exam 3"
                href="/courses/123456/assignments/1172058/submissions/12345678">Scored Exam Example</a></th>
        <td class="submissionStatus">
            <div class="submissionStatus--score">38.5 / 40.0</div>
        </td>
        <td class="sorting_1 sorting_2">
            <div class="submissionTimeChart">
                <div class="progressBar--caption"><span
                        aria-label="Released at April 14"
                        class="submissionTimeChart--releaseDate">Apr 14</span><span
                        aria-label="Due at April 14 at  5:00PM"
                        class="submissionTimeChart--dueDate">Apr 14 at 5:00PM</span>
                </div>
            </div>
        </td>
    </tr>
    """
    row_input_soup = BeautifulSoup(row_input_html, 'html.parser')
    extracted_assignment = extractor.extract_assignment_from_row(row_input_soup)
    assert extracted_assignment.name == 'Scored Exam Example'
    assert extracted_assignment.submitted == True
