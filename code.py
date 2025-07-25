import cv2
import torch
import numpy as np
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import time
import requests

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Load YOLO model (using YOLOv5 for this example)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # Pretrained YOLOv5 small model

class PeopleCounter:
    def _init_(self):
        self.people_entered = 0
        self.people_exited = 0

    def increment_entered(self):
        self.people_entered += 1

    def increment_exited(self):
        self.people_exited += 1

    def get_entered(self):
        return self.people_entered

    def get_exited(self):
        return self.people_exited

# Initialize people counter
people_counter = PeopleCounter()

# Global variables
train_present = False
announcement_made = False

# Define specific line coordinates (415, 710) to (469, 508)
start_point_yellow = (415, 710)
end_point_yellow = (469, 508)

# Calculate line equation (slope and intercept) for the yellow line
line_slope = (end_point_yellow[1] - start_point_yellow[1]) / (end_point_yellow[0] - start_point_yellow[0])  # Slope (m)
line_intercept = start_point_yellow[1] - (line_slope * start_point_yellow[0])  # Intercept (c)

def is_below_line(point):
    """Check if a point (x, y) is below the yellow line."""
    x, y = point
    return y > (line_slope * x + line_intercept)

# Function to send real-time notifications (dummy implementation)
def send_notification(message):
    print(f"Notification: {message}")

# Function to announce train arrival
def announce_train_arrival():
    engine.say("The train is coming. Please stand clear of the yellow line.")
    engine.runAndWait()

# Function to get the current temperature
def get_temperature():
    # Dummy implementation for temperature; replace with actual API call
    return "25°C"

# Function to get the current time
def get_time():
    return time.strftime("%H:%M:%S")

# Function to process video frames and perform detection
def process_video():
    global train_present, announcement_made
    video_path = r"C:\Users\syedz\Downloads\min1.mp4"
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define output video writer
    output_path = 'output_with_yellow_line.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect objects in the frame using YOLO
        results = model(frame)
        detections = results.xyxy[0]  # Detections (bounding boxes)

        # Check for train presence
        train_present = any(results.names[int(det[5])] == 'train' for det in detections)
        if train_present:
            if not announcement_made:
                announce_train_arrival()
                announcement_made = True
        else:
            cv2.line(frame, start_point_yellow, end_point_yellow, (0, 255, 255), 2)
            announcement_made = False

        # Process each detection
        for det in detections:
            x1, y1, x2, y2, conf, cls = map(int, det[:6])  # Bounding box, confidence, class
            label = results.names[cls]

            if label == 'person':
                bottom_left = (x1, y2)  # Bottom-left corner of bounding box
                bottom_right = (x2, y2)  # Bottom-right corner of bounding box

                if is_below_line(bottom_left) or is_below_line(bottom_right):
                    color = (0, 255, 0)  # Green box for crossing
                    send_notification(f"Person crossed the yellow line at position: ({x1}, {y1})")
                    people_counter.increment_entered()
                else:
                    color = (0, 0, 255)  # Red box otherwise
                    people_counter.increment_exited()
            else:
                color = (0, 0, 255)  # Red box for other objects

            # Draw the bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Write the frame to the output
        out.write(frame)

        # Display the frame (optional)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# GUI functions
def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "password":
        messagebox.showinfo("Login", "Login Successful!")
        login_frame.pack_forget()
        main_frame.pack()
    else:
        messagebox.showerror("Login", "Invalid username or password")

def start_detection():
    process_video()
    update_gui()

def update_gui():
    people_entered_label.config(text=f"People Entered: {people_counter.get_entered()}")
    people_exited_label.config(text=f"People Exited: {people_counter.get_exited()}")
    temperature_label.config(text=f"Temperature: {get_temperature()}")
    time_label.config(text=f"Time: {get_time()}")
    root.after(1000, update_gui)  # Update every second

# GUI setup
root = tk.Tk()
root.title("Railway Station Monitoring System")

# Login Frame
login_frame = tk.Frame(root)
login_frame.pack(pady=10)

username_label = tk.Label(login_frame, text="Username")
username_label.grid(row=0, column=0, padx=5, pady=5)
username_entry = tk.Entry(login_frame)
username_entry.grid(row=0, column=1, padx=5, pady=5)

password_label = tk.Label(login_frame, text="Password")
password_label.grid(row=1, column=0, padx=5, pady=5)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

login_button = tk.Button(login_frame, text="Login", command=login)
login_button.grid(row=2, columnspan=2, pady=10)

# Main Frame
main_frame = tk.Frame(root)
main_frame.pack(pady=10)

start_button = tk.Button(main_frame, text="Start Detection", command=start_detection)
start_button.pack(pady=10)

people_entered_label = tk.Label(main_frame, text="People Entered: 0")
people_entered_label.pack(pady=5)

people_exited_label = tk.Label(main_frame, text="People Exited: 0")
people_exited_label.pack(pady=5)

temperature_label = tk.Label(main_frame, text="Temperature: N/A")
temperature_label.pack(pady=5)

time_label = tk.Label(main_frame, text="Time: N/A")
time_label.pack(pady=5)

