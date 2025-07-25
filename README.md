# MiniProject
Metro Station Monitoring System
This project implements a real-time monitoring system for metro stations using computer vision and deep learning techniques. It aims to enhance passenger safety by detecting incoming metro trains, alerting commuters, and monitoring platform activity near designated safety zones (the yellow line).

Features
Metro Train Detection & Arrival Announcement: Utilizes a YOLOv5 model to detect incoming metro trains and triggers an audible announcement ("The metro is coming. Please stand clear of the yellow line.") to warn passengers.

Platform Safety Zone Monitoring (Yellow Line): Identifies individuals crossing or standing beyond a predefined "yellow safety line" on the metro platform.

People Activity Monitoring: Tracks the presence of people on the platform and beyond the safety line. (The current "entered/exited" logic might be better rephrased as "people in safe zone" vs "people in unsafe zone" for this type of system, as true entry/exit through a turnstile is different).

Real-time Notifications: Generates console notifications when a person crosses the safety line into the restricted area. (Extendable for SMS/Email alerts to station staff).

Basic GUI with Login: Provides a simple Tkinter-based graphical user interface for system control and displaying real-time statistics, secured by a basic login.

Time and Temperature Display: Shows current time and a placeholder for ambient temperature (can be integrated with actual sensors/APIs relevant to the station environment).

Video Output: Saves the processed video with detections and overlays to an output file for review or archival.

How It Works
The system processes video frames (from a file or live camera feed) using the following steps:

Object Detection: A pre-trained YOLOv5 model is used to detect objects within each frame, primarily focusing on person and, if trained, metro train classes.

Metro Train Detection Logic:

If a metro train is detected, a one-time audible safety announcement is triggered.

The yellow safety line is only prominently displayed (drawn on screen) when no metro train is detected, serving as a clear visual reminder for safe standing areas.

Passenger Safety Zone Monitoring:

For each detected person, the system checks if their position (specifically, the bottom corners of their bounding box) is "below" (i.e., on the unsafe side of, closer to the tracks) the yellow line.

If a person is detected in this unsafe zone, their bounding box is colored green, a notification is issued, and a counter for "people in unsafe zone" is incremented.

Otherwise, the bounding box is colored red, and a counter for "people in safe zone" is (currently people_exited) incremented. This counting logic might need refinement for a clearer "safe/unsafe" zone count.

GUI Updates: The Tkinter GUI continuously updates to show people counts, current time, and temperature readings.

Setup and Installation
Prerequisites
Python 3.8+

NVIDIA GPU with CUDA (highly recommended for faster performance with YOLOv5) or a strong CPU.

Basic understanding of command line/terminal.
