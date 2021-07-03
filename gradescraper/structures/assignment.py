import datetime


class Assignment:
    """A class for storing a Gradescope assignment and its information.

    Attributes:
        name (str): the assignment name
        course_name (str): the name of the course the assignment belongs to
        url (str): the assignment's full URL
        submitted (bool): the user's submission status for the assignment
        release_date (datetime.datetime, optional): the assignment's release
        date.
        due_date (datetime.datetime, optional): the assignment's due date.
        late_due_date (datetime.datetime, optional): the assignment's late
        due date.
    """

    def __init__(
        self,
        name: str,
        course_name: str,
        url: str,
        submitted: bool,
        release_date: datetime.datetime = None,
        due_date: datetime.datetime = None,
        late_due_date: datetime.datetime = None,
    ):
        """Create an Assignment with possible due dates.

        Args:
            name (str): the assignment name.
            course_name (str): the name of the course the assignment belongs to.
            url (str): the assignment's full URL.
            submitted (bool): the user's submission status for the assignment
            release_date (datetime.datetime, optional): the assignment's release
            date. Defaults to None.
            due_date (datetime.datetime, optional): the assignment's due date.
            Defaults to None.
            late_due_date (datetime.datetime, optional): the assignment's late
            due date. Defaults to None.
        """
        self.name = name
        self.course_name = course_name
        self.url = url
        self.submitted = submitted
        self.release_date = release_date
        self.due_date = due_date
        self.late_due_date = late_due_date

    def __str__(self):
        submission_emoji = '\U00002705' if self.submitted else '\U0000274C'
        return f'{self.course_name[:18]:<20} \U0001F4D3{self.name: <15} \U0001F4C5{self.due_date:%m/%d %I:%M%p} {submission_emoji}'
        #return f'\U0001F4D3[{self.course_name}] {self.name} \U0001F4C5Due {self.due_date:%m/%d/%y %I:%M%p} Submitted: {submission_emoji}'
