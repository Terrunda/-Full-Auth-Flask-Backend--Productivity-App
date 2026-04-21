# Dependencies
from flask import Flask, request, session, make_response
from models import User, db, JournalEntry
from schemas import JournalEntryCreateSchema,JournalEntryUpdateSchema,LoginSchema,PaginationQuerySchema,SignupSchema
from marshmallow import ValidationError
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Session retrieval
def current_user():
    return db.session.get(User, session.get("user_id"))

# Routes go here.
# /login route with POST
@app.route('/login', methods=['POST'])
def login():
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as exc:
        return make_response({"errors": exc.messages}, 422)

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        return make_response({"error": "Invalid username or password."}, 401)

    session["user_id"] = user.id
    return make_response({"id": user.id, "username": user.username}, 200)


# /signup route with POST
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as exc:
        return make_response({"errors": exc.messages}, 422)

    if User.query.filter_by(username=data["username"]).first():
        return make_response({"error": "Username already taken."}, 409)

    user = User(username=data["username"])
    user.set_password(data["password"])

    try:
        db.session.add(user)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return make_response({"error": str(exc)}, 422)

    session["user_id"] = user.id
    return make_response({"id": user.id, "username": user.username}, 201)


# /check_session with GET
@app.route('/check_session', methods=['GET'])
def check_session():
    user = db.session.get(User, session.get("user_id"))
    if not user:
        return make_response({}, 200)
    return make_response({"id": user.id, "username": user.username}, 200)


# /logout with DELETE
@app.route('/check_session', methods=['DELETE'])
@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop("user_id", None)
    return make_response({}, 200)



# Journal entries
  @app.route('/entries', methods=['POST'])
def create_entry():
    # Function for creating journal entries.
    pass

  @app.route('/entries/<int:entry_id>', methods=['GET'])
 def get_entry(entry_id):
    # Function for retrieving a journal based on id.
    pass

@app.route('/entries/<int:entry_id>', methods=['PATCH'])
  def update_entry(entry_id):
    # Function for updating journal entry.
    pass

@app.route('/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    # Function for deleting a journal entry.
    pass
   
if __name__ == '__main__':
    app.run(debug=True, port=5555)
    # App should run on port 5555.