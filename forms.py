from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class CreateGoalForm(FlaskForm):
    goal = StringField("Goal Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    date_completion = DateField("Deadline", validators=[DataRequired()])
    submit = SubmitField("Commit Goal")


class AddTaskForm(FlaskForm):
    task = StringField("Task Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    date_completion = DateField("Deadline", validators=[DataRequired()])
    submit = SubmitField("Commit Task")





    # new_goal = Goal(
    #     goal="TestGoal",
    #     description="testtesttest",
    #     date_created=formatted_date,
    #     date_completion="12/31/2024",
    # )
    # db.session.add(new_goal)
    # db.session.commit()
    #
    # requested_goal = db.get_or_404(Goal, 1)
    # new_task = Task(
    #     task="TestTask",
    #     description="task_task_task",
    #     date_created=formatted_date,
    #     date_completion="12/01/2024",
    #     parent_goal=requested_goal
    # )
    # db.session.add(new_task)
    # db.session.commit()
    #
    # result = db.session.execute(db.select(Goal))
    # goals = result.scalars().all()
    # goal = db.get_or_404(Goal, 1)
    # print(goal.goal_tasks)
