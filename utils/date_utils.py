from __future__ import annotations

from datetime import date, datetime
import calendar


def month_chunks(start_date: date, end_date: date) -> list[tuple[int, int, list[int]]]:
    """
    Split a date range into monthly chunks:
    (year, month, [valid days for that month inside the selected range])
    """
    chunks = []

    current = date(start_date.year, start_date.month, 1)

    while current <= end_date:
        year = current.year
        month = current.month
        last_day = calendar.monthrange(year, month)[1]

        month_start_day = 1
        month_end_day = last_day

        if year == start_date.year and month == start_date.month:
            month_start_day = start_date.day

        if year == end_date.year and month == end_date.month:
            month_end_day = end_date.day

        days = list(range(month_start_day, month_end_day + 1))
        chunks.append((year, month, days))

        if month == 12:
            current = date(year + 1, 1, 1)
        else:
            current = date(year, month + 1, 1)

    return chunks


def iso_to_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()