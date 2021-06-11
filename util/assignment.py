class Assignment: # TODO courseName variable?
    def __init__(self):
        self.name = ''
        self.url = ''
        self.submission_status = ''
        self.release_date = ''
        self.due_date = ''
        self.late_due_date = ''
    
    def __init__(self, name, submission_status):
        self.name = name
        self.submission_status = submission_status
        self.url = ''
        self.release_date = ''
        self.due_date = ''
        self.late_due_date = ''
    
    def __init__(self, name, url, submission_status, release_date, due_date, late_due_date):
        self.name = name
        self.url = url
        self.submission_status = submission_status
        self.release_date = release_date
        self.due_date = due_date
        self.late_due_date = late_due_date
    
    def __str__(self):
        return f'{self.name} Due Date: {self.due_date} Submission Status: {self.submission_status}'