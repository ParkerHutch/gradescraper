class Assignment:
    def __init__(
        self, name, course_name, url, submitted, release_date = None, due_date = None, late_due_date = None
    ):
        self.name = name
        self.course_name = course_name
        self.url = url
        self.submitted = submitted
        self.release_date = release_date
        self.due_date = due_date
        self.late_due_date = late_due_date

    def __str__(self):
        submission_emoji = '\U00002705' if self.submitted else '\U0000274C'
        return f"\U0001F4D3[{self.course_name}] {self.name} Due \U0001F4C5{self.due_date:%m/%d/%y %I:%M%p} Submitted: {submission_emoji}"

