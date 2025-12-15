# File: operations.py
import config
from tkinter import messagebox
from typing import List, Dict, Tuple, Optional

def list_users():
    """List all MySQL users and their authentication details"""
    try:
        query = """
        SELECT 
            User as username, 
            Host as host,
            IF(authentication_string = '', 'NO', 'YES') as has_password,
            plugin as auth_plugin
        FROM mysql.user
        ORDER BY User, Host
        """
        config.current_cursor.execute(query)
        return config.current_cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to list users: {str(e)}")
        return []

def create_user(username, password, host='localhost', user_type='admin', database=None):
    """Create a MySQL user with specified privileges"""
    try:
        # Create user
        create_query = f"CREATE USER IF NOT EXISTS '{username}'@'{host}' IDENTIFIED BY '{password}'"
        config.current_cursor.execute(create_query)
        
        # Grant privileges based on user type
        if user_type == 'root':
            # ROOT user - all privileges with grant option
            grant_query = f"GRANT ALL PRIVILEGES ON *.* TO '{username}'@'{host}' WITH GRANT OPTION"
        elif user_type == 'admin':
            # ADMIN user - all privileges but no grant option
            grant_query = f"GRANT ALL PRIVILEGES ON *.* TO '{username}'@'{host}'"
        else:  # specific database
            if not database:
                raise Exception("Database name required for specific user type")
            # Database-specific user
            grant_query = f"GRANT ALL PRIVILEGES ON `{database}`.* TO '{username}'@'{host}'"
        
        config.current_cursor.execute(grant_query)
        config.current_cursor.execute("FLUSH PRIVILEGES")
        config.current_connection.commit()
        return True
    except Exception as e:
        config.current_connection.rollback()
        raise Exception(f"Failed to create user: {str(e)}")

def create_table(table_name: str, columns: List[Dict]) -> bool:
    """
    Create a new table with the given name and columns
    
    Args:
        table_name: Name of the table to create
        columns: List of column definitions
            
    Returns:
        bool: True if table was created successfully, False otherwise
    """
    if not table_name or not columns:
        messagebox.showerror("Error", "Table name and at least one column are required")
        return False
        
    try:
        # Start building the CREATE TABLE statement
        create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ("
        
        # Add columns
        column_defs = []
        primary_keys = []
        
        for col in columns:
            col_def = f"`{col['name']}` {col['type']}"
            
            if col.get('not_null'):
                col_def += " NOT NULL"
                
            if col.get('auto_increment'):
                col_def += " AUTO_INCREMENT"
                
            if 'default' in col and col['default'] is not None and col['default'] != '':
                default_val = col['default']
                # Add quotes for string types if not a function
                if 'INT' not in col['type'].upper() and not str(default_val).startswith(('CURRENT_TIMESTAMP', 'NULL')):
                    default_val = f"'{default_val}'"
                col_def += f" DEFAULT {default_val}"
                
            if col.get('unique'):
                col_def += " UNIQUE"
                
            column_defs.append(col_def)
            
            if col.get('primary_key'):
                primary_keys.append(f"`{col['name']}`")
        
        # Add primary key constraint if any
        if primary_keys:
            column_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
        
        # Complete the CREATE TABLE statement
        create_sql += ",\n    ".join(column_defs)
        create_sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
        
        # Execute the statement
        config.current_cursor.execute(create_sql)
        config.current_connection.commit()
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create table: {str(e)}")
        if config.current_connection:
            config.current_connection.rollback()
        return False

def list_tables():
    """List all tables in current database"""
    if not config.current_db:
        raise Exception("No database selected")
    
    config.current_cursor.execute("SHOW TABLES")
    return [t[0] for t in config.current_cursor.fetchall()]

def truncate_table(table):
    """Remove all records from table (reset auto-increment)"""
    if not config.current_db:
        raise Exception("No database selected")
    
    config.current_cursor.execute(f"TRUNCATE TABLE `{table}`")
    config.current_connection.commit()

def delete_all(table):
    """Delete all records from table (keep auto-increment)"""
    if not config.current_db:
        raise Exception("No database selected")
    
    config.current_cursor.execute(f"DELETE FROM `{table}`")
    config.current_connection.commit()

def run_query(query):
    """Execute a custom SQL query"""
    if not config.current_db:
        raise Exception("No database selected")
    
    config.current_cursor.execute(query)
    
    # Check if query returns results
    if config.current_cursor.description:
        return config.current_cursor.fetchall()
    else:
        config.current_connection.commit()
        return None

# CRUD Operations
def get_table_columns(table):
    """Get column names and types for a table"""
    try:
        config.current_cursor.execute(f"DESCRIBE `{table}`")
        result = config.current_cursor.fetchall()
        # Returns list of tuples: (column_name, column_type)
        return [(row[0], row[1]) for row in result]
    except Exception as e:
        raise Exception(f"Failed to get columns: {str(e)}")

def view_table_data(table):
    """View all data from a table"""
    try:
        config.current_cursor.execute(f"SELECT * FROM `{table}`")
        data = config.current_cursor.fetchall()
        columns = [desc[0] for desc in config.current_cursor.description]
        return data, columns
    except Exception as e:
        raise Exception(f"Failed to view table data: {str(e)}")

def insert_record(table, values):
    """
    Insert a new record into a table
    
    Args:
        table: Table name
        values: Dictionary of column_name: value pairs
    """
    try:
        columns = ', '.join([f"`{col}`" for col in values.keys()])
        placeholders = ', '.join(['%s'] * len(values))
        
        query = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"
        config.current_cursor.execute(query, tuple(values.values()))
        config.current_connection.commit()
        return True
    except Exception as e:
        config.current_connection.rollback()
        messagebox.showerror("Error", f"Failed to insert record: {str(e)}")
        return False

def update_record(table, updates, where_clause):
    """
    Update records in a table
    
    Args:
        table: Table name
        updates: Dictionary of column_name: new_value pairs
        where_clause: WHERE condition (without 'WHERE' keyword)
    """
    try:
        set_clause = ', '.join([f"`{col}` = %s" for col in updates.keys()])
        query = f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}"
        
        config.current_cursor.execute(query, tuple(updates.values()))
        config.current_connection.commit()
        
        rows_affected = config.current_cursor.rowcount
        messagebox.showinfo("Success", f"{rows_affected} record(s) updated")
        return True
    except Exception as e:
        config.current_connection.rollback()
        messagebox.showerror("Error", f"Failed to update records: {str(e)}")
        return False

def delete_record(table, where_clause):
    """
    Delete records from a table
    
    Args:
        table: Table name
        where_clause: WHERE condition (without 'WHERE' keyword)
    """
    try:
        query = f"DELETE FROM `{table}` WHERE {where_clause}"
        config.current_cursor.execute(query)
        config.current_connection.commit()
        
        rows_affected = config.current_cursor.rowcount
        messagebox.showinfo("Success", f"{rows_affected} record(s) deleted")
        return True
    except Exception as e:
        config.current_connection.rollback()
        messagebox.showerror("Error", f"Failed to delete records: {str(e)}")
        return False