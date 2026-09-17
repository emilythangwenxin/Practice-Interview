# app/schedule.py
import logging # Import the logging module
# ... other imports

class ScheduleManager:
    # ... __init__ and other methods ...

    def record_payment(self, student_id, amount, method):
        # ... (logic to add payment record) ...
        self._save_data()
        # TODO: Add a log entry after a successful operation.
        logging.info(f"Payment of {amount} recorded for student ID {student_id}.")

    def cancel_lesson(self, lesson_id, reason):
        # ... (logic to cancel a lesson) ...
        self._save_data()
        # TODO: Add a log entry.
        logging.warning(f"Lesson ID {lesson_id} was cancelled. Reason: {reason}")