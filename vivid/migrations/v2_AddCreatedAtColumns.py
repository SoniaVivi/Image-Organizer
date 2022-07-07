from .migrations.helpers.recreate_table import recreate_table


data = {
    "change": [
        *recreate_table(
            "Image",
            "id integer primary key, name text, path text, hash text, image_type text, created_at timestamp default current_timestamp",
            "id, name, path, hash, image_type",
        ),
        *recreate_table(
            "Tag",
            "id integer primary key, name text, created_at timestamp default current_timestamp",
            "id, name",
        ),
        *recreate_table(
            "ImageTag",
            "id integer primary key, tag_id integer, image_id int, created_at timestamp default current_timestamp",
            "id, tag_id, image_id",
        ),
        "UPDATE Image SET created_at=CURRENT_TIMESTAMP WHERE created_at IS NULL;",
        "UPDATE Tag SET created_at=CURRENT_TIMESTAMP WHERE created_at IS NULL;",
        "UPDATE ImageTag SET created_at=CURRENT_TIMESTAMP WHERE created_at IS NULL;",
    ],
    "revert": [
        "ALTER TABLE Image DROP COLUMN created_at;",
        "ALTER TABLE Tag DROP COLUMN created_at;",
        "ALTER TABLE ImageTag DROP COLUMN created_at;",
    ],
    "logging": "Added created_at column to tables: Image, Tag, ImageTag",
    "reversible": False,
}
