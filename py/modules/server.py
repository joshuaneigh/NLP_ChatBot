#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Joshua Neighbarger
# Version: 30 January 2018
# Email: jneigh@uw.edu

""" WebSocket Server

This module demonstrates and handles an HTML client and Python server interaction through use of WebSockets. Each
client communicates with the server through its own listener thread on the specified network port by first sending
its nickname, followed by any plaintext (yet encoded) messages it wishes to send. The server outputs these messages
to its console and can interact through any of the following commands:

    "q": Quits/Kills the server and disconnects all clients
    other: Sends typed message to all clients

Attributes:
    GUID (str): Globally Unique Identifier is used to add a false sense of integrity to the WebSocket protocol.
    HANDSHAKE_RESP (str): HTTP handshake response format. Necessary for client to recognize connection as valid.
    HOST (str): The hostname which this server is run on. If localhost, leave as a null string.
    PORT (str): The statically defined port on which the server will be hosted
    CLIENTS (dict): Maps all client addresses/names to their respective connection.
    THREADS (list): Contains all active Threads currently running from this module.

Todo:
    * Add returns definitions to docstrings
    * Adapt server to use SSL/TLS encryption and secure sockets
    * Abstract data into Python objects

"""

import threading
import socket
import hashlib
import base64
import time
import sys
import importlib
import os

GUID = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_RESP = \
    b"HTTP/1.1 101 Switching Protocols\r\n" + \
    b"Upgrade: websocket\r\n" + \
    b"Connection: Upgrade\r\n" + \
    b"Sec-WebSocket-Accept: %s\r\n" + \
    b"\r\n"
HOST = b''
PORT = 9876
CLIENTS = {}
THREADS = []


def get_str_from_socket(data: str):
    """Encodes and unmasks str object from the passed HTTP response.

    Args:
        data: The decoded and masked byte string data from the HTTP client.

    Returns:
        Plaintext Python str
    """
    # data comes in as byte_string
    data_byte = bytearray(data)
    # data_len is the length of the string
    data_len = (0x7F & data_byte[1])
    str_data = ''
    if data_len > 0:
        mask_key = data_byte[2:6]
        masked_data = data_byte[6:(6 + data_len)]
        unmasked_data = [masked_data[i] ^ mask_key[i % 4] for i in range(len(masked_data))]
        str_data = str_data.join(map(chr, unmasked_data))
    return str_data


def message_client(conn: socket, message: str):
    """Sends decoded string to client on given socket.

    Args:
        conn: The client's respective connection.
        message: The encoded string message which will be sent.

    Returns:
        None
    """
    resp = bytearray([0b10000001, len(message)])
    for d in bytearray(message, 'utf-8'):
        resp.append(d)
    conn.sendall(resp)
    print(conn.getpeername(), "Server:", message)


def handle_client(conn: socket, addr: tuple):
    """Handles messages from client at the given socket and address.

    The first response is decoded and used to reference the client with a preferred "nickname" instead of their address
    for front-facing applications.

    Args:
        conn: The client's respective connection.
        addr: The address at which the client is connected. The tuple contains the client's IP address, followed by
            their socket number.

    Returns:
        None
    """
    print(addr, "Connection opened. Waiting for nickname...")
    CLIENTS[addr] = conn
    name = ""
    while 1:
        try:
            data = conn.recv(4096)
            if (not data) or (data[0] == 0x88 and data[1] == 0x82):
                break
            elif not len(name):
                name = get_str_from_socket(data)
                print(addr, "Connected as", name)
            else:
                message = get_str_from_socket(data)
                print(conn.getpeername(), ' ', name, ": ", message, sep='')
                message_client(conn, generate_message_response(message))
        except socket.timeout:
            continue
        except ConnectionResetError:
            break
        except OSError:
            break

    conn.close()
    THREADS.remove(threading.current_thread())
    CLIENTS.pop(addr, None)
    if name:
        print(addr, "Disconnected as", name)
    else:
        print(addr, "Disconnected with null response")


def handshake(conn: socket):
    """Sends HTTP handshake response to HTML WebSocket so that the connection is accepted by the client.

    Args:
        conn: The client's respective connection.

    Returns:
        None
    """
    data = conn.recv(4096)
    headers = {}
    lines = data.splitlines()
    for l in lines:
        parts = l.decode('utf-8').split(": ")
        if len(parts) == 2:
            headers[parts[0]] = parts[1].encode('utf-8')
    headers['code'] = lines[len(lines) - 1]
    key = headers['Sec-WebSocket-Key']
    resp_data = HANDSHAKE_RESP % (base64.b64encode(hashlib.sha1(key + GUID).digest()),)
    conn.send(resp_data)


def acquire_socket() -> socket:
    """Continually tries to start the server on the globally defined socket. Returns the socket when it is opened.

    Returns:
        The acquired server socket.
    """
    acquire_notified = False
    while 1:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST, PORT))
            s.listen(5)
            if acquire_notified:
                print()
            return s
        except OSError:
            if acquire_notified:
                sys.stdout.write(".")
                sys.stdout.flush()
            else:
                print("Acquiring port...", end="")
                sys.stdout.flush()
                acquire_notified = True
            time.sleep(3)  # 3 seconds
            continue


def handle_server(s: socket):
    """Listens for new connections to this server.

    Handles new clients by establishing their connection and creating a threaded handler for each client to listen for
    responses or messages.

    Args:
        s: The socket on which the server will listen for new clients.

    Returns:
        None
    """
    print("Server established on port", PORT)
    while 1:
        try:
            conn, addr = s.accept()
            handshake(conn)
            conn.settimeout(5)
            t = threading.Thread(target=handle_client, args=(conn, addr))
            THREADS.append(t)
            t.start()
        except ConnectionAbortedError:
            print("Socket closed by server")
            break


def start_server():
    """ Starts the server.

    Returns:
        None
    """
    print("\nStarting server...")
    s = acquire_socket()
    server_thread = threading.Thread(target=handle_server, args=(s,))
    THREADS.append(server_thread)
    server_thread.start()
    while 1:
        i = input().strip()
        if i == "q" or i == "quit":
            print("Killing server with", len(THREADS), "threads and", len(CLIENTS), "clients...")
            s.close()
            for client in CLIENTS:
                CLIENTS[client].close()
            for t in THREADS:
                t.join()
            print("Server terminated\n")
            return
        else:
            for client in CLIENTS:
                message_client(CLIENTS[client], i)
            print("Successfully messaged", len(CLIENTS.keys()), "client(s)")


def generate_message_response(message: str):
    return NLP_MODEL.findResponse(message)
    # return "How are you?"


def get_commands():
    """Defines commands for this module.

    Returns:
        Dictionary of commands related to this module
    """
    return {"start_server": (start_server, 0, "Starts the message server.")}


def launch():
    """The main method.

    Returns:
        None
    """
    start_server()


if os.path.exists(os.path.abspath(os.path.join(__file__, '../../model.p'))):
    NLP_MODEL = importlib.import_module("_model", "../objects").unpickleModel()
    pass
else:
    NLP_MODEL = importlib.import_module("_model", "../objects").generate()
    pass
