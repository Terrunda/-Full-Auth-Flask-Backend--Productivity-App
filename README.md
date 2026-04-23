# -Full-Auth-Flask-Backend--Productivity-App


## Description
This repository is a submission created for the submission: <br> [Link to assigment](https://moringa.instructure.com/courses/1389/assignments/87555).

The workout application is built using the following libraries:
- flask = "2.2.2"
- flask-sqlalchemy = "3.0.3"
- Werkzeug = "2.2.2"
- marshmallow = "3.20.1"
- faker = "15.3.2"
- flask-migrate = "4.0.0"
- flask-restful = "0.3.9"
- importlib-metadata = "6.0.0"
- importlib-resources = "5.10.0"
- pytest = "7.2.0"
- flask-bcrypt = "1.0.1"

This is a Flask application built with:
- Full Auth Flask Backend.

It is meant to be used to be used as a Productivity App. In this case, I chose to go with a Journal app.

# Relations
It is built on a relational database with 2 tables:
- Users: To store information about users.
- JournalEntry: To track journals written by different users.

## Installation steps.

Remember to switch to a **virtual environment**, such as `venv`.
### 1. Install dependencies
```bash
pipenv install
pipenv shell
```

### 2. Set up the database

Switch to the server directory using the command:
```bash
cd server
```

```bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

### 3. Seed the database
**Optional: **
```bash
python seed.py
```

To run the app, type:
```bash
python app.py
or 
flask run
```
in the terminal.

Once the Flask app is running, you can check the routes defined to view the data stored.
### 4. View the frontend
Switch to the directory `client-with-sessions`
```bash
cd client-with-sessions
```

After switching, install the necessary dependencies from which you can view the frontend.
```bash
npm install
npm start
```
---

## List of all endpoints

---

## Auth Routes

### `POST /signup`
Registers a new account. Accepts a `username`, `password`, and `password_confirmation`. Logs the user in immediately by opening a session.

### `POST /login`
Authenticates an existing user. Accepts a `username` and `password`. Opens a session on success.

### `GET /check_session`
Returns the currently logged-in user if a session is active, otherwise returns an empty object.

### `DELETE /logout`
Ends the current session by removing the `user_id` from the session store.

---

## Journal Entry Routes

### `GET /entries`
Returns a paginated list of the logged-in user's journal entries. Accepts the following query parameters:

- `page` — page number (default: `1`)
- `per_page` — results per page, max 50 (default: `10`)
- `search` — search across title and content
- `sort` — sort by `journal_creation_date` or `title` (default: `journal_creation_date`)
- `order` — `asc` or `desc` (default: `desc`)

### `GET /entries/<int:entry_id>`
Returns a single journal entry by ID. Only accessible by the user who created it.

### `POST /entries`
Creates a new journal entry. Accepts a `title`, `content`, and an optional list of `tags`.

### `PATCH /entries/<int:entry_id>`
Updates an existing journal entry. All fields are optional — only send the fields you want to change. Accepts `title`, `content`, and `tags`.

### `DELETE /entries/<int:entry_id>`
Deletes a journal entry by ID. Only accessible by the user who created it.

