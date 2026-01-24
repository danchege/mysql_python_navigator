# File: app.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, ttk, StringVar, BooleanVar, Menu
import mysql.connector
from mysql.connector import errorcode
import db, backup, operations, config
import re

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
        
        # Preview window reference
        self.preview_window = None
        
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
        
        # Right-click context menu
        self.tree.bind('<Button-3>', self.show_context_menu)  # Right-click
        
        # Load tables when database is expanded
        self.tree.bind('<<TreeviewOpen>>', self.on_tree_expand)
        
        # Preview window reference
        self.preview_window = None
    
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
                self.tree.insert('', 'end', db_name, text=db_name, 
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
            table_name = self.tree.item(item)['text']
            self.selection_label.config(text=f"Database: {parent} | Table: {table_name}")
    
    def show_context_menu(self, event):
        """Show right-click context menu for database/table"""
        # Select the item under cursor
        item = self.tree.identify_row(event.y)
        if not item:
            return "break"
            
        self.tree.selection_set(item)
        self.tree.focus(item)
        
        # Create context menu
        context_menu = Menu(self.root, tearoff=0)
        
        parent = self.tree.parent(item)
        
        def close_menu():
            """Close the context menu and clean up"""
            context_menu.grab_release()
            context_menu.unpost()
            context_menu.destroy()
        
        if parent == '':  # It's a database
            db_name = self.strip_emojis(item)
            context_menu.add_command(
                label=f"👁️ Preview Database '{db_name}'",
                command=lambda db=db_name: [self.preview_database(db), close_menu()]
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="📋 Show Tables",
                command=lambda db=db_name: [self.show_tables_from_context(db), close_menu()]
            )
            context_menu.add_command(
                label="➕ Create Table",
                command=lambda db=db_name: [self.create_table_from_context(db), close_menu()]
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="💾 Backup Database",
                command=lambda db=db_name: [self.backup_database_from_context(db), close_menu()]
            )
            context_menu.add_command(
                label="📤 Export Database",
                command=lambda db=db_name: [self.export_database_from_context(db), close_menu()]
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="🗑️ Drop Database",
                command=lambda db=db_name: [self.drop_database_from_context(db), close_menu()]
            )
        else:  # It's a table
            table_text = self.tree.item(item)['text']
            table_name = table_text.replace('📄 ', '').strip()
            db_name = parent.replace('📁 ', '').strip()
            
            if table_name not in ('Loading...', 'No tables'):
                context_menu.add_command(
                    label=f"👁️ Preview Table '{table_name}'",
                    command=lambda db=db_name, tbl=table_name: [self.preview_table(db, tbl), close_menu()]
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="📊 View All Data",
                    command=lambda db=db_name, tbl=table_name: [self.view_table_data_from_context(db, tbl), close_menu()]
                )
                context_menu.add_command(
                    label="🔍 View Structure",
                    command=lambda db=db_name, tbl=table_name: [self.view_table_structure(db, tbl), close_menu()]
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="➕ Insert Record",
                    command=lambda db=db_name, tbl=table_name: [self.insert_record_from_context(db, tbl), close_menu()]
                )
                context_menu.add_command(
                    label="✏️ Update Records",
                    command=lambda db=db_name, tbl=table_name: [self.update_record_from_context(db, tbl), close_menu()]
                )
                context_menu.add_command(
                    label="🗑️ Delete Records",
                    command=lambda db=db_name, tbl=table_name: [self.delete_record_from_context(db, tbl), close_menu()]
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="🗑️ Truncate Table",
                    command=lambda db=db_name, tbl=table_name: [self.truncate_table_from_context(db, tbl), close_menu()]
                )
                context_menu.add_command(
                    label="❌ Drop Table",
                    command=lambda db=db_name, tbl=table_name: [self.drop_table_from_context(db, tbl), close_menu()]
                )
        
        # Display the menu and prevent default behavior
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
            context_menu.focus_set()  # Ensure the menu has focus
            context_menu.grab_set()   # Ensure the menu captures all events
            
            # Close menu when clicking outside or pressing Escape
            def on_click(e):
                if e.widget not in (context_menu, self.tree):
                    close_menu()
            
            self.root.bind("<Button-1>", on_click, add='+')
            self.root.bind("<Escape>", lambda e: close_menu(), add='+')
            
        except Exception as e:
            print(f"Error showing context menu: {e}")
            if context_menu.winfo_exists():
                close_menu()
        
        return "break"  # Prevent default context menu
    
    def preview_database(self, db_name):
        """Preview database information in the main window"""
        try:
            # Clean database name (remove any emojis or extra whitespace)
            db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
            
            # Set current database
            config.current_db = db_name
            db.select_database(db_name)
            
            # Close existing preview window if open
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            
            # Create preview panel
            self.preview_window = tb.LabelFrame(self.left_pane, text=f"Preview: {db_name}", padding=10)
            self.preview_window.pack(fill=BOTH, expand=False, pady=10)
            
            # Get database stats
            tables = db.list_tables(db_name)
            
            # Display info
            info_frame = tb.Frame(self.preview_window)
            info_frame.pack(fill=X, pady=5)
            
            tb.Label(info_frame, text=f"📊 Database: {db_name}", 
                    font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=2)
            tb.Label(info_frame, text=f"📋 Total Tables: {len(tables)}", 
                    font=("Segoe UI", 10)).pack(anchor=W, pady=2)
            
            if tables:
                tb.Label(info_frame, text="Tables:", 
                        font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(10, 2))
                
                # Create scrollable frame for tables
                canvas = tb.Canvas(info_frame, height=150)
                scrollbar = tb.Scrollbar(info_frame, orient=VERTICAL, command=canvas.yview)
                table_frame = tb.Frame(canvas)
                
                table_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=table_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                
                for table in tables:
                    tb.Label(table_frame, text=f"  • {table}").pack(anchor=W)
                
                canvas.pack(side=LEFT, fill=BOTH, expand=True)
                scrollbar.pack(side=RIGHT, fill=Y)
            
            # Close button
            tb.Button(self.preview_window, text="✖ Close Preview", 
                     command=self.close_preview,
                     bootstyle="secondary-outline").pack(pady=5)
                     
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview database: {str(e)}")
    
    def preview_table(self, db_name, table_name):
        """Preview table structure and sample data"""
        try:
            # Clean table name (remove any emojis or extra whitespace)
            table_name = table_name.replace('📄 ', '').replace('📁 ', '').strip()
            db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
            
            # Set current database
            config.current_db = db_name
            db.select_database(db_name)
            
            # Close existing preview window if open
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            
            # Create preview panel
            self.preview_window = tb.LabelFrame(self.left_pane, 
                                               text=f"Preview: {db_name}.{table_name}", 
                                               padding=10)
            self.preview_window.pack(fill=BOTH, expand=False, pady=10)
            
            # Get table structure
            columns = operations.get_table_columns(table_name)
            
            # Get row count
            config.current_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            row_count = config.current_cursor.fetchone()[0]
            
            # Display info
            tb.Label(self.preview_window, text=f"📄 Table: {table_name}", 
                    font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=2)
            tb.Label(self.preview_window, text=f"📊 Total Rows: {row_count}", 
                    font=("Segoe UI", 10)).pack(anchor=W, pady=2)
            tb.Label(self.preview_window, text=f"📋 Columns: {len(columns)}", 
                    font=("Segoe UI", 10)).pack(anchor=W, pady=2)
            
            # Show structure
            tb.Label(self.preview_window, text="Structure:", 
                    font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(10, 5))
            
            struct_frame = tb.Frame(self.preview_window)
            struct_frame.pack(fill=BOTH, expand=True, pady=5)
            
            # Create tree for structure
            struct_tree = ttk.Treeview(struct_frame, columns=('Type',), 
                                      show='tree headings', height=5)
            struct_tree.heading('#0', text='Column')
            struct_tree.heading('Type', text='Type')
            struct_tree.column('#0', width=150)
            struct_tree.column('Type', width=150)
            
            for col_name, col_type in columns:
                struct_tree.insert('', 'end', text=col_name, values=(col_type,))
            
            struct_tree.pack(fill=BOTH, expand=True)
            
            # Show sample data
            if row_count > 0:
                tb.Label(self.preview_window, text="Sample Data (First 5 rows):", 
                        font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(10, 5))
                
                data_frame = tb.Frame(self.preview_window)
                data_frame.pack(fill=BOTH, expand=True, pady=5)
                
                config.current_cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5")
                sample_data = config.current_cursor.fetchall()
                col_names = [desc[0] for desc in config.current_cursor.description]
                
                # Create tree for sample data
                data_tree = ttk.Treeview(data_frame, columns=col_names, 
                                        show='headings', height=5)
                
                for col in col_names:
                    data_tree.heading(col, text=col)
                    data_tree.column(col, width=100)
                
                for row in sample_data:
                    data_tree.insert('', 'end', values=row)
                
                scrollbar = tb.Scrollbar(data_frame, orient=HORIZONTAL, command=data_tree.xview)
                data_tree.configure(xscrollcommand=scrollbar.set)
                
                data_tree.pack(fill=BOTH, expand=True)
                scrollbar.pack(fill=X)
            
            # Close button
            tb.Button(self.preview_window, text="✖ Close Preview", 
                     command=self.close_preview,
                     bootstyle="secondary-outline").pack(pady=5)
                     
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview table: {str(e)}")
    
    def close_preview(self):
        """Close the preview panel"""
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
            self.preview_window = None
    
    # Context menu helper methods
    def show_tables_from_context(self, db_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        config.current_db = db_name
        self.show_tables()
    
    def create_table_from_context(self, db_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        config.current_db = db_name
        self.create_table()
    
    def backup_database_from_context(self, db_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        config.current_db = db_name
        self.backup_current_db()
    
    def export_database_from_context(self, db_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        config.current_db = db_name
        self.export_database()
    
    def drop_database_from_context(self, db_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        config.current_db = db_name
        self.drop_database()
    
    def view_table_data_from_context(self, db_name, table_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        table_name = table_name.replace('📄 ', '').replace('📁 ', '').strip()
        config.current_db = db_name
        db.select_database(db_name)
        
        try:
            data, columns = operations.view_table_data(table_name)
            
            if not data:
                messagebox.showinfo("No Data", f"Table '{table_name}' has no records")
                return
            
            # Create window to display data
            data_window = tb.Toplevel(self.root)
            data_window.title(f"Data from '{table_name}'")
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
    
    def view_table_structure(self, db_name, table_name):
        """View detailed table structure"""
        try:
            db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
            table_name = table_name.replace('📄 ', '').replace('📁 ', '').strip()
            
            config.current_db = db_name
            db.select_database(db_name)
            
            config.current_cursor.execute(f"DESCRIBE `{table_name}`")
            structure = config.current_cursor.fetchall()
            
            struct_window = tb.Toplevel(self.root)
            struct_window.title(f"Structure of '{table_name}'")
            struct_window.geometry("800x400")
            
            tree_frame = tb.Frame(struct_window)
            tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = tb.Scrollbar(tree_frame)
            scrollbar.pack(side=RIGHT, fill=Y)
            
            columns = ('Field', 'Type', 'Null', 'Key', 'Default', 'Extra')
            struct_tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show='headings',
                yscrollcommand=scrollbar.set
            )
            
            for col in columns:
                struct_tree.heading(col, text=col)
                struct_tree.column(col, width=120)
            
            for row in structure:
                struct_tree.insert('', 'end', values=row)
            
            struct_tree.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.config(command=struct_tree.yview)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view structure: {str(e)}")
    
    def insert_record_from_context(self, db_name, table_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        table_name = table_name.replace('📄 ', '').replace('📁 ', '').strip()
        
        config.current_db = db_name
        db.select_database(db_name)
        
        try:
            columns = operations.get_table_columns(table_name)
            
            if not columns:
                messagebox.showerror("Error", f"Could not get columns for table '{table_name}'")
                return
            
            # Create insert window
            insert_window = tb.Toplevel(self.root)
            insert_window.title(f"Insert Record into '{table_name}'")
            insert_window.geometry("500x600")
            
            main_frame = tb.Frame(insert_window, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            
            tb.Label(main_frame, text=f"Insert into '{table_name}'", 
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
                
                if operations.insert_record(table_name, values):
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
    
    def update_record_from_context(self, db_name, table_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        table_name = table_name.replace('📄 ', '').replace('📁 ', '').strip()
        
        config.current_db = db_name
        db.select_database(db_name)
        
        try:
            columns = operations.get_table_columns(table_name)
            
            update_window = tb.Toplevel(self.root)
            update_window.title(f"Update Records in '{table_name}'")
            update_window.geometry("600x500")
            
            main_frame = tb.Frame(update_window, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            
            tb.Label(main_frame, text=f"Update records in '{table_name}'",
                    font=("Segoe UI", 12, "bold")).pack(pady=10)
            
            # WHERE clause
            where_frame = tb.LabelFrame(main_frame, text="WHERE Condition", padding=10)
            where_frame.pack(fill=X, pady=10)
            
            tb.Label(where_frame, text="WHERE:").pack(side=LEFT, padx=5)
            where_entry = tb.Entry(where_frame, width=50)
            where_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
            
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
                
                if operations.update_record(table_name, updates, where):
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
    
    def delete_record_from_context(self, db_name, table_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        table_name = table_name.replace('📄 ', '').replace('📁 ', '').strip()
        
        config.current_db = db_name
        db.select_database(db_name)
        
        delete_window = tb.Toplevel(self.root)
        delete_window.title(f"Delete Records from '{table_name}'")
        delete_window.geometry("500x200")
        
        main_frame = tb.Frame(delete_window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        tb.Label(main_frame, text=f"Delete records from '{table_name}'",
                font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        where_frame = tb.Frame(main_frame)
        where_frame.pack(fill=X, pady=20)
        
        tb.Label(where_frame, text="WHERE:").pack(side=LEFT, padx=5)
        where_entry = tb.Entry(where_frame, width=40)
        where_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        
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
                if operations.delete_record(table_name, where):
                    messagebox.showinfo("Success", "Records deleted successfully!")
                    delete_window.destroy()
        
        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        tb.Button(btn_frame, text="Delete", command=do_delete,
                 bootstyle=DANGER, width=12).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancel", command=delete_window.destroy,
                 bootstyle=SECONDARY, width=12).pack(side=LEFT, padx=5)
    
    def truncate_table_from_context(self, db_name, table_name):
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        table_name = table_name.replace('📄 ', '').replace('📁 ', '').strip()
        
        config.current_db = db_name
        db.select_database(db_name)
        
        confirm = messagebox.askyesno(
            "Confirm", 
            f"Are you sure you want to TRUNCATE table '{table_name}'?\n\nThis will delete ALL records!"
        )
        
        if confirm:
            try:
                operations.truncate_table(table_name)
                messagebox.showinfo("Success", f"Table '{table_name}' truncated successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def drop_table_from_context(self, db_name, table_name):
        """Drop a table from context menu"""
        db_name = db_name.replace('📄 ', '').replace('📁 ', '').strip()
        table_name = table_name.replace('📄 ', '').replace('📁 ', '').strip()
        
        config.current_db = db_name
        db.select_database(db_name)
        
        confirm = messagebox.askyesno(
            "Confirm Drop", 
            f"Are you sure you want to DROP table '{table_name}'?\n\nThis action cannot be undone!"
        )
        
        if confirm:
            try:
                config.current_cursor.execute(f"DROP TABLE `{table_name}`")
                config.current_connection.commit()
                messagebox.showinfo("Success", f"Table '{table_name}' dropped successfully")
                # Refresh the tree
                self.load_tables(db_name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to drop table: {str(e)}")
    
    def on_tree_expand(self, event):
        """Handle treeview expansion event to load tables for a database"""
        item = self.tree.focus()
        if not item:
            return
            
        # Check if it's a database (has no parent)
        if self.tree.parent(item) == '':
            # Remove emoji if present
            db_name = item.replace('📁 ', '').strip()
            self.load_tables(db_name)
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
        """Handle double-click on tree items"""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
            
        parent = self.tree.parent(item)
        if parent:  # It's a table
            db_name = parent.replace('📁 ', '').strip()
            table_name = self.tree.item(item)['text'].replace('📄 ', '').strip()
            self.view_table_data_from_context(db_name, table_name)
    
    def show_context_menu(self, event):
        """Show right-click context menu for database/table"""
        # Select the item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Create context menu
            context_menu = Menu(self.root, tearoff=0)
            
            parent = self.tree.parent(item)
            
            if parent == '':  # It's a database
                # Extract database name (remove emoji if present)
                db_name = item.replace('📁 ', '').strip()
                context_menu.add_command(
                    label=f"👁️ Preview Database '{db_name}'",
                    command=lambda: self.preview_database(db_name)
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="📋 Show Tables",
                    command=lambda: self.show_tables_from_context(db_name)
                )
                context_menu.add_command(
                    label="➕ Create Table",
                    command=lambda: self.create_table_from_context(db_name)
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="💾 Backup Database",
                    command=lambda: self.backup_database_from_context(db_name)
                )
                context_menu.add_command(
                    label="📤 Export Database",
                    command=lambda: self.export_database_from_context(db_name)
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="🗑️ Drop Database",
                    command=lambda: self.drop_database_from_context(db_name)
                )
            else:  # It's a table
                # Extract table name (remove emoji if present)
                table_text = self.tree.item(item)['text']
                table_name = table_text.replace('📄 ', '').strip()
                # Extract database name (remove emoji if present)
                db_name = parent.replace('📁 ', '').strip()
                
                if table_name != 'Loading...' and table_name != 'No tables':
                    context_menu.add_command(
                        label=f"👁️ Preview Table '{table_name}'",
                        command=lambda: self.preview_table(db_name, table_name)
                    )
                    context_menu.add_separator()
                    context_menu.add_command(
                        label="📊 View All Data",
                        command=lambda: self.view_table_data_from_context(db_name, table_name)
                    )
                    context_menu.add_command(
                        label="🔍 View Structure",
                        command=lambda: self.view_table_structure(db_name, table_name)
                    )
                    context_menu.add_separator()
                    context_menu.add_command(
                        label="➕ Insert Record",
                        command=lambda: self.insert_record_from_context(db_name, table_name)
                    )
                    context_menu.add_command(
                        label="✏️ Update Records",
                        command=lambda: self.update_record_from_context(db_name, table_name)
                    )
                    context_menu.add_command(
                        label="🗑️ Delete Records",
                        command=lambda: self.delete_record_from_context(db_name, table_name)
                    )
                    context_menu.add_separator()
                    context_menu.add_command(
                        label="🗑️ Truncate Table",
                        command=lambda: self.truncate_table_from_context(db_name, table_name)
                    )
                    context_menu.add_command(
                        label="❌ Drop Table",
                        command=lambda: self.drop_table_from_context(db_name, table_name)
                    )
            
            # Display the menu - remove grab_release to make menu persistent
            context_menu.tk_popup(event.x_root, event.y_root)
            # Menu will stay open until user clicks elsewhere or selects an option
    
    def preview_database(self, db_name):
        """Preview database information in the main window"""
        try:
            # Set current database
            config.current_db = db_name
            db.select_database(db_name)
            
            # Close existing preview window if open
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            
            # Create preview panel
            self.preview_window = tb.LabelFrame(self.left_pane, text=f"Preview: {db_name}", padding=10)
            self.preview_window.pack(fill=BOTH, expand=False, pady=10)
            
            # Get database stats
            tables = db.list_tables(db_name)
            
            # Display info
            info_frame = tb.Frame(self.preview_window)
            info_frame.pack(fill=X, pady=5)
            
            tb.Label(info_frame, text=f"📊 Database: {db_name}", 
                    font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=2)
            tb.Label(info_frame, text=f"📋 Total Tables: {len(tables)}", 
                    font=("Segoe UI", 10)).pack(anchor=W, pady=2)
            
            if tables:
                tb.Label(info_frame, text="Tables:", 
                        font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(10, 2))
                
                # Create scrollable frame for tables
                canvas = tb.Canvas(info_frame, height=150)
                scrollbar = tb.Scrollbar(info_frame, orient=VERTICAL, command=canvas.yview)
                table_frame = tb.Frame(canvas)
                
                table_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=table_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                
                for table in tables:
                    tb.Label(table_frame, text=f"  • {table}").pack(anchor=W)
                
                canvas.pack(side=LEFT, fill=BOTH, expand=True)
                scrollbar.pack(side=RIGHT, fill=Y)
            
            # Close button
            tb.Button(self.preview_window, text="✖ Close Preview", 
                     command=self.close_preview,
                     bootstyle="secondary-outline").pack(pady=5)
                     
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview database: {str(e)}")
    
    def preview_table(self, db_name, table_name):
        """Preview table structure and sample data"""
        try:
            # Set current database
            config.current_db = db_name
            db.select_database(db_name)
            
            # Close existing preview window if open
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            
            # Create preview panel with fixed height
            self.preview_window = tb.LabelFrame(self.left_pane, 
                                             text=f"Preview: {db_name}.{table_name}", 
                                             padding=10)
            self.preview_window.pack(fill=BOTH, expand=True, pady=10)
            
            # Create a canvas and scrollbar for the entire preview
            canvas = tb.Canvas(self.preview_window)
            vsb = ttk.Scrollbar(self.preview_window, orient="vertical", command=canvas.yview)
            hsb = ttk.Scrollbar(self.preview_window, orient="horizontal", command=canvas.xview)
            
            # Create a frame inside the canvas to hold the content
            content_frame = ttk.Frame(canvas)
            
            # Configure the canvas scrolling
            canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            # Get table structure
            columns = operations.get_table_columns(table_name)
            
            # Get row count
            config.current_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            row_count = config.current_cursor.fetchone()[0]
            
            # Display info
            tb.Label(content_frame, text=f"📄 Table: {table_name}", 
                    font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=2)
            tb.Label(content_frame, text=f"📊 Total Rows: {row_count}", 
                    font=("Segoe UI", 10)).pack(anchor=W, pady=2)
            tb.Label(content_frame, text=f"📋 Columns: {len(columns)}", 
                    font=("Segoe UI", 10)).pack(anchor=W, pady=2)
            
            # Show structure
            tb.Label(content_frame, text="Structure:", 
                    font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(10, 5))
            
            struct_frame = tb.Frame(content_frame)
            struct_frame.pack(fill=BOTH, expand=True, pady=5)
            
            # Create tree for structure with scrollbars
            struct_container = tb.Frame(struct_frame)
            struct_container.pack(fill=BOTH, expand=True)
            
            struct_tree = ttk.Treeview(struct_container, columns=('Type',), 
                                     show='tree headings', height=min(5, len(columns)))
            
            # Add scrollbars to the structure tree
            struct_vsb = ttk.Scrollbar(struct_container, orient="vertical", command=struct_tree.yview)
            struct_hsb = ttk.Scrollbar(struct_container, orient="horizontal", command=struct_tree.xview)
            struct_tree.configure(yscrollcommand=struct_vsb.set, xscrollcommand=struct_hsb.set)
            
            # Grid layout for structure tree and scrollbars
            struct_tree.grid(row=0, column=0, sticky='nsew')
            struct_vsb.grid(row=0, column=1, sticky='ns')
            struct_hsb.grid(row=1, column=0, sticky='ew')
            
            # Configure grid weights
            struct_container.grid_rowconfigure(0, weight=1)
            struct_container.grid_columnconfigure(0, weight=1)
            
            struct_tree.heading('#0', text='Column')
            struct_tree.heading('Type', text='Type')
            struct_tree.column('#0', width=150, minwidth=100, stretch=True)
            struct_tree.column('Type', width=150, minwidth=100, stretch=True)
            
            for col_name, col_type in columns:
                struct_tree.insert('', 'end', text=col_name, values=(col_type,))
            
            # Show sample data
            if row_count > 0:
                tb.Label(content_frame, text="Sample Data (First 5 rows):", 
                        font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(10, 5))
                
                # Create a container for the data tree with scrollbars
                data_container = tb.Frame(content_frame)
                data_container.pack(fill=BOTH, expand=True, pady=5)
                
                # Get sample data
                config.current_cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5")
                sample_data = config.current_cursor.fetchall()
                col_names = [desc[0] for desc in config.current_cursor.description]
                
                # Create tree for sample data with scrollbars
                data_tree = ttk.Treeview(data_container, columns=col_names, 
                                       show='headings', height=min(5, len(sample_data)))
                
                # Add scrollbars to the data tree
                data_vsb = ttk.Scrollbar(data_container, orient="vertical", command=data_tree.yview)
                data_hsb = ttk.Scrollbar(data_container, orient="horizontal", command=data_tree.xview)
                data_tree.configure(yscrollcommand=data_vsb.set, xscrollcommand=data_hsb.set)
                
                # Configure columns
                for col in col_names:
                    data_tree.heading(col, text=col)
                    data_tree.column(col, width=100, minwidth=50, stretch=True)
                
                # Insert sample data
                for row in sample_data:
                    data_tree.insert('', 'end', values=row)
                
                # Grid layout for data tree and scrollbars
                data_tree.grid(row=0, column=0, sticky='nsew')
                data_vsb.grid(row=0, column=1, sticky='ns')
                data_hsb.grid(row=1, column=0, sticky='ew')
                
                # Configure grid weights
                data_container.grid_rowconfigure(0, weight=1)
                data_container.grid_columnconfigure(0, weight=1)
            
            # Close button
            btn_frame = tb.Frame(content_frame)
            btn_frame.pack(fill=X, pady=5)
            
            tb.Button(btn_frame, text="✖ Close Preview", 
                     command=self.close_preview,
                     bootstyle="secondary-outline").pack(side=RIGHT)
            
            # Create a window in the canvas for the content frame
            canvas.create_window((0, 0), window=content_frame, anchor="nw")
            
            # Pack the canvas and scrollbars
            vsb.pack(side=RIGHT, fill=Y)
            hsb.pack(side=BOTTOM, fill=X)
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            
            # Update the scrollregion when the content changes size
            def update_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                
            content_frame.bind('<Configure>', update_scroll_region)
            
            # Enable mousewheel scrolling
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Update the canvas scroll region after everything is drawn
            self.root.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
                     
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview table: {str(e)}")
    
    def close_preview(self):
        """Close the preview panel"""
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
            self.preview_window = None
    
    # Context menu helper methods
    def show_tables_from_context(self, db_name):
        config.current_db = db_name
        self.show_tables()
    
    def create_table_from_context(self, db_name):
        config.current_db = db_name
        self.create_table()
    
    def backup_database_from_context(self, db_name):
        config.current_db = db_name
        self.backup_current_db()
    
    def export_database_from_context(self, db_name):
        config.current_db = db_name
        self.export_database()
    
    def drop_database_from_context(self, db_name):
        config.current_db = db_name
        self.drop_database()
    
    def view_table_data_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        
        try:
            data, columns = operations.view_table_data(table_name)
            
            if not data:
                messagebox.showinfo("No Data", f"Table '{table_name}' has no records")
                return
            
            # Create window to display data
            data_window = tb.Toplevel(self.root)
            data_window.title(f"Data from '{table_name}'")
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
    
    def view_table_structure(self, db_name, table_name):
        """View detailed table structure"""
        try:
            config.current_db = db_name
            db.select_database(db_name)
            
            config.current_cursor.execute(f"DESCRIBE `{table_name}`")
            structure = config.current_cursor.fetchall()
            
            struct_window = tb.Toplevel(self.root)
            struct_window.title(f"Structure of '{table_name}'")
            struct_window.geometry("800x400")
            
            tree_frame = tb.Frame(struct_window)
            tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = tb.Scrollbar(tree_frame)
            scrollbar.pack(side=RIGHT, fill=Y)
            
            columns = ('Field', 'Type', 'Null', 'Key', 'Default', 'Extra')
            struct_tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show='headings',
                yscrollcommand=scrollbar.set
            )
            
            for col in columns:
                struct_tree.heading(col, text=col)
                struct_tree.column(col, width=120)
            
            for row in structure:
                struct_tree.insert('', 'end', values=row)
            
            struct_tree.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.config(command=struct_tree.yview)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view structure: {str(e)}")
    
    def insert_record_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        
        try:
            columns = operations.get_table_columns(table_name)
            
            if not columns:
                messagebox.showerror("Error", f"Could not get columns for table '{table_name}'")
                return
            
            # Create insert window
            insert_window = tb.Toplevel(self.root)
            insert_window.title(f"Insert Record into '{table_name}'")
            insert_window.geometry("500x600")
            
            main_frame = tb.Frame(insert_window, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            
            tb.Label(main_frame, text=f"Insert into '{table_name}'", 
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
                
                if operations.insert_record(table_name, values):
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
    
    def update_record_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        
        try:
            columns = operations.get_table_columns(table_name)
            
            update_window = tb.Toplevel(self.root)
            update_window.title(f"Update Records in '{table_name}'")
            update_window.geometry("600x500")
            
            main_frame = tb.Frame(update_window, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            
            tb.Label(main_frame, text=f"Update records in '{table_name}'",
                    font=("Segoe UI", 12, "bold")).pack(pady=10)
            
            # WHERE clause
            where_frame = tb.LabelFrame(main_frame, text="WHERE Condition", padding=10)
            where_frame.pack(fill=X, pady=10)
            
            tb.Label(where_frame, text="WHERE:").pack(side=LEFT, padx=5)
            where_entry = tb.Entry(where_frame, width=50)
            where_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
            
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
                
                if operations.update_record(table_name, updates, where):
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
    
    def delete_record_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        
        delete_window = tb.Toplevel(self.root)
        delete_window.title(f"Delete Records from '{table_name}'")
        delete_window.geometry("500x200")
        
        main_frame = tb.Frame(delete_window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        tb.Label(main_frame, text=f"Delete records from '{table_name}'",
                font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        where_frame = tb.Frame(main_frame)
        where_frame.pack(fill=X, pady=20)
        
        tb.Label(where_frame, text="WHERE:").pack(side=LEFT, padx=5)
        where_entry = tb.Entry(where_frame, width=40)
        where_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        
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
                if operations.delete_record(table_name, where):
                    messagebox.showinfo("Success", "Records deleted successfully!")
                    delete_window.destroy()
        
        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        tb.Button(btn_frame, text="Delete", command=do_delete,
                 bootstyle=DANGER, width=12).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancel", command=delete_window.destroy,
                 bootstyle=SECONDARY, width=12).pack(side=LEFT, padx=5)
    
    def truncate_table_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        
        confirm = messagebox.askyesno(
            "Confirm", 
            f"Are you sure you want to TRUNCATE table '{table_name}'?\n\nThis will delete ALL records!"
        )
        
        if confirm:
            try:
                operations.truncate_table(table_name)
                messagebox.showinfo("Success", f"Table '{table_name}' truncated successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def drop_table_from_context(self, db_name, table_name):
        """Drop a table from context menu"""
        config.current_db = db_name
        db.select_database(db_name)
        
        confirm = messagebox.askyesno(
            "Confirm Drop", 
            f"Are you sure you want to DROP table '{table_name}'?\n\nThis action cannot be undone!"
        )
        
        if confirm:
            try:
                config.current_cursor.execute(f"DROP TABLE `{table_name}`")
                config.current_connection.commit()
                messagebox.showinfo("Success", f"Table '{table_name}' dropped successfully")
                # Refresh the tree
                self.load_tables(db_name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to drop table: {str(e)}")
    
    def load_tables(self, db_name):
        """Load tables for a specific database"""
        try:
            # Find the database item in the tree
            db_item = None
            for item in self.tree.get_children():
                if self.tree.item(item, 'text') == db_name:
                    db_item = item
                    break
            
            if not db_item:
                messagebox.showerror("Error", f"Database '{db_name}' not found in tree")
                return
            
            # Clear existing children (including any 'Loading...' placeholder)
            for child in self.tree.get_children(db_item):
                self.tree.delete(child)
            
            # Get tables
            tables = db.list_tables(db_name)
            
            if not tables:
                self.tree.insert(db_item, 'end', text='No tables')
            else:
                for table in tables:
                    self.tree.insert(db_item, 'end', text=table)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tables: {str(e)}")
            # Re-insert loading message on error
            if 'db_item' in locals() and db_item:
                self.tree.insert(db_item, 'end', text='Error loading tables')
    
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
        
        tb.Button(btn_frame, text="Delete", command=do_delete, bootstyle="danger").pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancel", command=delete_window.destroy, bootstyle="secondary").pack(side=LEFT, padx=5)
    def show_context_menu(self, event):
        """Show right-click context menu for database/table"""
        # Select the item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Create context menu with tearoff=0 to prevent it from being torn off
            context_menu = Menu(self.root, tearoff=0)
            
            parent = self.tree.parent(item)
            
            if parent == '':  # It's a database
                # Extract database name (remove emoji if present)
                db_name = self.strip_emojis(item)
                context_menu.add_command(
                    label=f"👁️ Preview Database '{db_name}'",
                    command=lambda: self.preview_database(db_name)
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="📋 Show Tables",
                    command=lambda: self.show_tables_from_context(db_name)
                )
                context_menu.add_command(
                    label="➕ Create Table",
                    command=lambda: self.create_table_from_context(db_name)
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="💾 Backup Database",
                    command=lambda: self.backup_database_from_context(db_name)
                )
                context_menu.add_command(
                    label="📤 Export Database",
                    command=lambda: self.export_database_from_context(db_name)
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="🗑️ Drop Database",
                    command=lambda: self.drop_database_from_context(db_name)
                )
            else:  # It's a table
                # Extract table name (remove emoji if present)
                table_text = self.tree.item(item)['text']
                table_name = self.strip_emojis(table_text)
                # Extract database name (remove emoji if present)
                db_name = self.strip_emojis(parent)
                
                if table_name not in ['Loading...', 'No tables']:
                    context_menu.add_command(
                        label=f"👁️ Preview Table '{table_name}'",
                        command=lambda: self.preview_table(db_name, table_name)
                    )
                    context_menu.add_separator()
                    context_menu.add_command(
                        label="📊 View All Data",
                        command=lambda: self.view_table_data_from_context(db_name, table_name)
                    )
                    context_menu.add_command(
                        label="🔍 View Structure",
                        command=lambda: self.view_table_structure(db_name, table_name)
                    )
                    context_menu.add_separator()
                    context_menu.add_command(
                        label="➕ Insert Record",
                        command=lambda: self.insert_record_from_context(db_name, table_name)
                    )
                    context_menu.add_command(
                        label="✏️ Update Records",
                        command=lambda: self.update_record_from_context(db_name, table_name)
                    )
                    context_menu.add_command(
                        label="🗑️ Delete Records",
                        command=lambda: self.delete_record_from_context(db_name, table_name)
                    )
                    context_menu.add_separator()
                    context_menu.add_command(
                        label="🗑️ Truncate Table",
                        command=lambda: self.truncate_table_from_context(db_name, table_name)
                    )
                    context_menu.add_command(
                        label="❌ Drop Table",
                        command=lambda: self.drop_table_from_context(db_name, table_name)
                    )
            
            # Display the menu - REMOVED finally block that was calling grab_release
            context_menu.tk_popup(event.x_root, event.y_root)
            # Menu will stay open until user clicks elsewhere or selects an option

    def strip_emojis(self, text):
        """Remove emojis and extra whitespace from text"""
        import re
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub('', text).strip()

    def preview_database(self, db_name):
        """Preview database information in the main window"""
        try:
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            self.preview_window = tb.LabelFrame(self.left_pane, text=f"Preview: {db_name}", padding=10)
            self.preview_window.pack(fill=BOTH, expand=False, pady=10)
            tables = db.list_tables(db_name)
            info_frame = tb.Frame(self.preview_window)
            info_frame.pack(fill=X, pady=5)
            tb.Label(info_frame, text=f"Database: {db_name}", font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=2)
            tb.Label(info_frame, text=f"Total Tables: {len(tables)}", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
            if tables:
                tb.Label(info_frame, text="Tables:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(10, 2))
                canvas = tb.Canvas(info_frame, height=150)
                scrollbar = tb.Scrollbar(info_frame, orient=VERTICAL, command=canvas.yview)
                table_frame = tb.Frame(canvas)
                table_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                canvas.create_window((0, 0), window=table_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                for table in tables:
                    tb.Label(table_frame, text=f"  {table}").pack(anchor=W)
                canvas.pack(side=LEFT, fill=BOTH, expand=True)
                scrollbar.pack(side=RIGHT, fill=Y)
            tb.Button(self.preview_window, text="Close Preview", command=self.close_preview, bootstyle="secondary-outline").pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview database: {str(e)}")

    def preview_table(self, db_name, table_name):
        """Preview table structure and sample data"""
        try:
            # Clean names
            display_table_name = self.strip_emojis(table_name)
            db_name = self.strip_emojis(db_name)
            
            # Set current database
            config.current_db = db_name
            if not db.select_database(db_name):
                raise Exception(f"Failed to select database: {db_name}")
            
            # Close existing preview window if open
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            
            # Create preview panel
            self.preview_window = tb.LabelFrame(
                self.left_pane, 
                text=f"Preview: {db_name}.{display_table_name}", 
                padding=10
            )
            self.preview_window.pack(fill=BOTH, expand=False, pady=10)
            
            # Create main container with fixed height
            main_container = tb.Frame(self.preview_window)
            main_container.pack(fill=BOTH, expand=True)
            
            # Create canvas for scrolling entire preview
            preview_canvas = tb.Canvas(main_container, height=400)
            preview_scrollbar = tb.Scrollbar(main_container, orient=VERTICAL, command=preview_canvas.yview)
            preview_content = tb.Frame(preview_canvas)
            
            preview_canvas.configure(yscrollcommand=preview_scrollbar.set)
            
            # Get table info
            columns = operations.get_table_columns(table_name)
            config.current_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            row_count_result = config.current_cursor.fetchone()
            row_count = row_count_result[0] if row_count_result else 0
            
            # Display info
            tb.Label(preview_content, text=f"📄 Table: {table_name}", 
                    font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=2)
            tb.Label(preview_content, text=f"📊 Total Rows: {row_count}", 
                    font=("Segoe UI", 10)).pack(anchor=W, pady=2)
            tb.Label(preview_content, text=f"📋 Columns: {len(columns)}", 
                    font=("Segoe UI", 10)).pack(anchor=W, pady=2)
            
            # Show structure
            tb.Label(preview_content, text="Structure:", 
                    font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(10, 5))
            
            struct_frame = tb.Frame(preview_content)
            struct_frame.pack(fill=X, pady=5)
            
            # Get full column info
            config.current_cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
            full_columns = config.current_cursor.fetchall()
            
            # Create tree for structure
            struct_tree = ttk.Treeview(
                struct_frame, 
                columns=('Type', 'Null', 'Key', 'Default'), 
                show='tree headings', 
                height=min(8, len(full_columns))
            )
            
            struct_tree.heading('#0', text='Column')
            struct_tree.heading('Type', text='Type')
            struct_tree.heading('Null', text='Null')
            struct_tree.heading('Key', text='Key')
            struct_tree.heading('Default', text='Default')
            
            struct_tree.column('#0', width=120)
            struct_tree.column('Type', width=100)
            struct_tree.column('Null', width=50)
            struct_tree.column('Key', width=50)
            struct_tree.column('Default', width=80)
            
            for col in full_columns:
                col_name = col[0]
                col_type = col[1]
                is_null = col[2]
                col_key = col[3] if col[3] else ''
                col_default = str(col[4]) if col[4] is not None else 'NULL'
                
                struct_tree.insert('', 'end', text=col_name, 
                                 values=(col_type, is_null, col_key, col_default))
            
            struct_tree.pack(fill=X)
            
            # Show sample data with scrollbars
            if row_count > 0:
                tb.Label(preview_content, 
                        text=f"Sample Data (First {min(5, row_count)} rows):", 
                        font=("Segoe UI", 10, "bold")
                       ).pack(anchor=W, pady=(15, 5))
                
                # Create frame for data with both scrollbars
                data_outer_frame = tb.Frame(preview_content)
                data_outer_frame.pack(fill=BOTH, expand=True, pady=5)
                
                try:
                    config.current_cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5")
                    sample_data = config.current_cursor.fetchall()
                    col_names = [desc[0] for desc in config.current_cursor.description]
                    
                    # Create Treeview with both scrollbars
                    data_tree = ttk.Treeview(
                        data_outer_frame, 
                        columns=col_names, 
                        show="headings", 
                        height=6  # Fixed height to show ~5 rows
                    )
                    
                    # Configure columns
                    for col in col_names:
                        data_tree.heading(col, text=col)
                        data_tree.column(col, width=120, minwidth=80)
                    
                    # Insert data
                    for row in sample_data:
                        data_tree.insert('', 'end', values=row)
                    
                    # Add scrollbars
                    v_scroll = tb.Scrollbar(data_outer_frame, orient=VERTICAL, command=data_tree.yview)
                    h_scroll = tb.Scrollbar(data_outer_frame, orient=HORIZONTAL, command=data_tree.xview)
                    data_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
                    
                    # Grid layout for proper scrollbar positioning
                    data_tree.grid(row=0, column=0, sticky='nsew')
                    v_scroll.grid(row=0, column=1, sticky='ns')
                    h_scroll.grid(row=1, column=0, sticky='ew')
                    
                    # Configure grid weights
                    data_outer_frame.grid_rowconfigure(0, weight=1)
                    data_outer_frame.grid_columnconfigure(0, weight=1)
                    
                except Exception as data_err:
                    tb.Label(preview_content, 
                            text=f"Error loading sample data: {str(data_err)}", 
                            bootstyle="danger").pack(pady=10)
            
            # Buttons at bottom
            btn_frame = tb.Frame(preview_content)
            btn_frame.pack(fill=X, pady=(15, 5))
            
            tb.Button(btn_frame, text="📊 View Full Table", 
                     command=lambda: self.view_table_data_from_context(db_name, table_name),
                     bootstyle="primary-outline"
                    ).pack(side=LEFT, padx=5)
            
            tb.Button(btn_frame, text="✖ Close Preview", 
                     command=self.close_preview, 
                     bootstyle="secondary-outline"
                    ).pack(side=RIGHT, padx=5)
            
            # Pack canvas and scrollbar
            preview_canvas.create_window((0, 0), window=preview_content, anchor="nw")
            preview_scrollbar.pack(side=RIGHT, fill=Y)
            preview_canvas.pack(side=LEFT, fill=BOTH, expand=True)
            
            # Update scroll region
            def update_scroll_region(event=None):
                preview_canvas.configure(scrollregion=preview_canvas.bbox("all"))
            
            preview_content.bind('<Configure>', update_scroll_region)
            
            # Enable mousewheel scrolling
            def on_mousewheel(event):
                preview_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            preview_canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Initial scroll region update
            self.root.update_idletasks()
            preview_canvas.config(scrollregion=preview_canvas.bbox("all"))
            if not db.select_database(db_name):
                raise Exception(f"Failed to select database: {db_name}")
            
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            
            self.preview_window = tb.LabelFrame(
                self.left_pane, 
                text=f"Preview: {db_name}.{display_table_name}", 
                padding=10
            )
            self.preview_window.pack(fill=BOTH, expand=False, pady=10)
            
            # Use table_name encoded in utf8mb4 for SQL queries to avoid invalid character errors
            encoded_table_name = table_name.encode('utf-8').decode('utf-8')
            
            try:
                columns = operations.get_table_columns(encoded_table_name)
                config.current_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                row_count_result = config.current_cursor.fetchone()
                row_count = row_count_result[0] if row_count_result else 0
                
                tb.Label(self.preview_window, text=f"Table: {table_name}", 
                        font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=2)
                tb.Label(self.preview_window, text=f"Total Rows: {row_count}", 
                        font=("Segoe UI", 10)).pack(anchor=W, pady=2)
                tb.Label(self.preview_window, text=f"Columns: {len(columns)}", 
                        font=("Segoe UI", 10)).pack(anchor=W, pady=2)
                
                tb.Label(self.preview_window, text="Structure:", 
                        font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(10, 5))
                
                struct_frame = tb.Frame(self.preview_window)
                struct_frame.pack(fill=BOTH, expand=True, pady=5)
                
                struct_tree = ttk.Treeview(
                    struct_frame, 
                    columns=("Type", "Null", "Key", "Default", "Extra"), 
                    show="headings", 
                    height=min(10, len(columns) + 1)
                )
                
                struct_tree.heading("#0", text="Column")
                struct_tree.heading("Type", text="Type")
                struct_tree.heading("Null", text="Null")
                struct_tree.heading("Key", text="Key")
                struct_tree.heading("Default", text="Default")
                struct_tree.heading("Extra", text="Extra")
                
                struct_tree.column("#0", width=150, anchor=W)
                struct_tree.column("Type", width=100, anchor=W)
                struct_tree.column("Null", width=50, anchor=CENTER)
                struct_tree.column("Key", width=50, anchor=CENTER)
                struct_tree.column("Default", width=100, anchor=W)
                struct_tree.column("Extra", width=100, anchor=W)
                
                config.current_cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
                for col in config.current_cursor.fetchall():
                    col_name = col[0]
                    col_type = col[1]
                    is_null = 'YES' if col[2] == 'YES' else 'NO'
                    col_key = col[3] if col[3] else ''
                    col_default = str(col[4]) if col[4] is not None else 'NULL'
                    col_extra = col[5] if col[5] else ''
                    
                    struct_tree.insert(
                        "", "end", 
                        text=col_name,
                        values=(col_type, is_null, col_key, col_default, col_extra)
                    )
                
                struct_tree.pack(fill=BOTH, expand=True)
                
                h_scroll = tb.Scrollbar(struct_frame, orient=HORIZONTAL, command=struct_tree.xview)
                struct_tree.configure(xscrollcommand=h_scroll.set)
                h_scroll.pack(fill=X)
                
                if row_count > 0:
                    tb.Label(self.preview_window, 
                            text=f"Sample Data (First {min(5, row_count)} rows):", 
                            font=("Segoe UI", 10, "bold")
                           ).pack(anchor=W, pady=(15, 5))
                    
                    data_frame = tb.Frame(self.preview_window)
                    data_frame.pack(fill=BOTH, expand=True, pady=5)
                    
                    try:
                        config.current_cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5")
                        sample_data = config.current_cursor.fetchall()
                        col_names = [desc[0] for desc in config.current_cursor.description]
                        
                        data_tree = ttk.Treeview(
                            data_frame, 
                            columns=col_names, 
                            show="headings", 
                            height=min(6, len(sample_data) + 1)
                        )
                        
                        for col in col_names:
                            data_tree.heading(col, text=col)
                            data_tree.column(col, width=100)
                        
                        for row in sample_data:
                            data_tree.insert('', 'end', values=row)
                        
                        data_tree.pack(fill=BOTH, expand=True)
                        
                        v_scroll = tb.Scrollbar(data_frame, orient=VERTICAL, command=data_tree.yview)
                        h_scroll = tb.Scrollbar(data_frame, orient=HORIZONTAL, command=data_tree.xview)
                        data_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
                        
                        v_scroll.pack(side=RIGHT, fill=Y)
                        h_scroll.pack(side=BOTTOM, fill=X)
                        
                    except Exception as data_err:
                        error_msg = f"Error loading sample data: {str(data_err)}"
                        print(error_msg)
                        tb.Label(self.preview_window, text=error_msg, bootstyle="danger").pack(pady=10)
                
                btn_frame = tb.Frame(self.preview_window)
                btn_frame.pack(fill=X, pady=(15, 5))
                
                tb.Button(btn_frame, text="View Full Table", 
                         command=lambda: self.view_table_data_from_context(db_name, table_name),
                         bootstyle="primary-outline"
                        ).pack(side=LEFT, padx=5)
                
                tb.Button(btn_frame, text="Close Preview", 
                         command=self.close_preview, 
                         bootstyle="secondary-outline"
                        ).pack(side=RIGHT, padx=5)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to preview table '{table_name}': {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview table: {str(e)}")
    
    def close_preview(self):
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
            self.preview_window = None

    def show_tables_from_context(self, db_name):
        config.current_db = db_name
        self.show_tables()

    def create_table_from_context(self, db_name):
        config.current_db = db_name
        self.create_table()

    def backup_database_from_context(self, db_name):
        config.current_db = db_name
        self.backup_current_db()

    def export_database_from_context(self, db_name):
        config.current_db = db_name
        self.export_database()

    def drop_database_from_context(self, db_name):
        config.current_db = db_name
        self.drop_database()

    def view_table_data_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        try:
            data, columns = operations.view_table_data(table_name)
            if not data:
                messagebox.showinfo("No Data", f"Table '{table_name}' has no records")
                return
            data_window = tb.Toplevel(self.root)
            data_window.title(f"Data from '{table_name}'")
            data_window.geometry("900x500")
            tree_frame = tb.Frame(data_window)
            tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            tree_scroll = tb.Scrollbar(tree_frame)
            tree_scroll.pack(side=RIGHT, fill=Y)
            data_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=tree_scroll.set)
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

    def view_table_structure(self, db_name, table_name):
        try:
            config.current_db = db_name
            db.select_database(db_name)
            config.current_cursor.execute(f"DESCRIBE `{table_name}`")
            structure = config.current_cursor.fetchall()
            struct_window = tb.Toplevel(self.root)
            struct_window.title(f"Structure of '{table_name}'")
            struct_window.geometry("800x400")
            tree_frame = tb.Frame(struct_window)
            tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            scrollbar = tb.Scrollbar(tree_frame)
            scrollbar.pack(side=RIGHT, fill=Y)
            columns = ('Field', 'Type', 'Null', 'Key', 'Default', 'Extra')
            struct_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
            for col in columns:
                struct_tree.heading(col, text=col)
                struct_tree.column(col, width=120)
            for row in structure:
                struct_tree.insert('', 'end', values=row)
            struct_tree.pack(fill=BOTH, expand=True)
            scrollbar.config(command=struct_tree.yview)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view structure: {str(e)}")

    def insert_record_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        try:
            columns = operations.get_table_columns(table_name)
            if not columns:
                messagebox.showerror("Error", f"Could not get columns for table '{table_name}'")
                return
            insert_window = tb.Toplevel(self.root)
            insert_window.title(f"Insert Record into '{table_name}'")
            insert_window.geometry("500x600")
            main_frame = tb.Frame(insert_window, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            tb.Label(main_frame, text=f"Insert into '{table_name}'", font=("Segoe UI", 12, "bold")).pack(pady=10)
            canvas = tb.Canvas(main_frame)
            scrollbar = tb.Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
            scrollable_frame = tb.Frame(canvas)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=RIGHT, fill=Y)
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            entries = {}
            for col_name, col_type in columns:
                field_frame = tb.Frame(scrollable_frame)
                field_frame.pack(fill=X, pady=5, padx=10)
                tb.Label(field_frame, text=f"{col_name} ({col_type}):", width=20, anchor=W).pack(side=LEFT, padx=5)
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
                if operations.insert_record(table_name, values):
                    messagebox.showinfo("Success", "Record inserted successfully!")
                    insert_window.destroy()
            btn_frame = tb.Frame(main_frame)
            btn_frame.pack(pady=10)
            tb.Button(btn_frame, text="Insert", command=do_insert, bootstyle=SUCCESS, width=12).pack(side=LEFT, padx=5)
            tb.Button(btn_frame, text="Cancel", command=insert_window.destroy, bootstyle=DANGER, width=12).pack(side=LEFT, padx=5)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_record_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        try:
            columns = operations.get_table_columns(table_name)
            update_window = tb.Toplevel(self.root)
            update_window.title(f"Update Records in '{table_name}'")
            update_window.geometry("600x500")
            main_frame = tb.Frame(update_window, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            tb.Label(main_frame, text=f"Update records in '{table_name}'", font=("Segoe UI", 12, "bold")).pack(pady=10)
            where_frame = tb.LabelFrame(main_frame, text="WHERE Condition", padding=10)
            where_frame.pack(fill=X, pady=10)
            tb.Label(where_frame, text="WHERE:").pack(side=LEFT, padx=5)
            where_entry = tb.Entry(where_frame, width=50)
            where_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
            set_frame = tb.LabelFrame(main_frame, text="SET Values", padding=10)
            set_frame.pack(fill=BOTH, expand=True, pady=10)
            canvas = tb.Canvas(set_frame)
            scrollbar = tb.Scrollbar(set_frame, orient=VERTICAL, command=canvas.yview)
            scrollable_frame = tb.Frame(canvas)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=RIGHT, fill=Y)
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            entries = {}
            for col_name, col_type in columns:
                field_frame = tb.Frame(scrollable_frame)
                field_frame.pack(fill=X, pady=3, padx=10)
                tb.Label(field_frame, text=f"{col_name}:", width=20, anchor=W).pack(side=LEFT, padx=5)
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
                if operations.update_record(table_name, updates, where):
                    messagebox.showinfo("Success", "Records updated successfully!")
                    update_window.destroy()
            btn_frame = tb.Frame(main_frame)
            btn_frame.pack(pady=10)
            tb.Button(btn_frame, text="Update", command=do_update, bootstyle=SUCCESS, width=12).pack(side=LEFT, padx=5)
            tb.Button(btn_frame, text="Cancel", command=update_window.destroy, bootstyle=DANGER, width=12).pack(side=LEFT, padx=5)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_record_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        delete_window = tb.Toplevel(self.root)
        delete_window.title(f"Delete Records from '{table_name}'")
        delete_window.geometry("500x200")
        main_frame = tb.Frame(delete_window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        tb.Label(main_frame, text=f"Delete records from '{table_name}'", font=("Segoe UI", 12, "bold")).pack(pady=10)
        where_frame = tb.Frame(main_frame)
        where_frame.pack(fill=X, pady=20)
        tb.Label(where_frame, text="WHERE:").pack(side=LEFT, padx=5)
        where_entry = tb.Entry(where_frame, width=40)
        where_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        def do_delete():
            where = where_entry.get().strip()
            if not where:
                messagebox.showwarning("Warning", "Please enter a WHERE condition")
                return
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete records WHERE {where}?")
            if confirm:
                if operations.delete_record(table_name, where):
                    messagebox.showinfo("Success", "Records deleted successfully!")
                    delete_window.destroy()
        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(pady=10)
        tb.Button(btn_frame, text="Delete", command=do_delete, bootstyle=DANGER, width=12).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancel", command=delete_window.destroy, bootstyle=SECONDARY, width=12).pack(side=LEFT, padx=5)
    def truncate_table_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to TRUNCATE table '{table_name}'?\n\nThis will delete ALL records!")
        if confirm:
            try:
                operations.truncate_table(table_name)
                messagebox.showinfo("Success", f"Table '{table_name}' truncated successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    def drop_table_from_context(self, db_name, table_name):
        config.current_db = db_name
        db.select_database(db_name)
        confirm = messagebox.askyesno("Confirm Drop", f"Are you sure you want to DROP table '{table_name}'?\n\nThis action cannot be undone!")
        if confirm:
            try:
                config.current_cursor.execute(f"DROP TABLE `{table_name}`")
                config.current_connection.commit()
                messagebox.showinfo("Success", f"Table '{table_name}' dropped successfully")
                self.load_tables(db_name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to drop table: {str(e)}")

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = MySQLNavigator(root)
    root.mainloop()