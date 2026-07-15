from datetime import datetime

from django.utils import timezone

TEST_EXAMS = [
    {
        "course_code": "TEST01",
        "date": timezone.make_aware(datetime(2026, 9, 1, 10, 0)),
        "room": "A1",
    },
    {
        "course_code": "TEST02",
        "date": timezone.make_aware(datetime(2026, 9, 3, 12, 0)),
        "room": "B2",
    },
    {
        "course_code": "TEST03",
        "date": timezone.make_aware(datetime(2026, 9, 5, 14, 0)),
        "room": "C3",
    },
]
