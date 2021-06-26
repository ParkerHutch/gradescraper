import datetime
from typing import List

from gradescraper.structures.assignment import Assignment
from gradescraper.structures.term import Term

class Course:
    """A class for storing a Course's identifying information and its
    assignments. Utilities for retrieving assignments are also included.
    """

    def __init__(
        self,
        term: Term,
        course_num: int,
        short_name: str,
        name: str,
        assignments_num: int,
    ):
        """Create a unique Course object.

        Create a Course for the given school term with identifying course
        number, name, and short name. Also store a number for the course's total
        number of assignments.

        Args:
            term (Term): the school term that the Course takes place during
            course_num (int): the course's number on the Gradescope system
            short_name (str): the course's short name in the Gradescope system
            name (str): The course's full name
            assignments_num (int): the number of assignments in the Course
            at the time of retrieval
        """
        self.term = term
        self.course_num = course_num
        self.short_name = short_name
        self.name = name
        self.assignments_num = assignments_num
        self.assignments = []
        return None

    def get_assignments_in_range(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        unsubmitted_only: bool = False,
    ) -> List[Assignment]:
        """Get the assignments within the specified range.

        Gets the assignments between the two specified dates. If
        unsubmitted_only is True, only unsubmitted assignments are returned,
        otherwise submitted and unsubmitted assignments may be returned. If an
        invalid range is passed (start_date refers to a date after end_date),
        an empty List is returned.

        Args:
            start_date (datetime.datetime): The start date of the range to
            search for assignments in
            end_date (datetime.datetime): The end date of the range to search
            for assignments in
            unsubmitted_only (bool, optional): Whether to only return
            unsubmitted assignments. Defaults to False.

        Returns:
            List[Assignment]: The assignments contained in the specified range
        """
        if start_date > end_date:
            return []

        assignments_to_return = []
        for assignment in self.assignments:
            if (
                assignment.due_date > start_date
                and assignment.due_date < end_date
            ):
                if unsubmitted_only:
                    if not assignment.submitted:
                        assignments_to_return.append(assignment)
                else:
                    assignments_to_return.append(assignment)
        # TODO add or to handle late due date

        return assignments_to_return

    def __str__(self):
        return f'{self.term}: {self.short_name} ({self.name})\t Assignments: {self.assignments_num}\t #:{self.course_num}'
