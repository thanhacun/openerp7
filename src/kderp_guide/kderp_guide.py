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
    
    _columns = {
                'name':fields.char('Description',size=250),
                'date':fields.date('Date',select=1,required=True),
                'user_id': fields.many2one('res.users', 'User Upload',select=1),
                'attachment_lines':fields.one2many('ir.attachment','res_id',context={'res_model':'kderp.guide'},domain=[('res_model','=','kderp.guide')]),
                'data': fields.binary('File'),
                'note':fields.char('Description'),
                
                }
    
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
                        dst_dir = os.path.dirname(dir_file)+'/source'
                    else:
                        dst_dir = os.path.dirname(dir_file)+'/source/kdvnstatic'
                    for file in os.listdir(src_dir):
                        src_file = os.path.join(src_dir, file)
                        shutil.copy(src_file,dst_dir) 
                        dst_file = os.path.join(dst_dir, file)
                        new_dst_file_name = os.path.join(dst_dir, name)
                        os.rename(dst_file, new_dst_file_name)
        
#         current_file = os.path.isfile(path)(path).realpath(__file__)   
            current_dir_build = os.path.dirname(dir_file)
            p= subprocess.call('sphinx-build -b html ' + current_dir_build+'/source'+' ' +current_dir_build +'/static/doc/',shell=True) 
        return True
       
    _defaults={
               'user_id':lambda obj, cr, uid, context: uid,
               'date' :fields.date.context_today,
              
               }
kderp_guide()

class ir_attachment(osv.osv):
        _name = 'ir.attachment'
        _inherit ="ir.attachment"  
        
        def onchange_name_guide(self, cr, uid, ids,name):
            if name:
                val={'value':{'name':name,'res_model':'kderp.guide'}}
            else:
                val={}
            return val
        
ir_attachment()

    
