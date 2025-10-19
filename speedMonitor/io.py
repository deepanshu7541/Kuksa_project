import csv
import time
# Note: List is not strictly needed here anymore, but keeping for reference if using other functions
from typing import List 
from .core import Alert 

class AlertSink:
    def __init__(self, filename: str):
        self.filename = filename
        # Ensure the file is opened for writing
        self.file = open(filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['timestamp', 'kind', 'speed', 'reason'])
        print(f"Alerts will be logged to: {filename}")

    # Renamed from 'log' to 'write' and updated arguments to match polling loop
    def write(self, kind: str, speed: float, reason: str):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Write the row using the explicit arguments
        self.writer.writerow([current_time, kind, speed, reason])
        
        # Print to console
        print(f"🚨 ALERT LOGGED: {reason}")
        
        # Force the OS to write data to disk immediately (fixes empty CSV files)
        self.file.flush() 
        
    def close(self):
        self.file.close()
        print(f"Alert logging finished. File closed: {self.filename}")