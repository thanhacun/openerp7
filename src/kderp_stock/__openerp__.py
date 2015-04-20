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
    'name':"KDERP Stock",
    'version':"7.0.0",
    'author':"KDERP IT-Dev. Team",
    'images' : ['images/kinden.png'],
    'summary':"Customize Purchase Module for Suiteable Kinden Procedure",
    'category':"KDERP Apps",
    'depends':['kderp_purchase','kderp_supplier_payment'],
    'description': """
    - Customize Database structure and function
    - Customize Procedure
    - Customize Interface""",
    'data':[
            "security/kderp_stock_security.xml",
            "security/ir.model.access.csv",
            "views/kderp_stock_menu.xml",
            "views/kderp_stock_views.xml",
            "wizard/kderp_packing_wizard_view.xml",
            'data/kderp_stock_data_code.xml'
            ],
    'demo':[],
    'installable':True
}