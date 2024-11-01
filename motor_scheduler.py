import customtkinter as ctk
import serial
import schedule
import time
import json
from datetime import datetime
import threading
from tkinter import messagebox

class MotorSchedulerApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Arduino Motor Scheduler")
        self.root.geometry("600x800")
        
        # Initialize serial connection (None until connected)
        self.serial_conn = None
        self.scheduled_moves = []
        self.scheduler_thread = None
        self.running = False

        self.setup_ui()

    def setup_ui(self):
        # Serial Connection Frame
        connection_frame = ctk.CTkFrame(self.root)
        connection_frame.pack(padx=10, pady=10, fill="x")

        self.port_entry = ctk.CTkEntry(connection_frame, placeholder_text="COM port (e.g., COM3 or /dev/ttyUSB0)")
        self.port_entry.pack(side="left", padx=5, expand=True)

        self.baud_entry = ctk.CTkEntry(connection_frame, placeholder_text="Baud rate", width=100)
        self.baud_entry.pack(side="left", padx=5)
        self.baud_entry.insert(0, "9600")

        self.connect_btn = ctk.CTkButton(connection_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.pack(side="left", padx=5)

        # Motor Control Frame
        control_frame = ctk.CTkFrame(self.root)
        control_frame.pack(padx=10, pady=10, fill="x")

        # Time input
        time_label = ctk.CTkLabel(control_frame, text="Schedule Time (HH:MM):")
        time_label.pack(pady=5)
        self.time_entry = ctk.CTkEntry(control_frame, placeholder_text="13:30")
        self.time_entry.pack(pady=5)

        # Direction input
        direction_label = ctk.CTkLabel(control_frame, text="Direction:")
        direction_label.pack(pady=5)
        self.direction_var = ctk.StringVar(value="clockwise")
        direction_frame = ctk.CTkFrame(control_frame)
        direction_frame.pack(pady=5)

        ctk.CTkRadioButton(direction_frame, text="Clockwise", variable=self.direction_var, value="clockwise").pack(side="left", padx=10)
        ctk.CTkRadioButton(direction_frame, text="Counter-Clockwise", variable=self.direction_var, value="counterclockwise").pack(side="left", padx=10)

        # Steps input
        steps_label = ctk.CTkLabel(control_frame, text="Number of Steps:")
        steps_label.pack(pady=5)
        self.steps_entry = ctk.CTkEntry(control_frame, placeholder_text="1000")
        self.steps_entry.pack(pady=5)

        # Add schedule button
        self.add_schedule_btn = ctk.CTkButton(control_frame, text="Add to Schedule", command=self.add_schedule)
        self.add_schedule_btn.pack(pady=10)

        # Scheduled moves list
        list_frame = ctk.CTkFrame(self.root)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        list_label = ctk.CTkLabel(list_frame, text="Scheduled Moves:")
        list_label.pack(pady=5)

        self.moves_listbox = ctk.CTkTextbox(list_frame)
        self.moves_listbox.pack(padx=10, pady=5, fill="both", expand=True)

        # Control buttons
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(padx=10, pady=10, fill="x")

        self.start_btn = ctk.CTkButton(button_frame, text="Start Scheduler", command=self.start_scheduler)
        self.start_btn.pack(side="left", padx=5, expand=True)

        self.stop_btn = ctk.CTkButton(button_frame, text="Stop Scheduler", command=self.stop_scheduler, state="disabled")
        self.stop_btn.pack(side="left", padx=5, expand=True)

        self.clear_btn = ctk.CTkButton(button_frame, text="Clear All", command=self.clear_schedule)
        self.clear_btn.pack(side="left", padx=5, expand=True)

    def toggle_connection(self):
        if self.serial_conn is None:
            try:
                port = self.port_entry.get()
                baud = int(self.baud_entry.get())
                self.serial_conn = serial.Serial(port, baud, timeout=1)
                self.connect_btn.configure(text="Disconnect")
                messagebox.showinfo("Success", "Connected to Arduino!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to connect: {str(e)}")
        else:
            self.serial_conn.close()
            self.serial_conn = None
            self.connect_btn.configure(text="Connect")

    def add_schedule(self):
        try:
            time_str = self.time_entry.get()
            direction = self.direction_var.get()
            steps = int(self.steps_entry.get())

            # Validate time format
            datetime.strptime(time_str, "%H:%M")

            move = {
                "time": time_str,
                "direction": direction,
                "steps": steps
            }

            self.scheduled_moves.append(move)
            self.update_moves_display()

            # Clear inputs
            self.time_entry.delete(0, "end")
            self.steps_entry.delete(0, "end")

        except ValueError as e:
            messagebox.showerror("Error", "Invalid input. Please check the time format (HH:MM) and steps number.")

    def update_moves_display(self):
        self.moves_listbox.delete("0.0", "end")
        for move in self.scheduled_moves:
            self.moves_listbox.insert("end", f"Time: {move['time']}, Direction: {move['direction']}, Steps: {move['steps']}\n")

    def send_motor_command(self, direction, steps):
        if self.serial_conn and self.serial_conn.is_open:
            command = json.dumps({"direction": direction, "steps": steps}) + "\n"
            self.serial_conn.write(command.encode())

    def scheduler_loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def start_scheduler(self):
        if not self.scheduled_moves:
            messagebox.showwarning("Warning", "No moves scheduled!")
            return

        if not self.serial_conn or not self.serial_conn.is_open:
            messagebox.showwarning("Warning", "Not connected to Arduino!")
            return

        self.running = True
        schedule.clear()

        # Schedule all moves
        for move in self.scheduled_moves:
            schedule.every().day.at(move["time"]).do(
                self.send_motor_command,
                move["direction"],
                move["steps"]
            )

        self.scheduler_thread = threading.Thread(target=self.scheduler_loop)
        self.scheduler_thread.start()

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

    def stop_scheduler(self):
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        schedule.clear()

        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def clear_schedule(self):
        self.scheduled_moves.clear()
        self.update_moves_display()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MotorSchedulerApp()
    app.run()