import psycopg2
from dbconf import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT

def connect_db():
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        print("Database connection established.")
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def create_table_if_not_exists(conn):
    try:
        # Create a cursor object
        cursor = conn.cursor()
        # SQL statement to create a table if it does not exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS db_metrics_tryton (
            id SERIAL PRIMARY KEY,
            transaction_status BOOLEAN,
            time_duration DECIMAL
        );
        '''
        # Execute the SQL statement
        cursor.execute(create_table_query)
        # Commit the changes to the database
        conn.commit()
        print("Table 'db_metrics_tryton' checked/created successfully.")
        # Close the cursor
        cursor.close()
    except Exception as e:
        print(f"Failed to create/check table: {e}")
        # Optionally, you could also close the cursor here in case of failure

# Main execution
if __name__ == "__main__":
    conn = connect_db()
    if conn is not None:
        create_table_if_not_exists(conn)
        # Don't forget to close the database connection when done with all operations
        conn.close()
