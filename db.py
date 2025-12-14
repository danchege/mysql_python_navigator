import mysql.connector
import config

def connect(host, user, password, port=3306):
    try:
        print(f"Attempting to connect to MySQL at {host}:{port} as user: {user}")
        config.current_connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connection_timeout=5  # 5 second timeout
        )
        if config.current_connection.is_connected():
            db_info = config.current_connection.get_server_info()
            print(f"Successfully connected to MySQL Server version {db_info}")
            config.current_cursor = config.current_connection.cursor()
            return True, "Connected successfully"
        else:
            return False, "Failed to establish connection"
    except mysql.connector.Error as err:
        error_msg = f"Error: {err}"
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            error_msg = "Access denied. Please check your username and password."
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            error_msg = "Database does not exist."
        elif err.errno == 2003:  # Can't connect to MySQL server
            error_msg = "Could not connect to MySQL server. Make sure it's running and accessible."
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return False, error_msg

def list_databases():
    config.current_cursor.execute("SHOW DATABASES")
    return [db[0] for db in config.current_cursor.fetchall()]

def select_database(db_name):
    config.current_cursor.execute(f"USE {db_name}")
    config.current_db = db_name

def create_database(db_name):
    """Create a new database"""
    try:
        config.current_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        config.current_connection.commit()
        return True, f"Database '{db_name}' created successfully"
    except mysql.connector.Error as err:
        return False, f"Failed to create database: {err}"

def drop_database(db_name):
    """Drop an existing database"""
    try:
        config.current_cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        config.current_connection.commit()
        return True, f"Database '{db_name}' dropped successfully"
    except mysql.connector.Error as err:
        return False, f"Failed to drop database: {err}"
