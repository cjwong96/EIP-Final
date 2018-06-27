
from __future__ import print_function
from pyimagesearch.panorama import Stitcher


import datetime
import time
import cv2
import socket
import numpy


stitcher = Stitcher()
rsp3_IP   = "192.168.1.35"
rsp3_PORT = 8004

rsp4_IP   = "192.168.1.70"
rsp4_PORT = 8005

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def getImg(IP,PORT):
	sock = socket.socket()
	sock.connect((IP, PORT))
	length = recvall(sock,16)
	stringData = recvall(sock, int(length))
	data = numpy.fromstring(stringData, dtype='uint8')
	frame_1=cv2.imdecode(data,1)
	return frame_1
	
def stitching(left, right):
	result = stitcher.stitch([left, right])
	return result
	
	
while True:
		try:
			frame_1 = getImg(rsp3_IP,rsp3_PORT)
		except:
			print("ReConnecting(RSP1,2)")
		try:
			cv2.imshow("Rsp2", frame_1)
		except:
			print("ReStitching(RSP1,2)")
		try:
			frame_2 = getImg(rsp4_IP,rsp4_PORT)
		except:
			print("ReConnecting(RSP3,4)")
		try:
			cv2.imshow("Rsp4", frame_2)
		except:
			print("ReStitching(RSP3,4)")

		try:
			result = stitching(frame_1,frame_2)
		except:
			print("stitch error")
		try:
			cv2.imshow("Result", result)
		except:
			print("Result error")
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
			
print("[INFO] cleaning up...")
cv2.destroyAllWindows()