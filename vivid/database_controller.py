import sqlite3
from pathlib import Path
import re


class DatabaseController:
    DEFAULT_TABLES = ["Image", "Tag", "ImageTag", "ImageBlacklist", "Version"]
    try:
        db_version
    except NameError:
        db_version = 0

    def __init__(self, test=False, conn=None):
        if conn:
            self.connection = conn
        elif test:
            self.connection = self._setup_database(test)
        else:
            self.connection = sqlite3.connect("imagedb.db")
            for table in DatabaseController.DEFAULT_TABLES:
                self._table_exists(table)
            self.migrate_database()

    def create(self, table, attributes):
        sql = """INSERT INTO %s(%s)
             VALUES (%s)""" % (
            table,
            ",".join(attributes.keys()),
            ("?," * len(attributes.keys()))[0:-1],
        )
        try:
            cur = self.execute(sql, tuple(attributes.values()))
            self.connection.commit()
            return self.execute("SELECT max(id) FROM %s" % (table,)).fetchone()[0]
        except Exception as e:
            print(e)

    def update(self, table, id, new_values):
        for attribute in new_values:
            self.execute(
                """UPDATE %s SET %s = ? WHERE id = ?""" % (table, attribute[0]),
                (
                    attribute[1],
                    str(id),
                ),
            )

        self.connection.commit()

    def delete(self, table, attribute_pair):
        self.execute(
            """DELETE FROM %s WHERE %s=?""" % (table, attribute_pair[0]),
            (attribute_pair[1],),
        )
        self.connection.commit()

    def find_by(self, table, attributes, fetchall=False):
        sql = ""
        if type(attributes) != dict:
            sql = f'SELECT * FROM {table} WHERE {attributes[0]} = "{attributes[1]}"'
        else:
            sql = f"SELECT * FROM {table} WHERE "
            for (key, value) in attributes.items():
                sql += f'{key} = "{value}" AND '
            sql = sql[0:-5]

        records = None

        if fetchall:
            records = self.execute(sql).fetchall()
        else:
            records = self.execute(sql).fetchone()

        if records:
            if not fetchall:
                return self.to_record(table, records)
            else:
                return [self.to_record(table, record) for record in records]
        return records

    def find_many(self, table, attributes=[], **kwargs):
        sql = f"SELECT * FROM {table} AS a WHERE "
        exclude_sql = f"SELECT id FROM {table} WHERE "
        inclusive = kwargs.get("inclusive", True)
        exclude_attributes = kwargs.get("exclude", [])

        sql += self.sql_from_lists(
            *self._data_from_dicts(attributes), "OR" if inclusive else "AND"
        )

        if len(exclude_attributes):
            exclude_sql += self.sql_from_lists(
                *self._data_from_dicts(exclude_attributes), "OR"
            )
            sql += f"{'AND' if len(attributes) else ''}\
              a.id NOT IN ({exclude_sql})".replace(
                "  ", " "
            )
        return [self.to_record(table, x) for x in self.execute(sql).fetchall()]

    def between(self, table, start, stop):
        asc = start < stop
        lower = start if asc else stop
        upper = stop if asc else start
        order = " ORDER BY id ASC" if asc else " ORDER BY id DESC"
        sql = f"SELECT * FROM {table} WHERE id BETWEEN {lower} AND {upper}"
        results = self.execute(sql + order).fetchall()
        return [self.to_record(table, result) for result in results if result]

    def search(self, table, attributes):
        sql = f"SELECT id FROM {table} WHERE "
        for (column, value) in attributes.items():
            sql += f'{column} LIKE "%{value}%" AND '

        sql = sql[0:-5]
        results = self.execute(sql).fetchall()
        return [self.find_by(table, ("id", result[0])) for result in results]

    def get_first(self, table):
        return self._get_limit(table, False)

    def get_last(self, table):
        return self._get_limit(table)

    def get_columns(self, table):
        cols = self.execute(f"PRAGMA table_info({table})").fetchall()
        return None if len(cols) == 0 else [row[1] for row in cols]

    def count(self, table):
        return self.execute(f"SELECT count(*) FROM {table}").fetchone()[0]

    def exists(self, table, attribute=None):
        if not attribute:
            result = self.execute(
                """SELECT name
                               FROM sqlite_master
                               WHERE type='table'
                               AND name='%s' """
                % (table,)
            ).fetchone()
            return True if result != None else False
        return True if self.find_by(table, attribute) else False

    def unique(self, table, attribute):
        sql = "SELECT id FROM {} WHERE {}=?".format(table, attribute[0])
        result = self.execute(sql, (attribute[1],)).fetchall()
        return True if len(result) <= 1 else False

    def execute(self, sql_string, *args):
        return self.connection.execute(sql_string, *args)

    def sql_from_lists(self, names, values, joiner):
        sql = ""
        names_is_list = type(names) is list
        for i, value in enumerate(values):
            sql += names[i] if names_is_list else names
            sql += f"='{value}' {joiner} "
        return sql[: -(len(joiner) + 2)]

    def get_id(self, table, attributes):
        attributes_sql = self.sql_from_lists(
            list(attributes.keys()), list(attributes.values()), "AND"
        )
        sql = f"SELECT id FROM {table} WHERE {attributes_sql}"
        result = self.execute(sql).fetchone()
        if result:
            return result[0]

    def to_record(self, table, record_data):
        return dict(zip(self.get_columns(table), record_data))

    def next_id(self, table, value, asc=True):
        placholder_id = -1 if asc else 2**63
        operator = ">" if asc else "<"
        order_by = "ASC" if asc else "DESC"
        sql = """SELECT id FROM %s WHERE id %s %s ORDER BY id %s"""
        record = self.execute(
            sql
            % (
                table,
                operator,
                value,
                order_by,
            )
        ).fetchone()
        return record[0] if record else placholder_id

    def migrate_database(self, **kwargs):
        force_version = kwargs.get("force_database_version", False)
        db_version_target = force_version
        force_version = not not force_version

        if not db_version_target:
            if DatabaseController.db_version == 0:
                latest = self.get_last("Version")["version_number"]
                latest = 0 if latest is None else latest
                DatabaseController.db_version = latest
        db_version_target = (
            DatabaseController.db_version if not force_version else db_version_target
        )

        for migration in Path("./vivid/migrations").glob("v*_*.py"):
            version_name = int(re.search(r"(?<=v)(.+)(?=_)", migration.name)[0])

            if (version_name <= db_version_target and force_version) or (
                version_name > db_version_target and not force_version
            ):
                data = compile(
                    open(
                        migration,
                        mode="rb",
                    ).read(),
                    filename=migration.name,
                    mode="exec",
                )
                migration_data = {}
                exec(data, globals(), migration_data), migration_data["data"]
                for statement in migration_data["data"]["change"]:
                    self.execute(statement)
                    self.connection.commit()
                self.create("Version", {"version_number": int(version_name)})
                DatabaseController.db_version = version_name

    def _data_from_dicts(self, list_of_dicts):
        keys = []
        values = []
        for dict_data in list_of_dicts:
            k, v = list(dict_data.items())[0]
            keys.append(k)
            values.append(v)
        return [keys, values]

    def _table_exists(self, table_name):
        exists = self.execute(
            f"SELECT count(name)\
                            FROM sqlite_master\
                            WHERE type='table'\
                            AND name='{table_name}' "
        ).fetchone()[0]
        if exists == 0:
            print(f"Creating table {table_name}")
            self._setup_database(False, tables=[table_name])

    def _get_limit(self, table, asc=True):
        order_by = "DESC" if asc else "ASC"
        # Returning an empty record alleviates crashing in GUI on first start.
        placholder_id = -1 if asc else 2**63

        columns = self.get_columns(table)
        record_data = self.execute(
            "SELECT * FROM %s ORDER BY id %s LIMIT 1" % (table, order_by)
        ).fetchone()
        if not record_data:
            record_data = [None for _ in range(0, len(columns))]
            record_data[0] = placholder_id
        return dict(zip(columns, record_data))

    def _setup_database(self, test, **kwargs):
        tables = kwargs.get("tables", DatabaseController.DEFAULT_TABLES)
        conn = (
            sqlite3.connect("imagedb.db") if not test else sqlite3.connect(":memory:")
        )
        table_sql = {
            "Image": """CREATE TABLE Image
                    (id integer primary key,
                     name text, path text,
                     hash text,
                     image_type text)""",
            "Tag": """CREATE TABLE Tag
                    (id integer primary key, name text)""",
            "ImageTag": """CREATE TABLE ImageTag
                    (id integer primary key, tag_id integer, image_id int)""",
            "ImageBlacklist": """CREATE TABLE ImageBlacklist
                    (id integer primary key,
                     textable string,
                     textable_type string)""",
            "Version": """CREATE TABLE Version
                    (id integer primary key,
                     version_number integer,
                     updated_at timestamp default current_timestamp)""",
        }
        for table in tables:
            conn.execute(table_sql[table])
        conn.commit()
        return conn if test == True else None
