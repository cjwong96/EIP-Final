# USAGE
# python realtime_stitching.py

# import the necessary packages
from __future__ import print_function
from pyimagesearch.panorama import Stitcher


import datetime
import time
import cv2
import socket
import numpy

stitcher = Stitcher()
sock = socket.socket()
cap_1 = cv2.VideoCapture(0)
	
	
Self_IP = "192.168.0.107"
Self_PORT = 8004

Pre_IP = "192.168.0.108"
Pre_PORT = 8002

sock.connect((Pre_IP, Pre_PORT))

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def getres(cap_1):
	try:
		length = recvall(sock,16)
		stringData = recvall(sock, int(length))
		data = numpy.fromstring(stringData, dtype='uint8')
		frame_1=cv2.imdecode(data,1)
		print("[INFO]get Previous image ")
	except:
		print("[INFO]get Previous image failed")
		
	try:
		ret_1, frame_2 = cap_1.read()
		print("[INFO]get camera image ")
	except:
		print("[INFO]get camera image failed")
		
	
	# resize the frames
	left = cv2.resize(frame_2, (400,300))
	right = cv2.resize(frame_1, (400,300))
	try:
		result = stitcher.stitch([left, right])
		print("[INFO]Stitch success")
	except:
		print("[INFO]Stitch Failed")
		return

	cv2.imshow("Left Frame", left)
	cv2.imshow("Right Frame", right)
	return result


def sendres(frame):

	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((Self_IP, Self_PORT))
	s.listen(5)
	print("start socket")
	conn, addr = s.accept()

	encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]

	try:
		result, imgencode = cv2.imencode('.jpg', frame, encode_param)
		data = numpy.array(imgencode)
		stringData = data.tostring()
		print("encoding success")
	except:
		print("encoding Failed")
	try:
		print()
		conn.send( str(len(stringData)).ljust(16))
		conn.send( stringData )
		print("sending success")
	except:
		print("sending Failed")
	print("send over")		
				
	conn.close()

	
while True:
	
	result = getres(cap_1)
	cv2.imshow("Result", result)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
	sendres(result)
	print("send reult Failded")
	
	
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
cap_1.release()
