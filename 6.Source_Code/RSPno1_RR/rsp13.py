import socket
import cv2
import numpy

capture = cv2.VideoCapture(0)
TCP_IP = "192.168.0.111"
TCP_PORT = 8002

while True:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(5)
	print("start socket")
	conn, addr = s.accept()

	ret, frame = capture.read()
	
	encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]

	while ret :
		result, imgencode = cv2.imencode('.jpg', frame, encode_param)
		data = numpy.array(imgencode)
		stringData = data.tostring()
		conn.send( str(len(stringData)).ljust(16) )
		conn.send( stringData )
		
		ret, frame = capture.read()

		decimg=cv2.imdecode(data,1)
		cv2.imshow('SERVER2',decimg)
		cv2.waitKey(30)
		
		key = cv2.waitKey(1) & 0xFF
		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break
				
	conn.close()
	cv2.destroyAllWindows()