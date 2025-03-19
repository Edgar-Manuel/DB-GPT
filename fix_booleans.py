import re

def fix_booleans(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Reemplazar 'true' por 'True' y 'false' por 'False'
    content = re.sub(r'(?<!"): *true(?=,|\n| *})', ': True', content)
    content = re.sub(r'(?<!"): *false(?=,|\n| *})', ': False', content)
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == '__main__':
    fix_booleans('clientes_actuales.py') 