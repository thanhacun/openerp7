# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.misc import unquote as unquote


class kderp_list_object(osv.osv_memory):
    _name = 'kderp.list.object'
    
    _columns = {
                'name':fields.char('Name', size=256, readonly=1),
                'obj_id':fields.many2one('ir.model','Object Relation', readonly="1"),
                'source':fields.text('Source', readonly="1")
                }
    
class ir_model(osv.osv):
    _name = "ir.model"
    _inherit = 'ir.model' 
    
    def _get_list_object(self, cr, uid, ids, name, args, cotnext):
        res = {}
        import inspect
        
        klo_obj = self.pool.get('kderp.list.object')
        for irm in self.browse(cr, uid, ids):
            res[irm.id] = []
            obj = self.pool.get(irm.model)
            for att in dir(obj):
                gid = klo_obj.search(cr, uid, [('obj_id','=',irm.id),('name','=',att)])
                if not gid:
                    try:
                        exec("source = inspect.getsource(klo_obj.%s)" % att)
                    except:
                        source = ""
                                            
                    gid = klo_obj.create(cr, uid, {'name': att,
                                                  'obj_id':irm.id,
                                                  'source': source })                    
                else:
                    gid = gid[0]
                    
                res[irm.id].append(gid)
        return res
    
    _columns = {
                'method_details_ids':fields.function(_get_list_object, relation='kderp.list.object', type='one2many')
                }   