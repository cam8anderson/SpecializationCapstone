from flask import (Flask, render_template, request, flash, session, redirect)
from model import connect_to_db, db, User, Team, Project, TeamUser
import crud

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = 'dev'
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def home():
        return render_template('homepage.html')

@app.route('/user')
def users():
        users = crud.get_users()

        return render_template('users.html', users=users)

@app.route('/login', methods=['POST'])
def user_login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = crud.get_user_by_email(email)

    if user:
        check = crud.get_user_password(password, email)
        if check:
            session['user_role'] = user.role
            flash("you have logged in!")
        else:
            flash('password was wrong. try again')
    else:
        flash("user doesn't exist please register.")

    return redirect('/')

@app.route('/users', methods=['POST'])
def register_user():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')


    user = crud.get_user_by_email(email)

    if user:
        flash("this email already exists")

    else:
        user = crud.create_user(name, email, password, role)
        db.session.add(user)
        db.session.commit()
        flash("account created! log in")
    
    return redirect('/')

@app.route('/teams')
def teams():
    user_role = session.get('user_role')

    if user_role is None:
        flash('Please login')
        return redirect('/')

    if user_role not in ['Admin', 'Team_lead']:
        flash('Access Denied')
        return redirect('/')

    teams = crud.get_teams()
    users = crud.get_users()

    team_users = {team.team_id: crud.get_active_users_by_team(team.team_id) for team in teams}

    return render_template('teams.html',users=users, teams=teams, team_users=team_users)

@app.route('/assign_team', methods=['GET', 'POST'])
def assign_team():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        team_id = request.form.get('team_id')

        user = User.query.get(user_id)
        team = Team.query.get(team_id)

        if user and team:
            if crud.assign_user_to_team(user_id, team_id):
                flash(f"User {user.name} has been assigned to team {team.team_name}")
            else:
                flash(f"Failed to assign user {user.name} to team {team.team_name}")
        else:
            flash("User or team not found")

        return redirect('/assign_team')

    teams = crud.get_teams()
    team_users = {team.team_id: crud.get_active_users_by_team(team.team_id) for team in teams}

    return render_template('teams.html', teams=teams, team_users=team_users)

if __name__ == '__main__':
        connect_to_db(app)
        app.run()