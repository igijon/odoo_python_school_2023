# -*- coding: utf-8 -*-
from odoo import http

class MyController(http.Controller):
    @http.route('/school/course', auth='user', type='json')
    def course(self):
        return {
            'html': """
                <div id="school_banner">
                    <link href="/school/static/src/css/banner.css" rel="stylesheet">
                    <h1 id="school_title">Curso</h1>
                    <p>Creación de cursos:</p>
                    <a class="course_button" type="action" data-reload-on-close="true" role="button" data-method="action_course_wizard" data-model="school.course_wizard"> 
                    Crear Cursos
                    </a>
                </div>
            """
        }