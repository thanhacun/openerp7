# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from osv import fields, osv

class kderp_wizard_cash_advance(osv.osv_memory):
    _name='kderp.wizard.cash.advance'
    _description = "KDERP Wizard Cash Advance"    
    _columns = {
                'advance_buying':fields.selection([('material','Material'),('others','Others'),('cash','Cash')],'Type',required=True),
    
                'type_cash':fields.char('Type',required=True,ondelete="restrict"),
               # 'type_cash':fields.selection([('payment','Payment')],'Cash type'),
                'account_analytic_id':fields.many2one('account.analytic.account','Job',ondelete="restrict"),
                'user_id':fields.many2one('hr.employee',string="User" ,required=True),
                'name': fields.char('Advance No.',size=32),
                'date':fields.date('Date',required=True)
               }
    
    def new_code(self,cr,uid,ids,staff_id,name=False,type='material'):
        if ids:
            try:
                ids=ids[0]
            except:
                ids=ids
        else:
            ids=0
        
        if (not staff_id):
            val={'value':{'name':False,'outstanding':False}}
        else:
            location = self.pool.get('res.users').browse(cr, uid, uid).location_user
            
            if location=='haiphong':
                location_code='P'
            elif location=='hcm':
                location_code='S'
            else:                
                location_code='H'
            
            cr.execute("""Select %s in 
                                    (Select 
                                            distinct user_id 
                                    from 
                                        kderp_advance_payment where state='approved' and advance_buying<>'cash'
                                    group by
                                        user_id
                                    having 
                                        count(id)>=3)""" % staff_id)
            if cr.fetchone()[0]:
                outstanding=True
            else:
                outstanding=False
                
            staff_code_list=self.pool.get("hr.employee").read(cr,uid,staff_id,['staffno'])
            if not staff_code_list:
                val={'value':{'name':False}}
            else:
                if type=='cash':
                    staff_code = staff_code_list['staffno'][1:]
    
                    prefix = len('C%s13-2009-X' % location_code) 
                    
                    cr.execute("Select \
                                    max(substring(name from "+str(prefix)+" for length(name)-"+str(prefix-1)+"))::integer \
                                from \
                                    kderp_advance_payment \
                                where name ilike 'C" + location_code + time.strftime('%y')+"-"+staff_code+"-"+"%%' and id!="+str(ids))
                    if cr.rowcount:
                        next_code=str(cr.fetchone()[0])
                        #raise osv.except_osv("E",next_code)
                        if next_code.isdigit():
                            next_code=str(int(next_code)+1)
                        else:
                            next_code='1'
                    else:
                        next_code='1'
                    val={'value':{'outstanding':False,'name':'C%s%s-%s-%s' %(location_code,time.strftime('%y'),staff_code,next_code.rjust(2,'0'))}}
                else:
                    staff_code = staff_code_list['staffno'][1:]
                    if name:
                        if staff_code.find(staff_code)>0:
                            return {'value':{'outstanding':outstanding}}
    
                    prefix = len('AD%s13-2009-X' % location_code) 
                    
                    cr.execute("Select \
                                    max(substring(name from "+str(prefix)+" for length(name)-"+str(prefix-1)+"))::integer \
                                from \
                                    kderp_advance_payment \
                                where name ilike 'AD" +  location_code +time.strftime('%y')+"-"+staff_code+"-"+"%%' and id!="+str(ids))
                    if cr.rowcount:
                        next_code=str(cr.fetchone()[0])
                        #raise osv.except_osv("E",next_code)
                        if next_code.isdigit():
                            next_code=str(int(next_code)+1)
                        else:
                            next_code='1'
                    else:
                        next_code='1'
                    val={'value':{'outstanding':outstanding,'name':'AD%s%s-%s-%s' % (location_code,time.strftime('%y'),staff_code,next_code.rjust(2,'0'))}}
        return val
    
    def action_ge_create_ge_cash_advance(self, cr, uid, ids, context): 
        if not context:
            context={}
        new_form_data = self.read(cr,uid,ids,['name','account_analytic_id','user_id','date',],context)
        advance_buying='cash'
        #date=time.strftime('%Y-%m-%d')
        kderp_kspe_id = False
        koe_obj = self.pool.get('kderp.other.expense')
        for koe in koe_obj.browse(cr,uid,[context.get('expense_id',False)]):  
            if koe.advance_payment_id:
                return True 
            advance_code=new_form_data[0]['name']
            user=new_form_data[0]['user_id']
            date=new_form_data[0]['date']            
# 
            advance_cash= {
                    'advance_buying':advance_buying,
                    'name':advance_code,
                    'type_cash':'payment',
                    'date':date,
                    'user_id':user[0]
                }

            cash_line = []
            for koel in koe.expense_line:            
                description = koel.name or koe.description or koel.budget_id.name
                amount = koel.amount                
                cash_line.append((0, False,{
                          'name':description,
                          'amount':amount,
                          'date': koe.date,
                          'user_id':user[0],
                          'supplier_id':koe.partner_id.id
                          }))
            advance_cash['cash_line'] = cash_line
            kderp_adv_id = self.pool.get('kderp.advance.payment').create(cr, uid, advance_cash)            
            koe.write({'advance_payment_id': kderp_adv_id})  
        return {
                'type': 'ir.actions.act_window',
                'name': 'Supplier Payment (OExpense)',
                'view_type': 'form',
                'res_id':kderp_adv_id,
                'target':'current',
                'nodestroy': True,
                'view_mode': 'form,tree',
                'res_model': 'kderp.advance.payment',
                'domain': "[('id','=',%s)]" % kderp_kspe_id
                }
            
    def _get_job(self,cr,uid,context={}):
        return context.get('account_analytic_id',False)
    _defaults={
               'type_cash':lambda *x:'payment',
               'advance_buying':lambda *x:'cash',
               'account_analytic_id':_get_job,
               'date': lambda *a: time.strftime('%Y-%m-%d'),
               
               
               }

kderp_wizard_cash_advance()
