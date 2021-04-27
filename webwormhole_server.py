# coding: utf-8
# Version 1.0. Working with one client.

import socket # to work with net
import logging # to catch the errors
from os import mkdir, listdir, path # to create and monitor content of the root directory
from time import strftime # to get formated time for log file name
from sys import argv # get arguments from user

# --- THIS PART OF CODE WAS TAKEN FROM OTHER CODE ---
if "Logs" not in listdir("."):
	mkdir("Logs") # if there is no Logs directory in the root

def get_logger(name: str=__name__) -> logging.Logger:
	"""
	Get simple logger.
	"""
	file_name = strftime("[%d-%m-%y] %H-%M-%S.log") # name of logger, can be changed

	logger = logging.getLogger(name) # logger
	logger.setLevel(logging.DEBUG) # set level of general logger
	stream_handler = logging.StreamHandler() # stream handler to monitor errors to the console
	file_handler = logging.FileHandler(path.join("Logs", file_name)) # write errors and info to the file

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
	root_logger = get_logger("ROOT") # try to get ROOT logger

except Exception as e:
	print("Critical error. Rewrite code.") # if something went wrong, you should rewrite the code
	print(e) # monitor error

	exit(1) # unknown error

else:
	root_logger.info("Logger initialized.") # info about starting logger successfully

class Server:
	def __init__(self, ip: str, port: int, max_clients: int) -> object:
		"""
		Returns Server object to work with.
		Do with it whatever you want.
		"""
		self.ip = ip # ip address of the host
		self.port = port # port to listen and work on
		self.max_clients = max_clients # maximum clients to listen to.
		self.clients = list() # list of clients, it's global because more than one functions need this list
		self.logger = get_logger("Server") # get exception handler for Server class


	def send_file(self, filename: str):
		# BETA FUNCTION TESTING
		try:
			array = list() # local array for splitting bytes by groups of 4096 bytes

			with open(filename, "rb") as file:
				data = file.read() # bytes
				self.logger.info(f"Size of file is {len(data)} bytes.") # info

				if len(data) <= 4096:
					self.logger.info("No need splitting file by packets. Sending raw.") # info
					self.clients[0].send(data) # send if size is already 4096 bytes or less without partitioning

				else:
					self.logger.info("Splitting packages into an array...") # info
				
					for packet in range(0, len(data) + 1, 4096):
						array.append(data[packet:packet + 4096]) # packet gives us a continue value
						self.logger.debug(f"The number is {packet} and the next is {packet + 4096}.")

					for package in array:
						self.clients[0].send(package) # send packages to the client

						self.logger.debug(f"Successfully sent package of {len(package)} bytes.") # debug

		except KeyboardInterrupt:
			self.logger.info("User terminated. Shutting down server.") # info

			self.server.close() # close the server

			exit(2) # 2 - user terminated

		except Exception as e:
			self.logger.exception(e) # monitor exception

			self.server.close()

			exit(1) # unknown error

		else:
			self.server.close() # closing server to serve this ip and port later.


	def listening(self) -> None:
		# BETA FUNCTION WITHOUT THREADING
		for i in range(self.max_clients):
			try:
				self.logger.info("Listening for incoming connection...") # info
				client, address = self.server.accept() # try to get clients to work with
				self.logger.info(f"{address[0]} connected to port {address[1]}.") # info
				self.clients.append(client) # append client to the list
				self.logger.debug(f"Appended {self.clients}.") # debug info
				self.logger.debug(f"Here the list:\n{self.clients}\n") # debug info

			except KeyboardInterrupt:
				self.logger.info("User terminated. Shutting down the server.") # if user wants to shutdown everything

				self.server.close()

				exit(2) # 2 - user terminated

			except Exception as e:
				self.logger.exception(e) # if there are any exceptions

				self.server.close()

				exit(1) # unknown error


	def run(self):
		"""
		Starts the server.
		Starting socket and listening.
		"""
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # for working via TCP connection, not UDP.
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # setting up "recycling"
			self.server.bind((self.ip, self.port)) # try to bind to ip address
			self.server.listen(1) # listen for x clients

		except KeyboardInterrupt:
			self.logger.info("User terminated. Shutting down the server.") # if user wants to stop the program

			self.server.close() # closing server and breaking the connection

			exit(2) # 2 - user terminated

		except Exception as e:
			self.logger.exception(e) # if there are any exceptions

			self.server.close()

			exit(1) # unknown error

		else:
			self.logger.info(f"Started server on {self.ip}:{self.port}") # info for logger

			if self.max_clients == 1:
				self.logger.info(f"Listening for {self.max_clients} client.") # just a logic for user
			else:
				self.logger.info(f"Listening for {self.max_clients} clients.") # just another logic

			self.listening() # listening for incoming, returns None because we have self.clients list


# test area
if __name__ == '__main__':
	server = Server(argv[1], argv[2], 5)
	server.run()
	server.send_file("hWsCrCvkJKUFj.jpg")