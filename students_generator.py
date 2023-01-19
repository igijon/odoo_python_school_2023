from os import remove
from os import path

def writeText(text):
    with open('demo/students.xml', 'a') as f:
        f.write(text)


def writeLine(line):
    writeText(f'<record id=\'student{line[1]}\' model=\'school.student\'>')
    writeText(f'<field name=\'name\'>{line[0]}</field>')
    writeText(f'<field name=\'dni\'>{line[1]}</field>')
    writeText(f'<field name=\'birth_year\'>{line[2]}</field>')
    writeText('</record>')


if path.exists('demo/students.xml'):
    remove('demo/students.xml')
writeText('<odoo><data>')
nLine = 0
with open("MOCK_DATA.csv") as file:
    for line in file:
        nLine+=1
        if nLine > 1:
            line = line.split(',')
            writeLine(line)
    
writeText('</data></odoo>')