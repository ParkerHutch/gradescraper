class Course:
    def __init__(self, course_num, short_name, name, assignments_num):
        self.course_num = course_num
        self.short_name = short_name
        self.name = name
        self.assignments_num = assignments_num
    
    def __str__(self):
        return f'{self.short_name} ({self.name})\t Assignments: {self.assignments_num}\t #:{self.course_num}'