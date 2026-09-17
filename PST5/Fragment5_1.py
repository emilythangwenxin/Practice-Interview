# ... inside ScheduleManager class ...
import csv
import datetime

def record_payment(self, student_id, amount, method):
    """Adds a payment record to the finance log."""
    # TODO: Find the student to ensure they exist.
    # Create a payment dictionary with student_id, amount, method, and a timestamp.
    payment_record = {
        "student_id": student_id,
        "amount": amount,
        "method": method,
        "timestamp": datetime.datetime.now().isoformat()
    }
    # TODO: Append the record to self.finance_log and save the data.
    self.finance_log.append(payment_record)
    self._save_data()
    print(f"Payment of {amount} for student {student_id} recorded.")

def get_payment_history(self, student_id):
    """Returns a list of all payments for a given student."""
    # TODO: Use a list comprehension to filter self.finance_log
    # and return only the records that match the student_id.
    return [p for p in self.finance_log if p['student_id'] == student_id]

def export_report(self, kind, out_path):
    """Exports a log to a CSV file."""
    print(f"Exporting {kind} report to {out_path}...")
    # TODO: Use an if/elif block to select the correct data list based on 'kind'.
    if kind == "finance":
        data_to_export = self.finance_log
        headers = ["student_id", "amount", "method", "timestamp"]
    elif kind == "attendance":
        data_to_export = self.attendance_log # Assuming this exists from PST2
        headers = ["student_id", "course_id", "timestamp"]
    else:
        print("Error: Unknown report type.")
        return

    # TODO: Use Python's 'csv' module to write the data.
    # Open the file, create a csv.DictWriter, write the header, then write all the rows.
    # with open(out_path, 'w', newline='') as f:
    #     writer = csv.DictWriter(f, fieldnames=headers)
    #     writer.writeheader()
    #     writer.writerows(data_to_export)

    # ... inside ScheduleManager class ...