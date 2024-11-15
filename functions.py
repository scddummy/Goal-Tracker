from datetime import datetime


def split_date(date_str):
    date_object = datetime.strptime(date_str, "%Y-%m-%d")

    day = date_object.strftime("%d")
    month = date_object.strftime("%b").upper()
    year = date_object.strftime("%Y")

    return day, month, year


def get_task_dates(goal):
    task_dates = []
    for task in goal.goal_tasks:
        day, month, year = split_date(task.date_completion)
        cal_date = {
            "id": task.id,
            "day": day,
            "month": month,
            "year": year
        }
        task_dates.append(cal_date)
    return task_dates


def get_goal_date(goal):
    goal_date = []
    day, month, year = split_date(goal.date_completion)
    cal_date = {
        "id": goal.id,
        "day": day,
        "month": month,
        "year": year
    }
    goal_date.append(cal_date)
    return goal_date


def get_goal_dates(goals):
    goal_dates = []
    for goal in goals:
        day, month, year = split_date(goal.date_completion)
        cal_date = {
            "id": goal.id,
            "day": day,
            "month": month,
            "year": year
        }
        goal_dates.append(cal_date)
    return goal_dates
