# test_connection.py
import db
import config

def test_connection():
    host = input("Enter MySQL host (default: localhost): ") or "localhost"
    port = input("Enter MySQL port (default: 3306): ") or "3306"
    user = input("Enter MySQL username: ")
    password = input("Enter MySQL password: ")
    
    try:
        port = int(port)
    except ValueError:
        print("Port must be a number. Using default 3306")
        port = 3306
    
    success, message = db.connect(host, user, password, port)
    print(f"\nConnection {'successful' if success else 'failed'}: {message}")
    
    if success:
        try:
            dbs = db.list_databases()
            print("\nAvailable databases:")
            for db_name in dbs:
                print(f"- {db_name}")
        except Exception as e:
            print(f"Error listing databases: {e}")
        finally:
            if config.current_connection and config.current_connection.is_connected():
                config.current_connection.close()
                print("\nConnection closed.")

if __name__ == "__main__":
    test_connection()