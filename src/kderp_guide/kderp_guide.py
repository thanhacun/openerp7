import subprocess
import os
import os.path
import pwd
from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from path import path
import tools
from tools.config import config
from openerp import pooler
import shutil
class kderp_guide(osv.osv):
    _name = 'kderp.guide'
#     def get_id_guide_attachment(self, cr, uid, ids, context):
#         if not context:
#             context={}
#         res={}
#         current_file = 'c/a'
#         current_dir = os.path.dirname(current_file)
#         name_database = cr.dbname
#         #att_path = os.path.normpath(os.path.join(current_dir, '../..')+ "/filestore/"+name_database)
#         ad = os.path.abspath(os.path.join(tools.ustr(config['root_path']), u'filestore'))
#         att_path = (ad)+'/'+ name_database
#        
#         if ids:
#             cur_obj=self.pool.get('ir.attachment')
#             att_ids = cur_obj.search(cr, uid,(('res_model','=','kderp.guide'),('res_id','=',ids)))
#             if att_ids:
#                 att = cur_obj.read(cr, uid, att_ids, ['datas_fname','store_fname'])
#                 res_name = []
#                 res_location=[]
#                 for record in att:
#                     name =record['datas_fname']
#                     res_name.append(name)
#                     location= os.path.normpath(os.path.join(record['store_fname'], '../'))
#                     #res_location.append(att_path+'/'+location)
#                     src_dir  = os.path.dirname(att_path)+'/'+name_database +'/'+location
#                     
#                     #src_dir = k[1:]
#                     
#                     dir_file = os.path.realpath(__file__) 
#                     if name[-4:]=='.rst':
#                         dst_dir = os.path.dirname(dir_file)+'/doc'
#                     else:
#                         dst_dir = os.path.dirname(dir_file)+'/doc/kdvntemplates'
#                     for file in os.listdir(src_dir):
#               
#                         src_file = os.path.join(src_dir, file)
#                         shutil.copy(src_file,dst_dir) 
#                         dst_file = os.path.join(dst_dir, file)
#                         new_dst_file_name = os.path.join(dst_dir, name)
#                         os.rename(dst_file, new_dst_file_name)
# #                     for i in range(len(name)):
# #                         res.append(name)
#                     #for i in append([dir_file, name]):
#                         
#                 #dt = os.path.dirname(os.path.abspath(k[1]))
#                 #a =k[2]
# #                     local_file = os.path.realpath(dir_file)
# #                     curent_dir = os.path.dirname(local_file)
#                 #raise osv.except_osv("KDERP Warning",curent_dir)
#                 
# #                 for i in att:
# #                 import pdb 
# #                     pdb.set_trace()
# #                     k =i.values()
# #                     raise osv.except_osv("KDERP Warning",k)
# #         
#         
# #         for kg in att_ids:
# #             t = kg.id
# #             raise osv.except_osv("KDERP Warning",t)
# #             kg_ids.append(kg.id)
# #         args.append((('id', 'in',  kg_ids)))     
#           
#         import pdb 
#         pdb.set_trace()
#         return True
#                     
   
    def _get_guide_attachment(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if ids:
            kg_id_list = ",".join(map(str,ids))
            cr.execute("""Select
                           kg.id as id,
                           case when sum(case when coalesce(ia.rst_file,False) then 1 else 0 end) >0 then 1 else 0 end as rst_file
                         
                       from
                           kderp_guide kg
                       left join
                           ir_attachment ia on kg.id=ia.res_id and res_model='kderp.guide'
                       where
                           kg.id in (%s) 
                       group by 
                            kg.id""" % (kg_id_list))
            for kgl in cr.dictfetchall():
                res[kgl.pop('id')]=kgl
        return res
       
    def _get_attachement_link(self, cr, uid, ids, context=None):
        res={}
        for att_obj in self.pool.get('ir.attachment').browse(cr,uid,ids):
            if att_obj.res_model=='kderp.guide' and att_obj.res_id:
                res[att_obj.res_id] = True
        return res.keys()
     
    _columns = {
                'name':fields.char('Description',size=250),
                'date':fields.date('Date',select=1,required=True),
                'user_id': fields.many2one('res.users', 'User Upload',select=1),
                'rst_file':fields.function(_get_guide_attachment,method=True,string='Rst File',readonly=True,type='boolean',multi='Kderp Guide Attachment',
                                             store={
                                                    'kderp.guide':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','rst_file'],20)}),
               
                
               
                'attachment_lines':fields.one2many('ir.attachment','res_id',context={'res_model':'kderp.guide'},domain=[('res_model','=','kderp.guide')]),
           
                'data': fields.binary('File'),
                'note':fields.char('Description'),
                
                }
#     def import_file(self, cr, uid, ids, context=None):
#         fileobj = TemporaryFile('w+')
#         fileobj.write(base64.decodestring(data)) 
#     
#         # your treatment
#         return
    
    def action_submit(self, cr, uid, ids, context):
        if not context:
            context={}
        res={}
        #current_dir = os.path.dirname(current_file)
        name_database = cr.dbname
        #path_store_file lay thu muc duong dan filestore
        path_store_file = os.path.abspath(os.path.join(tools.ustr(config['root_path']), u'filestore'))
        #path_store_file_db duong dan storefile cua database
        path_store_file_db = (path_store_file)+'/'+ name_database
        # dir_file thu muc hien hanh cua module kderp_guide
        dir_file = os.path.realpath(__file__) 
        if ids:
            cur_obj=self.pool.get('ir.attachment')
            att_ids = cur_obj.search(cr, uid,(('res_model','=','kderp.guide'),('res_id','=',ids)))
            if att_ids:
                att = cur_obj.read(cr, uid, att_ids, ['datas_fname','store_fname'])
                #res_name ten file
                res_name = []
                #res_location ten folder luu tru file
                res_location=[]
                for record in att:
                    name =record['datas_fname']
                    res_name.append(name)
                    location= os.path.normpath(os.path.join(record['store_fname'], '../'))
                    src_dir  = os.path.dirname(path_store_file_db)+'/'+name_database +'/'+location
                    # truong hop file la rst thi luu vao /opt/oe7/openerp/addons/kderp_guide/doc
                    # khac file .rst thi luu vao /opt/oe7/openerp/addons/kderp_guide/doc/kdvntemplates
                    if  name[-4:]=='.rst' or name[-3:]=='.py' :
                        dst_dir = os.path.dirname(dir_file)+'/doc'
                    else:
                        dst_dir = os.path.dirname(dir_file)+'/doc/kdvntemplates'
                    for file in os.listdir(src_dir):
                        src_file = os.path.join(src_dir, file)
                        shutil.copy(src_file,dst_dir) 
                        dst_file = os.path.join(dst_dir, file)
                        new_dst_file_name = os.path.join(dst_dir, name)
                        os.rename(dst_file, new_dst_file_name)
        
#         current_file = os.path.isfile(path)(path).realpath(__file__)   
            current_dir_build = os.path.dirname(dir_file)
            p= subprocess.call('sphinx-build -b html ' + current_dir_build+'/doc ' +current_dir_build +'/static/doc',shell=True) 
        return True
       
    _defaults={
               'user_id':lambda obj, cr, uid, context: uid,
               'date' :fields.date.context_today,
              
               }
    class ir_attachment(osv.osv):
        _name = 'ir.attachment'
        _inherit ="ir.attachment"  
        
        def onchange_name_guide(self, cr, uid, ids,name):
            if name:
                val={'value':{'name':name,'res_model':'kderp.guide'}}
            else:
                val={}
            return val
    
    class kderp_guide_upload(osv.osv):
        _name = 'kderp.guide.upload'
        
        _columns = {
               # 'attachment_id':fields.many2one("ir.attachment","Code",required=True,select=1),
                'guide_id':fields.many2one('kderp.guide',required=True,ondelete='cascade'),
                
              
        }
#         raise osv.except_osv ("Please refresh the form")   