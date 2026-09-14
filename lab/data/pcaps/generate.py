#!/usr/bin/env python3
# Generates incident.pcap, the sample capture read in lesson 13.
# Author: Ali AlEnezi (SiteQ8)
#
# The capture tells a small, deterministic story:
#   1. 10.13.37.66 SYN scans 10.13.37.10 across common ports.
#   2. 10.13.37.5 logs in to a web app on 10.13.37.10 over cleartext HTTP.
#   3. 10.13.37.5 asks the lab resolver for a name.
# Everything is written by hand so the file is the same on every run and so
# tcpdump and wireshark read it with correct checksums.

import struct

OUT = "incident.pcap"

MAC_SCANNER = bytes.fromhex("0242ac130042")
MAC_CLIENT  = bytes.fromhex("0242ac130005")
MAC_SERVER  = bytes.fromhex("0242ac13000a")
MAC_DNS     = bytes.fromhex("0242ac130001")

IP_SCANNER = "10.13.37.66"
IP_CLIENT  = "10.13.37.5"
IP_SERVER  = "10.13.37.10"
IP_DNS     = "10.13.37.1"

def ip_bytes(a):
    return bytes(int(x) for x in a.split("."))

def csum(data):
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return (~s) & 0xFFFF

def ipv4(src, dst, proto, payload, ident):
    ihl_ver = 0x45
    total = 20 + len(payload)
    hdr = struct.pack("!BBHHHBBH4s4s", ihl_ver, 0, total, ident, 0x4000, 64, proto, 0,
                      ip_bytes(src), ip_bytes(dst))
    chk = csum(hdr)
    hdr = hdr[:10] + struct.pack("!H", chk) + hdr[12:]
    return hdr + payload

def tcp(src, dst, sport, dport, seq, ack, flags, payload=b"", window=64240):
    offset_flags = (5 << 12) | flags
    hdr = struct.pack("!HHIIHHHH", sport, dport, seq, ack, offset_flags, window, 0, 0)
    pseudo = ip_bytes(src) + ip_bytes(dst) + struct.pack("!BBH", 0, 6, len(hdr) + len(payload))
    chk = csum(pseudo + hdr + payload)
    hdr = hdr[:16] + struct.pack("!H", chk) + hdr[18:]
    return hdr + payload

def udp(src, dst, sport, dport, payload):
    length = 8 + len(payload)
    hdr = struct.pack("!HHHH", sport, dport, length, 0)
    pseudo = ip_bytes(src) + ip_bytes(dst) + struct.pack("!BBH", 0, 17, length)
    chk = csum(pseudo + hdr + payload)
    if chk == 0:
        chk = 0xFFFF
    hdr = hdr[:6] + struct.pack("!H", chk)
    return hdr + payload

def frame(dst_mac, src_mac, ippkt):
    return dst_mac + src_mac + b"\x08\x00" + ippkt

SYN, SYNACK, RST, RSTACK, ACK, PSHACK, FINACK = 0x02, 0x12, 0x04, 0x14, 0x10, 0x18, 0x11

packets = []   # (t_sec, t_usec, bytes)
t = [1_757_820_000, 0]   # 2025-09-14 UTC as a fixed epoch base, deterministic
ident = [0x1000]

def tick(us):
    t[1] += us
    while t[1] >= 1_000_000:
        t[0] += 1
        t[1] -= 1_000_000

def emit(dst_mac, src_mac, src, dst, proto, seg, gap_us=1500):
    ident[0] += 1
    pkt = frame(dst_mac, src_mac, ipv4(src, dst, proto, seg, ident[0]))
    packets.append((t[0], t[1], pkt))
    tick(gap_us)

# 1. SYN scan from the scanner to the server.
OPEN = {22, 80, 8080, 8443}
scan_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080, 8443]
sport = 40001
for p in scan_ports:
    seq = 0x11110000 + p
    emit(MAC_SERVER, MAC_SCANNER, IP_SCANNER, IP_SERVER, 6,
         tcp(IP_SCANNER, IP_SERVER, sport, p, seq, 0, SYN), gap_us=800)
    if p in OPEN:
        emit(MAC_SCANNER, MAC_SERVER, IP_SERVER, IP_SCANNER, 6,
             tcp(IP_SERVER, IP_SCANNER, p, sport, 0x22220000 + p, seq + 1, SYNACK), gap_us=300)
        emit(MAC_SERVER, MAC_SCANNER, IP_SCANNER, IP_SERVER, 6,
             tcp(IP_SCANNER, IP_SERVER, sport, p, seq + 1, 0, RST, window=0), gap_us=900)
    else:
        emit(MAC_SCANNER, MAC_SERVER, IP_SERVER, IP_SCANNER, 6,
             tcp(IP_SERVER, IP_SCANNER, p, sport, 0, seq + 1, RSTACK, window=0), gap_us=900)
    sport += 1

