import config
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk

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