# test_schedule.py
import json
import os
import datetime
from pathlib import Path
import pytest

# Import the ScheduleManager from the uploaded file
from app.schedule import ScheduleManager

# ---------------------------
# Mock dependency classes
# ---------------------------
# These mirror the attributes/methods the ScheduleManager expects.
class StudentUser:
    def __init__(self, id, name, enrolled_course_ids=None):
        self.id = id
        self.name = name
        self.enrolled_course_ids = enrolled_course_ids or []

    def display_info(self):
        return f"ID: {self.id} Name: {self.name}"


class TeacherUser:
    def __init__(self, id, name, speciality=""):
        self.id = id
        self.name = name
        self.speciality = speciality

    def display_info(self):
        return f"ID: {self.id} Name: {self.name} Specialty: {self.speciality}"


class Course:
    def __init__(self, id, name, instrument, teacher_id):
        self.id = id
        self.name = name
        self.instrument = instrument
        self.teacher_id = teacher_id
        self.lessons = []
        self.enrolled_student_ids = []

    def add_lesson(self, title, day, time, duration_minutes):
        self.lessons.append({
            "title": title,
            "day": day,
            "time": time,
            "duration": duration_minutes
        })


class AdminUser:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def authenticate(self, username, password):
        return self.username == username and self.password == password

    def __repr__(self):
        return f"<Admin {self.id}:{self.username}>"


class StaffUser:
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# ---------------------------
# Fixtures
# ---------------------------



@pytest.fixture(autouse=True)
def patch_deps(monkeypatch):
    """
    Patch the imports inside schedule.ScheduleManager so it uses our mock classes.
    Also patch os.system to no-op to prevent terminal clear calls during tests.
    """
    monkeypatch.setattr("schedule.StudentUser", StudentUser)
    monkeypatch.setattr("schedule.TeacherUser", TeacherUser)
    monkeypatch.setattr("schedule.Course", Course)
    monkeypatch.setattr("schedule.AdminUser", AdminUser)
    monkeypatch.setattr("schedule.StaffUser", StaffUser)
    monkeypatch.setattr("os.system", lambda *_: None)
    yield


@pytest.fixture
def manager():
    """Return a fresh ScheduleManager using a temporary file."""
    test_file = "test_data.json"
    # ARRANGE: Ensure no old test file exists.
    if os.path.exists(test_file):
        os.remove(test_file)
    return ScheduleManager(data_path=test_file)


# ---------------------------
# Tests for creation & basic lists
# ---------------------------

def test_add_student_and_list(manager):
    s = manager.add_student("Alice")
    assert s.id >= 4000
    assert s.name == "Alice"
    lst = manager.list_students()
    assert any("Alice" in info for info in lst)

def test_add_teacher_and_list(manager):
    t = manager.add_teacher("Mr. T", "Piano")
    assert t.id >= 3000
    assert "Piano" in t.speciality or "Piano" == t.speciality
    teacher_list = manager.list_teachers()
    assert any("Mr. T" in s for s in teacher_list)

def test_add_course_requires_valid_teacher(manager):
    # invalid teacher id -> None
    course_none = manager.add_course("Intro", "Piano", teacher_id=9999)
    assert course_none is None

    # add teacher then add course
    teacher = manager.add_teacher("Mme Beethoven", "Violin")
    course = manager.add_course("Violin 101", "Violin", teacher.id)
    assert course is not None
    assert course.instrument == "Violin"
    course_list = manager.list_courses()
    assert any("Violin 101" in s for s in course_list)

# ---------------------------
# Enrollment, check-in, attendance
# ---------------------------

def test_enroll_and_prevent_duplicate(manager):
    s = manager.add_student("Bob")
    t = manager.add_teacher("Teach", "Guitar")
    c = manager.add_course("Guitar A", "Guitar", t.id)
    ok = manager.enroll_student_in_course(s.id, c.id)
    assert ok is True
    # duplicate enrollment should return False
    ok2 = manager.enroll_student_in_course(s.id, c.id)
    assert ok2 is False
    # invalid ids
    assert manager.enroll_student_in_course(9999, c.id) is False
    assert manager.enroll_student_in_course(s.id, 9999) is False

