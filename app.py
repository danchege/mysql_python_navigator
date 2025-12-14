# File: app.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, ttk
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
        self.user_entry.pack(side=LEFT, padx=5)
        
        tb.Label(conn_row, text="Port:").pack(side=LEFT, padx=5)
        self.port_entry = tb.Entry(conn_row, width=8)
        self.port_entry.insert(0, "3306")
        self.port_entry.pack(side=LEFT, padx=5)
        self.user_entry.insert(0, "root")
        self.user_entry.pack(side=LEFT, padx=5)
        
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
        # Theme Toggle Button
        self.theme_btn = tb.Button(conn_row, text="🌙 Dark", 
                                   command=self.toggle_theme, 
                                   bootstyle="secondary-outline",
                                   width=10)
        self.theme_btn.pack(side=RIGHT, padx=5)
        
        # Main Content Frame (Bottom - split panes)
        self.main_frame = tb.Frame(root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Right Pane - Operations (MOVED TO RIGHT FIRST)
        # Calculate responsive width (25% of window, min 300px, max 450px)
        operations_width = max(300, min(450, int(window_width * 0.25)))
        
        self.right_pane = tb.LabelFrame(self.main_frame, text="Operations", 
                                        padding=10, width=operations_width)
        self.right_pane.pack(side=RIGHT, fill=BOTH, expand=False, padx=(5, 0))
        self.right_pane.pack_propagate(False)  # Maintain fixed width
        
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
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Operation buttons (now in scrollable frame)
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
        
        tb.Button(tbl_ops, text="👁 Show Tables", 
                 command=self.show_tables,
                 bootstyle=INFO, width=25).pack(pady=3, fill=X)
        
        tb.Button(tbl_ops, text="🗑 Truncate Table", 
                 command=self.truncate_table,
                 bootstyle=WARNING, width=25).pack(pady=3, fill=X)
        
        tb.Button(tbl_ops, text="❌ Delete All Records", 
                 command=self.delete_all_records,
                 bootstyle=DANGER, width=25).pack(pady=3, fill=X)
        
        # Query operations
        query_ops = tb.LabelFrame(btn_frame, text="Query Operations", padding=10)
        query_ops.pack(fill=X, pady=5)
        
        tb.Button(query_ops, text="✏ Run Custom Query", 
                 command=self.run_query,
                 bootstyle=SUCCESS, width=25).pack(pady=3, fill=X)
        
        # Left Pane - Database TreeView (NOW ON LEFT)
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
    
    def list_users(self):
        """Display a list of all MySQL users"""
        try:
            # Check if connected
            if not hasattr(config, 'current_connection') or not config.current_connection.is_connected():
                messagebox.showwarning("Not Connected", "Please connect to the database first")
                return

            # Get users using the operations module
            users = operations.list_users()

            # Create a new window
            user_window = tb.Toplevel(self.root)
            user_window.title("MySQL Users")
            user_window.geometry("700x400")
            
            # Create a treeview to display users
            columns = ("Username", "Host", "Has Password", "Auth Plugin")
            tree = ttk.Treeview(user_window, columns=columns, show="headings")
            
            # Configure columns with appropriate widths
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
            close_btn.pack(side=RIGHT, padx=10)
            
            # Make the window resizable
            user_window.minsize(600, 300)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list users: {str(e)}")
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        if self.current_theme == "darkly":
            # Switch to light theme
            self.current_theme = "flatly"
            self.theme_btn.config(text="☀️ Light")
            self.root.style.theme_use("flatly")
        else:
            # Switch to dark theme
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
                # Skip system databases but keep track of them
                if db_name.lower() in ['information_schema', 'mysql', 'performance_schema', 'sys']:
                    continue
                non_system_dbs.append(db_name)
                
                # Insert database with a dummy child (for expand arrow)
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
            
        # Create dialog window
        dialog = tb.Toplevel(self.root)
        dialog.title("Create Database")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Database name input
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
        
        # Buttons
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
        
        # Only allow dropping databases (not tables)
        if parent != '':
            return
            
        # Confirm before dropping
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
        
        # Only expand if it's a database (no parent)
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
        
        # Simple input dialog
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
        
        # Create query window
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
                    # Show results in a new window
                    result_window = tb.Toplevel(query_window)
                    result_window.title("Query Results")
                    result_window.geometry("700x400")
                    
                    # Create text widget for results
                    result_text = tb.Text(result_window, height=20, width=80)
                    result_text.pack(padx=10, pady=10, fill=BOTH, expand=True)
                    
                    # Format and display results
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
        
        # Create user window
        user_window = tb.Toplevel(self.root)
        user_window.title("Create MySQL User")
        user_window.geometry("500x500")
        
        # Username
        tb.Label(user_window, text="Username:", 
                font=("Segoe UI", 10, "bold")).pack(pady=(20, 5))
        username_entry = tb.Entry(user_window, width=40)
        username_entry.pack(pady=5)
        
        # Password
        tb.Label(user_window, text="Password:", 
                font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        password_entry = tb.Entry(user_window, show="*", width=40)
        password_entry.pack(pady=5)
        
        # Show password checkbox
        show_pass_var = tb.BooleanVar(value=False)
        def toggle_password():
            if show_pass_var.get():
                password_entry.config(show="")
            else:
                password_entry.config(show="*")
        
        tb.Checkbutton(user_window, text="Show password", 
                      variable=show_pass_var, 
                      command=toggle_password).pack(pady=3)
        
        # Host
        tb.Label(user_window, text="Host (default: localhost):", 
                font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        host_entry = tb.Entry(user_window, width=40)
        host_entry.insert(0, "localhost")
        host_entry.pack(pady=5)
        
        # User type frame
        type_frame = tb.LabelFrame(user_window, text="User Type", padding=10)
        type_frame.pack(pady=15, padx=20, fill=X)
        
        user_type = tb.StringVar(value="admin")
        
        tb.Radiobutton(type_frame, 
                      text="🔑 ROOT USER (Full system access + grant privileges)", 
                      variable=user_type, value="root").pack(anchor=W, pady=5)
        
        tb.Radiobutton(type_frame, 
                      text="👑 ADMIN USER (All databases access)", 
                      variable=user_type, value="admin").pack(anchor=W, pady=5)
        
        tb.Radiobutton(type_frame, 
                      text="📁 DATABASE USER (Specific database only)", 
                      variable=user_type, value="specific").pack(anchor=W, pady=5)
        
        # Database selection for specific privileges
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
                    # Create ROOT user with full privileges
                    operations.create_user(username, password, host, 
                                         user_type="root")
                    messagebox.showinfo("Success", 
                        f"🔑 ROOT USER Created!\n\n"
                        f"Username: {username}\n"
                        f"Host: {host}\n\n"
                        f"✓ ALL privileges on ALL databases\n"
                        f"✓ Can create users\n"
                        f"✓ Can grant privileges\n"
                        f"✓ Full system access\n\n"
                        f"⚠️ This user has complete control over MySQL!")
                
                elif selected_type == "admin":
                    # Create ADMIN user
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
                    # Create DATABASE-SPECIFIC user
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
        
        # Create button
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
            
            # Create users window
            users_window = tb.Toplevel(self.root)
            users_window.title("MySQL Users")
            users_window.geometry("600x400")
            
            tb.Label(users_window, text="MySQL Users", 
                    font=("Segoe UI", 12, "bold")).pack(pady=10)
            
            # Create treeview for users
            tree_frame = tb.Frame(users_window)
            tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbar
            scrollbar = tb.Scrollbar(tree_frame)
            scrollbar.pack(side=RIGHT, fill=Y)
            
            # Treeview with all columns
            columns = ('username', 'host', 'has_password', 'auth_plugin')
            users_tree = ttk.Treeview(
                tree_frame, 
                columns=columns, 
                show='headings', 
                yscrollcommand=scrollbar.set
            )
            
            # Configure columns
            users_tree.heading('username', text='Username')
            users_tree.heading('host', text='Host')
            users_tree.heading('has_password', text='Has Password')
            users_tree.heading('auth_plugin', text='Auth Plugin')
            
            # Set column widths
            users_tree.column('username', width=150)
            users_tree.column('host', width=150)
            users_tree.column('has_password', width=100)
            users_tree.column('auth_plugin', width=150)
            
            users_tree.pack(fill=BOTH, expand=True)
            scrollbar.config(command=users_tree.yview)
            
            # Populate users with all columns
            for user_data in users:
                users_tree.insert('', 'end', values=user_data)
            
            tb.Label(users_window, 
                    text=f"Total users: {len(users)}", 
                    font=("Segoe UI", 9)).pack(pady=5)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list users:\n{str(e)}")

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = MySQLNavigator(root)
    root.mainloop()


# File: config.py
current_connection = None
current_cursor = None
current_db = None


# File: db.py
import mysql.connector
import config

def connect(host, user, password):
    """Establish MySQL connection"""
    try:
        # Debug output
        print(f"[DEBUG] Attempting connection:")
        print(f"  Host: '{host}'")
        print(f"  User: '{user}'")
        print(f"  Password length: {len(password)} chars")
        print(f"  Password empty: {password == ''}")
        
        # Handle empty password
        if password == "":
            print("[DEBUG] Connecting without password...")
            config.current_connection = mysql.connector.connect(
                host=host,
                user=user
            )
        else:
            print("[DEBUG] Connecting with password...")
            config.current_connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
        
        config.current_cursor = config.current_connection.cursor()
        print("[DEBUG] Connection successful!")
        return True, "Connected successfully to MySQL"
    except mysql.connector.Error as err:
        print(f"[DEBUG] MySQL Error: {err}")
        print(f"[DEBUG] Error code: {err.errno}")
        if err.errno == 1045:
            return False, "Access denied. Check username and password."
        elif err.errno == 2003:
            return False, "Can't connect to MySQL server. Is it running?"
        else:
            return False, f"MySQL Error: {str(err)}"
    except Exception as e:
        print(f"[DEBUG] General error: {e}")
        return False, str(e)

def list_databases():
    """Get all databases"""
    if not config.current_cursor:
        raise Exception("Not connected to MySQL")
    
    config.current_cursor.execute("SHOW DATABASES")
    return [db[0] for db in config.current_cursor.fetchall()]

def select_database(db_name):
    """Select a database"""
    if not config.current_cursor:
        raise Exception("Not connected to MySQL")
    
    config.current_cursor.execute(f"USE `{db_name}`")
    config.current_db = db_name

def list_tables(db_name):
    """Get all tables in a database"""
    if not config.current_cursor:
        raise Exception("Not connected to MySQL")
    
    # Temporarily use the database
    config.current_cursor.execute(f"USE `{db_name}`")
    config.current_cursor.execute("SHOW TABLES")
    return [table[0] for table in config.current_cursor.fetchall()]


# File: operations.py
import config

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