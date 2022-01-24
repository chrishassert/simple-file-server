#!/usr/bin/env python3

# Code written by Christopher Hassert (ch8jd)
# On my honor as student, I have neither given nor received aid on this assignment


import socket
import sys
import select
from queue import Queue

from file_reader import FileReader


class Jewel:

    def __init__(self, port, file_path, file_reader):
        self.file_path = file_path
        self.file_reader = file_reader

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.bind(('0.0.0.0', port))

        s.listen(5)
        # (client, address) = s.accept()

        inputs = [s]
        outputs = []
        message_queues = {}

        while True:
            # boolean values to check for valid HTTP request
            httpCommandCheck = False
            requestedFileCheck = False
            httpVersionCheck = False
            try:
                readable, writable, exceptional = select.select(
                    inputs, [], [])
            except:
                del inputs[-1]
            for x in readable:
                if x is s:
                    client, address = x.accept()
                    client.setblocking(0)
                    inputs.append(client)
                    message_queues[client] = Queue()
                else:
                    data = client.recv(1024)
                    message_queues[client].put(data)
                    if client not in outputs:
                        outputs.append(client)
                    else:
                        if client in outputs:
                            outputs.remove(client)
                        inputs.remove(client)
                        client.close()
                        del message_queues[client]
            try:
                data = client.recv(1024)
            except:
                continue
            sys.stdout.write(
                ('[CONN] Connection from ' + str(address[0]) + ' on port ' + str(address[1]) + '\n'))

            if not data:
                break

            data = data.decode()

            # Splits the string after the first space to get the HTTP command (GET/HEAD)
            try:
                request_type = data.split(' ', 1)
                request_type = request_type[0]
                httpCommandCheck = True
            except:
                httpCommandCheck = False

            # Splits the string after space to get the filename
            try:
                requested_file = data.split(' ', 2)
                requested_file = requested_file[1]
                requestedFileCheck = True
            except:
                requestedFileCheck = False

            # Splits the string after space to get the HTTP version
            try:
                requested_version = data.split(' ', 3)
                requested_version = requested_version[2].split('\r', 1)[0]
                # checks to make sure HTTP version is valid
                if(requested_version == 'HTTP/0.9' or requested_version == 'HTTP/1.0' or requested_version == 'HTTP/1.1' or requested_version == 'HTTP/2.0'):
                    httpVersionCheck = True
            except:
                httpVersionCheck = False

            # checking for cookies
            try:
                cookies = data.split('Cookie: ')[-1]
            except:
                # no cookies available
                cookies = ''

            try:
                thePath = file_path + requested_file
            except:
                requestedFileCheck = False

            sys.stdout.write(('[REQU] [' + str(address[0]) + ':' + str(address[1]) +
                              '] ' + request_type + ' request for ' + requested_file + '\n'))

            messageBody = file_reader.get(thePath, cookies)
            fileSize = file_reader.head(thePath, cookies)
            mimeType = file_reader.getMime(thePath)

            directoryExists = file_reader.checkPath(thePath)

            # pass the request type to a function to create the header, then encode it
            if(messageBody is None):
                response = self.createHTTPHeader(
                    request_type, False, address, fileSize, mimeType).encode()
                if request_type == 'GET' and not directoryExists:
                    response = 'HTTP/1.1 404 Not Found\n\n'

                    response += '<html><h1> 404 Not Found </h1></html>'
                    response = response.encode()
                    sys.stdout.write(('[ERRO] [' + str(address[0]) + ':' + str(
                        address[1]) + '] ' + request_type + ' request returned error ' + '404' + '\n'))
                elif (request_type != 'HEAD') and (request_type != 'GET'):
                    pass
                else:
                    response = 'HTTP/1.1 200 OK\n\n'
                    response += ('<html><body><h1>' + file_path +
                                 requested_file + '</h1></body></html>')
                    response = response.encode()
            else:
                response = self.createHTTPHeader(
                    request_type, True, address, fileSize, mimeType).encode()
                if(request_type == 'GET'):  # only send body if a GET
                    response += messageBody
            # this checks for a bad request, if so, respond with error code 400
            if(not(httpCommandCheck and httpVersionCheck and requestedFileCheck)):
                response = 'HTTP/1.1 400 Bad Request\n'
                response += 'Connection: close \n\n'
                response = response.encode()

            client.send(response)
            client.close()
        s.close()

    def createHTTPHeader(self, command, fileExist, address, fileSize, mimeType):
        response = ''
        if command != 'GET' and command != 'HEAD':
            response = 'HTTP/1.1 501 Method Unimplemented\n'
            response += 'Connection: close\n\n'
            sys.stdout.write(('[ERRO] [' + str(address[0]) + ':' + str(address[1]) +
                              '] ' + command + ' request returned error ' + '501' + '\n'))
        elif not fileExist:
            response += 'HTTP/1.1 404 Not Found\n'
            response += 'Connection: close\n\n'
        elif command == 'GET':
            response += 'HTTP/1.1 200 OK\n'
            response += 'Server: Jewel Python3\n'
            response += 'Content-Type: ' + mimeType + '\n'
            response += 'Content-Length: ' + str(fileSize) + '\n'
            response += 'Connection: close\n\n'
        elif command == 'HEAD':
            response += 'HTTP/1.1 200 OK\n'
            response += 'Server: Jewel Python3\n'
            response += 'Content-Type: ' + mimeType + '\n'
            response += 'Content-Length: ' + str(fileSize) + '\n'
            response += 'Connection: close\n\n'
        return response


if __name__ == "__main__":
    port = int(sys.argv[1])
    file_path = sys.argv[2]

    FR = FileReader()

    J = Jewel(port, file_path, FR)
