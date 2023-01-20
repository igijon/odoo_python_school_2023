from os import remove
from os import path

def write_text(text, name_file):
    with open(name_file, 'a') as f:
        f.write(text)

def write_student(line, name_file):
    write_text(f'<record id=\'student{line[1]}\' model=\'school.student\'>', name_file)
    write_text(f'<field name=\'name\'>{line[0]}</field>', name_file)
    write_text(f'<field name=\'dni\'>{line[1]}</field>', name_file)
    write_text(f'<field name=\'birth_year\'>{line[2]}</field>', name_file)
    write_text('</record>', name_file)

def write_classroom(line, name_file):
    write_text(f'<record id=\'classroom{line}\' model=\'school.classroom\'>', name_file)
    write_text(f'<field name=\'name\'>{line}</field>', name_file)
    write_text('</record>', name_file)

def delete_file(name_file):
    if path.exists(name_file):
        remove(name_file)

def classroom_generator(name_file):
    delete_file(name_file)
    write_text('<odoo><data>', name_file)
    with open("classrooms.csv") as file:
        for line in file:
            write_classroom(line.strip(), name_file)
    write_text('</data></odoo>', name_file)


def student_generator(name_file):
    delete_file(name_file)
    write_text('<odoo><data>', name_file)
    with open("students.csv") as file:
        for line in file:
            line = line.split(',')
            write_student(line, name_file)
    write_text('</data></odoo>', name_file)


classroom_generator('demo/classrooms.xml')
student_generator('demo/students.xml')

