from model import db, User, Team, Project, TeamUser, connect_to_db

def create_user(name, email, password, role):

    user = User(name=name, email=email, password=password, role=role)

    return user

def create_team(supervisor_id, team_name):
    
    team = Team( supervisor_id=supervisor_id,team_name=team_name)

    return team

def create_project(team_id, description, status):

    project = Project( team_id=team_id, description=description, status=status)

    return project

def get_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_user_by_email(email):
    return User.query.filter(User.email == email).first()

def get_user_password(password, email):
    user = get_user_by_email(email)

    if user and user.password == password:
        return True
    return False

def get_teams():
    return Team.query.all()

def get_team_by_id(team_id):
    return Team.query.get(team_id)

def assign_user_to_team(user_id, team_id):

    team_user = TeamUser.query.filter_by(user_id=user_id, team_id=team_id).first()

    if not team_user:
        team_user = TeamUser(user_id=user_id, team_id=team_id, is_active=True)
        db.session.add(team_user)
        db.session.commit()
        return True
    else:
        team_user.is_active = True
        db.session.commit()
        return True

def get_active_users_by_team(team_id):
    
    active_team_users = TeamUser.query.filter_by(team_id=team_id, is_active=True).all()

    active_users = [team_user.user for team_user in active_team_users]

    return active_users

def join_teamuser():

    joined_data = db.session.query(Team, User).join(TeamUser).join(User)

    teams = [team for team, _ in joined_data]
    users = [user for _, user in joined_data]

    return teams, users

    #team = Team.query.join(TeamUser, Team.team_id == TeamUser.team_id).all()
    #user = User.query.join(TeamUser, User.user_id == TeamUser.user_id).all()
#
    #return team, user

def get_projects():
    return Project.query.all()

def get_project_by_id(project_id):
    return Project.query.get(project_id)

def get_teams_with_projects():
    
    teams = Team.query.all()
    teams_with_projects = []

    for team in teams:

        team_info = {
            'team': team,
            'projects': team.projects
        }
        teams_with_projects.append(team_info)
    return teams_with_projects

if __name__ == '__main__':

    from server import app
    
    connect_to_db(app)