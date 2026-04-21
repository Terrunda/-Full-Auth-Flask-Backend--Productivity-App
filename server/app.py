# Dependencies
from flask import Flask 
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Routes go here.

# /login route with POST
# /signup route with POST
# /check_session with GET
# /logout with DELETE

if __name__ == "__main__":
    app.run(debug=True, port=5555)
    # App should run on port 5555.