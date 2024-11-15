from datetime import datetime
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreateGoalForm, AddTaskForm
import os
from functions import get_task_dates, get_goal_date, get_goal_dates

date = datetime.today()
formatted_date = date.strftime("%Y-%m-%d")

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///goals.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    goals = relationship("Goal", back_populates="user")


class Goal(db.Model):
    __tablename__ = "goals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="goals")
    goal: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    date_created: Mapped[str] = mapped_column(String(25), nullable=False)
    date_completion: Mapped[str] = mapped_column(String(25), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Not Started")
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    goal_tasks = relationship("Task", back_populates="parent_goal")


class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    date_created: Mapped[str] = mapped_column(String(25), nullable=False)
    date_completion: Mapped[str] = mapped_column(String(25), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Not Started")
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    goal_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("goals.id"))
    parent_goal = relationship("Goal", back_populates="goal_tasks")


with app.app_context():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        password = request.form.get('password')
        result = db.session.execute(db.select(User).where(User.email == request.form.get('email')))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('sign_in'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('sign_in'))
        else:
            login_user(user)
            return redirect(url_for('get_all_goals'))
    return render_template("sign_in.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('sign_in'))


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = db.session.execute(db.select(User).where(User.email == request.form.get('email')))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('sign_in'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            password=hash_and_salted_password,
            name=request.form.get('fullname')
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_goals'))
    return render_template("register.html")


@app.route('/get-goals')
def get_all_goals():
    result = db.session.execute(db.select(Goal).where(Goal.user == current_user))
    goals = result.scalars().all()
    goal_dates = get_goal_dates(goals)
    return render_template("get_goals.html", goals=goals, goal_dates=goal_dates, current_user=current_user)


@app.route('/goal/<int:goal_id>', methods=["GET", "POST"])
def get_goal(goal_id):
    requested_goal = db.get_or_404(Goal, goal_id)
    if request.method == "POST" and request.form.get('task_id'):
        task_id = int(request.form.get('task_id'))
        task_index = task_id - 1
        task_update = requested_goal.goal_tasks[task_index]
        if request.form.get('task_input'):
            task_update.task = request.form.get('task_input')
        if request.form.get('status_select'):
            task_update.status = request.form.get('status_select')
            if request.form.get('status_select') == "Completed":
                task_update.completed = True
            else:
                task_update.completed = False
        if request.form.get('date_completion'):
            task_update.date_completion = request.form.get('date_completion')
        if request.form.get('task_description'):
            task_update.description = request.form.get('task_description')
        db.session.commit()
        return redirect(url_for('get_goal', goal_id=goal_id))
    if request.method == "POST" and request.form.get('goal_id'):
        if request.form.get('goal_input'):
            requested_goal.goal = request.form.get('goal_input')
        # if request.form.get('status_select'):
        #     requested_goal.status = request.form.get('status_select')
        #     if request.form.get('status_select') == "Completed":
        #         requested_goal.completed = True
        #     else:
        #         requested_goal.completed = False
        if request.form.get('date_completion'):
            requested_goal.date_completion = request.form.get('date_completion')
        if request.form.get('goal_description'):
            requested_goal.description = request.form.get('task_description')
        db.session.commit()
        return redirect(url_for('get_goal', goal_id=goal_id))
    task_dates = get_task_dates(requested_goal)
    goal_date = get_goal_date(requested_goal)
    return render_template("goal.html", goal=requested_goal, task_dates=task_dates, goal_date=goal_date)


@app.route('/edit-task/<int:goal_id>/<int:task_id>', methods=["GET", "POST"])
def edit_task(goal_id, task_id):
    requested_goal = db.get_or_404(Goal, goal_id)
    task_edit = None
    for task in requested_goal.goal_tasks:
        if task_id == task.id:
            task_edit = task
    task_dates = get_task_dates(requested_goal)
    return render_template("edit_task.html", goal=requested_goal, task_dates=task_dates, task_edit=task_edit)


@app.route('/edit-goal/<int:goal_id>', methods=["GET", "POST"])
def edit_goal(goal_id):
    requested_goal = db.get_or_404(Goal, goal_id)
    task_dates = get_task_dates(requested_goal)
    goal_date = get_goal_date(requested_goal)
    return render_template("edit_goal.html", goal=requested_goal, task_dates=task_dates, goal_date=goal_date)


@app.route('/add-goal', methods=["GET", "POST"])
def add_goal():
    form = CreateGoalForm()
    if form.validate_on_submit():
        new_goal = Goal(
            user=current_user,
            goal=form.goal.data,
            description=form.description.data,
            date_created=formatted_date,
            date_completion=form.date_completion.data
        )
        db.session.add(new_goal)
        db.session.commit()
        return redirect(url_for("get_all_goals"))
    return render_template("add_goal.html", form=form)


@app.route('/goal/<int:goal_id>/add-task', methods=["GET", "POST"])
def add_task(goal_id):
    print(goal_id)
    form = AddTaskForm()
    if form.validate_on_submit():
        new_task = Task(
            task=form.task.data,
            description=form.description.data,
            date_created=formatted_date,
            date_completion=form.date_completion.data,
            goal_id=goal_id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('get_goal', goal_id=goal_id))
    return render_template("add_task.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
