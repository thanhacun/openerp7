from openerp.osv.orm import Model
from openerp.osv import fields
import openerp.addons.decimal_precision as dp
import re

class kderp_contract_client(Model):
    _name='kderp.contract.client'
    _description='KDERP Contract to Client'
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if not context:
            context={}
        # Open Contract from Job
        job_ids = context.get("kderp_search_default_job_contract_lists",[])
        if job_ids:
            contract_ids=[]
            for job in self.pool.get('account.analytic.account').browse(cr, uid, job_ids):
                for kcc in job.contract_ids:
                       contract_ids.append(kcc.id)
            args.append((('id', 'in', contract_ids)))  
        return super(kderp_contract_client, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=False)
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if context is None:
            context={}

        if name:
            name=name.strip()
            ctc_ids = self.search(cr, uid, [('code', '=', name)] + args, limit=limit, context=context)
            if not ctc_ids:
                ctc_ids = self.search(cr, uid, [('code', operator, name)] + args, limit=limit, context=context)
            if not ctc_ids:
                ctc_ids = self.search(cr, uid,[('name', 'ilike', name)] + args, limit=limit, context=context)
        else:
            ctc_ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ctc_ids, context=context)
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            full_name = record.code + " - "  + record.name 
            res.append((record.id, full_name))
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        new_obj = super(kderp_contract_client, self).write(cr, uid, ids, vals, context=context)
        self.pool.get('ir.rule').clear_cache(cr,uid)
        return new_obj
        
    def create(self, cr, uid, vals, context={}):        
        id_test=Model.create(self, cr, uid, vals, context=context)
        new_id=self.pool.get('kderp.contract.currency').create_currency(cr,uid,id_test,context)
        self.pool.get('ir.rule').clear_cache(cr,uid)
        return id_test
        
    def _newcode_suggest(self,cr,uid,context={}):
        selection=[]
        cr.execute("Select seq_code || '_' || prefix,name from vwnewcode_contract order by newcode asc")
        list_newcode=cr.fetchall()
        return list_newcode

    def onchange_suggest_code(self, cr, uid, ids,new_code):
        cr.execute("Select newcode,name from vwnewcode_contract where seq_code || '_' || prefix='%s'" % new_code)
        res = cr.dictfetchone()
        if res:
            val={'value':{'code':res['newcode'],'newcode_suggest':False}}
        else:
            val={}
        return val
    
    def _get_company_currency(self, cr, uid, ids, name, arg, context=None):
        res={}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_currency_id = user.company_id.currency_id.id
        for id in ids:
            res[id] =company_currency_id
        return res 
    
    def _get_sort(self, cr, uid, ids, name=None, args=None, context=None):
        if context == None:
            context = {}
        res = {}
        for kcc in self.browse(cr, uid, ids, context=context):
            res[kcc.id] = kcc.code[:4][2:]+"-"+kcc.code[5:]
        return res
    
    def _get_combine_quotations(self, cr, uid, ids, name, args, context=None):
        #tmp={'quotations':False, 'scopeofwork':False}
        res={}
        kcc_ids=",".join(map(str,ids))
        cr.execute("""Select
                kcc.id,
                trim(array_to_string(array_agg(so.name::text),';'))::text
            from
                kderp_contract_client kcc
            left join
                sale_order so on kcc.id =so.contract_id and so.state='done'
            where
                kcc.id in (%s)
            group by
                kcc.id""" % (kcc_ids))
        for id,quotations in cr.fetchall():
            res[id]=quotations
        return res
    
    def _get_contract_attachment(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if ids:
            cont_id_list = ",".join(map(str,ids))
            cr.execute("""Select
                                kcc.id as id,
                                case when sum(case when coalesce(ia.attached_contract_sent,False) then 1 else 0 end) >0 then 1 else 0 end as attached_contract_sent,
                                case when sum(case when coalesce(ia.attached_contract_received,False) then 1 else 0 end) >0 then 1 else 0 end as attached_contract_received,
                                case when sum(case when coalesce(ia.attached_approved_quotation,False) then 1 else 0 end)>0 then 1 else 0 end as attached_approved_quotation
                          from
                                   kderp_contract_client  kcc
                          left join
                                   ir_attachment ia on kcc.id=ia.res_id and res_model='kderp.contract.client'
                          where
                                   kcc.id in (%s) 
                          group by 
                                    kcc.id""" % (cont_id_list))
            for contl in cr.dictfetchall():
                res[contl.pop('id')]=contl
        return res
    
    def _get_attachement_link(self, cr, uid, ids, context=None):
        res={}
        for att_obj in self.pool.get('ir.attachment').browse(cr,uid,ids):
            if att_obj.res_model=='kderp.contract.client' and att_obj.res_id:
                res[att_obj.res_id] = True
        return res.keys()
    
    def _get_company_link(self, cr, uid, ids, context=None):
        res={}
        cr.execute("Select id from kderp_contract_client")
        for ctc_id in cr.fetchall():
            res[ctc_id[0]]=True
        return res.keys()
    
    _order = 'sort desc,code, date desc'
    
    _columns={
              
            'sort':fields.function(_get_sort, type='char', size=16, string='Full Name',
                                             store={
                                                    'kderp.contract.client':(lambda self, cr, uid, ids, c={}: ids, ['code'], 50),
                                                    }),
              
            'state':fields.selection([('uncompleted','Uncompleted'),('completed','Completed')],'Status',select=2,required=True,readonly=True),
            'outstanding':fields.selection([('none','None'),('pm_check','PM Check'),('bc_check','BC Check')],'Outstanding',select=2,required=True,readonly=True),
            
            'code':fields.char('Number',size=32,required=True,readonly=True,states={'uncompleted':[('readonly',False)]}),
            'newcode_suggest':fields.selection(_newcode_suggest,'New Suggest Code',readonly=True,states={'uncompleted':[('readonly',False)]}),
            
            'name':fields.char('Description',size=256,required=True,translate=True), #Description in OpenERP 5 readonly=True,states={'uncompleted':[('readonly',False)]},
            'date':fields.date('Date of contract',select=1,required=True),
            'project_name':fields.char('Prj. Name',size=255,translate=True),#states={'uncompleted':[('readonly',False)]},
            'contract_ref':fields.char('Contract Ref.',size=100,readonly=True,states={'uncompleted':[('readonly',False)]}),
            
            'title_id': fields.many2one('res.partner.title', 'Title',readonly=True,states={'uncompleted':[('readonly',False)]}),
            'client_representative_name':fields.char('Representative',size=32,readonly=True,states={'uncompleted':[('readonly',False)]}),
            
            'project_location_id':fields.many2one('kderp.location','IP Location',ondelete='restrict',required=True,readonly=True,states={'uncompleted':[('readonly',False)]}),
            
            'owner_id':fields.many2one('res.partner','Owner',ondelete='restrict', domain="[('customer','=',1)]",required=True,readonly=True,states={'uncompleted':[('readonly',False)]}),
            'client_id':fields.many2one('res.partner','Client',ondelete='restrict', domain="[('customer','=',1)]",required=True,readonly=True,states={'uncompleted':[('readonly',False)]}),
            'address_id':fields.many2one('res.partner','Address',ondelete='restrict',required=True,readonly=True,states={'uncompleted':[('readonly',False)]}),
            'invoice_address_id':fields.many2one('res.partner','Invoice Address',ondelete='restrict',required=True,readonly=True,states={'uncompleted':[('readonly',False)]}),
            
            'registration_date':fields.date("Reg. Date",select=2),
            'started_date':fields.date('Started Date',select=2),
            'completion_date':fields.date('Completion Date',select=2),
            'closed_date':fields.date('Closed Date',select=2),
            
            #Contract Attached Info
            'attached_contract_sent':fields.function(_get_contract_attachment,method=True,string='Contract Sent',readonly=True,type='boolean',multi='Contract_attachment',
                                             store={
                                                    'kderp.contract.client':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','attached_contract_sent','attached_contract_received','attached_approved_quotation'],20)}),
            'attached_contract_received':fields.function(_get_contract_attachment,method=True,string='Contract Received',readonly=True,type='boolean',multi='Contract_attachment',
                                             store={
                                                    'kderp.contract.client':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','attached_contract_sent','attached_contract_received','attached_approved_quotation'],20)}),
            'attached_approved_quotation':fields.function(_get_contract_attachment,method=True,string='Approved Quotation',readonly=True,type='boolean',multi='Contract_attachment',
                                             store={
                                                    'kderp.contract.client':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','attached_contract_sent','attached_contract_received','attached_approved_quotation'],20)}),
            
            'period_id':fields.many2one('account.period', 'Force Period', domain=[('state','<>','done')], readonly=True, states={'uncompleted':[('readonly',False)]}),
            
            'payment_term_ids':fields.one2many('kderp.client.payment.term','contract_id','Payment Term',readonly=True,states={'uncompleted':[('readonly',False)]}),
            'contract_currency_ids':fields.one2many('kderp.contract.currency','contract_id','Currency System'),
            'contract_summary_currency_ids':fields.one2many('kderp.contract.currency','contract_id', string = 'Cur.', domain=[('default_curr','=',True)],readonly=True,states={'uncompleted':[('readonly',False)]}),
            'progress_evaluation_ids':fields.one2many('kderp.progress.evaluation','contract_id','Progress',readonly=True,states={'uncompleted':[('readonly',False)]}),

            #View Object
            'contract_job_summary_ids':fields.one2many('kderp.quotation.contract.project.line','contract_id','Jobs',readonly=True),
            
            'company_currency_id':fields.function(_get_company_currency,type='many2one',relation='res.currency',string='Company Currency',method=True,
                                                  store={
                                                         'res.company':(_get_company_link,['currency_id'],20)}),
            'quotations':fields.function(_get_combine_quotations,type='char',
                                             size='128',method=True,string='Quotations'),
              }
    _sql_constraints = [('kderp_unique_contract_no', 'unique(code)', 'KDERP Error: The contract number must be unique!')]
    _defaults={
               'state':lambda *a:'uncompleted',
               'outstanding':lambda *a:'bc_check',
               }
    
    def init(self,cr):
        cr.execute("""CREATE OR REPLACE VIEW vwnewcode_contract AS 
                        SELECT 
                            wnewcode.pattern || 
                            btrim(to_char(max(substring(wnewcode.code::text, length(wnewcode.pattern) + 1,padding )::integer) + 1, '0000')) AS newcode,
                            wnewcode.name,
                            seq_code,
                            prefix
                        from
                            (
                            SELECT 
                                isq.name,
                                isq.code as seq_code,
                                to_char(now()::timestamp with time zone, (isq.prefix || suffix) || lpad('_',padding,'_')) AS to_char, 
                                CASE WHEN cnewcode.code IS NULL 
                                THEN isq.prefix::text || to_char(now()::timestamp with time zone, suffix || lpad('0',padding,'0'))
                                ELSE cnewcode.code
                                END AS code, 
                                isq.prefix::text || to_char('now'::text::date::timestamp with time zone, 'YY-'::text) AS pattern,
                                padding,
                                prefix
                            FROM 
                                ir_sequence isq
                            LEFT JOIN 
                                (SELECT 
                                    kderp_contract_client.code AS code
                                FROM 
                                kderp_contract_client
                                WHERE
                                    length(kderp_contract_client.code::text)=
                                    ((SELECT 
                                        length(prefix || suffix) + padding AS length
                                    FROM 
                                        ir_sequence
                                    WHERE 
                                        ir_sequence.code::text = 'kderp_contract_code'::text LIMIT 1))
                                ) cnewcode ON cnewcode.code::text ~~ to_char(now()::timestamp with time zone, (isq.prefix || suffix) || lpad('_',padding,'_'))
                            WHERE isq.code::text = 'kderp_contract_code'::text AND isq.active) wnewcode
                        GROUP BY 
                            pattern, 
                            name,
                            seq_code,
                            prefix;""")
kderp_contract_client()
