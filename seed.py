from server import app
from model import db, User, Team, Project, TeamUser, connect_to_db

connect_to_db(app)

with app.app_context():
    users = [
        User(name='test', email='test@test.test', password='test', role='test'),
        User(name='t', email='t@test.test', password='test', role='test'),
        User(name='te', email='te@test.test', password='test', role='test'),
        User(name='tes', email='tes@test.test', password='test', role='test'),
        User(name='testi', email='testi@test.test', password='test', role='test'),
        User(name='testin', email='testin@test.test', password='test', role='test'),
        User(name='testing', email='testing@test.test', password='test', role='test')
    ]
    db.session.add_all(users)
    db.session.commit()

    teams = [
        Team(supervisor_id=1, team_name='test_team'),
        Team(supervisor_id=2, team_name='test_team'),
        Team(supervisor_id=3, team_name='test_team')
    ]
    db.session.add_all(teams)
    db.session.commit()

    projects = [
        Project(team_id=1, description='this is the description', status='incomplete')
    ]
    db.session.add_all(projects)
    db.session.commit()

    teamuser = [
        TeamUser(team_id=1, user_id=1, is_active=True),
        TeamUser(team_id=2, user_id=2, is_active=True)
    ]
    db.session.add_all(teamuser)
    db.session.commit()