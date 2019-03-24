import cv2
import os

vc = cv2.VideoCapture(0)
vc.set(3, 400)
vc.set(4, 400)



face_detector = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')

face_id = input('\n Enter user id and press <return> ==> ')

print("\n [INFO] Initializing face capture. Look at the camera and wait ...")

count = 0

while(True):
	ret, frame = vc.read()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faces = face_detector.detectMultiScale(gray, 1.3, 5)
	os.system('cd /home/pi/Desktop/TPJ_AutomaticSurveillanceSystem/dataset')
	for (x,y,w,h) in faces:
		cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
		roi_gray = gray[y:y+h, x:x+w]
		count += 1
		
		cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", roi_gray)
	
	cv2.imshow('feed', frame)
		
	key = cv2.waitKey(1) & 0XFF
	
	if key == ord('q'):
		break
	
	if(count >= 30):
		break
		
		
vc.release()
cv2.destroyAllWindows()
