import socket,hashlib,base64
from threading import Thread

MAGIC = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HSHAKE_RESP = b"HTTP/1.1 101 Switching Protocols\r\n" + \
            b"Upgrade: websocket\r\n" + \
            b"Connection: Upgrade\r\n" + \
            b"Sec-WebSocket-Accept: %s\r\n" + \
            b"\r\n"
HOST = b''
PORT = 9876
CLIENTS = []


def handle_client(conn, addr):
    while 1:
        data = conn.recv(4096)
        if not data:
            break
        databyte = bytearray(data)
        datalen = (0x7F & databyte[1])
        str_data = ''
        if(datalen > 0):
            mask_key = databyte[2:6]
            masked_data = databyte[6:(6+datalen)]
            unmasked_data = [masked_data[i] ^ mask_key[i%4] for i in range(len(masked_data))]
            str_data = str_data.join(map(chr, unmasked_data))
        print(str(addr) + ": " + str_data)
        resp = bytearray([0b10000001, len(str_data)])
        for d in bytearray(str_data, 'utf-8'):
            resp.append(d)
        conn.sendall(resp)
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
    resp_data = HSHAKE_RESP % ((base64.b64encode(hashlib.sha1(key+MAGIC).digest()),))
    conn.send(resp_data)


def launch():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    conn, addr = s.accept()
    handshake(conn)
    print('Connected by', addr)
    Thread(target=handle_client, args=(conn, addr)).start()
