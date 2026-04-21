from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    date_of_creation = fields.DateTime(dump_only=True)


class SignupSchema(Schema):
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=80, error="Username must be between 3 and 80 characters."),
    )
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, error="Password must be at least 8 characters."),
    )
    password_confirmation = fields.Str(required=True, load_only=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get("password") != data.get("password_confirmation"):
            raise ValidationError("Passwords do not match.", field_name="password_confirmation")


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class JournalEntrySchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(dump_only=True)
    content = fields.Str(dump_only=True)
    tags = fields.Method("get_tags", dump_only=True)
    user_id = fields.Int(dump_only=True)
    journal_creation_date = fields.DateTime(dump_only=True)

    def get_tags(self, obj) -> list[str]:
        if not obj.tags:
            return []
        return [tag.strip() for tag in obj.tags.split(",") if tag.strip()]


class JournalEntryCreateSchema(Schema):
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200, error="Title must be between 1 and 200 characters."),
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, error="Content cannot be empty."),
    )
    tags = fields.List(
        fields.Str(validate=validate.Length(min=1, max=50)),
        load_default=[],
    )


class JournalEntryUpdateSchema(Schema):
    title = fields.Str(
        validate=validate.Length(min=1, max=200, error="Title must be between 1 and 200 characters.")
    )
    content = fields.Str(
        validate=validate.Length(min=1, error="Content cannot be empty.")
    )
    tags = fields.List(
        fields.Str(validate=validate.Length(min=1, max=50)),
    )


class PaginationQuerySchema(Schema):
    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1, error="Page number must be 1 or greater."),
    )
    per_page = fields.Int(
        load_default=10,
        validate=validate.Range(min=1, max=50, error="per_page must be between 1 and 50."),
    )
    search = fields.Str(load_default=None)
    sort = fields.Str(
        load_default="journal_creation_date",
        validate=validate.OneOf(
            ["journal_creation_date", "title"],
            error="sort must be 'journal_creation_date' or 'title'.",
        ),
    )
    order = fields.Str(
        load_default="desc",
        validate=validate.OneOf(["asc", "desc"], error="order must be 'asc' or 'desc'."),
    )