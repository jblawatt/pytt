from dataclasses import dataclass
from datetime import date, time, timedelta, datetime


@dataclass
class Defaults:
    project: str | None = None
    hours: timedelta = timedelta(seconds=0)


@dataclass
class Project:
    key: str | None = None
    title: str | None = None
    ticket: str | None = None
    alias: list[str] | None = None


@dataclass
class Work:
    start: time | None
    end: time | None

    @property
    def duration(self) -> timedelta:
        """."""
        if self.start is None or self.end is None:
            return timedelta(seconds=0)
        return datetime.combine(date.today(), self.end) - datetime.combine(
            date.today(), self.start
        )


@dataclass
class Task:
    text: str | None = None
    duration: str | None = None
    day: date | None = None
    project_key: str | None = None


@dataclass
class Day:
    date_: date | None = None
    work: list[Work] | None = None
    tasks: list[Task] | None = None
