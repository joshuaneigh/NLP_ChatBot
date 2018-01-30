#!/usr/bin/python
# Author: Joshua Neighbarger
# Version: 30 January 2018
# Email: jneigh@uw.edu

import threading
import socket
import hashlib
import base64
import time
import sys

MAGIC = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
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


def get_str_from_socket_data(data):
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


def message_client(conn, message):
    resp = bytearray([0b10000001, len(message)])
    for d in bytearray(message, 'utf-8'):
        resp.append(d)
    conn.sendall(resp)


def handle_client(conn, addr):
    print(addr, "Connection opened. Waiting for nickname...")
    CLIENTS[addr] = conn
    name = ""
    while 1:
        try:
            data = conn.recv(4096)
            if (not data) or (data[0] == 0x88 and data[1] == 0x82):
                print(addr, "Disconnected with null response")
                break
            elif not len(name):
                name = get_str_from_socket_data(data)
                print(addr, "Connected as", name)
            else:
                print(name, ": ", get_str_from_socket_data(data), sep="")
        except socket.timeout:
            continue
        except ConnectionResetError:
            break
        except OSError:
            break

    conn.close()
    THREADS.remove(threading.current_thread())  # TODO: Figure out why threads aren't removed from list
    CLIENTS.pop(addr, None)
    if name:
        print(addr, "Disconnected as", name)


def handshake(conn):
    data = conn.recv(4096)
    headers = {}
    lines = data.splitlines()
    for l in lines:
        parts = l.decode('utf-8').split(": ")
        if len(parts) == 2:
            headers[parts[0]] = parts[1].encode('utf-8')
    headers['code'] = lines[len(lines) - 1]
    key = headers['Sec-WebSocket-Key']
    resp_data = HANDSHAKE_RESP % (base64.b64encode(hashlib.sha1(key + MAGIC).digest()),)
    conn.send(resp_data)


def acquire_socket():
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


def handle_server(s):
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


def launch():
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
