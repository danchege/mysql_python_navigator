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

1. Create a `.env` file in the project root with your MySQL credentials:
   ```
   DB_HOST=localhost
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

## 🚦 Usage

1. **Start the application**
   ```bash
   python app.py
   ```

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

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

Daniel Chege - [Your Email]

Project Link: [https://github.com/yourusername/mysql-navigator](https://github.com/yourusername/mysql-navigator)
