# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     d
#
##############################################################################
{
    'name':"KDERP Guide",
    'version':"7.0.0",
    'author':"KDERP IT-Dev. Team",
    'images' : [''],
    'summary':"Customize Web module",
    'category':"KDERP Apps",
    'depends':['kderp_base'],
#     'doc': ['static/doc/index.html'], 
    'description': """
    - Customize Database structure and function
    - Customize Procedure
    - Customize Interface""",
    'css': ['static/src/css/*.css'],
    'js':['static/src/js/kderp_guide.js'],
    'qweb':['static/src/xml/kderp_guide.xml'],
    'data':[
            "security/kderp_guide_group.xml",
            "security/ir.model.access.csv",
            'kderp_guide_view.xml'
            ],
    'demo':[],
    'installable':True,
    'application': True,
    
}