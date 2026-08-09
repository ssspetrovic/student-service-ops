# Scenario keys are stable fixture identifiers.  Their dates are calculated by
# the seeder so the behavioural windows remain valid whenever the demo is reset.
TEST_EXAMS = [
    {
        "key": "professor1-completed-ungraded",
        "course_code": "TEST01",
        "days_from_now": -3,
        "hour": 10,
        "minute": 0,
        "room": "A1",
    },
    {
        "key": "professor1-completed-graded",
        "course_code": "TEST01",
        "days_from_now": -4,
        "hour": 12,
        "minute": 0,
        "room": "A2",
    },
    {
        "key": "professor1-future-ungradeable",
        "course_code": "TEST01",
        "days_from_now": 7,
        "hour": 14,
        "minute": 0,
        "room": "A3",
    },
    {
        "key": "student-open-affordable",
        "course_code": "TEST01",
        "days_from_now": 9,
        "hour": 16,
        "minute": 0,
        "room": "A4",
    },
    {
        "key": "student-open-unaffordable",
        "course_code": "TEST02",
        "days_from_now": 10,
        "hour": 10,
        "minute": 0,
        "room": "B1",
    },
    {
        "key": "student-active-cancellable",
        "course_code": "TEST02",
        "days_from_now": 8,
        "hour": 12,
        "minute": 0,
        "room": "B2",
    },
    {
        "key": "student-active-not-cancellable",
        "course_code": "TEST02",
        "days_from_now": 1,
        "hour": 14,
        "minute": 0,
        "room": "B3",
    },
    {
        "key": "student-canceled-history",
        "course_code": "TEST02",
        "days_from_now": 11,
        "hour": 16,
        "minute": 0,
        "room": "B4",
    },
    {
        "key": "professor3-completed-failed",
        "course_code": "TEST03",
        "days_from_now": -5,
        "hour": 10,
        "minute": 0,
        "room": "C1",
    },
    {
        "key": "professor3-future-active",
        "course_code": "TEST03",
        "days_from_now": 6,
        "hour": 12,
        "minute": 0,
        "room": "C2",
    },
    {
        "key": "student-registration-not-open",
        "course_code": "TEST03",
        "days_from_now": 16,
        "hour": 14,
        "minute": 0,
        "room": "C3",
    },
]

TEST_EXAM_REGISTRATIONS = [
    {
        "student_email": "student@example.com",
        "exam_key": "professor1-completed-ungraded",
    },
    {
        "student_email": "student@example.com",
        "exam_key": "professor1-completed-graded",
        "grade": 8,
    },
    {
        "student_email": "student2@example.com",
        "exam_key": "professor1-completed-graded",
        "grade": 5,
    },
    {
        "student_email": "student@example.com",
        "exam_key": "professor1-future-ungradeable",
    },
    {
        "student_email": "student@example.com",
        "exam_key": "student-active-cancellable",
    },
    {
        "student_email": "student@example.com",
        "exam_key": "student-active-not-cancellable",
    },
    {
        "student_email": "student@example.com",
        "exam_key": "student-canceled-history",
        "canceled": True,
    },
    {
        "student_email": "student2@example.com",
        "exam_key": "professor3-completed-failed",
        "grade": 5,
    },
    {
        "student_email": "student3@example.com",
        "exam_key": "professor3-future-active",
    },
]
