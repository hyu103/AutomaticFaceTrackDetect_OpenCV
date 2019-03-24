import numpy as np
import cv2
import Tkinter
from Tkinter import *
import time
import datetime
import RPi.GPIO as GPIO
import os
import threading

from face_trainer import imageTrainer

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')

id = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
rLED=7
gLED=15
yLED=22
GPIO.setup(rLED,GPIO.OUT)
GPIO.setup(gLED,GPIO.OUT)
GPIO.setup(yLED,GPIO.OUT)

names = ['Unknown', 'Javier', 'Eric']


font = cv2.FONT_HERSHEY_SIMPLEX

root = Tk()
app = Frame(root)
app.grid()

recognized = False

vc = cv2.VideoCapture(0)
vc.set(3,340)
vc.set(4,260)

Pins = [11,13,29,31]
Pins2 = [16,18,36,38]

faceCascade = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')
global automatic
global count
count = 0
automatic = False

centerX = 170
centerY = 130

for i in Pins:
	GPIO.setup(i,GPIO.OUT)
	GPIO.output(i,0)

for r in Pins2:
	GPIO.setup(r,GPIO.OUT)
	GPIO.output(r,0)

motor = [[1,0,0,0],
		[1,1,0,0],
		[0,1,0,0],
		[0,1,1,0],
		[0,0,1,0],
		[0,0,1,1],
		[0,0,0,1],
		[1,0,0,1]]
		
def Blink():
	GPIO.output(rLED,GPIO.HIGH)
	time.sleep(0.005)
	GPIO.output(rLED, GPIO.LOW)
	time.sleep(0.005)

def Left():
	for step in range(8):
		for i in range(4):
			GPIO.output(Pins[i], motor[step][i])
		time.sleep(.001)
			
def Right():
	for step in reversed(range(8)):
		for i in reversed(range(4)):
			GPIO.output(Pins[i], motor[step][i])
		time.sleep(.001)
		
def Down():
	for step in range(8):
		for r in range(4):
			GPIO.output(Pins2[r], motor[step][r])
		time.sleep(.001)
			
def Up():
	for step in reversed(range(8)):
		for r in reversed(range(4)):
			GPIO.output(Pins2[r], motor[step][r])
		time.sleep(.001)
			
def Manual():
	global automatic
	automatic = False
	upBtn = Button(app,text="Up", command = Up)
	leftBtn = Button(app,text="Left", command=Left)
	rightBtn = Button(app,text="Right", command=Right)
	downBtn = Button(app,text="Down", command = Down)
	upBtn.grid(row=1,column=2)
	leftBtn.grid(row=2,column=1)
	rightBtn.grid(row=2,column=3)
	downBtn.grid(row=3,column=2)

		
def Automatic():
	global automatic
	automatic = True
	print ("Automatic Enabled")
	
def Screenshot():
	global count
	ret, frame = vc.read()
	timestamp = datetime.datetime.now()
	ts = timestamp.strftime("%B %d %Y %I : %M : %S%p")
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	cv2.imwrite(ts + ".jpg", frame)
	count += 1
	
	
def ControlGUI():
	root.title("Survallince Control")
	root.geometry("300x150")
	manualBtn = Button(app,text="Manual",command=Manual)
	automaticBtn = Button(app,text="Automatic", command=Automatic)
	screenshotBtn = Button(app,text="Screenshot", command=Screenshot)
	manualBtn.grid(row=0,column=1)
	automaticBtn.grid(row=0,column=2)
	screenshotBtn.grid(row=0,column=3)

	root.mainloop()
	
def Stream():

	while True:
		global automatic
		timestamp = datetime.datetime.now()
		ret, frame = vc.read()  #get live video capture 
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #convert video feed into grayscale
		faces = faceCascade.detectMultiScale(gray, scaleFactor = 2, minNeighbors= 5, minSize=(20,20))  #detect frontal faces from the feed
		ts = timestamp.strftime("%A %d %B %Y %I : %M : %S%p")
		cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		for (x,y,w,h) in faces:
			cv2.rectangle(frame,(x,y), (x+w, y+h), (0,255,0),2)  #for every frontal faces detected on feed place a rectangle
			id, confidence = recognizer.predict(gray[y:y+h, x:x+w])  
			
			
			if (confidence < 100):
				id = names[id]
				recognized = True
				#recognized so turn on green led
				GPIO.output(gLED,GPIO.HIGH)
				GPIO.output(rLED,GPIO.LOW)
				GPIO.output(yLED,GPIO.LOW)
			
			else:
				id = "Unknown"
				recognized = False
				GPIO.output(gLED,GPIO.LOW)
				GPIO.output(rLED,GPIO.LOW)
			
			cv2.putText(frame, str(id), (x+5,y-5), font, 1, (255,255,255),2)
			roi_gray = gray[y:y+h, x:x+w]
			roi_color = frame[y:y+h, x:x+w]
			
			centeredX = False
			centeredY = False

			if(recognized == False):
				GPIO.output(gLED, GPIO.LOW) #not recognized so turn off green led
				
				#centering pan motor
				if((x+w/2 < centerX+15) & (x+w/2 > centerX-15)):
					centeredX = True
				else:
					
					if((automatic == True )& (x+w/2 < centerX+15)):
						Left()
						
					if((automatic == True) & (x+w/2 > centerX-15)):
						Right()
						
				#centering tilt motor
				if((y+h/2 < centerY+12) & (y+h/2 > centerY-12)):
					centeredY = True
				else:
					centeredY = False
					if((automatic == True) & (y+h/2 > centerY+12)):
						Down()
					if((automatic == True) & (y+h/2 < centerY-12)):
						Up()
				#centered, so turn on red led and take screen shot
				if(centeredX & centeredY):
					GPIO.output(rLED,GPIO.HIGH)  #not recognized so turn on red led
					GPIO.output(yLED,GPIO.LOW)

				else:
					GPIO.output(yLED,GPIO.HIGH)  #not recognized and not centered so turn on yellow led
				

		cv2.namedWindow('feed', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('feed', 600,500)
		cv2.imshow('feed', frame)
		
		key = cv2.waitKey(1) & 0XFF
		#keyboard press commands to control motor manually
		
		if (key == ord('w')) & (automatic == False):
			Up()
		elif (key == ord('s')) & (automatic == False):
			Down()
		elif (key == ord('a')) & (automatic == False):
			Left()
		elif (key == ord('d')) & (automatic == False):
			Right()
		elif (key == ord('p')): #p press to take screenshot
			Screenshot()
		elif key == ord('q'):
			vc.release()	
			cv2.destroyAllWindows()
			GPIO.cleanup()
			root.quit()
		else:
			continue

def main():
	
	th = threading.Thread(target=Stream)
	th.setDaemon(True)
	th.start()
	ControlGUI()
		


if __name__ == "__main__":
	main()
	
