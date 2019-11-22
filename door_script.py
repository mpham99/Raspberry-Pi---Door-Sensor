import RPi.GPIO as GPIO
import time
import sys
import signal
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

def read_template_email(filename):
    with open(filename, 'r') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


# Set Broadcom mode so we can address GPIO pins by number.
GPIO.setmode(GPIO.BCM)

# This is the GPIO pin number we have one of the door sensor
# wires attached to, the other should be attached to a ground
DOOR_SENSOR_PIN = 18

# Initially we don't know if the door sensor is open or closed...
isOpen = None
oldIsOpen = None

# Clean up when the user exits with keyboard interrupt
def cleanupLights(signal, frame):
    GPIO.cleanup()
    sys.exit(0)

# Set up the door sensor pin.
GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

counter = 0
now = None
smtp_address = "";
server = smtplib.SMTP(smtp_address, 25)

# Make sure all lights are off.
# Set the cleanup handler for when user hits Ctrl-C to exit
while True:
    oldIsOpen = isOpen
    isOpen = GPIO.input(DOOR_SENSOR_PIN)
    if (isOpen):
        if now is None:
          now = datetime.datetime.now()
        time.sleep(1)
        counter += 1
        #print (counter)
        #print (now)
        if(counter == 40):
            #print ("SEND EMAIL")
            msg = MIMEMultipart()
            message_template = read_template_email('message.txt')
            message = message_template.substitute(DATE_TIME=now.strftime("%Y-%m-%d %H:%M:%S"))
            msg['Subject'] = "The door is open"
            msg.attach(MIMEText(message, 'plain'))
            server.sendmail("", "", msg.as_string())
            del msg

    elif (isOpen == 0):
     time.sleep(1)
     counter = 0
     #print (counter)
     now = None

    time.sleep(0.1)
