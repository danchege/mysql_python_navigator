import config

def list_tables():
    config.current_cursor.execute("SHOW TABLES")
    return [t[0] for t in config.current_cursor.fetchall()]

def truncate_table(table):
    config.current_cursor.execute(f"TRUNCATE TABLE {table}")
    config.current_connection.commit()

def delete_all(table):
    config.current_cursor.execute(f"DELETE FROM {table}")
    config.current_connection.commit()
