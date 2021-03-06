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
    'name':"KDERP Purchase",
    'version':"7.0.0",
    'author':"KDERP IT-Dev. Team",
    'images' : ['images/kinden.png'],
    'summary':"Customize Purchase Module for Suiteable Kinden Procedure",
    'category':"KDERP Apps",
    'depends':['kderp_product','purchase'],
    'description': """
    - Customize Database structure and function
    - Customize Procedure
    - Customize Interface""",
    'data':[
            "security/kderp_purchase_security.xml",
            "security/ir.model.access.csv",
            "kderp_purchase_view.xml",
            "kderp_purchase_workflow.xml",
            "kderp_expense_budget_line_view.xml",
            "incoterm_view.xml",
            "kderp_purchase_menu.xml"
            ],
    'demo':[],
    'installable':True
}