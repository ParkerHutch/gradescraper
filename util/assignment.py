class Assignment: # TODO courseName variable?
    
    def __init__(self, name, submitted):
        self.name = name
        self.submitted = submitted
        self.url = ''
        self.release_date = ''
        self.due_date = ''
        self.late_due_date = ''
    
    def __init__(self, name, url, submitted, release_date, due_date, late_due_date):
        self.name = name
        self.url = url
        self.submitted = submitted
        self.release_date = release_date
        self.due_date = due_date
        self.late_due_date = late_due_date
    
    def __str__(self):
        return f'{self.name} Due Date: {self.due_date} Submission Status: {self.submitted}'