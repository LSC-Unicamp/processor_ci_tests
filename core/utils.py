def hex_string_to_bytes(hex_str: str) -> bytes:
    # Remove o prefixo '0x' se existir
    hex_str = hex_str[2:] if hex_str.startswith('0x') else hex_str
    # Garante número par de caracteres
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return bytes.fromhex(hex_str)


def hex_to_int(hex_str: str, endian='big') -> int:
    hex_str = hex_str[2:] if hex_str.startswith('0x') else hex_str
    byte_data = bytes.fromhex(hex_str)

    if endian == 'little':
        byte_data = byte_data[::-1]

    return int.from_bytes(byte_data, byteorder='big')


def hex_to_string(hex_str: str, endian='big') -> str:
    # Remove o "0x" do começo se existir
    hex_str = hex_str[2:] if hex_str.startswith('0x') else hex_str

    # Converte para bytes
    byte_data = bytes.fromhex(hex_str)

    # Ajusta a ordem dos bytes
    if endian == 'little':
        byte_data = byte_data[::-1]

    # Converte para string ASCII
    return byte_data.decode('ascii')
