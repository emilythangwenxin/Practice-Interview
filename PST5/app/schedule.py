import json
from app.student import StudentUser
# Corrected Import: TeacherUser and Course now come from the same file.
from app.teacher import TeacherUser, Course

class ScheduleManager:
    """The main controller for all business logic and data handling."""
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []
        self.next_lesson_id = 1
        self._load_data()

    def _load_data(self):
        """Loads data from the JSON file and populates the object lists."""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                # The logic here remains the same, but the source of the Course class has changed.
                # TODO: For each dictionary in data['students'], create a StudentUser object and append to self.students.
                # TODO: Do the same for teachers (creating TeacherUser objects).
                # TODO: Do the same for courses (creating Course objects).
        except FileNotFoundError:
            print("Data file not found. Starting with a clean state.")
    
    def _save_data(self):
    """Converts object lists back to dictionaries and saves to JSON."""
    data_to_save = {
        "students": [vars(student) for student in self.students],
        "teachers": [vars(teacher) for teacher in self.teachers],
        "courses": [vars(course) for course in self.courses]
    }
    
    try:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)
    except IOError as e:
        print(f"Error saving data to file: {e}")