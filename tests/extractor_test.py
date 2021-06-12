import requests
from util import extractor
import pytest  # make sure to pip install pytest-dependency
from bs4 import BeautifulSoup

@pytest.mark.dependency(name='auth_token')
def test_get_auth_token():
    with requests.session() as session:
        assert extractor.get_auth_token(session).strip() is not ''

@pytest.mark.dependency(depends=['auth_token'])
def test_get_login_soup():
    bad_login_json = {
        "username": "invalid",
        "password": "wrong"
    }
    with requests.session() as session:
        with pytest.raises(Exception):
            extractor.get_login_soup(session, bad_login_json)


def test_extract_courses():
    with open('tests/courses_dashboard.html', 'r') as courses_html:
        soup = BeautifulSoup(courses_html, 'lxml')
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
    row_input_soup = BeautifulSoup(row_input_html, 'lxml')
    extracted_assignment = extractor.extract_assignment_from_row(row_input_soup)
    assert extracted_assignment.name == 'Final Exam'
    assert extracted_assignment.submitted == True
    assert extracted_assignment.due_date.month == 5
    assert extracted_assignment.due_date.day == 10
    assert extracted_assignment.due_date.hour == 23
    assert extracted_assignment.due_date.minute == 59

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
    row_input_soup = BeautifulSoup(row_input_html, 'lxml')
    extracted_assignment = extractor.extract_assignment_from_row(row_input_soup)
    assert extracted_assignment.name == 'Incomplete Assignment'
    assert extracted_assignment.submitted == False
    assert extracted_assignment.due_date.month == 3
    assert extracted_assignment.due_date.day == 17
    assert extracted_assignment.due_date.hour == 17
    assert extracted_assignment.due_date.minute == 0


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
                        class="submissionTimeChart--dueDate">Apr 14 at 11:59PM</span>
                </div>
            </div>
        </td>
    </tr>
    """
    row_input_soup = BeautifulSoup(row_input_html, 'lxml')
    extracted_assignment = extractor.extract_assignment_from_row(row_input_soup)
    assert extracted_assignment.name == 'Scored Exam Example'
    assert extracted_assignment.submitted == True
    assert extracted_assignment.due_date.month == 4
    assert extracted_assignment.due_date.day == 14
    assert extracted_assignment.due_date.hour == 23
    assert extracted_assignment.due_date.minute == 59


def test_extract_assignment_with_late_due_date():
    row_input_html = """
    <tr role="row" class="even">
        <th class="table--primaryLink" role="rowheader" scope="row">Assignment with Late Due Date</th>
        <td class="submissionStatus submissionStatus-warning">
            <div aria-hidden="true" class="submissionStatus--bullet"
                role="presentation"></div>
            <div class="submissionStatus--text">No Submission</div>
        </td>
        <td class="sorting_1 sorting_2">
            <div class="submissionTimeChart">
                <div class="progressBar--caption"><span
                        aria-label="Released at February 20"
                        class="submissionTimeChart--releaseDate">Feb 20</span><span
                        aria-label="Due at February 20 at  5:00PM"
                        class="submissionTimeChart--dueDate">Feb 20 at
                        5:00PM</span><br><span
                        aria-label="Late Due Date at February 20 at  5:10PM"
                        class="submissionTimeChart--dueDate">Late Due Date: Feb 20 at
                        5:10PM</span></div>
            </div>
        </td>
    </tr>
    """
    row_input_soup = BeautifulSoup(row_input_html, 'lxml')
    extracted_assignment = extractor.extract_assignment_from_row(row_input_soup)
    assert extracted_assignment.name == 'Assignment with Late Due Date'
    assert extracted_assignment.submitted == False
    
    assert extracted_assignment.due_date.month == 2
    assert extracted_assignment.due_date.day == 20
    assert extracted_assignment.due_date.hour == 17
    assert extracted_assignment.due_date.minute == 0
    
    assert extracted_assignment.late_due_date.month == 2
    assert extracted_assignment.late_due_date.day == 20
    assert extracted_assignment.late_due_date.hour == 17
    assert extracted_assignment.late_due_date.minute == 10

