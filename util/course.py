class Course:
    def __init__(self, term, course_num, short_name, name, assignments_num):
        self.term = term
        self.course_num = course_num
        self.short_name = short_name
        self.name = name
        self.assignments_num = assignments_num
        self.assignments = []

    def get_assignments_in_range(
        self, start_date, end_date, unsubmitted_only=False
    ):
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
        """
        return [
            assignment
            for assignment in self.assignments
            if assignment.due_date > start_date
            and assignment.due_date < end_date
            and 
            # TODO add or to handle late due date if assignment not submitted
        ]"""

    def __str__(self):
        return f'{self.term}: {self.short_name} ({self.name})\t Assignments: {self.assignments_num}\t #:{self.course_num}'
