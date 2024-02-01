import operator

from pathlib import Path
from functools import reduce
from datetime import date, timedelta, datetime
from dataclasses import dataclass

from lark import Token, Tree
from pytimeparse.timeparse import timeparse
from rich.console import Console
from rich.table import Table

from pytt.spec import spec
from pytt.models import Project, Task, Day, Defaults, Work


@dataclass
class ParserContext:
    defaults: Defaults


def parse_project_short(p, context: ParserContext) -> Project:
    """."""
    match p.children:
        case [key_token, title_token, ticket_token]:
            return Project(
                key=key_token.value,
                title=title_token.value[1:-1],
                ticket=ticket_token.value[1:-1],
            )
        case [key_token, title_token]:
            return Project(key=key_token.value, title=title_token.value[1:-1])
        case [key_token]:
            return Project(key=key_token.value, title=key_token.value)
        case _:
            raise Exception("invalid project short")


def parse_prject_compl(p, context: ParserContext) -> Project:
    """."""
    project = Project()
    project.alias = []
    for token in p.children:
        if token.data == "proj_attr_key":
            project.key = token.children[0].value
        if token.data == "proj_attr_name":
            project.title = token.children[0].value[1:-1]
        if token.data == "proj_attr_alias":
            project.alias.append(token.children[0].value)
        if token.data == "proj_attr_ticket":
            project.ticket = token.children[0].value
    return project


def parse_task(p: list, day=None, project_key: str | None = None) -> Task:
    """."""
    t = Task()
    t.day = day
    t.project_key = project_key
    text_parts = []
    for item in p:
        match item:
            case Token("WORD", text):
                text_parts.append(text)
            case Token("DURATION_TIME"):
                sec = timeparse(item.value)
                t.duration = timedelta(seconds=sec)
            case Token("DURATION_DOTS"):
                sec = len(item.value) * (15 * 60)
                t.duration = timedelta(seconds=sec)

    t.text = " ".join(text_parts)

    return t


def parse_day(d, context: ParserContext) -> Day:
    """."""
    current_date = None
    tasks: list[Task] = []
    works: list[Work] = []
    day = Day()
    work: Work | None = None
    for token in d.children:
        match token:
            case Token("DAY_KEY", _):
                current_date = date.fromisoformat(token.value)
            case Tree() as tree:
                match tree.children:
                    case [Token("WORK_START_RUNE", _), Token("TIME", start_time)]:
                        state_time_parsed = datetime.strptime(start_time, "%H:%M").time()
                        if work is not None:
                            raise ValueError("you cannot start work if you did not end.")
                        work = Work(state_time_parsed, None)
                    case [Token("WORK_END_RUNE", _), Token("TIME", end_time)]:
                        end_time_parsed = datetime.strptime(end_time, "%H:%M").time()
                        if work is None:
                            raise ValueError("you cannot end work if you did not start.")
                        work.end = end_time_parsed
                        works.append(work)
                        work = None
                    case [proj_token, Tree() as project_work, *_]:
                        tasks.append(
                            parse_task(project_work.children, current_date, proj_token.value)
                        )
                    case _:
                        tasks.append(parse_task(tree.children, current_date))

    # __import__("ipdb").set_trace()
    current_work = reduce(operator.add, map(lambda w: w.duration, works), timedelta(seconds=0))

    current_duration = reduce(operator.add, map(lambda t: t.duration, tasks), timedelta(seconds=0))
    work_duration = current_work if current_work.seconds > 0 else context.defaults.hours
    if current_duration < work_duration:
        diff = work_duration - current_duration
        tasks.append(
            Task(
                project_key=context.defaults.project,
                text=context.defaults.text,
                duration=diff,
                day=current_date,
            )
        )

    day.date_ = current_date
    day.work = works
    day.tasks = tasks

    # day.work.append(Work(start=time.fromisoformat(time_token.value), end=None))
    return day


def load(infile: str):
    """."""
    defaults = Defaults()
    projects = []
    days = []

    raw = Path(infile).read_text()
    p = spec.parse(raw)

    context = ParserContext(defaults=defaults)

    for child in p.children:
        match child.data:  # type: ignore
            case Token(_, "default_hours"):
                context.defaults.hours = timedelta(seconds=timeparse(child.children[0].value))
            case Token(_, "default_project"):
                context.defaults.project = child.children[0].value
            case Token(_, "default_text"):
                context.defaults.text = child.children[0].value[1:-1]
            case Token(_, "project"):
                for proj in child.children:
                    match proj.data:
                        case Token(_, "proj_short"):
                            projects.append(parse_project_short(proj, context))
                        case Token(_, "proj_compl"):
                            projects.append(parse_prject_compl(proj, context))
            case Token(_, "day"):
                days.append(parse_day(child, context))
            case Token(_, "include"):
                raise NotImplementedError("include not yet implemented")
            case _:
                raise Exception("invalid token")

    table = Table()
    table.add_column("Date")
    table.add_column("Project")
    table.add_column("Task")
    table.add_column("Time", justify="right")

    for day in sorted(days, key=lambda d: d.date_, reverse=True):
        time_sum = timedelta()
        for task in day.tasks:
            table.add_row(
                day.date_.strftime("%d.%m.%Y"),
                task.project_key,
                task.text,
                str(task.duration),
            )
            time_sum += task.duration
        table.add_row("", "", "", f"={str(time_sum)}")
        table.add_row("", "", "", "")

    console = Console()
    console.print(table)
