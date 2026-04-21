# Dependencies
from flask import Flask 
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Routes go here.

# /login route with POST
@app.route('/login', methods=['POST'])
def login():
    pass

# /signup route with POST
@app.route('/signup', methods=['POST'])
def signup():


# /check_session with GET
@app.route('/check_session', methods=['GET'])
def check_session():


# /logout with DELETE
@app.route('/check_session', methods=['DELETE'])
def logout():


if __name__ == '__main__':
    app.run(debug=True, port=5555)
    # App should run on port 5555.