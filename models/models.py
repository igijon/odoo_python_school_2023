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
    classroom = fields.Many2one("school.classroom", ondelete="set null", help="Clase a la que pertenece")
    level = fields.Selection([('1','1'), ('2','2')])
    #photo = fields.Binary()
    photo = fields.Image(max_widtth=200, max_height=200)
    # Clave ajena a la clave primaria de classroom. Se guarda en BDD
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


    @api.onchange('birth_year')
    def _onchange_byear(self):
        if self.birth_year > 2010:
            self.birth_year = 2010
            return { 
                        'warning': 
                        { 
                            'title': 'Bad birth year', 
                            'message': 'The student is too young',
                            'type': 'notification'
                        } 
                    }

    @api.onchange('level')
    def _onchange_level(self):
        return {
            'domain': {
                'classroom': [('level', '=', self.level)]
            }
        }  


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
    
    course = fields.Many2one('school.course')

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
    

class course(models.Model):
    _name= 'school.course'
    name = fields.Char()

    classrooms = fields.One2many('school.classroom', 'course')
    students = fields.Many2many('res.partner')
    enrolled_students = fields.Many2many('res.partner', compute='_get_enrolled')

    # Alumnos asignados a alguna clase
    def _get_enrolled(self):
        for c in self:
            c.enrolled_students = c.students.filtered(lambda s: len(s.classroom) == 1)


class course_wizard(models.TransientModel):
    _name = 'school.course_wizard'

    name = fields.Char()
    # Vamos a hacer la lista de clases y estudiantes 
    c_name=fields.Char(string="Classroom Name")
    c_level=fields.Selection([('1','1'),('2','2')], string="Classroom Level")
    classrooms = fields.Many2many('school.classroom_aux') 

    s_name = fields.Char(string='Student Name')
    s_birth_year = fields.Integer(string='Student Birth Year')
    s_dni = fields.Char(string='DNI')
    students = fields.Many2many('school.student_aux')

    #Función que afecta al modelo, no al recordset del modelo
    @api.model
    def action_course_wizard(self):
        action = self.env.ref('school.action_course_wizard').read()[0]
        return action
    
    def add_classroom(self):
        for c in self:
            c.write({'classrooms':[(0,0,{'name':c.c_name, 'level':c.c_level})]})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new'
        }
    
    def add_student(self):
        for c in self:
            c.write({'students':[(0,0,{'name':c.s_name, 'dni':c.s_dni, 'birth_year':c.s_birth_year})]})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new'
        }

    def create_course(self):
        _logger.warning('Llama a la función')
        for c in self:
            students = []
            for st in c.students:
                student = c.env['res.partner'].create({'name':st.name, 
                                             'dni':st.dni, 
                                             'birth_year': st.birth_year,
                                             'is_student': True})
                students.push(student.id)
            _logger.warning('Estoy aquí.')
            curse = c.env['school.course'].create({'name':c.name, 'students': [(6, 0, students)]})
            _logger.warning('Después del curso'+str(curse.id))
            for cl in c.classrooms:
                _logger.warning(cl+' '+curse.id)
                c.env['school.classroom'].create({'name':cl.name, 'course':curse.id, 'level': cl.level})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'school.course',
            'res_id': curse.id,
            'view_mode': 'form',
            'target': 'current'
        }


class classroom_aux(models.TransientModel):
    _name = 'school.classroom_aux'
    name = fields.Char()
    level = fields.Selection([('1','1'),('2','2')])

class student_aux(models.TransientModel):
    _name = 'school.student_aux'
    name = fields.Char()
    birth_year = fields.Integer()
    dni = fields.Char(string='DNI')