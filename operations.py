import config
from tkinter import messagebox, ttk, StringVar, BooleanVar, IntVar
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
from tkinter.ttk import Combobox
from typing import List, Dict, Tuple, Optional

def list_users():
    """List all MySQL users and their authentication details"""
    try:
        # Query to get users and their authentication details
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

def create_table(table_name: str, columns: List[Dict]) -> bool:
    """
    Create a new table with the given name and columns
    
    Args:
        table_name: Name of the table to create
        columns: List of column definitions, where each column is a dict with:
            - name: Column name
            - type: Column data type (e.g., 'VARCHAR(255)', 'INT', 'TEXT')
            - not_null: Boolean indicating if column is NOT NULL
            - default: Default value (optional)
            - auto_increment: Boolean for AUTO_INCREMENT
            - primary_key: Boolean for PRIMARY KEY
            - unique: Boolean for UNIQUE constraint
            
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
    config.current_cursor.execute("SHOW TABLES")
    return [t[0] for t in config.current_cursor.fetchall()]

def truncate_table(table):
    config.current_cursor.execute(f"TRUNCATE TABLE {table}")
    config.current_connection.commit()

def delete_all(table):
    config.current_cursor.execute(f"DELETE FROM {table}")
    config.current_connection.commit()

def list_mysql_users(self):
    """Show all MySQL users"""
    if not config.current_connection:
        messagebox.showwarning("Warning", "Please connect to MySQL first")
        return

    try:
        # Get users using the operations module
        users = operations.list_users()
        
        # Create a new window
        user_window = tb.Toplevel(self.root)
        user_window.title("MySQL Users")
        user_window.geometry("600x400")
        
        # Create a treeview to display users
        columns = ("Username", "Host", "Has Password", "Auth Plugin")
        tree = ttk.Treeview(user_window, columns=columns, show="headings")
        
        # Configure columns
        column_widths = {
            "Username": 150, 
            "Host": 150, 
            "Has Password": 100, 
            "Auth Plugin": 150
        }
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Add users to the treeview
        for user in users:
            tree.insert("", "end", values=user)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(user_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack everything
        tree.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Add close button
        btn_frame = tb.Frame(user_window)
        btn_frame.pack(fill=X, pady=5)
        
        close_btn = tb.Button(
            btn_frame,
            text="Close",
            command=user_window.destroy,
            bootstyle="danger",
            width=10
        )
        close_btn.pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to list users: {str(e)}")