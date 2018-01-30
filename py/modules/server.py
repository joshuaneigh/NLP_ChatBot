from threading import Thread
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
CLIENTS = []


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
    while 1:
        try:
            data = conn.recv(4096)
        except ConnectionResetError:
            break
        if not data:
            break
        print(addr, ": ", get_str_from_socket_data(data), sep="")
        message_client(conn, "Message received")
    print("Connection closed by", addr)
    conn.close()


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
    resp_data = HANDSHAKE_RESP % ((base64.b64encode(hashlib.sha1(key + MAGIC).digest()),))
    conn.send(resp_data)


def launch():
    acquire_notified = False
    print("Starting server...")
    while 1:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST, PORT))
            s.listen(5)
            break
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
    if acquire_notified:
        print()
    while 1:
        print("Listening for connection on port", PORT, "...", sep=" ")
        conn, addr = s.accept()
        handshake(conn)
        print('Connected opened by', addr)
        Thread(target=handle_client, args=(conn, addr)).start()

# TODO: Close listening socket from another thread to cancel s.accept()
