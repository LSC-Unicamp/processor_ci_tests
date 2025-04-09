import re


def parse_march(march: str):
    """
    Faz o parse de uma string 'march' e retorna:
      - XLEN: 32 ou 64
      - extensões principais e opcionais (ex: I, M, Zicsr, etc.)
    """
    # Determina XLEN
    xlen_match = re.match(r'rv(32|64)', march)
    if not xlen_match:
        raise ValueError(f'Formato inválido de march: {march}')
    xlen = int(xlen_match.group(1))

    # Remove o prefixo rv32/rv64
    march_body = march[xlen_match.end() :]

    # Divide a parte principal das extensões custom (ex: _Zicsr)
    base_match = re.match(r'([a-z]+)', march_body)
    base_exts = list(base_match.group(1).upper()) if base_match else []

    # Captura extensões Z (e outras prefixadas com _) ex: _Zicsr_Zifencei
    extra_exts = re.findall(r'_([A-Za-z0-9]+)', march_body)

    # Junta tudo
    all_extensions = base_exts + extra_exts

    return {'xlen': xlen, 'extensions': all_extensions}


if __name__ == '__main__':
    # Exemplos de uso
    print(parse_march('rv32imac'))
    # Saída: {'xlen': 32, 'extensions': ['I', 'M', 'A', 'C']}

    print(parse_march('rv64i_Zicsr_Zifencei'))
    # Saída: {'xlen': 64, 'extensions': ['I', 'Zicsr', 'Zifencei']}

    print(parse_march('rv32imafd_Zicsr'))
    # Saída: {'xlen': 32, 'extensions': ['I', 'M', 'A', 'F', 'D', 'Zicsr']}