tick(2_000_000)

# 2. Cleartext HTTP login from the client to the server.
cs, ss = 0x3333_0000, 0x4444_0000
cport = 52814
emit(MAC_SERVER, MAC_CLIENT, IP_CLIENT, IP_SERVER, 6, tcp(IP_CLIENT, IP_SERVER, cport, 80, cs, 0, SYN))
emit(MAC_CLIENT, MAC_SERVER, IP_SERVER, IP_CLIENT, 6, tcp(IP_SERVER, IP_CLIENT, 80, cport, ss, cs + 1, SYNACK))
emit(MAC_SERVER, MAC_CLIENT, IP_CLIENT, IP_SERVER, 6, tcp(IP_CLIENT, IP_SERVER, cport, 80, cs + 1, ss + 1, ACK))
body = b"user=admin&password=lab-P@ss"
req = (b"POST /login HTTP/1.1\r\nHost: portal.shabakah.lab\r\nUser-Agent: curl/8.5.0\r\n"
       b"Content-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n" % len(body)) + body
emit(MAC_SERVER, MAC_CLIENT, IP_CLIENT, IP_SERVER, 6, tcp(IP_CLIENT, IP_SERVER, cport, 80, cs + 1, ss + 1, PSHACK, req))
emit(MAC_CLIENT, MAC_SERVER, IP_SERVER, IP_CLIENT, 6, tcp(IP_SERVER, IP_CLIENT, 80, cport, ss + 1, cs + 1 + len(req), ACK))
rbody = b"<h1>Welcome admin</h1>\n"
resp = (b"HTTP/1.1 200 OK\r\nServer: Shabakah-Web/1.0\r\nSet-Cookie: session=9c1f7e2a; HttpOnly\r\n"
        b"Content-Type: text/html\r\nContent-Length: %d\r\n\r\n" % len(rbody)) + rbody
emit(MAC_SERVER, MAC_CLIENT, IP_SERVER, IP_CLIENT, 6, tcp(IP_SERVER, IP_CLIENT, 80, cport, ss + 1, cs + 1 + len(req), PSHACK, resp))
emit(MAC_SERVER, MAC_CLIENT, IP_CLIENT, IP_SERVER, 6, tcp(IP_CLIENT, IP_SERVER, cport, 80, cs + 1 + len(req), ss + 1 + len(resp), ACK))
emit(MAC_SERVER, MAC_CLIENT, IP_CLIENT, IP_SERVER, 6, tcp(IP_CLIENT, IP_SERVER, cport, 80, cs + 1 + len(req), ss + 1 + len(resp), FINACK))
emit(MAC_CLIENT, MAC_SERVER, IP_SERVER, IP_CLIENT, 6, tcp(IP_SERVER, IP_CLIENT, 80, cport, ss + 1 + len(resp), cs + 2 + len(req), FINACK))
emit(MAC_SERVER, MAC_CLIENT, IP_CLIENT, IP_SERVER, 6, tcp(IP_CLIENT, IP_SERVER, cport, 80, cs + 2 + len(req), ss + 2 + len(resp), ACK))

tick(500_000)

# 3. A DNS lookup from the client to the lab resolver.
def dns_name(n):
    out = b""
    for part in n.split("."):
        out += bytes([len(part)]) + part.encode()
    return out + b"\x00"

qname = dns_name("update.shabakah.lab")
query = struct.pack("!HHHHHH", 0x5a3c, 0x0100, 1, 0, 0, 0) + qname + struct.pack("!HH", 1, 1)
emit(MAC_DNS, MAC_CLIENT, IP_CLIENT, IP_DNS, 17, udp(IP_CLIENT, IP_DNS, 41022, 53, query))
answer = (struct.pack("!HHHHHH", 0x5a3c, 0x8180, 1, 1, 0, 0) + qname + struct.pack("!HH", 1, 1)
          + b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 300, 4) + ip_bytes("10.13.37.30"))
emit(MAC_CLIENT, MAC_DNS, IP_DNS, IP_CLIENT, 17, udp(IP_DNS, IP_CLIENT, 53, 41022, answer))

with open(OUT, "wb") as fh:
    fh.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    for sec, usec, data in packets:
        fh.write(struct.pack("<IIII", sec, usec, len(data), len(data)))
        fh.write(data)

print("wrote %s with %d packets" % (OUT, len(packets)))
