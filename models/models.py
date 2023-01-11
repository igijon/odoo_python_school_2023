# -*- coding: utf-8 -*-

from odoo import models, fields, api


class student(models.Model):
    _name = 'school.student'
    _description = 'school.student'

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Este es el nombre")
    birth_year = fields.Integer()
    description = fields.Text()
    inscription_date = fields.Date()
    last_login = fields.Datetime()
    is_student = fields.Boolean()
    #photo = fields.Binary()
    photo = fields.Image(max_widtth=200, max_height=200)
    # Clave ajena a la clave primaria de classroom. Se guarda en BDD
    classroom = fields.Many2one("school.classroom", ondelete="set null", help="Clase a la que pertenece")
    

class classroom(models.Model):
    _name = 'school.classroom'
    _description = 'Las clases'

    name = fields.Char() # Todos los modelos deben tener un field name
    # Esto es una consulta, no se guarda en BDD
    # Se declara como un field pero no se guarda porque es simplemente una
    # consulta a partir del many2one que sí se guarda en BDD
    students = fields.One2many(string="Alumnos", comodel_name="school.student", inverse_name='classroom')
    # comodel_name es el modelo con el que establecemos la relación. Una clase tiene
    # muchos estudiantes, el modelo serían los estudiantes
    # inverse_name sería la clave ajena de la clase con la que relacionamos.
    # En este caso una clase tiene varios estudiantes y el campo que será la clave 
    # ajena del modelo student es classroom
    teachers = fields.Many2many(comodel_name='school.teacher',
                                relation='teachers_classroom',
                                column1='classroom_id',
                                column2='teacher_id')
    #relation: puedo establecer el nombre de la tabla intermedia.
    #column1: se establece el nombre de la columna que va a hacer referencia
    #al modelo de la clase actual, en este caso classroom para el campo
    #teachers de classroom
    #column2: establece el nombre de la columna que va a hacer referencia al modelo
    #de la clase con la que referenciamos, en este caso teacher para el campo teachers de
    #classroom

class teacher(models.Model):
    _name = 'school.teacher'
    _description = 'Los profesores'

    name = fields.Char()
    # Un profesor puede dar clase en varias aulas y en un aula, varios profesores
    classrooms = fields.Many2many(comodel_name='school.classroom',
                                  relation='teachers_classroom',
                                  column1='teacher_id',
                                  column2='classroom_id')
