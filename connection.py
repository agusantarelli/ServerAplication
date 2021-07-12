# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
from base64 import b64encode
import os


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):

        self.conn, self.client = socket.accept()
        self.dir = directory
        self.error_count = 0

    def file_listing(self):
        try:
            entries = os.listdir(str(self.dir))
            msg = str(CODE_OK) + " " + str(error_messages[CODE_OK]) + EOL
            for e in entries:
                msg += (str(e) + EOL)
            msg += EOL

        except BaseException:
            msg = str(INTERNAL_ERROR) + " " + \
                str(error_messages[INTERNAL_ERROR]) + EOL

        return msg

    def get_size(self, file):

        filename = self.dir + '/' + file

        try:
            if len(file) < 256:
                sizeoffile = os.stat(filename).st_size
                msg = str(CODE_OK) + " " + str(error_messages[CODE_OK]) + EOL
                msg += str(sizeoffile) + EOL
            else:
                msg = str(FILE_NOT_FOUND) + " " + \
                    str(error_messages[FILE_NOT_FOUND]) + EOL
                self.error_count += 1

        except BaseException:
            msg = str(FILE_NOT_FOUND) + " " + \
                str(error_messages[FILE_NOT_FOUND]) + EOL
            self.error_count += 1
        return msg

    def do_slice(self, file, begin, end):

        filename = self.dir + '/' + file

        try:

            sizeoffile = os.stat(filename).st_size

            if(int(begin) < sizeoffile and int(end) <= sizeoffile):
                f = open(filename, "rb")
                f.seek(begin)
                message = f.read(end)
                msg = b64encode(message) + (EOL.encode("ascii"))
                f.close()
            else:
                msg = str(BAD_OFFSET) + " " + \
                    str(error_messages[BAD_OFFSET]) + EOL
                self.error_count += 1

        except BaseException:
            msg = str(INTERNAL_ERROR) + " " + \
                str(error_messages[INTERNAL_ERROR]) + EOL

        return msg

    def quit(self):
        return str(CODE_OK) + " " + str(error_messages[CODE_OK]) + EOL

    def eol_incomplete(self, data):
        if(len(data) > 1):
            for i in range(0, len(data) - 1):
                if data[i] == '\r' and data[i + 1] != '\n':
                    return True
                elif data[i] == '\n' and data[i - 1] != '\r':
                    return True
            return False
        return False

    def multiple_commands(self, data):
        data_line = data.split(EOL)
        return data_line

    def ok_command(self, command):

        if(command[0] in ['get_file_listing', 'get_metadata', 'get_slice', 'quit']):
            return True
        else:
            return False

    def ok_arguments(self, command):
        if command[0] == 'get_file_listing':
            if len(command) == 1:
                return True
            else:
                return False
        elif command[0] == 'get_metadata':
            if (len(command) == 2):
                return True
            else:
                return False
        elif command[0] == 'get_slice':
            if(len(command) == 4):
                return True
            else:
                return False
        elif command[0] == 'quit':
            if len(command) == 1:
                return True
            else:
                return False

    def do_command(self, command):
        connected = True
        if(command[0] == 'get_file_listing'):
            msg = self.file_listing()

            self.conn.send(msg.encode("ascii"))
            if(msg == str(INTERNAL_ERROR) + " " + str(error_messages[INTERNAL_ERROR]) + EOL):
                self.conn.close()
                connected = False

        elif(command[0] == 'get_metadata'):

            try:

                # Debe venir el mensaje completo con codigo de error.
                msg = self.get_size(command[1])

                self.conn.send(msg.encode("ascii"))

            except BaseException:
                msg = str(INVALID_ARGUMENTS) + " " + \
                    str(error_messages[INVALID_ARGUMENTS]) + EOL
                self.error_count += 1
                self.conn.send(msg.encode("ascii"))

        elif(command[0] == 'get_slice'):

            if len(command) < 4:
                msg = self.quit()
                self.conn.send(msg.encode('ascii'))
                self.conn.close()
                connected = False
            else:
                try:
                    begin = int(command[2])
                    size = int(command[3])
                    msg = self.do_slice(command[1], begin, size)

                    if(msg == str(INTERNAL_ERROR) + " " + str(error_messages[INTERNAL_ERROR]) + EOL):
                        self.conn.send(msg.encode("ascii"))
                        self.conn.close()
                        connected = False
                    else:
                        self.conn.send(("0 OK" + EOL).encode("ascii"))
                        self.conn.send(msg)

                except ValueError:
                    msg = str(INVALID_ARGUMENTS) + " " + \
                        str(error_messages[INVALID_ARGUMENTS]) + EOL
                    self.error_count += 1
                    try:
                        self.conn.send(msg.encode("ascii"))
                    except BaseException:
                        pass

        elif(command[0] == 'quit'):
            if (len(command) == 1):
                msg = self.quit()
                self.conn.send(msg.encode('ascii'))
                self.conn.close()
                connected = False
            else:
                msg = str(INVALID_ARGUMENTS) + " " + \
                    str(error_messages[INVALID_ARGUMENTS]) + EOL
                self.error_count += 1
                self.conn.send(msg.encode("ascii"))

        return connected

    def handle(self):

        connected = True
        data_buffer = ""
        while connected:
            try:
                data = self.conn.recv(BUFFER_SIZE)
                if not data:
                    self.conn.close()
                    connected = False
                    break
                try:
                    data_buffer += data.decode('ascii')
                except BaseException:
                    msg = str(BAD_REQUEST) + " " + \
                        str(error_messages[BAD_REQUEST]) + EOL
                    self.conn.send(msg.encode("ascii"))
                    self.conn.close()

                if self.error_count >= MAX_ERROR:
                    msg = str(BAD_REQUEST) + " " + \
                        str(error_messages[BAD_REQUEST]) + EOL
                    self.conn.send(msg.encode("ascii"))
                    self.conn.close()
                    connected = False
                    break

                if EOL in data_buffer:
                    if (self.eol_incomplete(data_buffer)):
                        msg = str(BAD_EOL) + " " + \
                            str(error_messages[BAD_EOL]) + EOL
                        self.conn.send(msg.encode("ascii"))
                        self.conn.close()
                        connected = False
                        break
                    buf = self.multiple_commands(data_buffer)
                    for i in range(0, len(buf)):

                        data_parsed = buf[i].split()
                        if(len(data_parsed) > 0):
                            if(self.ok_command(data_parsed)):
                                if(self.ok_arguments(data_parsed)):
                                    if(i == len(buf)):
                                        data_buffer = ""
                                    connected = self.do_command(data_parsed)
                                else:
                                    msg = str(INVALID_ARGUMENTS) + " " + \
                                        str(error_messages[INVALID_ARGUMENTS]) + EOL
                                    self.error_count += 1
                                    self.conn.send(msg.encode("ascii"))

                            elif i == len(buf) and i > 1:
                                resto = buf[i]
                                data_buffer = resto
                            else:
                                msg = str(INVALID_COMMAND) + " " + \
                                    str(error_messages[INVALID_COMMAND]) + EOL
                                self.error_count += 1
                                self.conn.send(msg.encode("ascii"))
                        else:
                            data_buffer = ""

            except ConnectionResetError:
                self.conn.close()
                connected = False
                break

        return connected

        """
        Atiende eventos de la conexión hasta que termina.
        """
