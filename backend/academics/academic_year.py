from datetime import date
from zoneinfo import ZoneInfo

from django.utils import timezone


ACADEMIC_YEAR_START_MONTH = 10
SERBIA_TIME_ZONE = ZoneInfo("Europe/Belgrade")


def current_school_year(current_date: date | None = None) -> str:
    if current_date is None:
        current_date = timezone.localtime(timezone.now(), SERBIA_TIME_ZONE).date()

    start_year = current_date.year
    if current_date.month < ACADEMIC_YEAR_START_MONTH:
        start_year -= 1
    return f"{start_year}/{start_year + 1}"
