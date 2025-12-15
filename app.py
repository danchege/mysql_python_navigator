# File: app.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, ttk, StringVar, BooleanVar
import db, backup, operations, config

class MySQLNavigator:
    def __init__(self, root):
        self.root = root
        self.root.title("MySQL Navigator - by Daniel Chege")
        
        # Auto-adjust window size based on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calculate 70% of screen size for app window
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.7)
        
        # Calculate center position
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        
        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Set minimum window size (responsive)
        self.root.minsize(800, 500)
        
        # Current theme
        self.current_theme = "darkly"  # Default dark theme
        
        # Store window width for responsive calculations
        self.window_width = window_width
        
        # Connection Frame (Top)
        self.connection_frame = tb.LabelFrame(root, text="Connection", padding=10)
        self.connection_frame.pack(fill=X, padx=10, pady=10)
        
        # Connection inputs
        conn_row = tb.Frame(self.connection_frame)
        conn_row.pack(fill=X)
        
        tb.Label(conn_row, text="Host:").pack(side=LEFT, padx=5)
        self.host_entry = tb.Entry(conn_row, width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side=LEFT, padx=5)
        
        tb.Label(conn_row, text="User:").pack(side=LEFT, padx=5)
        self.user_entry = tb.Entry(conn_row, width=15)
        self.user_entry.insert(0, "root")
        self.user_entry.pack(side=LEFT, padx=5)
        
        tb.Label(conn_row, text="Port:").pack(side=LEFT, padx=5)
        self.port_entry = tb.Entry(conn_row, width=8)
        self.port_entry.insert(0, "3306")
        self.port_entry.pack(side=LEFT, padx=5)
        
        tb.Label(conn_row, text="Password:").pack(side=LEFT, padx=5)
        self.password_entry = tb.Entry(conn_row, show="*", width=15)
        self.password_entry.pack(side=LEFT, padx=5)
        
        self.connect_btn = tb.Button(conn_row, text="Connect", 
                                     command=self.connect_db, bootstyle=SUCCESS)
        self.connect_btn.pack(side=LEFT, padx=10)
        
        self.status_label = tb.Label(conn_row, text="Not connected", 
                                     bootstyle=DANGER)
        self.status_label.pack(side=LEFT, padx=10)
        
        # Theme toggle button
        self.theme_btn = tb.Button(conn_row, text="🌙 Dark", 
                                   command=self.toggle_theme, 
                                   bootstyle="secondary-outline",
                                   width=10)
        self.theme_btn.pack(side=RIGHT, padx=5)
        
        # Main Content Frame (Bottom - split panes)
        self.main_frame = tb.Frame(root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Right Pane - Operations
        operations_width = max(300, min(450, int(window_width * 0.25)))
        
        self.right_pane = tb.LabelFrame(self.main_frame, text="Operations", 
                                        padding=10, width=operations_width)
        self.right_pane.pack(side=RIGHT, fill=BOTH, expand=False, padx=(5, 0))
        self.right_pane.pack_propagate(False)
        
        # Current selection label
        self.selection_label = tb.Label(self.right_pane, 
                                       text="No database selected",
                                       font=("Segoe UI", 10, "bold"))
        self.selection_label.pack(pady=10)
        
        # Create canvas and scrollbar for operations
        canvas = tb.Canvas(self.right_pane, highlightthickness=0)
        scrollbar = tb.Scrollbar(self.right_pane, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Operation buttons
        btn_frame = scrollable_frame
        
        # User Management
        user_ops = tb.LabelFrame(btn_frame, text="User Management", padding=10)
        user_ops.pack(fill=X, pady=5)
        
        tb.Button(user_ops, text="👤 Create MySQL User", 
                 command=self.create_mysql_user,
                 bootstyle=SUCCESS, width=25).pack(pady=3, fill=X)
        
        tb.Button(user_ops, text="👥 List MySQL Users", 
                 command=self.list_mysql_users,
                 bootstyle=INFO, width=25).pack(pady=3, fill=X)
        
        # Database operations
        db_ops = tb.LabelFrame(btn_frame, text="Database Operations", padding=10)
        db_ops.pack(fill=X, pady=5)
        
        tb.Button(db_ops, text="🔄 Refresh Databases", 
                 command=self.refresh_databases, 
                 bootstyle=INFO, width=25).pack(pady=3, fill=X)
        
        tb.Button(db_ops, text="➕ Create Database", 
                 command=self.create_database,
                 bootstyle=SUCCESS, width=25).pack(pady=3, fill=X)
        
        self.drop_db_btn = tb.Button(db_ops, text="🗑 Drop Database", 
                 command=self.drop_database,
                 bootstyle=DANGER, width=25, state='disabled')
        self.drop_db_btn.pack(pady=3, fill=X)
        
        tb.Button(db_ops, text="💾 Backup Database", 
                 command=self.backup_current_db,
                 bootstyle=PRIMARY, width=25).pack(pady=3, fill=X)
        
        tb.Button(db_ops, text="📤 Export Database", 
                 command=self.export_database,
                 bootstyle=PRIMARY, width=25).pack(pady=3, fill=X)
        
        # Table operations
        tbl_ops = tb.LabelFrame(btn_frame, text="Table Operations", padding=10)
        tbl_ops.pack(fill=X, pady=5)
        
        tb.Button(tbl_ops, text="📋 Show Tables", 
                 command=self.show_tables,
                 bootstyle=INFO, width=25).pack(pady=3, fill=X)
        
        tb.Button(tbl_ops, text="➕ Create Table",
                 command=self.create_table,
                 bootstyle=SUCCESS, width=25).pack(pady=3, fill=X)
        
        tb.Button(tbl_ops, text="📊 View Table Data", 
                 command=self.view_table_data,
                 bootstyle=INFO, width=25).pack(pady=3, fill=X)
        
        tb.Button(tbl_ops, text="➕ Insert Record", 
                 command=self.insert_record,
                 bootstyle=SUCCESS, width=25).pack(pady=3, fill=X)
        
        tb.Button(tbl_ops, text="✏️ Update Record", 
                 command=self.update_record,
                 bootstyle=WARNING, width=25).pack(pady=3, fill=X)
        
        tb.Button(tbl_ops, text="🗑 Delete Record", 
                 command=self.delete_record,
                 bootstyle=DANGER, width=25).pack(pady=3, fill=X)
        
        tb.Button(tbl_ops, text="🗑 Truncate Table", 
                 command=self.truncate_table,
                 bootstyle=WARNING, width=25).pack(pady=3, fill=X)
        
        tb.Button(tbl_ops, text="❌ Delete All Records", 
                 command=self.delete_all_records,
                 bootstyle=DANGER, width=25).pack(pady=3, fill=X)
        
        # Query operations
        query_ops = tb.LabelFrame(btn_frame, text="Query Operations", padding=10)
        query_ops.pack(fill=X, pady=5)
        
        tb.Button(query_ops, text="✅ Run Custom Query", 
                 command=self.run_query,
                 bootstyle=SUCCESS, width=25).pack(pady=3, fill=X)
        
        # Left Pane - Database TreeView
        self.left_pane = tb.LabelFrame(self.main_frame, text="Databases & Tables", 
                                       padding=10)
        self.left_pane.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        # TreeView
        tree_frame = tb.Frame(self.left_pane)
        tree_frame.pack(fill=BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame, selectmode='browse')
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, 
                                 command=self.tree.yview)
        tree_scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Bind tree selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        if self.current_theme == "darkly":
            self.current_theme = "flatly"
            self.theme_btn.config(text="☀️ Light")
            self.root.style.theme_use("flatly")
        else:
            self.current_theme = "darkly"
            self.theme_btn.config(text="🌙 Dark")
            self.root.style.theme_use("darkly")
    
    def connect_db(self):
        host = self.host_entry.get() or "localhost"
        user = self.user_entry.get()
        password = self.password_entry.get()
        
        try:
            port = int(self.port_entry.get() or "3306")
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
        
        ok, msg = db.connect(host, user, password, port)
        
        if ok:
            self.status_label.config(text="✓ Connected", bootstyle=SUCCESS)
            messagebox.showinfo("Success", msg)
            self.refresh_databases()
        else:
            self.status_label.config(text="✗ Failed", bootstyle=DANGER)
            messagebox.showerror("Connection Error", msg)
    
    def _check_connection(self):
        """Helper method to check database connection"""
        if not hasattr(config, 'current_connection') or not config.current_connection or not config.current_connection.is_connected():
            messagebox.showwarning("Warning", "Please connect to MySQL first")
            return False
        return True
        
    def refresh_databases(self):
        if not self._check_connection():
            return
        
        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            databases = db.list_databases()
            non_system_dbs = []
            
            # Add databases to tree
            for db_name in databases:
                # Skip system databases
                if db_name.lower() in ['information_schema', 'mysql', 'performance_schema', 'sys']:
                    continue
                non_system_dbs.append(db_name)
                
                # Insert database with a dummy child
                self.tree.insert('', 'end', db_name, text=f"📁 {db_name}", 
                               values=['database'], open=False)
                self.tree.insert(db_name, 'end', text='Loading...')
            
            if not non_system_dbs:
                self.tree.insert('', 'end', text="No user databases found")
            
            messagebox.showinfo("Success", f"Found {len(non_system_dbs)} user databases")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load databases: {str(e)}")
            self.tree.insert('', 'end', text="Error loading databases")
    
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            self.drop_db_btn.config(state='disabled')
            return
        
        item = selected[0]
        parent = self.tree.parent(item)
        
        if parent == '':  # It's a database
            config.current_db = item
            self.selection_label.config(text=f"Selected: {item}")
            self.drop_db_btn.config(state='normal')
        else:  # It's a table
            table_name = self.tree.item(item)['text'].replace('📄 ', '')
            self.selection_label.config(text=f"Database: {parent} | Table: {table_name}")
    
    def create_database(self):
        """Show dialog to create a new database"""
        if not self._check_connection():
            return
            
        dialog = tb.Toplevel(self.root)
        dialog.title("Create Database")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        tb.Label(dialog, text="Database Name:").pack(pady=(20, 5))
        db_name_entry = tb.Entry(dialog, width=30)
        db_name_entry.pack(pady=5)
        db_name_entry.focus()
        
        def on_create():
            db_name = db_name_entry.get().strip()
            if not db_name:
                messagebox.showwarning("Warning", "Please enter a database name")
                return
                
            success, message = db.create_database(db_name)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_databases()
                dialog.destroy()
            else:
                messagebox.showerror("Error", message)
        
        btn_frame = tb.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tb.Button(btn_frame, text="Create", 
                 command=on_create,
                 bootstyle=SUCCESS, width=10).pack(side=LEFT, padx=5)
        
        tb.Button(btn_frame, text="Cancel", 
                 command=dialog.destroy,
                 bootstyle=SECONDARY, width=10).pack(side=LEFT, padx=5)
    
    def drop_database(self):
        """Drop the currently selected database"""
        if not self._check_connection():
            return
            
        selected = self.tree.selection()
        if not selected:
            return
            
        db_name = selected[0]
        parent = self.tree.parent(db_name)
        
        if parent != '':
            return
            
        if not messagebox.askyesno("Confirm Drop", 
                                 f"Are you sure you want to drop database '{db_name}'?\nThis action cannot be undone!"):
            return
        
        success, message = db.drop_database(db_name)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_databases()
            self.drop_db_btn.config(state='disabled')
        else:
            messagebox.showerror("Error", message)
    
    def on_tree_double_click(self, event):
        """Expand database to show tables"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        parent = self.tree.parent(item)
        
        if parent == '':
            self.load_tables(item)
    
    def load_tables(self, db_name):
        """Load tables for a specific database"""
        try:
            # Clear existing children
            for child in self.tree.get_children(db_name):
                self.tree.delete(child)
            
            # Get tables
            tables = db.list_tables(db_name)
            
            if not tables:
                self.tree.insert(db_name, 'end', text='No tables')
            else:
                for table in tables:
                    self.tree.insert(db_name, 'end', text=f"📄 {table}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tables: {str(e)}")
    
    def show_tables(self):
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        try:
            tables = db.list_tables(config.current_db)
            
            if not tables:
                messagebox.showinfo("Tables", f"No tables in database '{config.current_db}'")
            else:
                table_list = '\n'.join([f"• {t}" for t in tables])
                messagebox.showinfo(f"Tables in '{config.current_db}'", table_list)
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def backup_current_db(self):
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        try:
            user = self.user_entry.get()
            password = self.password_entry.get()
            
            filename = backup.backup_database(user, password)
            messagebox.showinfo("Success", f"Backup created:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def export_database(self):
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        try:
            user = self.user_entry.get()
            password = self.password_entry.get()
            
            filename = backup.export_database(user, password)
            messagebox.showinfo("Success", f"Export created:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def truncate_table(self):
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        table = tb.dialogs.Querybox.get_string(
            prompt="Enter table name to truncate:",
            title="Truncate Table"
        )
        
        if not table:
            return
        
        confirm = messagebox.askyesno(
            "Confirm", 
            f"Are you sure you want to TRUNCATE table '{table}'?\n\nThis will delete ALL records!"
        )
        
        if confirm:
            try:
                operations.truncate_table(table)
                messagebox.showinfo("Success", f"Table '{table}' truncated successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def delete_all_records(self):
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        table = tb.dialogs.Querybox.get_string(
            prompt="Enter table name:",
            title="Delete All Records"
        )
        
        if not table:
            return
        
        confirm = messagebox.askyesno(
            "Confirm", 
            f"Are you sure you want to DELETE all records from '{table}'?"
        )
        
        if confirm:
            try:
                operations.delete_all(table)
                messagebox.showinfo("Success", f"All records deleted from '{table}'")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def run_query(self):
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        query_window = tb.Toplevel(self.root)
        query_window.title("Run SQL Query")
        query_window.geometry("600x400")
        
        tb.Label(query_window, text="Enter SQL Query:", 
                font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        query_text = tb.Text(query_window, height=10, width=70)
        query_text.pack(padx=10, pady=10)
        
        def execute_query():
            query = query_text.get("1.0", "end-1c")
            if not query.strip():
                messagebox.showwarning("Warning", "Please enter a query")
                return
            
            try:
                result = operations.run_query(query)
                
                if result:
                    result_window = tb.Toplevel(query_window)
                    result_window.title("Query Results")
                    result_window.geometry("700x400")
                    
                    result_text = tb.Text(result_window, height=20, width=80)
                    result_text.pack(padx=10, pady=10, fill=BOTH, expand=True)
                    
                    for row in result:
                        result_text.insert("end", str(row) + "\n")
                    
                    result_text.config(state='disabled')
                else:
                    messagebox.showinfo("Success", "Query executed successfully (no results to display)")
            
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tb.Button(query_window, text="Execute Query", 
                 command=execute_query, bootstyle=SUCCESS).pack(pady=10)
    
    def create_mysql_user(self):
        """Create a new MySQL user with privileges"""
        if not config.current_connection:
            messagebox.showwarning("Warning", "Please connect to MySQL first")
            return
        
        user_window = tb.Toplevel(self.root)
        user_window.title("Create MySQL User")
        user_window.geometry("500x500")
        
        tb.Label(user_window, text="Username:", 
                font=("Segoe UI", 10, "bold")).pack(pady=(20, 5))
        username_entry = tb.Entry(user_window, width=40)
        username_entry.pack(pady=5)
        
        tb.Label(user_window, text="Password:", 
                font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        password_entry = tb.Entry(user_window, show="*", width=40)
        password_entry.pack(pady=5)
        
        show_pass_var = tb.BooleanVar(value=False)
        def toggle_password():
            if show_pass_var.get():
                password_entry.config(show="")
            else:
                password_entry.config(show="*")
        
        tb.Checkbutton(user_window, text="Show password", 
                      variable=show_pass_var, 
                      command=toggle_password).pack(pady=3)
        
        tb.Label(user_window, text="Host (default: localhost):", 
                font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        host_entry = tb.Entry(user_window, width=40)
        host_entry.insert(0, "localhost")
        host_entry.pack(pady=5)
        
        type_frame = tb.LabelFrame(user_window, text="User Type", padding=10)
        type_frame.pack(pady=15, padx=20, fill=X)
        
        user_type = tb.StringVar(value="admin")
        
        tb.Radiobutton(type_frame, 
                      text="🔒 ROOT USER (Full system access + grant privileges)", 
                      variable=user_type, value="root").pack(anchor=W, pady=5)
        
        tb.Radiobutton(type_frame, 
                      text="👑 ADMIN USER (All databases access)", 
                      variable=user_type, value="admin").pack(anchor=W, pady=5)
        
        tb.Radiobutton(type_frame, 
                      text="📁 DATABASE USER (Specific database only)", 
                      variable=user_type, value="specific").pack(anchor=W, pady=5)
        
        db_label = tb.Label(type_frame, text="Database name:")
        db_entry = tb.Entry(type_frame, width=30)
        
        def update_db_field(*args):
            if user_type.get() == "specific":
                db_label.pack(pady=(10, 2), padx=20, anchor=W)
                db_entry.pack(pady=2, padx=20, anchor=W)
            else:
                db_label.pack_forget()
                db_entry.pack_forget()
        
        user_type.trace('w', update_db_field)
        
        def create_user():
            username = username_entry.get().strip()
            password = password_entry.get()
            host = host_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required")
                return
            
            try:
                selected_type = user_type.get()
                
                if selected_type == "root":
                    operations.create_user(username, password, host, 
                                         user_type="root")
                    messagebox.showinfo("Success", 
                        f"🔒 ROOT USER Created!\n\n"
                        f"Username: {username}\n"
                        f"Host: {host}\n\n"
                        f"✓ ALL privileges on ALL databases\n"
                        f"✓ Can create users\n"
                        f"✓ Can grant privileges\n"
                        f"✓ Full system access\n\n"
                        f"⚠️ This user has complete control over MySQL!")
                
                elif selected_type == "admin":
                    operations.create_user(username, password, host, 
                                         user_type="admin")
                    messagebox.showinfo("Success", 
                        f"👑 ADMIN USER Created!\n\n"
                        f"Username: {username}\n"
                        f"Host: {host}\n\n"
                        f"✓ ALL privileges on ALL databases\n"
                        f"✓ Cannot create users\n"
                        f"✓ Cannot grant privileges")
                
                else:
                    db_name = db_entry.get().strip()
                    if not db_name:
                        messagebox.showerror("Error", "Please specify a database name")
                        return
                    
                    operations.create_user(username, password, host, 
                                         user_type="specific", database=db_name)
                    messagebox.showinfo("Success", 
                        f"📁 DATABASE USER Created!\n\n"
                        f"Username: {username}\n"
                        f"Host: {host}\n"
                        f"Database: {db_name}\n\n"
                        f"✓ ALL privileges on '{db_name}' only")
                
                user_window.destroy()
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create user:\n{str(e)}")
        
        btn_frame = tb.Frame(user_window)
        btn_frame.pack(pady=20)
        
        tb.Button(btn_frame, text="✓ Create User", 
                 command=create_user, bootstyle=SUCCESS, width=15).pack(side=LEFT, padx=5)
        
        tb.Button(btn_frame, text="✗ Cancel", 
                 command=user_window.destroy, bootstyle=DANGER, width=15).pack(side=LEFT, padx=5)
    
    def list_mysql_users(self):
        """Show all MySQL users"""
        if not config.current_connection:
            messagebox.showwarning("Warning", "Please connect to MySQL first")
            return
        
        try:
            users = operations.list_users()
            
            users_window = tb.Toplevel(self.root)
            users_window.title("MySQL Users")
            users_window.geometry("600x400")
            
            tb.Label(users_window, text="MySQL Users", 
                    font=("Segoe UI", 12, "bold")).pack(pady=10)
            
            tree_frame = tb.Frame(users_window)
            tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = tb.Scrollbar(tree_frame)
            scrollbar.pack(side=RIGHT, fill=Y)
            
            columns = ('username', 'host', 'has_password', 'auth_plugin')
            users_tree = ttk.Treeview(
                tree_frame, 
                columns=columns, 
                show='headings', 
                yscrollcommand=scrollbar.set
            )
            
            users_tree.heading('username', text='Username')
            users_tree.heading('host', text='Host')
            users_tree.heading('has_password', text='Has Password')
            users_tree.heading('auth_plugin', text='Auth Plugin')
            
            users_tree.column('username', width=150)
            users_tree.column('host', width=150)
            users_tree.column('has_password', width=100)
            users_tree.column('auth_plugin', width=150)
            
            users_tree.pack(fill=BOTH, expand=True)
            scrollbar.config(command=users_tree.yview)
            
            for user_data in users:
                users_tree.insert('', 'end', values=user_data)
            
            tb.Label(users_window, 
                    text=f"Total users: {len(users)}", 
                    font=("Segoe UI", 9)).pack(pady=5)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list users:\n{str(e)}")
    
    def create_table(self):
        """Show dialog to create a new table"""
        if not config.current_connection:
            messagebox.showwarning("Warning", "Please connect to MySQL first")
            return
            
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        # Use the database
        db.select_database(config.current_db)
        
        self.create_table_window = tb.Toplevel(self.root)
        self.create_table_window.title("Create New Table")
        self.create_table_window.geometry("800x600")
        self.create_table_window.minsize(700, 500)
        
        main_frame = tb.Frame(self.create_table_window, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        table_frame = tb.Frame(main_frame)
        table_frame.pack(fill=X, pady=(0, 10))
        
        tb.Label(table_frame, text="Table Name:", width=15).pack(side=LEFT, padx=5)
        self.table_name_var = StringVar()
        tb.Entry(table_frame, textvariable=self.table_name_var).pack(side=LEFT, fill=X, expand=True, padx=5)
        
        columns_frame = tb.LabelFrame(main_frame, text="Columns", padding=10)
        columns_frame.pack(fill=BOTH, expand=True, pady=5)
        
        canvas = tb.Canvas(columns_frame, highlightthickness=0)
        scrollbar = tb.Scrollbar(columns_frame, orient=VERTICAL, command=canvas.yview)
        self.scrollable_columns = tb.Frame(canvas)
        
        self.scrollable_columns.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_columns, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        self.add_column_row()
        
        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(fill=X, pady=(10, 0))
        
        add_col_btn = tb.Button(
            btn_frame,
            text="➕ Add Column",
            command=self.add_column_row,
            bootstyle="success-outline",
            width=15
        )
        add_col_btn.pack(side=LEFT, padx=5)
        
        create_btn = tb.Button(
            btn_frame,
            text="Create Table",
            command=self.execute_create_table,
            bootstyle="success",
            width=15
        )
        create_btn.pack(side=RIGHT, padx=5)
        
        cancel_btn = tb.Button(
            btn_frame,
            text="Cancel",
            command=self.create_table_window.destroy,
            bootstyle="danger",
            width=10
        )
        cancel_btn.pack(side=RIGHT, padx=5)
    
    def add_column_row(self, col_data=None):
        """Add a new row for column definition"""
        if not hasattr(self, 'scrollable_columns') or not self.scrollable_columns.winfo_exists():
            return
            
        row_frame = tb.Frame(self.scrollable_columns)
        row_frame.pack(fill=X, pady=2)
        
        col_name = StringVar(value=col_data['name'] if col_data and 'name' in col_data else '')
        tb.Entry(row_frame, textvariable=col_name, width=15).pack(side=LEFT, padx=2)
        
        data_types = [
            'INT', 'VARCHAR(255)', 'TEXT', 'DATE', 'DATETIME', 
            'TIMESTAMP', 'FLOAT', 'DOUBLE', 'DECIMAL(10,2)', 'BOOLEAN'
        ]
        data_type = StringVar(value=col_data['type'] if col_data and 'type' in col_data else 'VARCHAR(255)')
        type_combo = tb.Combobox(
            row_frame, 
            textvariable=data_type, 
            values=data_types,
            width=15,
            state='readonly'
        )
        type_combo.pack(side=LEFT, padx=2)
        
        not_null = BooleanVar(value=col_data.get('not_null', False) if col_data else False)
        tb.Checkbutton(
            row_frame, 
            text="NOT NULL", 
            variable=not_null,
            bootstyle="round-toggle"
        ).pack(side=LEFT, padx=2)
        
        primary_key = BooleanVar(value=col_data.get('primary_key', False) if col_data else False)
        tb.Checkbutton(
            row_frame, 
            text="PRIMARY KEY", 
            variable=primary_key,
            bootstyle="round-toggle"
        ).pack(side=LEFT, padx=2)
        
        auto_inc = BooleanVar(value=col_data.get('auto_increment', False) if col_data else False)
        tb.Checkbutton(
            row_frame, 
            text="AUTO_INC", 
            variable=auto_inc,
            bootstyle="round-toggle"
        ).pack(side=LEFT, padx=2)
        
        unique = BooleanVar(value=col_data.get('unique', False) if col_data else False)
        tb.Checkbutton(
            row_frame, 
            text="UNIQUE", 
            variable=unique,
            bootstyle="round-toggle"
        ).pack(side=LEFT, padx=2)
        
        default_val = StringVar(value=col_data.get('default', '') if col_data else '')
        tb.Label(row_frame, text="Default:").pack(side=LEFT, padx=(10, 2))
        tb.Entry(row_frame, textvariable=default_val, width=15).pack(side=LEFT, padx=2)
        
        def remove_row():
            row_frame.destroy()
            
        tb.Button(
            row_frame,
            text="🗑",
            command=remove_row,
            bootstyle="danger-outline",
            width=3
        ).pack(side=RIGHT, padx=2)
        
        row_frame.vars = {
            'name': col_name,
            'type': data_type,
            'not_null': not_null,
            'primary_key': primary_key,
            'auto_increment': auto_inc,
            'unique': unique,
            'default': default_val
        }
    
    def execute_create_table(self):
        """Execute the CREATE TABLE statement"""
        table_name = self.table_name_var.get().strip()
        if not table_name:
            messagebox.showerror("Error", "Please enter a table name")
            return
            
        columns = []
        for child in self.scrollable_columns.winfo_children():
            if hasattr(child, 'vars'):
                col_data = {
                    'name': child.vars['name'].get().strip(),
                    'type': child.vars['type'].get().strip(),
                    'not_null': child.vars['not_null'].get(),
                    'primary_key': child.vars['primary_key'].get(),
                    'auto_increment': child.vars['auto_increment'].get(),
                    'unique': child.vars['unique'].get(),
                    'default': child.vars['default'].get().strip() or None
                }
                
                if not col_data['name']:
                    messagebox.showerror("Error", "Column name cannot be empty")
                    return
                    
                columns.append(col_data)
        
        if not columns:
            messagebox.showerror("Error", "At least one column is required")
            return
            
        if operations.create_table(table_name, columns):
            messagebox.showinfo("Success", f"Table '{table_name}' created successfully!")
            self.create_table_window.destroy()
            if config.current_db:
                self.load_tables(config.current_db)
    
    # CRUD Operations
    def view_table_data(self):
        """View all data in a table"""
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        table = tb.dialogs.Querybox.get_string(
            prompt="Enter table name:",
            title="View Table Data"
        )
        
        if not table:
            return
        
        try:
            data, columns = operations.view_table_data(table)
            
            if not data:
                messagebox.showinfo("No Data", f"Table '{table}' has no records")
                return
            
            # Create window to display data
            data_window = tb.Toplevel(self.root)
            data_window.title(f"Data from '{table}'")
            data_window.geometry("900x500")
            
            # Create treeview
            tree_frame = tb.Frame(data_window)
            tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            tree_scroll = tb.Scrollbar(tree_frame)
            tree_scroll.pack(side=RIGHT, fill=Y)
            
            data_tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show='headings',
                yscrollcommand=tree_scroll.set
            )
            
            for col in columns:
                data_tree.heading(col, text=col)
                data_tree.column(col, width=100)
            
            for row in data:
                data_tree.insert('', 'end', values=row)
            
            data_tree.pack(side=LEFT, fill=BOTH, expand=True)
            tree_scroll.config(command=data_tree.yview)
            
            tb.Label(data_window, text=f"Total records: {len(data)}").pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def insert_record(self):
        """Insert a new record into a table"""
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        table = tb.dialogs.Querybox.get_string(
            prompt="Enter table name:",
            title="Insert Record"
        )
        
        if not table:
            return
        
        try:
            columns = operations.get_table_columns(table)
            
            if not columns:
                messagebox.showerror("Error", f"Could not get columns for table '{table}'")
                return
            
            # Create insert window
            insert_window = tb.Toplevel(self.root)
            insert_window.title(f"Insert Record into '{table}'")
            insert_window.geometry("500x600")
            
            main_frame = tb.Frame(insert_window, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            
            tb.Label(main_frame, text=f"Insert into '{table}'", 
                    font=("Segoe UI", 12, "bold")).pack(pady=10)
            
            # Canvas for scrolling
            canvas = tb.Canvas(main_frame)
            scrollbar = tb.Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
            scrollable_frame = tb.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side=RIGHT, fill=Y)
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            
            # Create entry fields for each column
            entries = {}
            for col_name, col_type in columns:
                field_frame = tb.Frame(scrollable_frame)
                field_frame.pack(fill=X, pady=5, padx=10)
                
                tb.Label(field_frame, text=f"{col_name} ({col_type}):", 
                        width=20, anchor=W).pack(side=LEFT, padx=5)
                
                entry = tb.Entry(field_frame, width=30)
                entry.pack(side=LEFT, padx=5, fill=X, expand=True)
                entries[col_name] = entry
            
            def do_insert():
                values = {}
                for col_name, entry in entries.items():
                    val = entry.get().strip()
                    if val:
                        values[col_name] = val
                
                if not values:
                    messagebox.showwarning("Warning", "Please enter at least one value")
                    return
                
                if operations.insert_record(table, values):
                    messagebox.showinfo("Success", "Record inserted successfully!")
                    insert_window.destroy()
            
            btn_frame = tb.Frame(main_frame)
            btn_frame.pack(pady=10)
            
            tb.Button(btn_frame, text="Insert", command=do_insert,
                     bootstyle=SUCCESS, width=12).pack(side=LEFT, padx=5)
            tb.Button(btn_frame, text="Cancel", command=insert_window.destroy,
                     bootstyle=DANGER, width=12).pack(side=LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def update_record(self):
        """Update records in a table"""
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        table = tb.dialogs.Querybox.get_string(
            prompt="Enter table name:",
            title="Update Record"
        )
        
        if not table:
            return
        
        try:
            columns = operations.get_table_columns(table)
            
            update_window = tb.Toplevel(self.root)
            update_window.title(f"Update Records in '{table}'")
            update_window.geometry("600x500")
            
            main_frame = tb.Frame(update_window, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            
            tb.Label(main_frame, text=f"Update records in '{table}'",
                    font=("Segoe UI", 12, "bold")).pack(pady=10)
            
            # WHERE clause
            where_frame = tb.LabelFrame(main_frame, text="WHERE Condition", padding=10)
            where_frame.pack(fill=X, pady=10)
            
            tb.Label(where_frame, text="WHERE:").pack(side=LEFT, padx=5)
            where_entry = tb.Entry(where_frame, width=50)
            where_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
            tb.Label(where_frame, text="(e.g., id=1 or name='John')").pack(side=LEFT, padx=5)
            
            # SET values
            set_frame = tb.LabelFrame(main_frame, text="SET Values", padding=10)
            set_frame.pack(fill=BOTH, expand=True, pady=10)
            
            canvas = tb.Canvas(set_frame)
            scrollbar = tb.Scrollbar(set_frame, orient=VERTICAL, command=canvas.yview)
            scrollable_frame = tb.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side=RIGHT, fill=Y)
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            
            entries = {}
            for col_name, col_type in columns:
                field_frame = tb.Frame(scrollable_frame)
                field_frame.pack(fill=X, pady=3, padx=10)
                
                tb.Label(field_frame, text=f"{col_name}:", 
                        width=20, anchor=W).pack(side=LEFT, padx=5)
                
                entry = tb.Entry(field_frame, width=30)
                entry.pack(side=LEFT, padx=5, fill=X, expand=True)
                entries[col_name] = entry
            
            def do_update():
                where = where_entry.get().strip()
                if not where:
                    messagebox.showwarning("Warning", "Please enter a WHERE condition")
                    return
                
                updates = {}
                for col_name, entry in entries.items():
                    val = entry.get().strip()
                    if val:
                        updates[col_name] = val
                
                if not updates:
                    messagebox.showwarning("Warning", "Please enter at least one value to update")
                    return
                
                if operations.update_record(table, updates, where):
                    messagebox.showinfo("Success", "Records updated successfully!")
                    update_window.destroy()
            
            btn_frame = tb.Frame(main_frame)
            btn_frame.pack(pady=10)
            
            tb.Button(btn_frame, text="Update", command=do_update,
                     bootstyle=SUCCESS, width=12).pack(side=LEFT, padx=5)
            tb.Button(btn_frame, text="Cancel", command=update_window.destroy,
                     bootstyle=DANGER, width=12).pack(side=LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def delete_record(self):
        """Delete records from a table"""
        if not config.current_db:
            messagebox.showwarning("Warning", "Please select a database first")
            return
        
        table = tb.dialogs.Querybox.get_string(
            prompt="Enter table name:",
            title="Delete Record"
        )
        
        if not table:
            return
        
        delete_window = tb.Toplevel(self.root)
        delete_window.title(f"Delete Records from '{table}'")
        delete_window.geometry("500x200")
        
        main_frame = tb.Frame(delete_window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        tb.Label(main_frame, text=f"Delete records from '{table}'",
                font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        where_frame = tb.Frame(main_frame)
        where_frame.pack(fill=X, pady=20)
        
        tb.Label(where_frame, text="WHERE:").pack(side=LEFT, padx=5)
        where_entry = tb.Entry(where_frame, width=40)
        where_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        
        tb.Label(main_frame, text="Example: id=1 or name='John'",
                font=("Segoe UI", 9, "italic")).pack(pady=5)
        
        def do_delete():
            where = where_entry.get().strip()
            if not where:
                messagebox.showwarning("Warning", "Please enter a WHERE condition")
                return
            
            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete records WHERE {where}?"
            )
            
            if confirm:
                if operations.delete_record(table, where):
                    messagebox.showinfo("Success", "Records deleted successfully!")
                    delete_window.destroy()
        
        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        tb.Button(btn_frame, text="Delete", command=do_delete,
                 bootstyle=DANGER, width=12).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancel", command=delete_window.destroy,
                 bootstyle=SECONDARY, width=12).pack(side=LEFT, padx=5)


if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = MySQLNavigator(root)
    root.mainloop()