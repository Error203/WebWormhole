# coding: utf-8
# Version 1.0. Simple testing beta client.

import socket # to work with TCP connections and UDP.
import logging # to catch the errors
from os import mkdir, listdir, path # to create and monitor content of the root directory
from time import strftime # to get formated time for log file name
from sys import argv # terminal arguments

# --- THIS PART OF CODE WAS TAKEN FROM OTHER CODE AND EDITED ---
if "Logs Client" not in listdir("."):
	mkdir("Logs Client") # if there is no Logs Client directory in the root

def get_logger(name: str=__name__) -> logging.Logger:
	"""
	Get simple logger.
	"""
	file_name = strftime("[%d-%m-%y] %H-%M-%S.log") # name of logger, can be changed

	logger = logging.getLogger(name) # logger
	logger.setLevel(logging.DEBUG) # set level of general logger
	stream_handler = logging.StreamHandler() # stream handler to monitor errors to the console
	file_handler = logging.FileHandler(path.join("Logs Client", file_name)) # write errors and info to the file

	formatter = logging.Formatter(fmt="%(asctime)s : %(levelname)s, %(name)s -> %(message)s") # format of logs

	stream_handler.setFormatter(formatter) # setting format
	file_handler.setFormatter(formatter) # ^^^

	stream_handler.setLevel(logging.DEBUG) # setting level debug to debug this code
	file_handler.setLevel(logging.DEBUG) # ^^^

	logger.addHandler(stream_handler) # add handler to handle exceptions
	logger.addHandler(file_handler) # ^^^

	return logger # return ready logger to work with
# --- END OF TAKEN CODE ---

try:
	root_logger = get_logger("ROOT") # root logger

except Exception as e:
	print("Critical error. Rewrite the code.") # notice
	print(e) # monitor exception

	exit(1) # unknown error

else:
	root_logger.info("Logger initialized.") # if everything is okay.

class Client:
	def __init__(self, remote_ip: str, remote_port: int):
		"""
		Client is created to connect to the server and accept
		and receive data from it.
		"""
		self.remote_ip = remote_ip # ip to connect to
		self.remote_port = remote_port # port to connect to
		self.logger = get_logger("Client") # creating Client logger


	def connect(self):
		"""
		Establish connection with server.
		"""
		try:
			self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initializing TCP connection, not UDP.
			self.client.settimeout(3) # setting time out to 3, beacuse we don't want to wait a lot of time.
			self.client.connect((self.remote_ip, self.remote_port)) # establish connection to server.
			self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # setting options for socket

		except KeyboardInterrupt:
			self.logger.info("User terminated. Closing the connection.") # info

			self.client.close() # close the connection

			exit(2) # 2 - user terminated

		except socket.timeout:
			self.logger.warning("Timed out while trying to connect to server. Shutting down client.")

			self.client.close()

			exit(3) # 3 - timed out

		except Exception as e:
			self.logger.exception(e) # monitor exception

			self.client.close() # closing connection

			exit(1) # unknown error

		else:
			self.logger.info(f"Connection established with {self.remote_ip}:{self.remote_port}") # info


	def listen_incoming_data(self):
		"""
		Listening for incoming data from the server.
		It should be packets of bytes by 4096.
		"""
		try:
			data = self.client.recv(4096) # get packets of bytes

			if len(data) < 4096:
				self.logger.info(f"Got packet with size {len(data)}. Writing on disk...") # info
				with open("test.txt", "wb") as file:
					file.write(data) # writes data to the file once.

					self.logger.info(f"Wrote {len(data)} bytes into the file.") # info

				self.client.send(b"END")

			else:
				self.logger.info(f"File size is 4096 or more. Capturing packets...") # info

				file = open("test.txt", "wb") # we don't want to open file each time with "ab" to write this. So that's buffer file.

				file.write(data) # write first data to file

				while True:
					data = self.client.recv(4096) # accepting packets of bytes

					if not data:
						self.logger.info("No more data. Buffered file was written.") # info

						file.close() # closing buffer

						self.client.send(b"END")
						
						break # breaking out of the loop

					self.logger.debug(f"Got {len(data)} bytes of data. Writing...") # info

					file.write(data) # writing to buffer

					self.client.send(b"ACK")


		except KeyboardInterrupt:
			self.logger.info("User terminated. Closing the connection.") # info

			self.client.close() # close the connection
			file.close() # close buffered file

			exit(2) # 2 - user terminated

		except socket.timeout:
			self.logger.warning("Timed out while accepting data from server. Shutting down client.")

			self.client.close()

			exit(3) # 3 - timed out

		except Exception as e:
			self.logger.exception(e) # monitor exception

			self.client.close() # closing the connection
			file.close() # close buffered file

			exit(1) # unknown error


# testing area
if __name__ == '__main__':
	if len(argv) != 3 or len(argv) <= 2:
		print(f"Usage: {argv[0]} [IP_ADDRESS] [PORT]\nAllows you to connect to webwormhole_server.py")
	else:
		ip_address = argv[1]
		port = int(argv[2])
		client = Client(ip_address, port)
		client.connect()
		client.listen_incoming_data()