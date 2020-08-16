import sys

__all__ = [
    "encode_ulid_base32",
    "decode_ulid_base32",
]

text_type = str


class InvalidULID(ValueError):
    pass


def _to_binary(byte_list):
    return bytes(byte_list)


# Unrolled and optimized ULID Base32 encoding/decoding
# implementations based on NUlid:
# https://github.com/RobThree/NUlid/blob/5f2678b4d/NUlid/Ulid.cs#L159

_decode_table = [
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x00,
    0x01,
    0x02,
    0x03,
    0x04,
    0x05,
    0x06,
    0x07,
    0x08,
    0x09,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x0A,
    0x0B,
    0x0C,
    0x0D,
    0x0E,
    0x0F,
    0x10,
    0x11,
    0xFF,
    0x12,
    0x13,
    0xFF,
    0x14,
    0x15,
    0xFF,
    0x16,
    0x17,
    0x18,
    0x19,
    0x1A,
    0xFF,
    0x1B,
    0x1C,
    0x1D,
    0x1E,
    0x1F,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x0A,
    0x0B,
    0x0C,
    0x0D,
    0x0E,
    0x0F,
    0x10,
    0x11,
    0xFF,
    0x12,
    0x13,
    0xFF,
    0x14,
    0x15,
    0xFF,
    0x16,
    0x17,
    0x18,
    0x19,
    0x1A,
    0xFF,
    0x1B,
    0x1C,
    0x1D,
    0x1E,
    0x1F,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
]
_symbols = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def encode_ulid_base32(binary):
    """
    Encode 16 binary bytes into a 26-character long base32 string.
    :param binary: Bytestring or list of bytes
    :return: ASCII string of 26 characters
    :rtype: str
    """
    assert len(binary) == 16

    binary = [int(b) for b in binary]

    symbols = _symbols
    return "".join(
        [
            symbols[(binary[0] & 224) >> 5],
            symbols[binary[0] & 31],
            symbols[(binary[1] & 248) >> 3],
            symbols[((binary[1] & 7) << 2) | ((binary[2] & 192) >> 6)],
            symbols[(binary[2] & 62) >> 1],
            symbols[((binary[2] & 1) << 4) | ((binary[3] & 240) >> 4)],
            symbols[((binary[3] & 15) << 1) | ((binary[4] & 128) >> 7)],
            symbols[(binary[4] & 124) >> 2],
            symbols[((binary[4] & 3) << 3) | ((binary[5] & 224) >> 5)],
            symbols[binary[5] & 31],
            symbols[(binary[6] & 248) >> 3],
            symbols[((binary[6] & 7) << 2) | ((binary[7] & 192) >> 6)],
            symbols[(binary[7] & 62) >> 1],
            symbols[((binary[7] & 1) << 4) | ((binary[8] & 240) >> 4)],
            symbols[((binary[8] & 15) << 1) | ((binary[9] & 128) >> 7)],
            symbols[(binary[9] & 124) >> 2],
            symbols[((binary[9] & 3) << 3) | ((binary[10] & 224) >> 5)],
            symbols[binary[10] & 31],
            symbols[(binary[11] & 248) >> 3],
            symbols[((binary[11] & 7) << 2) | ((binary[12] & 192) >> 6)],
            symbols[(binary[12] & 62) >> 1],
            symbols[((binary[12] & 1) << 4) | ((binary[13] & 240) >> 4)],
            symbols[((binary[13] & 15) << 1) | ((binary[14] & 128) >> 7)],
            symbols[(binary[14] & 124) >> 2],
            symbols[((binary[14] & 3) << 3) | ((binary[15] & 224) >> 5)],
            symbols[binary[15] & 31],
        ]
    )


def decode_ulid_base32(encoded):
    """
    Decode a 26-character long base32 string into the original 16 bytes.
    :param encoded: 26-character long string
    :return: 16 bytes
    """
    if len(encoded) != 26:
        raise InvalidULID(
            "base32 ulid is %d characters long, expected 26" % len(encoded)
        )

    if not all(c in _symbols for c in encoded):
        raise InvalidULID("invalid characters in base32 ulid")

    b = [ord(c) for c in encoded]

    if b[0] < 48 or b[0] > 55:
        # See https://github.com/oklog/ulid/issues/9:
        #   Technically, a 26-character Base32 encoded string can contain 130 bits of information,
        #   whereas a ULID must only contain 128 bits.
        #   Therefore, the largest valid ULID encoded in Base32 is 7ZZZZZZZZZZZZZZZZZZZZZZZZZ,
        #   which corresponds to an epoch time of 281474976710655 or 2 ^ 48 - 1.
        raise InvalidULID(
            "base32 ulid is out of range (starts with %s; accepted are 01234567)"
            % encoded[0]
        )

    tab = _decode_table
    binary = [
        (c & 0xFF)
        for c in [
            ((tab[b[0]] << 5) | tab[b[1]]),
            ((tab[b[2]] << 3) | (tab[b[3]] >> 2)),
            ((tab[b[3]] << 6) | (tab[b[4]] << 1) | (tab[b[5]] >> 4)),
            ((tab[b[5]] << 4) | (tab[b[6]] >> 1)),
            ((tab[b[6]] << 7) | (tab[b[7]] << 2) | (tab[b[8]] >> 3)),
            ((tab[b[8]] << 5) | tab[b[9]]),
            ((tab[b[10]] << 3) | (tab[b[11]] >> 2)),
            ((tab[b[11]] << 6) | (tab[b[12]] << 1) | (tab[b[13]] >> 4)),
            ((tab[b[13]] << 4) | (tab[b[14]] >> 1)),
            ((tab[b[14]] << 7) | (tab[b[15]] << 2) | (tab[b[16]] >> 3)),
            ((tab[b[16]] << 5) | tab[b[17]]),
            ((tab[b[18]] << 3) | tab[b[19]] >> 2),
            ((tab[b[19]] << 6) | (tab[b[20]] << 1) | (tab[b[21]] >> 4)),
            ((tab[b[21]] << 4) | (tab[b[22]] >> 1)),
            ((tab[b[22]] << 7) | (tab[b[23]] << 2) | (tab[b[24]] >> 3)),
            ((tab[b[24]] << 5) | tab[b[25]]),
        ]
    ]
    return _to_binary(binary)
