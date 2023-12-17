import psycopg
from app import login_manager, app
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, login, password, role):
        self.id = id
        self.login = login
        self.password = password
        self.role = role


@login_manager.user_loader
def load_user(id):
    with psycopg.connect(user=app.config['DB_USER'],
                         host=app.config['DB_SERVER'],
                         port=app.config['DB_PORT'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        cur = con.cursor()
        login, password, role = cur.execute('SELECT login, password, role '
                                            'FROM "user" '
                                            'WHERE id = %s', (id,)).fetchone()
        con.commit()
        cur.close()
        con.close()
    return User(id, login, password, role)