def test_check_in_and_attendance_log(manager):
    s = manager.add_student("Cathy")
    t = manager.add_teacher("Teacher C", "Piano")
    c = manager.add_course("Piano Basics", "Piano", t.id)
    manager.enroll_student_in_course(s.id, c.id)
    ok = manager.check_in_student(s.id, c.id)
    assert ok is True
    logs = manager.get_attendance_log()
    assert any(entry["student_id"] == s.id and entry["course_id"] == c.id for entry in logs)

# ---------------------------
# Daily roster and lesson functions
# ---------------------------

def test_add_lesson_and_daily_roster(manager):
    t = manager.add_teacher("T1", "Violin")
    c = manager.add_course("Violin 2", "Violin", t.id)
    # add lesson
    added = manager.add_lesson_to_course(c.id, "Week 1", "Monday", "10:00", 60)
    assert added is True
    roster = manager.get_daily_roster("monday")
    assert any(r["course_id"] == c.id for r in roster)

def test_front_desk_daily_roster(manager):
    t = manager.add_teacher("T2", "Drums")
    c = manager.add_course("Drum Lessons", "Drums", t.id)
    manager.add_lesson_to_course(c.id, "Drum Basics", "Tuesday", "09:00", 30)
    roster = manager.front_desk_daily_roster("tuesday")
    assert any(r["course_name"] == "Drum Lessons" for r in roster)

# ---------------------------
# Switch courses, remove operations
# ---------------------------

def test_switch_student_course(manager):
    s = manager.add_student("D")
    t = manager.add_teacher("Teach1", "Flute")
    c1 = manager.add_course("Flute A", "Flute", t.id)
    c2 = manager.add_course("Flute B", "Flute", t.id)
    manager.enroll_student_in_course(s.id, c1.id)
    switched = manager.switch_student_course(s.id, c1.id, c2.id)
    assert switched is True
    # can't switch if not enrolled in from_course
    assert manager.switch_student_course(s.id, c1.id, c2.id) is False

def test_remove_student_and_cleanup(manager):
    s = manager.add_student("E")
    t = manager.add_teacher("Tremove","Cello")
    c = manager.add_course("Cello 1", "Cello", t.id)
    manager.enroll_student_in_course(s.id, c.id)
    removed = manager.remove_student(s.id)
    assert removed is True
    # student no longer present
    assert manager.find_student_by_id(s.id) is None
    # ensure course no longer has the student id
    assert s.id not in c.enrolled_student_ids

def test_remove_teacher_and_courses(manager):
    t = manager.add_teacher("Zed", "Sax")
    c1 = manager.add_course("Sax 1", "Sax", t.id)
    c2 = manager.add_course("Sax 2", "Sax", t.id)
    s = manager.add_student("StudentX")
    manager.enroll_student_in_course(s.id, c1.id)
    removed = manager.remove_teacher(t.id)
    assert removed is True
    # teacher removed and their courses removed
    assert manager.find_teacher_by_id(t.id) is None
    assert all(c.teacher_id != t.id for c in manager.courses)
    # student's enrolled courses updated
    assert c1.id not in s.enrolled_course_ids

def test_remove_course_and_unenroll(manager):
    t = manager.add_teacher("TT", "Oboe")
    c = manager.add_course("Oboe 1", "Oboe", t.id)
    s = manager.add_student("StuY")
    manager.enroll_student_in_course(s.id, c.id)
    removed = manager.remove_course(c.id)
    assert removed is True
    assert manager.find_course_by_id(c.id) is None
    assert c.id not in s.enrolled_course_ids

# ---------------------------
# Admin / Staff / Instrument flows
# ---------------------------

