import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psycopg2
from dbconf import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT


def connect_db():
    try:
        return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_db_size_bytes(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT pg_database_size(current_database());")
    size_bytes = cursor.fetchone()[0]
    cursor.close()
    return size_bytes

def get_current_db_timestamp(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT CURRENT_TIMESTAMP;")
    current_db_timestamp = cursor.fetchone()[0]
    cursor.close()
    return current_db_timestamp

    
def reset_statistics(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT pg_stat_reset();")
        connection.commit()
        cursor.close()
        print("Statistics reset successfully.")
    except Exception as e:
        print(f"Error resetting statistics: {e}")


db_conn = connect_db()
reset_statistics(db_conn)
current_timestamp = get_current_db_timestamp(db_conn)
print("stats_reset_time: ", current_timestamp)
print("current_timestamp: ", get_current_db_timestamp(db_conn))
if db_conn:
    db_size_bytes = get_db_size_bytes(db_conn)
    db_conn.close()
else:
    print("Failed to connect to the database. Using default values for demonstration.")
    db_size_bytes = 0

total_allocated_db_size_gb = 200 / 1024
db_size_gb = db_size_bytes / (1024**3)
free_memory_gb = total_allocated_db_size_gb - db_size_gb
values = [total_allocated_db_size_gb, db_size_gb, free_memory_gb]

# Sample Data for All Metrics
total_data_acquired = 950
number_of_errors = 50
tpm_data = [0]
throughput_data = [0]

# Main window setup
root = tk.Tk()
root.title("DB Performance Metrics")
root.geometry("1300x800")

# Scrollable Canvas
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def add_figure_to_frame(figure, frame, side=tk.LEFT, fill=tk.BOTH, expand=True):
    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.pack(side=side, fill=fill, expand=expand)
    return canvas


# Creating frames for each section within scrollable_frame instead of root
top_frame = ttk.Frame(scrollable_frame, height=200)
top_frame.pack(side=tk.TOP, fill=tk.X)
middle_frame = ttk.Frame(scrollable_frame)
middle_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

# Pie Chart for Ratio of Data to Errors
fig1 = Figure(figsize=(4, 5), dpi=80)
plot1 = fig1.add_subplot(1, 1, 1)
plot1.pie(
    [total_data_acquired, number_of_errors],
    labels=["Total Data Acquired", "Errors"],
    autopct="%1.1f%%",
    startangle=140,
    colors=["#4caf50", "#f44336"],
)
plot1.set_title("Ratio of Data to Errors")
add_figure_to_frame(fig1, top_frame)

# Line Plot for Average Transaction Entry Time
timestamps = [0]
fig2 = Figure(figsize=(13, 5), dpi=80)
plot2 = fig2.add_subplot(1, 1, 1)
plot2.plot(timestamps, marker="o", linestyle="-", color="b")
plot2.set_title("Average Transaction Entry Time vs. Time")
add_figure_to_frame(fig2, top_frame)

# Middle Frame: TPM, Throughput, and Database Size Metrics side by side
fig3 = Figure(figsize=(17, 5), dpi=80)
plot3 = fig3.add_subplot(1, 3, 1)
plot3.plot(tpm_data, marker="o", linestyle="-", color="c")
plot3.set_title("Transactions Per Minute (TPM)")
plot3.set_xlabel("Time (minutes)")
plot3.set_ylabel("TPM")

plot4 = fig3.add_subplot(1, 3, 2)
plot4.plot(throughput_data, marker="o", linestyle="-", color="m")
plot4.set_title("Throughput")
plot4.set_xlabel("Time (minutes)")
plot4.set_ylabel("Transactions")

plot5 = fig3.add_subplot(1, 3, 3)
categories = ["Total Allocated", "Used", "Free"]
plot5.bar(categories, values, color=["blue", "red", "green"])
plot5.set_title("Database Size Metrics (200 MB Allocated)")
plot5.set_ylabel("GB")

add_figure_to_frame(fig3, middle_frame)


def get_transaction_metrics():
    try:
        with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT) as conn:
            with conn.cursor() as cur:
                
                cur.execute(
                    """
                SELECT 
                  datname, 
                  xact_commit + xact_rollback AS total_transactions, 
                  (xact_commit + xact_rollback) / (extract(epoch from now() - %s) / 60) AS transactions_per_minute,
                  (xact_commit + xact_rollback) / extract(epoch from now() - %s) AS transactions_per_second
                FROM 
                  pg_stat_database
                WHERE
                  datname = 'trytonnew';
                """,(current_timestamp, current_timestamp)
                )
                result = cur.fetchone()
                print(result)
                return {"total_transactions": abs(result[3]), "transactions_per_minute": abs(result[2])}
    except Exception as e:
        print(f"Error fetching transaction metrics: {e}")
        return {"total_transactions": 0, "transactions_per_minute": 0}


def count_transactions_by_status(conn, transaction_status):
    try:
        cursor = conn.cursor()
        # Prepare SQL query to count entries by transaction status
        count_query = """SELECT COUNT(*) FROM db_metrics_tryton WHERE transaction_status = %s"""
        cursor.execute(count_query, (transaction_status,))
        count = cursor.fetchone()[0]
        print(f"Number of transactions where status is {transaction_status}: {count}")
        cursor.close()
        return count
    except Exception as e:
        print(f"Failed to count transactions: {e}")
        return None


def avg_time_duration_for_true_status(conn):
    try:
        cursor = conn.cursor()
        # Prepare SQL query to calculate average time duration where transaction status is True
        avg_query = """SELECT AVG(time_duration) FROM db_metrics_tryton WHERE transaction_status = TRUE"""
        cursor.execute(avg_query)
        avg_time_duration = cursor.fetchone()[0]
        print(f"Average time duration for transactions with status True: {avg_time_duration}")
        cursor.close()
        return avg_time_duration
    except Exception as e:
        print(f"Failed to calculate average time duration: {e}")
        return None


def refresh_db_transactions_metrics():
    conn = connect_db()
    if conn:
        total_transactions = count_transactions_by_status(conn, True) + count_transactions_by_status(conn, False)
        total_errors = count_transactions_by_status(conn, False)
        avg_time_duration = avg_time_duration_for_true_status(conn)
        conn.close()
    else:
        print("Failed to connect to the database. Using default values for demonstration.")
        total_transactions = 0
        avg_time_duration = 0
    
    total_data_acquired = total_transactions
    number_of_errors = total_errors

    plot1.clear()
    plot1.pie([total_data_acquired, number_of_errors], labels=["Total Data Acquired", "Errors"], autopct="%1.1f%%", startangle=140, colors=["#4caf50", "#f44336"])
    plot1.set_title("Ratio of Data to Errors")

    if len(timestamps) > 10:
        timestamps.pop(0)
    timestamps.append(avg_time_duration)
    plot2.clear()
    plot2.plot(timestamps, marker="o", linestyle="-", color="b")
    plot2.set_title(f"Average Transaction Entry Time {round(avg_time_duration * 1000, 8)} ms")
    plot2.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)
    fig2.canvas.draw_idle()

    # Schedule the next call
    root.after(3000, refresh_db_transactions_metrics)
    print("Database transactions metrics refreshed!")


def refresh_db_size_metrics():
    # Assuming you have a function to get the updated database size
    db_conn = connect_db()
    if db_conn:
        db_size_bytes = get_db_size_bytes(db_conn)
        db_conn.close()
    else:
        print("Failed to connect to the database. Using default values for demonstration.")
        db_size_bytes = 0

    db_size_gb = db_size_bytes / (1024**3)
    free_memory_gb = total_allocated_db_size_gb - db_size_gb
    values = [total_allocated_db_size_gb, db_size_gb, free_memory_gb]

    # Update the figure or metrics here
    # For example, updating a bar chart's values
    # This is a placeholder, replace with actual update logic
    plot5.clear()
    plot5.bar(categories, values, color=["blue", "red", "green"])
    plot5.set_title(f"200 MB Allocated {round(db_size_gb * 1000, 2)} MB Used, {round(free_memory_gb * 1000, 2)} MB Free")
    plot5.set_ylabel("GB")
    fig3.canvas.draw_idle()

    # Schedule the next call
    root.after(3000, refresh_db_size_metrics)
    print("Database size metrics refreshed!")


def refresh_transaction_metrics():
    metrics = get_transaction_metrics()
    total_transactions = metrics["total_transactions"]
    tpm = metrics["transactions_per_minute"]
    
    if tpm is None:
       tpm = 0
    if total_transactions is None:
       total_transactions = 0 

    # Assuming you have placeholders for these metrics in your GUI
    # Update the placeholders with the latest metrics
    plot3.clear()
    plot4.clear()

    # You might want to keep a history of TPM and transactions to plot over time
    if len(tpm_data) > 5:
        tpm_data.pop(0)

    if len(throughput_data) > 5:
        throughput_data.pop(0)

    tpm_data.append(tpm)
    throughput_data.append(total_transactions)

    # Redraw the TPM plot
    plot3.plot(tpm_data, marker="o", linestyle="-", color="c")
    plot3.set_title(f"TPM {round(tpm,2)} transactions per min")
    plot3.set_ylabel("TPM")
    plot3.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)

    # Redraw the Throughput plot
    plot4.plot(throughput_data, marker="o", linestyle="-", color="m")
    plot4.set_title(f"Throughput {round(total_transactions,2)} transactions per sec")
    plot4.set_ylabel("Transactions Per Second (TPS)")
    plot4.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)

    fig3.canvas.draw_idle()

    # Schedule the next call
    root.after(3000, refresh_transaction_metrics)
    print("Transaction metrics refreshed!")

refresh_db_size_metrics()
refresh_transaction_metrics()
refresh_db_transactions_metrics()
root.mainloop()