# Run the GUI
root.after(1000, update_gui)  # Start updating the GUI
root.mainloop()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Load YOLO model (using YOLOv5 for this example)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # Pretrained YOLOv5 small model

class PeopleCounter:
    def _init_(self):
        self.people_entered = 0
        self.people_exited = 0

    def increment_entered(self):
        self.people_entered += 1

    def increment_exited(self):
        self.people_exited += 1

    def get_entered(self):
        return self.people_entered

    def get_exited(self):
        return self.people_exited

# Initialize people counter
people_counter = PeopleCounter()

# Global variables
train_present = False
announcement_made = False

# Define specific line coordinates (415, 710) to (469, 508)
start_point_yellow = (415, 710)
end_point_yellow = (469, 508)

# Calculate line equation (slope and intercept) for the yellow line
line_slope = (end_point_yellow[1] - start_point_yellow[1]) / (end_point_yellow[0] - start_point_yellow[0])  # Slope (m)
line_intercept = start_point_yellow[1] - (line_slope * start_point_yellow[0])  # Intercept (c)

def is_below_line(point):
    """Check if a point (x, y) is below the yellow line."""
    x, y = point
    return y > (line_slope * x + line_intercept)

# Function to send real-time notifications (dummy implementation)
def send_notification(message):
    print(f"Notification: {message}")

# Function to announce train arrival
def announce_train_arrival():
    engine.say("The train is coming. Please stand clear of the yellow line.")
    engine.runAndWait()

# Function to get the current temperature
def get_temperature():
    # Dummy implementation for temperature; replace with actual API call
    return "25°C"

# Function to get the current time
def get_time():
    return time.strftime("%H:%M:%S")

# Function to process video frames and perform detection
def process_video():
    global train_present, announcement_made
    video_path = r"C:\Users\syedz\Downloads\min1.mp4"
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define output video writer
    output_path = 'output_with_yellow_line.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect objects in the frame using YOLO
        results = model(frame)
        detections = results.xyxy[0]  # Detections (bounding boxes)

        # Check for train presence
        train_present = any(results.names[int(det[5])] == 'train' for det in detections)
        if train_present:
            if not announcement_made:
                announce_train_arrival()
                announcement_made = True
        else:
            cv2.line(frame, start_point_yellow, end_point_yellow, (0, 255, 255), 2)
            announcement_made = False

        # Process each detection
        for det in detections:
            x1, y1, x2, y2, conf, cls = map(int, det[:6])  # Bounding box, confidence, class
            label = results.names[cls]

            if label == 'person':
                bottom_left = (x1, y2)  # Bottom-left corner of bounding box
                bottom_right = (x2, y2)  # Bottom-right corner of bounding box

                if is_below_line(bottom_left) or is_below_line(bottom_right):
                    color = (0, 255, 0)  # Green box for crossing
                    send_notification(f"Person crossed the yellow line at position: ({x1}, {y1})")
                    people_counter.increment_entered()
                else:
                    color = (0, 0, 255)  # Red box otherwise
                    people_counter.increment_exited()
            else:
                color = (0, 0, 255)  # Red box for other objects

            # Draw the bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Write the frame to the output
        out.write(frame)

        # Display the frame (optional)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# GUI functions
def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "password":
        messagebox.showinfo("Login", "Login Successful!")
        login_frame.pack_forget()
        main_frame.pack()
    else:
        messagebox.showerror("Login", "Invalid username or password")

def start_detection():
    process_video()
    update_gui()

def update_gui():
    people_entered_label.config(text=f"People Entered: {people_counter.get_entered()}")
    people_exited_label.config(text=f"People Exited: {people_counter.get_exited()}")
    temperature_label.config(text=f"Temperature: {get_temperature()}")
    time_label.config(text=f"Time: {get_time()}")
    root.after(1000, update_gui)  # Update every second

# GUI setup
root = tk.Tk()
root.title("Railway Station Monitoring System")

# Login Frame
login_frame = tk.Frame(root)
login_frame.pack(pady=10)

username_label = tk.Label(login_frame, text="Username")
username_label.grid(row=0, column=0, padx=5, pady=5)
username_entry = tk.Entry(login_frame)
username_entry.grid(row=0, column=1, padx=5, pady=5)

password_label = tk.Label(login_frame, text="Password")
password_label.grid(row=1, column=0, padx=5, pady=5)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

login_button = tk.Button(login_frame, text="Login", command=login)
login_button.grid(row=2, columnspan=2, pady=10)

# Main Frame
main_frame = tk.Frame(root)
main_frame.pack(pady=10)

start_button = tk.Button(main_frame, text="Start Detection", command=start_detection)
start_button.pack(pady=10)

people_entered_label = tk.Label(main_frame, text="People Entered: 0")
people_entered_label.pack(pady=5)

people_exited_label = tk.Label(main_frame, text="People Exited: 0")
people_exited_label.pack(pady=5)

temperature_label = tk.Label(main_frame, text="Temperature: N/A")
temperature_label.pack(pady=5)

time_label = tk.Label(main_frame, text="Time: N/A")
time_label.pack(pady=5)

# Run the GUI
root.after(1000, update_gui)  # Start updating the GUI
root.mainloop()