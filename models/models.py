# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import secrets
import logging
import re

_logger = logging.getLogger(__name__)


class student(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner' #herencia de clase

    #_description = 'school.student'

    #name = fields.Char(string="Nombre", readonly=False, required=True, help="Este es el nombre")
    birth_year = fields.Integer()
    dni = fields.Char(string="DNI")
    password = fields.Char(default=lambda p: secrets.token_urlsafe(12))
    description = fields.Text()
    inscription_date = fields.Datetime(default=lambda d: fields.Datetime().now())
    last_login = fields.Datetime()
    is_student = fields.Boolean()
    level = fields.Selection([('1','1'), ('2','2')])
    #photo = fields.Binary()
    photo = fields.Image(max_widtth=200, max_height=200)
    # Clave ajena a la clave primaria de classroom. Se guarda en BDD
    classroom = fields.Many2one("school.classroom", domain="[('level', '=', level)]", ondelete="set null", help="Clase a la que pertenece")
    #Campo relacionado no almacenado en BDD
    teachers = fields.Many2many('school.teacher', related='classroom.teachers', readonly=True)
    state = fields.Selection([('1', 'Matriculado'), ('2', 'Estudiante'), ('3', 'Ex-estudiante')], default="2")

    individual_tasks = fields.One2many('school.individual_task', 'student')
    groupal_tasks = fields.Many2many('school.groupal_task')

    @api.constrains('dni')
    def _check_dni(self):
        regex = re.compile('[0-9]{8}[a-z]\Z', re.I)
        for student in self:
            #Validamos si se cumple la condición
            if regex.match(student.dni):
                _logger.info('DNI correcto')
            else:
                #No coinciden por lo que tenemos que informar para que no se guarde
                raise ValidationError('El formato del DNI no es correcto')

    _sql_constraints = [('dni_uniq', 'unique(dni)', 'DNI can\'t be repeated')]
    
    # También recibe un recordset
    def regenerate_password(self):
        for student in self:
            pw = secrets.token_urlsafe(12)
            student.write({'password':pw})


class classroom(models.Model):
    _name = 'school.classroom'
    _description = 'Las clases'

    name = fields.Char() # Todos los modelos deben tener un field name

    level = fields.Selection([('1','1'), ('2','2')])
    # El primero es el valor que se guarda en BDD y el segundo el texto que se muestra

    # Esto es una consulta, no se guarda en BDD
    # Se declara como un field pero no se guarda porque es simplemente una
    # consulta a partir del many2one que sí se guarda en BDD
    students = fields.One2many(string="Alumnos", comodel_name="res.partner", inverse_name='classroom')
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

    teachers_last_year = fields.Many2many(comodel_name='school.teacher',
                                relation='teachers_classroom_ly',
                                column1='classroom_id',
                                column2='teacher_id')
    # Vamos a considerar que una  clase puede tener un coordinador (profesor) y que un mismo profesor
    # pudiera ser coordinador de varias clases
    coordinator = fields.Many2one('school.teacher', compute='_get_coordinator')

    all_teachers = fields.Many2many('school.teacher', compute='_get_teacher')

    def _get_coordinator(self):
        for classroom in self:
            if len(classroom.teachers) > 0:
                classroom.coordinator = classroom.teachers[0].id # Para el ejemplo vamos a establecer como coordinador el primero de la lista
            else: 
                classroom.coordinator = None

    def _get_teacher(self):
        for classroom in self:
            classroom.all_teachers = classroom.teachers + classroom.teachers_last_year

class teacher(models.Model):
    _name = 'school.teacher'
    _description = 'Los profesores'
    topic = fields.Char()
    phone = fields.Char()

    name = fields.Char()
    # Un profesor puede dar clase en varias aulas y en un aula, varios profesores
    classrooms = fields.Many2many(comodel_name='school.classroom',
                                  relation='teachers_classroom',
                                  column1='teacher_id',
                                  column2='classroom_id')

class seminar(models.Model):
    _name='school.seminar'
    name = fields.Char()
    date = fields.Datetime()
    finish = fields.Datetime()
    hours = fields.Integer()
    classroom = fields.Many2one('school.classroom')

class task(models.Model):
    _name='school.task'
    _description='base class for tasks'
    name = fields.Char()
    qualification = fields.Float()

class individual_task(models.Model):
    _name='school.individual_task'
    _description='one student task'
    _inherits = {'school.task':'task_id'} 
    
    student = fields.Many2one('res.partner', ondelente='cascade')

class groupal_task(models.Model):
    _name = 'school.groupal_task'
    _description = 'many student task'
    _inherits = {'school.task':'task_id'} 

    def _get_default_student(self):
        student = self.browse(self._context.get('current_student'))
        if student:
            _logger.warning(self._context.get('current_student'))
            return [student.id]
        else:
            return []
        
    students = fields.Many2many('res.partner', default=_get_default_student)
    