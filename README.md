# MySQL Navigator

A modern, user-friendly GUI application for managing MySQL databases, built with Python and ttkbootstrap.

![MySQL Navigator Screenshot](screenshot.png)

## ✨ Features

- **Modern Dark/Light Theme** - Clean, responsive interface with theme support
- **Database Management** - View, create, and manage databases
- **Table Operations** - Browse tables, view data, and execute custom queries
- **Data Import/Export** - Easily backup and restore your databases
- **User-Friendly Interface** - Intuitive layout with easy navigation
- **Cross-Platform** - Works on Windows, macOS, and Linux

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mysql-navigator.git
   cd mysql-navigator
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Configuration

## 🔌 Connection Setup

### Option 1: Using Default Root User (Not Recommended for Production)
1. Ensure your MySQL server is running
2. Use the following credentials in the application:
   - Host: `localhost`
   - Port: `3306` (default)
   - User: `root`
   - Password: [your root password]

### Option 2: Create a New Database User (Recommended)
1. Access MySQL as root:
   ```bash
   sudo mysql
   ```
2. Create a new user (replace 'your_password' with a strong password):
   ```sql
   CREATE USER 'dbuser'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON *.* TO 'dbuser'@'localhost' WITH GRANT OPTION;
   FLUSH PRIVILEGES;
   EXIT;
   ```
3. Use these credentials in the application:
   - Host: `localhost`
   - Port: `3306`
   - User: `dbuser`
   - Password: `your_password`

### Option 3: Using Environment Variables
Create a `.env` file in the project root with your MySQL credentials:
```
   DB_HOST=localhost
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

## 🚦 Usage

1. **Start the application**
   ```bash
   # Activate virtual environment first (if created)
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate  # Windows
   
   # Run the application
   python app.py
   ```

2. **Connection Troubleshooting**
   - If you get "Access denied" errors:
     - Verify your username and password
     - Ensure the user has proper privileges
     - Try connecting with `sudo` if using root
   - If MySQL server is not running:
     ```bash
     # On Linux
     sudo systemctl start mysql
     
     # On macOS (using Homebrew)
     brew services start mysql
     
     # On Windows
     net start mysql
     ```
   - If you can't create users:
     - Try logging in as root: `sudo mysql -u root`
     - Check existing users: `SELECT user, host FROM mysql.user;`
     - Drop problematic users: `DROP USER 'username'@'localhost';`

2. **Connect to your MySQL server**
   - Enter your MySQL credentials
   - Click "Connect"

3. **Navigate the interface**
   - Left sidebar: Database and table navigation
   - Main panel: Query results and table data
   - Toolbar: Common actions and settings

## 🧩 Features in Detail

### Database Operations
- View all databases
- Create new databases
- Drop existing databases
- Set default database

### Table Operations
- Browse table schemas
- View and edit table data
- Execute custom SQL queries
- Import/export table data

### Data Management
- Insert new records
- Update existing records
- Delete records
- Truncate tables

## 📦 Dependencies

- `ttkbootstrap` - Modern themed widgets for Tkinter
- `mysql-connector-python` - MySQL database connector
- `python-dotenv` - Environment variable management

### Installation
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install manually
pip install ttkbootstrap mysql-connector-python python-dotenv
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

Daniel Chege - [Your Email]

Project Link: [https://github.com/yourusername/mysql-navigator](https://github.com/yourusername/mysql-navigator)
