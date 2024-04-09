import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psycopg2
from dbconf import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT
import re
from automate_decentralised import (
    automate_inventory,
    get_response_time,
    get_tpm,
    get_total_time,
    get_gas_spent,
)
from automate_inventory import (
    setup_all,
    get_response_time_cen,
    get_tpm_cen,
    get_total_time_cen,
)


def connect_db():
    try:
        return psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None


def get_db_size_bytes(connection):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT datname, pg_size_pretty(pg_database_size(datname)) AS size FROM pg_database WHERE datname='trytonnew';"
    )
    size_bytes = cursor.fetchone()[1]
    cursor.close()
    return size_bytes


def get_memory_usage(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW shared_buffers;")
    memory_usage = cursor.fetchone()[0]
    cursor.close()
    return memory_usage


def get_current_db_timestamp(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT CURRENT_TIMESTAMP;")
    current_db_timestamp = cursor.fetchone()[0]
    cursor.close()
    return current_db_timestamp


def reset_statistics(connection):
    try:
        cursor = connection.cursor()
        # cursor.execute("DELETE FROM db_metrics_tryton;")
        cursor.execute("SELECT pg_stat_reset();")
        connection.commit()
        cursor.close()
        print("Statistics reset successfully.")
    except Exception as e:
        print(f"Error resetting statistics: {e}")


def create_window(title, geometry):
    window = tk.Toplevel()
    window.title(title)
    window.geometry(geometry)
    return window


db_conn = connect_db()
reset_statistics(db_conn)
current_timestamp = get_current_db_timestamp(db_conn)
experiment_time = 30
print("stats_reset_time: ", current_timestamp)
print("current_timestamp: ", get_current_db_timestamp(db_conn))
if db_conn:
    db_size_bytes = get_db_size_bytes(db_conn)
    db_conn.close()
else:
    print("Failed to connect to the database. Using default values for demonstration.")
    db_size_bytes = 0

total_allocated_db_size_gb = 200 / 1024
db_size_gb = int(db_size_bytes.split()[0])
free_memory_gb = total_allocated_db_size_gb - db_size_gb
values = [db_size_gb, free_memory_gb]
values_decentralized = [0, 0]

tpm_data = [0]
tpm_data_decentralized = [0]
throughput_data = [0]
throughput_data_decentralized = [0]

# Main window setup
root = tk.Tk()
root.title("Centralised ERP System Metrics Dashboard")
root.geometry("1300x800")

timer_label = tk.Label(
    root,
    text=f"(Total Experiment Time 30 sec) Time Remaining: {experiment_time} seconds",
)
timer_label.pack(side="top", fill="x")

win1 = create_window("Decentralized ERP System Metrics Dashboard", "1300x800")
timer_label1 = tk.Label(
    win1,
    text=f"(Total Experiment Time 30 sec) Time Remaining: {experiment_time} seconds",
)
timer_label1.pack(side="top", fill="x")

# Create and setup the second additional window
win2 = create_window("Centralized VS Decentralized", "1300x800")
timer_label2 = tk.Label(
    win2,
    text=f"(Total Experiment Time 30 sec) Time Remaining: {experiment_time} seconds",
)
timer_label2.pack(side="top", fill="x")

# Scrollable Canvas
canvas = tk.Canvas(root)
canvas1 = tk.Canvas(win1)
canvas2 = tk.Canvas(win2)


scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar1 = ttk.Scrollbar(win1, orient="vertical", command=canvas1.yview)
scrollbar2 = ttk.Scrollbar(win2, orient="vertical", command=canvas2.yview)

scrollable_frame = ttk.Frame(canvas)
scrollable_frame1 = ttk.Frame(canvas1)
scrollable_frame2 = ttk.Frame(canvas2)

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
scrollable_frame1.bind(
    "<Configure>", lambda e: canvas1.configure(scrollregion=canvas1.bbox("all"))
)
scrollable_frame2.bind(
    "<Configure>", lambda e: canvas2.configure(scrollregion=canvas2.bbox("all"))
)


canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas1.create_window((0, 0), window=scrollable_frame1, anchor="nw")
canvas2.create_window((0, 0), window=scrollable_frame2, anchor="nw")

canvas.configure(yscrollcommand=scrollbar.set)
canvas1.configure(yscrollcommand=scrollbar1.set)
canvas2.configure(yscrollcommand=scrollbar2.set)

canvas.pack(side="left", fill="both", expand=True)
canvas1.pack(side="left", fill="both", expand=True)
canvas2.pack(side="left", fill="both", expand=True)

scrollbar.pack(side="right", fill="y")
scrollbar1.pack(side="right", fill="y")
scrollbar2.pack(side="right", fill="y")


def add_figure_to_frame(figure, frame, side=tk.LEFT, fill=tk.BOTH, expand=True):
    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.pack(side=side, fill=fill, expand=expand)
    return canvas


# Creating frames for each section within scrollable_frame instead of root
top_frame = ttk.Frame(scrollable_frame, height=200)
top_frame1 = ttk.Frame(scrollable_frame1, height=200)
top_frame2 = ttk.Frame(scrollable_frame2, height=200)

top_frame.pack(side=tk.TOP, fill=tk.X)
top_frame1.pack(side=tk.TOP, fill=tk.X)
top_frame2.pack(side=tk.TOP, fill=tk.X)

middle_frame = ttk.Frame(scrollable_frame)
middle_frame1 = ttk.Frame(scrollable_frame1)
middle_frame2 = ttk.Frame(scrollable_frame2)

middle_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
middle_frame1.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
middle_frame2.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

# Pie Chart for Ratio of Data to Errors
fig1 = Figure(figsize=(4, 5), dpi=80)
plot1 = fig1.add_subplot(1, 1, 1)
# Centralized Data To Errors Ratio
plot1.pie(
    [100, 0],
    labels=["Total Data Acquired", "Errors"],
    autopct="%1.1f%%",
    startangle=140,
    colors=["#4caf50", "#f44336"],
)
plot1.set_title("Data to Errors Ratio (centralized)")
add_figure_to_frame(fig1, top_frame)

# Decentralized Data To Errors Ratio
fig11 = Figure(figsize=(4, 5), dpi=80)
plot11 = fig11.add_subplot(1, 1, 1)
plot11.pie(
    [100, 0],
    labels=["Total Data Acquired", "Errors"],
    autopct="%1.1f%%",
    startangle=140,
    colors=["#4caf50", "#f44336"],
)
plot11.set_title("Data to Errors Ratio (decentralized)")
add_figure_to_frame(fig11, top_frame1)

fig111 = Figure(figsize=(2, 5), dpi=80)
plot111 = fig111.add_subplot(1, 1, 1)
plot111.pie(
    [100, 0],
    labels=["Total Data Acquired", "Errors"],
    autopct="%1.1f%%",
    startangle=140,
    colors=["#4caf50", "#f44336"],
)
plot111.set_title("Data to Errors Ratio (centralized)")

fig1111 = Figure(figsize=(2, 5), dpi=80)
plot1111 = fig1111.add_subplot(1, 1, 1)
plot1111.pie(
    [100, 0],
    labels=["Total Data Acquired", "Errors"],
    autopct="%1.1f%%",
    startangle=140,
    colors=["#4caf50", "#f44336"],
)
plot1111.set_title("Data to Errors Ratio (decentralized)")

add_figure_to_frame(fig111, top_frame2)
add_figure_to_frame(fig1111, top_frame2)


# Line Plot for Average Transaction Entry Time
timestamps = [0]
fig2 = Figure(figsize=(13, 5), dpi=80)
plot2 = fig2.add_subplot(1, 1, 1)
plot2.plot(timestamps, marker="o", linestyle="-", color="b")
plot2.set_title("Response Time (ms) for Transaction (centralized)")
add_figure_to_frame(fig2, top_frame)

timestamps_decentralized = [0]
fig22 = Figure(figsize=(13, 5), dpi=80)
plot22 = fig22.add_subplot(1, 1, 1)
plot22.plot(timestamps_decentralized, marker="o", linestyle="-", color="b")
plot22.set_title("Response Time (ms) for Transaction (decentralized)")

add_figure_to_frame(fig22, top_frame1)

fig21 = Figure(figsize=(4, 4), dpi=80)
plot21 = fig21.add_subplot(1, 1, 1)
plot21.plot(timestamps, marker="o", linestyle="-", color="b")
plot21.set_title("Response Time (ms) for Transaction (centralized)")

fig221 = Figure(figsize=(4, 4), dpi=80)
plot221 = fig221.add_subplot(1, 1, 1)
plot221.plot(timestamps_decentralized, marker="o", linestyle="-", color="b")
plot221.set_title("Response Time (ms) for Transaction (decentralized)")

add_figure_to_frame(fig21, top_frame2)
add_figure_to_frame(fig221, top_frame2)


# Middle Frame: TPM, Throughput, and Database Size Metrics side by side
fig3 = Figure(figsize=(17, 5), dpi=80)
plot3 = fig3.add_subplot(1, 3, 1)
plot3.plot(tpm_data, marker="o", linestyle="-", color="c")
plot3.set_title("TPM (centralized)")
plot3.set_xlabel("Time (minutes)")
plot3.set_ylabel("TPM")

plot4 = fig3.add_subplot(1, 3, 2)
plot4.plot(throughput_data, marker="o", linestyle="-", color="m")
plot4.set_title("Throughput (centralized)")
plot4.set_xlabel("Time (minutes)")
plot4.set_ylabel("Transactions")

plot5 = fig3.add_subplot(1, 3, 3)
categories = ["Memory Ut.", "Disk Ut."]
plot5.bar(categories, values, color=["red", "red"])
plot5.set_title("Database Size Metrics")
plot5.set_ylabel("MB")

add_figure_to_frame(fig3, middle_frame)

fig33 = Figure(figsize=(17, 5), dpi=80)
plot33 = fig33.add_subplot(1, 3, 1)
plot33.plot(tpm_data_decentralized, marker="o", linestyle="-", color="c")
plot33.set_title("TPM (decentralized)")
plot33.set_xlabel("Time (minutes)")
plot33.set_ylabel("TPM")

plot44 = fig33.add_subplot(1, 3, 2)
plot44.plot(throughput_data_decentralized, marker="o", linestyle="-", color="m")
plot44.set_title("Throughput (decentralized)")
plot44.set_xlabel("Time (minutes)")
plot44.set_ylabel("Transactions")

plot55 = fig33.add_subplot(1, 3, 3)
categories_decentralised = ["Gas Spent", "Blockchain Ut."]
plot55.bar(categories_decentralised, values_decentralized, color=["red", "red"])
plot55.set_title("Blockchain Ut Metrics")
plot55.set_ylabel("ETH")

add_figure_to_frame(fig33, middle_frame1)

fig333 = Figure(figsize=(9, 5), dpi=70)
plot333 = fig333.add_subplot(1, 3, 1)
plot333.plot(tpm_data, marker="o", linestyle="-", color="c")
plot333.set_title("TPM (centralized)")
plot333.set_xlabel("Time (minutes)")
plot333.set_ylabel("TPM")

plot444 = fig333.add_subplot(1, 3, 2)
plot444.plot(throughput_data, marker="o", linestyle="-", color="m")
plot444.set_title("Throughput (centralized)")
plot444.set_xlabel("Time (minutes)")
plot444.set_ylabel("Transactions")

plot555 = fig333.add_subplot(1, 3, 3)
categories = ["Memory Ut.", "Disk Ut."]
plot555.bar(categories, values, color=["red", "red"])
plot555.set_title("Database Size Metrics")
plot555.set_ylabel("MB")

fig3333 = Figure(figsize=(9, 5), dpi=70)
plot3333 = fig3333.add_subplot(1, 3, 1)
plot3333.plot(tpm_data_decentralized, marker="o", linestyle="-", color="c")
plot3333.set_title("TPM (decentralized)")
plot3333.set_xlabel("Time (minutes)")
plot3333.set_ylabel("TPM")

plot4444 = fig3333.add_subplot(1, 3, 2)
plot4444.plot(throughput_data_decentralized, marker="o", linestyle="-", color="m")
plot4444.set_title("Throughput (decetralized)")
plot4444.set_xlabel("Time (minutes)")
plot4444.set_ylabel("Transactions")

plot5555 = fig3333.add_subplot(1, 3, 3)
categories_decentralised = ["Gas Spent", "Blockchain Ut."]
plot5555.bar(categories_decentralised, values_decentralized, color=["red", "red"])
plot5555.set_title("Blockchain Ut Metrics")
plot5555.set_ylabel("ETH")

add_figure_to_frame(fig333, middle_frame2)
add_figure_to_frame(fig3333, middle_frame2)


def get_transaction_metrics():
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
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
                """,
                    (current_timestamp, current_timestamp),
                )
                result = cur.fetchone()
                print(result)
                return {
                    "total_transactions": abs(result[3]),
                    "transactions_per_minute": abs(result[2]),
                }
    except Exception as e:
        print(f"Error fetching transaction metrics: {e}")
        return {"total_transactions": 0, "transactions_per_minute": 0}


def count_transactions_by_status(conn, transaction_status):
    try:
        cursor = conn.cursor()
        # Prepare SQL query to count entries by transaction status
        count_query = (
            """SELECT COUNT(*) FROM db_metrics_tryton WHERE transaction_status = %s"""
        )
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
        print(
            f"Average time duration for transactions with status True: {avg_time_duration}"
        )
        cursor.close()
        return avg_time_duration
    except Exception as e:
        print(f"Failed to calculate average time duration: {e}")
        return None


def refresh_db_transactions_metrics():

    if experiment_time > 0:
        conn = connect_db()
        if conn:
            total_transactions = count_transactions_by_status(
                conn, True
            ) + count_transactions_by_status(conn, False)
            total_errors = count_transactions_by_status(conn, False)
            conn.close()
        else:
            print(
                "Failed to connect to the database. Using default values for demonstration."
            )
            total_transactions = 0
            avg_time_duration = 0

        total_data_acquired = total_transactions
        number_of_errors = 0
        print("total_data_acquired: ", total_data_acquired)
        print("number_of_errors: ", number_of_errors)

        plot1.clear()
        plot1.pie(
            [total_data_acquired, number_of_errors],
            labels=["Total Data Acquired", "Errors"],
            autopct="%1.1f%%",
            startangle=140,
            colors=["#4caf50", "#f44336"],
        )
        plot1.set_title("Data to Errors Ratio (centralized)")

        avg_time_duration = get_response_time_cen()

        if len(timestamps) > 5:
            timestamps.pop(0)
        timestamps.append(avg_time_duration)
        print("timestamps: ", timestamps)

        response_decentralized = get_response_time()
        timestamps_decentralized.append(response_decentralized)
        if len(timestamps_decentralized) > 5:
            timestamps_decentralized.pop(0)
        print("timestamps_decentralized: ", timestamps_decentralized)

        plot2.clear()
        plot21.clear()
        plot22.clear()
        plot221.clear()
        plot2.plot(timestamps, marker="o", linestyle="-", color="b")
        plot21.plot(timestamps, marker="o", linestyle="-", color="b")
        plot22.plot(timestamps_decentralized, marker="o", linestyle="-", color="b")
        plot221.plot(timestamps_decentralized, marker="o", linestyle="-", color="b")
        plot2.set_title(f"Response  Time Centralized {round(avg_time_duration, 8)} ms")
        plot21.set_title(
            f"Response  Time for Centralized {round(avg_time_duration , 8)} ms"
        )
        plot22.set_title(
            f"Response  Time for Decentralized {round(response_decentralized , 8)} ms"
        )
        plot221.set_title(
            f"Response  Time for Decentralized {round(response_decentralized , 8)} ms"
        )
        plot2.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )
        plot21.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )
        plot22.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )
        plot221.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )
        fig2.canvas.draw_idle()
        fig21.canvas.draw_idle()
        fig22.canvas.draw_idle()
        fig221.canvas.draw_idle()

        # Schedule the next call
        root.after(3000, refresh_db_transactions_metrics)
        print("Database transactions metrics refreshed!")
    else:
        print("Stopping refresh_db_transactions_metrics due to timer completion.")


def refresh_db_size_metrics():

    if experiment_time > 0:
        # Assuming you have a function to get the updated database size
        db_conn = connect_db()
        if db_conn:
            db_size_bytes = get_db_size_bytes(db_conn)
            db_memory_usage = get_memory_usage(db_conn)
            print("db_size_bytes: ", db_size_bytes)
            print("db_memory_usage: ", db_memory_usage)
            db_conn.close()
        else:
            print(
                "Failed to connect to the database. Using default values for demonstration."
            )
            db_size_bytes = 0

        db_size_gb = int(re.match(r"\d+", db_size_bytes).group())
        free_memory_gb = int(re.match(r"\d+", db_memory_usage).group())
        values = [free_memory_gb, db_size_gb]

        gas_spent = get_gas_spent() / 10**9
        values_decentralized = [gas_spent, gas_spent]

        # Update the figure or metrics here
        # For example, updating a bar chart's values
        # This is a placeholder, replace with actual update logic
        plot5.clear()
        plot555.clear()
        plot55.clear()
        plot5555.clear()
        plot5.bar(categories, values, color=["red", "red"])
        plot555.bar(categories, values, color=["red", "red"])
        plot5.set_title(
            f"Memory Usage: {free_memory_gb} MB. Disk Usage {db_size_gb} MB,"
        )
        plot555.set_title(f"Memory: {free_memory_gb} MB. Disk{db_size_gb} MB")
        plot5.set_ylabel("MB")
        plot555.set_ylabel("MB")

        plot55.bar(categories_decentralised, values_decentralized, color=["red", "red"])
        plot55.set_title(
            f"Gas Spent: {round(gas_spent,5)} ETH. Blockchain Ut. {round(gas_spent,5)} ETH,"
        )
        plot55.set_ylabel("ETH")

        plot5555.bar(categories_decentralised, values_decentralized, color=["red", "red"])
        plot5555.set_title(
            f"Gas Spent: {round(gas_spent,5)} ETH"
        )
        plot5555.set_ylabel("ETH")

        fig3.canvas.draw_idle()
        fig333.canvas.draw_idle()
        fig33.canvas.draw_idle()
        fig3333.canvas.draw_idle()

        # Schedule the next call
        root.after(3000, refresh_db_size_metrics)
        print("Database size metrics refreshed!")

    else:
        print("Stopping refresh_db_transactions_metrics due to timer completion.")


def refresh_transaction_metrics():

    if experiment_time > 0:
        metrics = get_transaction_metrics()
        total_transactions = metrics["total_transactions"]
        tpm = metrics["transactions_per_minute"]

        tpm_dec = get_tpm()
        total_time_dec = get_total_time()
        res_time_dec = get_response_time()
        throughput_dec = res_time_dec / total_time_dec

        tpm_cen = get_tpm_cen()
        total_time_cen = get_total_time_cen()
        res_time_cen = get_response_time_cen()
        throughput_cen = res_time_cen / total_time_cen

        if tpm is None:
            tpm = 0
        if total_transactions is None:
            total_transactions = 0

        # Assuming you have placeholders for these metrics in your GUI
        # Update the placeholders with the latest metrics
        plot3.clear()
        plot4.clear()
        plot333.clear()
        plot444.clear()

        plot33.clear()
        plot3333.clear()
        plot44.clear()
        plot4444.clear()

        # You might want to keep a history of TPM and transactions to plot over time
        if len(tpm_data) > 5:
            tpm_data.pop(0)

        if len(tpm_data_decentralized) > 5:
            tpm_data_decentralized.pop(0)

        if len(throughput_data) > 5:
            throughput_data.pop(0)

        if len(throughput_data_decentralized) > 5:
            throughput_data_decentralized.pop(0)

        tpm_data.append(tpm_cen)
        throughput_data.append(throughput_cen)
        tpm_data_decentralized.append(tpm_dec)
        throughput_data_decentralized.append(throughput_dec)

        # Redraw the TPM plot
        plot3.plot(tpm_data, marker="o", linestyle="-", color="c")
        plot3.set_title(f"TPM {round(tpm_cen,2)}")
        plot3.set_ylabel("TPM")
        plot3.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        plot333.plot(tpm_data, marker="o", linestyle="-", color="c")
        plot333.set_title(f"TPM {round(tpm_cen,2)} (Cent.)")
        plot333.set_ylabel("TPM")
        plot333.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        # Redraw the Throughput plot
        plot4.plot(throughput_data, marker="o", linestyle="-", color="m")
        plot4.set_title(f"Throughput {round(throughput_cen,2)}")
        plot4.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        plot444.plot(throughput_data, marker="o", linestyle="-", color="m")
        plot444.set_title(f"Throughput {round(throughput_cen,2)} (Cent.)")
        plot444.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        plot33.plot(tpm_data_decentralized, marker="o", linestyle="-", color="c")
        plot33.set_title(f"TPM {round(tpm_dec,2)}")
        plot33.set_ylabel("TPM")
        plot33.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        plot3333.plot(tpm_data_decentralized, marker="o", linestyle="-", color="c")
        plot3333.set_title(f"TPM {round(tpm_dec,2)} (decent.)")
        plot3333.set_ylabel("TPM")
        plot3333.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        plot44.plot(throughput_data_decentralized, marker="o", linestyle="-", color="m")
        plot44.set_title(f"Throughput {round(throughput_dec,2)}")
        plot44.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        plot4444.plot(
            throughput_data_decentralized, marker="o", linestyle="-", color="m"
        )
        plot4444.set_title(f"Throughput {round(throughput_dec,2)} (decent.)")
        plot4444.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        fig3.canvas.draw_idle()
        fig333.canvas.draw_idle()
        fig33.canvas.draw_idle()
        fig3333.canvas.draw_idle()

        # Schedule the next call
        root.after(3000, refresh_transaction_metrics)
        print("Transaction metrics refreshed!")

    else:
        print("Stopping refresh_db_transactions_metrics due to timer completion.")


def update_timer():
    global experiment_time
    if experiment_time > 0:
        experiment_time -= 1
        timer_label.config(
            text=f"Time Remaining: {experiment_time} seconds (Total Experiment Time 30 sec)"
        )
        timer_label1.config(
            text=f"Time Remaining: {experiment_time} seconds (Total Experiment Time 30 sec)"
        )
        timer_label2.config(
            text=f"Time Remaining: {experiment_time} seconds (Total Experiment Time 30 sec)"
        )
        root.after(1000, update_timer)
        
    else:
        print("Experiment finished!")

def run_scripts():
    automate_inventory()
    setup_all()
    root.after(8000, run_scripts)



automate_inventory()
setup_all()
refresh_db_size_metrics()
refresh_transaction_metrics()
refresh_db_transactions_metrics()
update_timer()
run_scripts()
root.mainloop()
