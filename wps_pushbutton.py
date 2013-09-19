import RPi.GPIO as GPIO
import time
import threading
import wpactrl

##################
# Configuration: #
##################

Buttonpin = 11
LEDpin = 12
Socketaddress = "/var/run/hostapd/wlan0"

##############################
# Set up background threads: #
##############################

class messageMonitor(threading.Thread):
	def __init__(self, connection = Socketaddress):
		threading.Thread.__init__(self)
		self.daemon = True
		self.wpa_event = wpactrl.WPACtrl(connection)
		self.wpa_event.attach()
	
	def run(self):
		while 1:
			message = self.wpa_event.recv()
			if message[3:14] == "WPS-SUCCESS":
				print "connection successful!"
				if blinker.isAlive():
					blinker.stop()
				print "blinker stopped!"
				time.sleep(0.5)
				messageblink(3, LEDpin) # indicate success


class blinkThread(threading.Thread):
	def __init__(self, pin = LEDpin, timeout = 120):
		threading.Thread.__init__(self)
		self.daemon = True
		self.pin = pin
		self.timeout = timeout
		self._stop = threading.Event()

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()	

	def run(self):
		print "WPS Active for 2 Minutes"
		startTime = time.time()
		while self.stopped() != True:
			GPIO.output(self.pin, GPIO.HIGH)
			time.sleep(1)
			GPIO.output(self.pin, GPIO.LOW)
			time.sleep(1)
			if time.time() - startTime >= self.timeout:
				print "WPS Button Timed out with no connection made"
				break

######################
# Utility functions: #
######################

def messageblink(num = 3, pin = LEDpin):
	blinks = 0
	while num > blinks:
		GPIO.output(pin, GPIO.HIGH)
		time.sleep(0.2)
		GPIO.output(pin, GPIO.LOW)
		time.sleep(0.2)
		blinks += 1


def blink(pin = LEDpin, timeout=120):
	startTime = time.time()
	while True:
		GPIO.output(pin, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(pin, GPIO.LOW)
		time.sleep(1)
		if time.time() - startTime >= 120:
			break

################
# Main script: #
################

if __name__ == "__main__":
	
	# Set up GPIO:

	GPIO.setmode(GPIO.BOARD) # use board pin numbers rather than cpu pin numbers

	GPIO.setup(Buttonpin, GPIO.IN) # Button (pulled down)
	GPIO.setup(LEDpin, GPIO.OUT) # indicator LED
	GPIO.output(LEDpin, GPIO.LOW)

	# Set up the socket connection for controlling hostapd:

	wpa = wpactrl.WPACtrl(Socketaddress)
	
	# Initialise our threads:	

	blinker = blinkThread()
	monitor = messageMonitor()
	monitor.start() # Monitor will run continuously for length of program

	messageblink(2, 12) # Show that we're ready to go!
	
	# Main loop:

	while True:
		if GPIO.input(Buttonpin):
			time.sleep(2)
			if GPIO.input(Buttonpin) and blinker.isAlive() == False: # Button has been held down for 2 seconds
				if wpa.request("WPS_PBC")[0:2] == "OK":
					blinker = blinkThread()
					blinker.start()
				else: # Something went wrong!
					GPIO.output(LEDpin, GPIO.HIGH)
					raise Exception("Failed to activate WPS button!")