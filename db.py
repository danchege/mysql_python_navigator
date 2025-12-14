import mysql.connector
import config

def connect(host, user, password):
    try:
        config.current_connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        config.current_cursor = config.current_connection.cursor()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)

def list_databases():
    config.current_cursor.execute("SHOW DATABASES")
    return [db[0] for db in config.current_cursor.fetchall()]

def select_database(db_name):
    config.current_cursor.execute(f"USE {db_name}")
    config.current_db = db_name
