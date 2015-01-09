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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class kderp_create_allocation_sheet(osv.osv_memory):
    _name = 'kderp.create.allocation.sheet'
    _description = 'KDERP Wizard Create allocation Sheet'
    
    ALLOCATION_MONTH = [(1,'1 Month'),
                        (0,'All Remaining Amount'),
                        (-1,'Custom')]
    
    def _get_default_value(self, cr, uid, context = {}, field='number_of_month'):
        if not context:
            context = {}
        ge_id = context.get('ge_id', False)
        if ge_id:
            ge_pool = self.pool.get('kderp.other.expense')
            ge_obj = ge_pool.read(cr, uid, ge_id, [field])
            return ge_obj[field] if ge_obj else ge_obj  
        else:
            return False
    
    _columns = {
                'start_date_allocated':fields.date('Start Date',required=True),
                'startdate_default':fields.boolean('Start Date Defaults',invisible=True),
                'number_of_month':fields.integer("Number of month?", help='Number of months expense will be allocated automatically. This field use for automatically create Allocation Sheet'),                
                'allocated_selection':fields.selection(ALLOCATION_MONTH,'Select', required = True),
                'allocated_to_month':fields.integer("")
                }
    _defaults={
               'allocated_selection':lambda *x:1,
               'number_of_month': _get_default_value,
               'start_date_allocated':lambda self, cr, uid, context: self._get_default_value(cr, uid, context, 'start_date_allocated'),
               'startdate_default': lambda self, cr, uid, context: True if self._get_default_value(cr, uid, context, 'start_date_allocated') else False,
               }
    
    def create_allocation_sheet(self, cr, uid, ids, context={}):
        pass
        return
        state='draft'
        quantity=self.read(cr, uid, ids,['quantity_to_create'])[0]['quantity_to_create']
        list_ids=[]
        asset_id=context.get('active_id',False) 
        if asset_id:
            asset_obj=self.pool.get('kderp.asset.management')
            ass_list=asset_obj.copy_data(cr, uid, asset_id)
            ass_list['asset_ids']=[]
            ass_list['related_asset_ids']=[]
            a=ass_list.pop('asset_usage_ids') if 'asset_usage_ids' in ass_list else False
            a=ass_list.pop('sub_asset_ids') if 'sub_asset_ids' in ass_list else False
            ass_list['state']=state
            asset_code=ass_list['code']
            for sub in range(1,quantity+1):
                ass_list['code']=asset_code + "-" + str(sub).zfill(3)   
                ass_list['parent_id']=asset_id
#                list_to_create.append(ass_list)
                list_ids.append(asset_obj.create(cr, uid, ass_list))
        return list_ids

kderp_create_allocation_sheet()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
