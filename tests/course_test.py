from bs4 import BeautifulSoup
from gradescraper.structures.course import Course
from gradescraper.structures.term import Term
from gradescraper.util import processor
from gradescraper.structures.assignment import Assignment
import datetime

def test_course_init():
    with open('tests/course_row.html') as course_html:
        soup = BeautifulSoup(course_html, 'lxml').find('a', class_='courseBox')
    course = processor.extract_course(soup, Term('Summer', 1776))
    assert course.assignments == []

def test_get_assignments_in_range():
    course = Course(Term('Summer', 1776), '12345', 'MATH', 'Mathematics', 5)
    start = datetime.datetime(2021, 4, 10)

    assignments = [
        Assignment('Assignment 1', course.name, '', False, None, start + datetime.timedelta(days=1), None),
        Assignment('Assignment 2', course.name, '', True, None, start + datetime.timedelta(days=1), None),
        Assignment('Assignment 3', course.name, '', False, None, start + datetime.timedelta(days=3), None),
        Assignment('Assignment 4', course.name, '', False, None, start + datetime.timedelta(days=5), None),
        Assignment('Assignment 5', course.name, '', False, None, start + datetime.timedelta(days=14), None),
    ]
    course.assignments = assignments

    assert course.get_assignments_in_range(start, start-datetime.timedelta(days=1)) == []
    assert course.get_assignments_in_range(start, start+datetime.timedelta(days=0)) == []
    assert course.get_assignments_in_range(start, start+datetime.timedelta(days=1), unsubmitted_only=False) == assignments[:2]
    temp = course.get_assignments_in_range(start, start+datetime.timedelta(days=1), unsubmitted_only=True)
    assert len(temp) == 1
    assert temp[0] == assignments[0]
    assert course.get_assignments_in_range(start, start+datetime.timedelta(days=2), unsubmitted_only=False) == assignments[:2]
    assert course.get_assignments_in_range(start, start+datetime.timedelta(days=3), unsubmitted_only=False) == assignments[:3]
    assert course.get_assignments_in_range(start, start+datetime.timedelta(days=15), unsubmitted_only=False) == assignments

