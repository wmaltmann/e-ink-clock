import urandom

def generate_uuid():
    b = bytearray(16)
    for i in range(16):
        b[i] = urandom.getrandbits(8)
    b[6] = (b[6] & 0x0F) | 0x40
    b[8] = (b[8] & 0x3F) | 0x80
    
    return ''.join('%02x' % byte for byte in b)
