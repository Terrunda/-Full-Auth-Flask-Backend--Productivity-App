from flask import Flask, request, session, make_response
from models import User, db, JournalEntry
from schemas import JournalEntryCreateSchema, JournalEntryUpdateSchema, LoginSchema, PaginationQuerySchema, SignupSchema, JournalEntrySchema
from marshmallow import ValidationError
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '20764909c5084ed404708a7d72c85f54be2238b1b9d6588cd070d897d387b989'  

CORS(app, supports_credentials=True)

db.init_app(app)
migrate = Migrate(app, db)

def current_user():
    return db.session.get(User, session.get("user_id"))

def flatten_errors(messages):
    return [msg for field_errors in messages.values() for msg in field_errors]

@app.route('/login', methods=['POST'])
def login():
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as exc:
        return make_response({"errors": flatten_errors(exc.messages)}, 422)

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return make_response({"error": "Invalid username or password."}, 401)

    session["user_id"] = user.id
    return make_response({"id": user.id, "username": user.username}, 200)


@app.route('/signup', methods=['POST'])
def signup():
    schema = SignupSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as exc:
        return make_response({"errors": flatten_errors(exc.messages)}, 422)

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


@app.route('/check_session', methods=['GET'])
def check_session():
    user = db.session.get(User, session.get("user_id"))
    if not user:
        return make_response({}, 200)
    return make_response({"id": user.id, "username": user.username}, 200)


@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop("user_id", None)
    return make_response({}, 200)


@app.route('/entries', methods=['GET'])
def get_entries():
    user = current_user()
    if not user:
        return make_response({"error": "Unauthorized: You must be logged in."}, 401)

    schema = PaginationQuerySchema()
    try:
        params = schema.load(request.args)
    except ValidationError as exc:
        return make_response({"errors": flatten_errors(exc.messages)}, 422)

    from sqlalchemy import asc, desc
    query = JournalEntry.query.filter_by(user_id=user.id)

    if params.get("search"):
        pattern = f"%{params['search']}"
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
        return make_response({"errors": flatten_errors(exc.messages)}, 422)

    tags = data.get("tags", [])
    new_entry = JournalEntry(
        title=data["title"],
        content=data["content"],
        tags=",".join(tags) if tags else "",
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
    if not user:
        return make_response({"error": "Unauthorized: You must be logged in."}, 401)

    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        return make_response({"error": "Journal entry not found."}, 404)

    schema = JournalEntryUpdateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as exc:
        return make_response({"errors": flatten_errors(exc.messages)}, 422)

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

    db.session.delete(entry)
    db.session.commit()
    return make_response({}, 200)


if __name__ == '__main__':
    app.run(debug=True, port=5555)