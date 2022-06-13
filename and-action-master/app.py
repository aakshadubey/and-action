from flask import Flask, redirect, render_template, session, request, url_for
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://niyopnnfdhkrsl:7f22f516c905bdf2e047447fca89e9e0eebc2a5224817d32a959ee57829dc9dd@ec2-52-72-99-110.compute-1.amazonaws.com:5432/d9cfqe6vhdgqs8'
#os.environ.get('DATABASE_URL', 'sqlite:///abc.db')
app.config['SECRET_KEY'] = '\x08\x9dw,\xcah\xe8\x9eD5\xc8@\xb5\x9a\xab\x1a\xdd\xa2\x01Z\x1fp\xc9"P\xa9\x02\r8\xe7\xb38'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

API_KEY = os.environ.get('OMDB_KEY', '9dfd4110')
OMDB_API_URL = f'https://www.omdbapi.com/?apikey={API_KEY}&i='


db = SQLAlchemy(app)

# Defining the data models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    password = db.Column(db.Text)
    email = db.Column(db.String(100), unique=True)
    lists = db.relationship('Lists', backref='user', lazy=True)

    def __init__(self, full_name, email, password):
        self.full_name = full_name
        self.email = email
        self.password = password
        super().__init__()


class Lists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_ids = db.relationship('ListToMovie', backref='list', lazy=True)

    def __init__(self, list_name, user_id):
        self.list_name = list_name
        self.user_id = user_id
        super().__init__()


class ListToMovie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)
    omdb_id = db.Column(db.String(25), nullable=False)

    def __init__(self, list_id, omdb_id):
        self.list_id = list_id
        self.omdb_id = omdb_id
        super().__init__()


# Views to control user flow

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    email_id = request.form.get('email')
    password = request.form.get('psw')
    user = User.query.filter_by(email=email_id).first()
    if user:
        if user.password == password:
            session['logged_in'] = True
            session['username'] = email_id
            return redirect(url_for('dashboard'))
        else:
            return 'Password mismatch, login again'
    else:
        return 'No such user found'


@app.route('/signup', methods=['POST'])
def signup():
    full_name = request.form.get('name')
    email_id = request.form.get('email')
    password = request.form.get('psw')
    user = User.query.filter_by(email=email_id).first()
    if user is None:
        new_user = User(full_name, email_id, password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('confirm.html')
    else:
        return 'User already Exists'


@app.route('/dashboard', methods=['GET'])
def dashboard():
    logged_in = session.get('logged_in')
    if logged_in:
        user = User.query.filter_by(email=session['username']).first()
        name = user.full_name
        return render_template('search.html', name=name, lists=user.lists)
    else:
        return redirect(url_for('index'))


@app.route('/newplaylist', methods=['POST'])
def new_playlist():
    logged_in = session.get('logged_in')
    if logged_in:
        user = User.query.filter_by(email=session['username']).first()
        new_list = Lists(request.form.get('list_name'), user.id)
        return redirect(url_for('playlist', new_list.id))
    else:
        return 'Not Logged In'


@app.route('/playlist/<playlist_id>', methods=['GET'])
def playlist(playlist_id):
    list = Lists.query.filter_by(id=playlist_id).first()
    if list:
        return render_template('playlist.html', list_name = list.list_name)
    else:
        return 'playlist not found'

if __name__ == '__main__':
    db.create_all()
    app.debug = False
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
