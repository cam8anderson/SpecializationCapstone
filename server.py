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


    teams = crud.get_teams()
    users = crud.get_users()
    team_users = {team.team_id: crud.get_active_users_by_team(team.team_id) for team in teams}
    supervisors = {team.supervisor_id for team in teams}

    
    users_without_teams = [user for user in users if user.user_id not in team_users and user.user_id not in supervisors]

    print('here')
    print(user_role)

    return render_template('teams.html', teams=teams, users=users_without_teams, team_users=team_users)


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
    users = crud.get_users()

    return render_template('teams.html', teams=teams, team_users=team_users, users=users)

@app.route('/create_team', methods=['POST'])
def create_team():
    supervisor_id = request.form.get('supervisor_id')
    team_name = request.form.get('team_name')

    if supervisor_id is None:
        flash('Please login')
        return redirect('/')

    team = crud.create_team(supervisor_id, team_name)

    db.session.add(team)
    db.session.commit()

    flash(f"Team '{team_name}' created successfully!")

    return redirect('/teams')

@app.route('/projects', methods=['GET', 'POST'])
def projects():
    if request.method == 'POST':
        team_id = request.form.get('team_id')
        description = request.form.get('description')
        status = request.form.get('status')

        project = crud.create_project(team_id, description, status)

        db.session.add(project)
        db.session.commit()

        flash(f"Project '{description}' created successfully!")

        return redirect('/projects')

    teams_with_projects = crud.get_teams_with_projects()

    for team_info in teams_with_projects:
        team_info['incomplete_projects'] = [project for project in team_info['projects'] if project.status != 'complete']
        team_info['complete_projects'] = [project for project in team_info['projects'] if project.status == 'complete']

    teams = crud.get_teams()

    return render_template('projects.html', teams_with_projects=teams_with_projects, teams=teams)

@app.route('/update_project_status', methods=['POST'])
def update_project_status():
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        status = request.form.get('status')

        project = crud.get_project_by_id(project_id)

        if project:
            project.status = status
            db.session.commit()
            flash(f"Project status updated successfully!")
        else:
            flash("Project not found")

        return redirect('/projects')

@app.route('/create_project', methods=['POST'])
def create_project():
    team_id = request.form.get('team_id')
    description = request.form.get('description')
    status = request.form.get('status')

    if not team_id or not description or not status:
        flash('Please fill out all fields')
        return redirect('/projects')

    project = crud.create_project(team_id, description, status)

    db.session.add(project)
    db.session.commit()

    flash('Project created successfully!')
    return redirect('/projects')

@app.route('/history')
def history():

    users = User.query.all()
    teams = Team.query.all()
    projects = Project.query.all()
    team_users = TeamUser.query.all()

    all_records = users + teams + projects + team_users

    sorted_records = sorted(all_records, key=lambda x: x.created_at if x.created_at else x.updated_at)

    current_user_name = session.get('user_name')

    return render_template('history.html', sorted_records=sorted_records, current_user_name=current_user_name)

if __name__ == '__main__':
        connect_to_db(app)
        app.run()