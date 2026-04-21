from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    date_of_creation = fields.DateTime(dump_only=True)


class JournalEntrySchema(Schema):
    """Read-only serializer for JournalEntry — used in responses."""

    id = fields.Int(dump_only=True)
    title = fields.Str(dump_only=True)
    content = fields.Str(dump_only=True)
    tags = fields.Method("get_tags", dump_only=True)
    user_id = fields.Int(dump_only=True)
    journal_creation_date = fields.DateTime(dump_only=True)

    def get_tags(self, obj) -> list[str]:
        """Split the stored comma-separated tags string into a list."""
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
