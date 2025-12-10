"""
Lightweight XDR packing and unpacking helpers.

Vendored because Python 3.13 removed the stdlib xdrlib module.
Implements the subset used by NfSpy (uint/int/enum/bool/hyper, strings,
opaque buffers, and array/list helpers).
"""

import struct


class Error(Exception):
    pass


class ConversionError(Error):
    pass


class Packer:
    def __init__(self):
        self.reset()

    def reset(self):
        self._buffer = []

    def get_buffer(self):
        return b"".join(self._buffer)

    # Backwards-compat alias
    get_buf = get_buffer

    def _pad(self, n):
        pad = (-n) % 4
        if pad:
            self._buffer.append(b"\0" * pad)

    def pack_uint(self, x):
        self._buffer.append(struct.pack("!I", x & 0xFFFFFFFF))

    def pack_int(self, x):
        self._buffer.append(struct.pack("!i", int(x)))

    def pack_enum(self, x):
        self.pack_int(x)

    def pack_bool(self, x):
        self.pack_int(1 if x else 0)

    def pack_uhyper(self, x):
        self._buffer.append(struct.pack("!Q", x & 0xFFFFFFFFFFFFFFFF))

    def pack_hyper(self, x):
        self._buffer.append(struct.pack("!q", int(x)))

    def pack_float(self, x):
        self._buffer.append(struct.pack("!f", float(x)))

    def pack_double(self, x):
        self._buffer.append(struct.pack("!d", float(x)))

    def pack_fstring(self, n, data):
        if isinstance(data, str):
            data = data.encode()
        if len(data) > n:
            raise ConversionError("string too long")
        self.pack_uint(len(data))
        self._buffer.append(data)
        self._pad(len(data))

    def pack_string(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.pack_uint(len(data))
        self._buffer.append(data)
        self._pad(len(data))

    def pack_fopaque(self, n, data):
        if isinstance(data, str):
            data = data.encode()
        if len(data) != n:
            raise ConversionError("opaque data is wrong size")
        self._buffer.append(data)
        self._pad(n)

    def pack_opaque(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.pack_uint(len(data))
        self._buffer.append(data)
        self._pad(len(data))

    def pack_list(self, items, pack_item):
        for item in items:
            self.pack_uint(1)
            pack_item(item)
        self.pack_uint(0)

    def pack_farray(self, n, array, pack_item):
        if len(array) != n:
            raise ConversionError("array length mismatch")
        for item in array:
            pack_item(item)

    def pack_array(self, array, pack_item):
        n = len(array)
        self.pack_uint(n)
        self.pack_farray(n, array, pack_item)


class Unpacker:
    def __init__(self, data):
        self.reset(data)

    def reset(self, data):
        if data is None:
            data = b""
        if isinstance(data, str):
            data = data.encode()
        self._buffer = data
        self._pos = 0

    def get_position(self):
        return self._pos

    def set_position(self, pos):
        self._pos = pos

    def done(self):
        if self._pos != len(self._buffer):
            raise ConversionError("unpacked data remains")

    def _read(self, n):
        if self._pos + n > len(self._buffer):
            raise Error("unpack failed: insufficient data")
        data = self._buffer[self._pos:self._pos + n]
        self._pos += n
        return data

    def _skip(self, n):
        self._read(n)

    def _unpack(self, fmt):
        data = self._read(struct.calcsize(fmt))
        return struct.unpack(fmt, data)[0]

    def unpack_uint(self):
        return self._unpack("!I")

    def unpack_int(self):
        return self._unpack("!i")

    def unpack_enum(self):
        return self.unpack_int()

    def unpack_bool(self):
        return bool(self.unpack_int())

    def unpack_uhyper(self):
        return self._unpack("!Q")

    def unpack_hyper(self):
        return self._unpack("!q")

    def unpack_float(self):
        return self._unpack("!f")

    def unpack_double(self):
        return self._unpack("!d")

    def unpack_fstring(self, n):
        length = self.unpack_uint()
        if length > n:
            raise ConversionError("string exceeds maximum length")
        data = self._read(length)
        self._skip((-length) % 4)
        return data

    def unpack_string(self):
        length = self.unpack_uint()
        data = self._read(length)
        self._skip((-length) % 4)
        return data

    def unpack_fopaque(self, n):
        data = self._read(n)
        self._skip((-n) % 4)
        return data

    def unpack_opaque(self):
        length = self.unpack_uint()
        data = self._read(length)
        self._skip((-length) % 4)
        return data

    def unpack_list(self, unpack_item):
        items = []
        while self.unpack_uint():
            items.append(unpack_item())
        return items

    def unpack_farray(self, n, unpack_item):
        return [unpack_item() for _ in range(n)]

    def unpack_array(self, unpack_item):
        n = self.unpack_uint()
        return self.unpack_farray(n, unpack_item)