def test_add_admin_and_sign_in(manager):
    a = manager.add_admin("admin2", "pass2")
    assert a.id >= 1000
    assert manager.find_admin_by_id(a.id) is not None
    # successful sign in
    assert manager.sign_in_admin("admin2", "pass2") is True
    # wrong credentials
    assert manager.sign_in_admin("admin2", "wrong") is False

def test_add_staff_and_sign_in(manager):
    st = manager.add_staff("Staff1", "pwd")
    assert st.id >= 2000
    assert manager.find_staff_by_id(st.id) is not None
    assert manager.sign_in_staff("Staff1", "pwd") is True
    assert manager.sign_in_staff("Staff1", "bad") is False

def test_instrument_add_list_remove(manager):
    assert manager.add_instrument("Violin") is True
    assert manager.add_instrument("Violin") is False  # duplicate
    assert "Violin" in manager.list_instruments()
    assert manager.remove_instrument("Violin") is True
    assert manager.remove_instrument("Violin") is False  # now gone

# ---------------------------
# Listing functions
# ---------------------------

def test_list_helpers(manager):
    # lists are strings; ensure they return lists
    manager.add_student("L1")
    manager.add_teacher("TL", "Spec")
    manager.add_admin("adm", "p")
    manager.add_staff("SF", "pw")
    _ = manager.list_students()
    _ = manager.list_teachers()
    _ = manager.list_courses()
    _ = manager.list_admins()
    _ = manager.list_staff()
    # basic sanity
    assert isinstance(manager.list_students(), list)
    assert isinstance(manager.list_teachers(), list)

# ---------------------------
# Lesson remove + print card + edit functions
# ---------------------------

def test_add_remove_lesson(manager, tmp_path):
    t = manager.add_teacher("LT", "Lyre")
    c = manager.add_course("Lyre 1", "Lyre", t.id)
    manager.add_lesson_to_course(c.id, "Lesson A", "Sunday", "12:00", 45)
    assert any(l["title"] == "Lesson A" for l in c.lessons)
    removed = manager.remove_lesson_from_course(c.id, "Lesson A")
    assert removed is True
    # removing missing lesson returns False
    assert manager.remove_lesson_from_course(c.id, "Nope") is False

def test_print_student_card_creates_file(manager, tmp_path):
    s = manager.add_student("CardUser")
    # ensure working directory is tmp for file creation
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        manager.print_student_card(s.id)
        expected = tmp_path / f"{s.id}_card.txt"
        assert expected.exists()
        content = expected.read_text()
        assert "MUSIC SCHOOL ID BADGE" in content
    finally:
        os.chdir(cwd)

def test_edit_functions_and_edit_instrument(manager):
    s = manager.add_student("OldName")
    t = manager.add_teacher("Told", "Spec")
    a = manager.add_admin("adold", "pw")
    st = manager.add_staff("Stold", "pw2")
    # edit
    assert manager.edit_student(s.id, name="NewName") is True
    assert manager.find_student_by_id(s.id).name == "NewName"
    assert manager.edit_teacher(t.id, name="Tnew", speciality="NewSpec") is True
    assert manager.find_teacher_by_id(t.id).name == "Tnew"
    assert manager.edit_admin(a.id, username="adnew", password="pwnew") is True
    assert manager.find_admin_by_id(a.id).username == "adnew"
    assert manager.edit_staff(st.id, name="Stnew", new_password="pw3") is True
    assert manager.find_staff_by_id(st.id).name == "Stnew"

    # instruments
    manager.add_instrument("Harp")
    assert manager.edit_instrument("Harp", "HarpNew") is True
    # rename to an existing name fails
    manager.add_instrument("Piano")
    assert manager.edit_instrument("HarpNew", "Piano") is False

def test_remove_admin_and_staff(manager):
    a = manager.add_admin("delme", "pw")
    s = manager.add_staff("delstaff", "pw2")
    assert manager.remove_admin(a.id) is True
    assert manager.find_admin_by_id(a.id) is None
    assert manager.remove_staff(s.id) is True
    assert manager.find_staff_by_id(s.id) is None
