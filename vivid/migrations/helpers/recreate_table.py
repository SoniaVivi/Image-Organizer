def recreate_table(table_name, create_columns, current_columns):
    return [
        f"CREATE table new_table({create_columns});",
        f"INSERT INTO new_table({current_columns}) SELECT {current_columns} FROM {table_name};",
        f"DROP TABLE {table_name};",
        f"ALTER TABLE new_table RENAME TO {table_name};",
    ]
