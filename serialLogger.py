"""
Serial Data Logger for Load Cell Force Measurements
This script connects to a microcontroller (e.g., Arduino) via a serial COM port, 
and reads incoming comma-separated data (Time, Reading), and logs it to a CSV file.
"""

import serial
import csv
import os
import keyboard
from datetime import datetime

#Configuration & File Setup

#Generate a unique suffix using current date and time to prevent overwriting old files
suffix = datetime.now().strftime("%m-%d_%H-%M")

#Serial connection settings (Must match microcontroller's settings)
COM_PORT = 'COM10' 
BAUD_RATE = 500000
FILE_NAME = f'friction_data_{suffix}.csv'

#State variables for the logging logic
logging = False         #Tracks whether data is currently being saved to the CSV
resetTime = False       #Flag to zero-out the time when logging resumes
startTime = 0.0         #Stores baseline time to subtract from incoming data
insertNewLine = False   #Flag to insert a blank row in the CSV when logging is paused

#Define directory path (defaults to a folder on the user's Desktop)
FOLDER_NAME = "friction data"
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
SAVE_FOLDER = os.path.join(DESKTOP_PATH, FOLDER_NAME)

#Absolute path for the output CSV
FULL_FILE_PATH = os.path.join(SAVE_FOLDER, FILE_NAME)

def toggleLogging(e):
    
    #Callback function triggered when the spacebar is pressed. Toggles the logging state on or off.
    
    global logging 
    global resetTime
    global insertNewLine

    logging = not logging
    
    if logging:
        #If we just started logging, flag system to reset the starting timestamp
        resetTime = True
    else:
        #If we just stopped logging, flag system to insert a visual break in the CSV
        insertNewLine = True

#Main Execution Block
try:
    print(f"COM port: {COM_PORT}")
    
    #Initialize serial connection
    ser = serial.Serial(COM_PORT, BAUD_RATE)
    print(f"Good connection. Press 'Space' to start/stop logging. Press 'Ctrl+C' to exit.")

    #Bind spacebar to toggle function
    keyboard.on_press_key('space', toggleLogging)

    #Open CSV file in write mode
    with open(FULL_FILE_PATH, 'w', newline='') as file:
        writer = csv.writer(file)
        
        #Infinite loop to continuously monitor serial port
        while True:
            
            #If logging was just paused, add an empty row to separate data chunks in the CSV
            if insertNewLine:
                writer.writerow([])
                insertNewLine = False

            #Check if there is data waiting in serial buffer
            if ser.in_waiting > 0:
                try:
                    #Read the line, decode from bytes to string, ignore weird characters, and strip whitespace
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    data = line.split(',')
                    
                    if logging:
                        #Ensure received exactly two pieces of data before processing
                        if len(data) == 2: 
                            try:
                                #Parse raw time from the microcontroller
                                arduinoTime = float(data[0])
                                reading = data[1]
                                
                                #If this is the first reading after starting/resuming, baseline the time
                                if resetTime:
                                    resetTime = False
                                    startTime = arduinoTime

                                #Calculate the elapsed time since logging started (rounded to 3 decimals)
                                adjustedTime = round(arduinoTime - startTime, 3)

                                #Write the adjusted time and the sensor reading to the CSV
                                writer.writerow([adjustedTime, reading])
                                print(f"{adjustedTime}s, {reading}")
                                
                            except ValueError:
                                #Catch instances where data cannot be converted to float 
                                print("val error")
                                pass
                                
                except UnicodeDecodeError:
                    print("bad data")

#exit upon pressing Ctrl+C in the terminal
except KeyboardInterrupt:
    print(f"\nData saved to {FULL_FILE_PATH}")

#Catch-all for other errors (e.g., COM port not found/already open)
except Exception as e:
    print(f"\nERROR: {e}")