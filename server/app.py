# Dependencies
from flask import Flask, request, session, make_response
from models import User, db, JournalEntry
from schemas import JournalEntryCreateSchema,JournalEntryUpdateSchema,LoginSchema,PaginationQuerySchema,SignupSchema, JournalEntrySchema
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
    schema = SignupSchema()
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
@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop("user_id", None)
    return make_response({}, 200)



# Journal entries
@app.route('/entries', methods=['GET'])
def get_entries():
    user = current_user()
    if not user:
        return make_response({"error": "Unauthorized: You must be logged in."}, 401)

    schema = PaginationQuerySchema()
    try:
        params = schema.load(request.args)
    except ValidationError as exc:
        return make_response({"errors": exc.messages}, 422)

    from sqlalchemy import asc, desc
    query = JournalEntry.query.filter_by(user_id=user.id)

    if params.get("search"):
        pattern = f"%{params['search']}%"
        query = query.filter(
            db.or_(
                JournalEntry.title.ilike(pattern),
                JournalEntry.content.ilike(pattern),
            )
        )

    sort_col = getattr(JournalEntry, params["sort"])
    order_fn = desc if params["order"] == "desc" else asc
    pagination = query.order_by(order_fn(sort_col)).paginate(
        page=params["page"], per_page=params["per_page"], error_out=False
    )

    return make_response({
        "entries": [JournalEntrySchema().dump(e) for e in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "next_page": pagination.next_num if pagination.has_next else None,
            "prev_page": pagination.prev_num if pagination.has_prev else None,
        },
    }, 200)

@app.route('/entries', methods=['POST'])
def create_entry():

    user = current_user()
    if not user:
        return make_response({"error": "Unauthorized: You must be logged in."}, 401)

    schema = JournalEntryCreateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as exc:
        return make_response({"errors": exc.messages}, 422)

    tags = data.get("tags", [])
    tags_string = ",".join(tags) if tags else ""

    new_entry = JournalEntry(
        title=data["title"],
        content=data["content"],
        tags=tags_string,
        user_id=user.id
    )
    
    db.session.add(new_entry)
    db.session.commit()
    return make_response(JournalEntrySchema().dump(new_entry), 201)


@app.route('/entries/<int:entry_id>', methods=['GET'])
def get_entry(entry_id):
    user = current_user()
    if not user:
        return make_response({"error": "Unauthorized: You must be logged in."}, 401)

    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user.id).first()
    
    if not entry:
        return make_response({"error": "Journal entry not found."}, 404)

    return make_response(JournalEntrySchema().dump(entry), 200)


@app.route('/entries/<int:entry_id>', methods=['PATCH'])
def update_entry(entry_id):
    user = current_user()
    #case that user is not logged in.
    if not user:
        return make_response({"error": "Unauthorized: You must be logged in."}, 401)
    
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        return make_response({"error": "Journal entry not found."}, 404)

    schema = JournalEntryUpdateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as exceptions:
        return make_response({"Errors": exceptions.messages}, 422)

    if "title" in data:
        entry.title = data["title"]
    if "content" in data:
        entry.content = data["content"]
    if "tags" in data:
        entry.tags = ",".join(data["tags"])

    db.session.commit()

    return make_response(JournalEntrySchema().dump(entry), 200)


@app.route('/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    user = current_user()
    if not user:
        return make_response({"error": "Unauthorized: You must be logged in."}, 401)

    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        return make_response({"error": "Journal entry not found."}, 404)

    # Deleting the record.
    db.session.delete(entry)
    db.session.commit()


    return make_response({}, 200)
   
if __name__ == '__main__':
    app.run(debug=True, port=5555)
    # App should run on port 5555.