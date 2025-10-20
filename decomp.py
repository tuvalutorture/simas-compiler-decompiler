import sys
import os
import json

XKEY = 71  # xor key

def xstring(s: str) -> str:
    return ''.join(chr(ord(c) ^ XKEY) for c in s)

# === SIMAS <-> JSON conversion ===
def simas_to_json(source: str):
    """Convert SIMAS source code to a JSON structure like simas.run() might output."""
    instructions = []
    lines = [ln.strip() for ln in source.splitlines() if ln.strip()]
    for line in lines:
        # remove trailing semicolon if exists
        if line.endswith(';'):
            line = line[:-1]
        parts = line.split()
        instructions.append(parts)
    return instructions

def json_to_simas(data):
    """Convert parsed JSON array of arrays back into SIMAS source code."""
    lines = []
    for instr in data:
        lines.append(' '.join(str(x) for x in instr) + ';')
    return '\n'.join(lines)

# === file processing ===
def compile_simas(input_path):
    """Encrypt .simas -> .csa"""
    with open(input_path, 'r', encoding='utf-8') as f:
        src = f.read()

    simas_data = simas_to_json(src)
    json_text = json.dumps(simas_data, separators=(',', ':'))
    encrypted = xstring(json_text)

    output_path = os.path.splitext(input_path)[0] + '.csa'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(encrypted)
    print(f'compiled: {input_path} -> {output_path}')

def decompile_csa(input_path):
    """Decrypt .csa -> .simas"""
    with open(input_path, 'r', encoding='utf-8') as f:
        encrypted = f.read()

    decrypted = xstring(encrypted)
    try:
        json_data = json.loads(decrypted)
    except json.JSONDecodeError as e:
        print(f'error: invalid csa (cannot decode json): {e}')
        sys.exit(1)

    simas_source = json_to_simas(json_data)
    output_path = os.path.splitext(input_path)[0] + '.simas'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(simas_source)
    print(f'decompiled: {input_path} -> {output_path}')

def print_help():
    print('usage: python decomp.py <file.simas | file.csa>')
    print('  if .simas → compiles (encrypts) into .csa')
    print('  if .csa → decompiles (decrypts) back into .simas')

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    arg = sys.argv[1]
    if arg == '-h':
        print_help()
        sys.exit(0)

    if not os.path.exists(arg):
        print(f'error: file not found: {arg}')
        sys.exit(1)

    if arg.endswith('.simas'):
        compile_simas(arg)
    elif arg.endswith('.csa'):
        decompile_csa(arg)
    else:
        print('error: unknown extension. use .simas or .csa')
        sys.exit(1)

if __name__ == '__main__':
    main()
