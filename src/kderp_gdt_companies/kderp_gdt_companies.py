# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields
#from osv.orm import intersect
#from openerp import tools

class gdt_companies_wizard(osv.TransientModel):
    """
    Wizard ho tro tim kiem va update du lieu cac cong ty
    tu trang web cua GDT
    """
    _name = 'gdt.companies.wizard'
    _description = 'GDT Companies Search'
    #su dung 1 bien global _raise_error = True de xac dinh co popup thong bao loi hay khong
    raise_error = True
    def _query_data_from_gdt(self, tax_code, popup=True):
        import requests
        url = 'http://mst-thanhacun-1.c9.io/mst/'
        result = {'tax_code':'','name':'','address':'','status':''}
        
        try:
            response = requests.get(url + tax_code, timeout=5)
            if response.status_code == 200:
                info_company = response.json()
                result['tax_code']=info_company['mst']
                result['name']=info_company['ten']
                if info_company['mst']!='':
                    result['address']=(info_company['diachi']+', '+info_company['phuong']+', '+info_company['quan']+', '+info_company['thanhpho']).replace(' ,','')
                result['status']=info_company['trangthai']
            else:
                if self.raise_error and popup:
                    raise osv.except_osv("KDERP Warning",'Contact Administrator')
        except requests.exceptions.ConnectionError:
            if self.raise_error and popup:
                raise osv.except_osv("KDERP Warning",'Contact Administrator')
        except requests.exceptions.Timeout:
            if self.raise_error and popup:
                raise osv.except_osv("KDERP Warning",'Please try again')
        except:
            if self.raise_error and popup:
                raise osv.except_osv("KDERP Warning",'Contact Administrator')
        return result
        
    def _get_tax_code_ids(self, cr, uid, ids, context):
        #tax_code_list = self.browse(cr, uid, ids[0],context).split(",")
        #for tax_code in tax_code_list:
        pass
    
    def _code_cleanup(self,codes):
        #first cleanup
        if (not codes):
            return ['','']
        codes_clean = codes.split('\n')
        for code in codes_clean:
            code = code.strip()
        code_list =[]
        error_list =[]
        #second cleanup
        for code in codes_clean:
            if (len(code)==14): #13 number code
                code_list.append(code[0:10] + '-' + code[11:])
            elif (len(code)==10):
                code_list.append(code)
            else:
                error_list.append(code)
        return [code_list, error_list]
    
    def update_for_code(self, cr, uid, ids, context):
        """
        Cap nhat hoac tao moi du lieu query tu GDT
        TODO: parallel python
        """
        #doi tuong Transient se tu xoa sau 1 khoang thoi gian
        #se sinh loi khong ton tai ids neu form de qua lau tren man hinh
        #xu ly bang cach check ids[0]
        if (not ids[0]):
            #thoat khoi chuong trinh hoac gan cho ids[0] gia tri nao do
            raise osv.except_osv ("Please refresh the form") 
        #getting the list
        tax_code_raw = self.browse(cr,uid,ids[0]).codes_to_search
        
        #clean-up tax_code: 10 and 13 character
        tax_code_list_error=self._code_cleanup(tax_code_raw)[1]
        #Show error vat code to form
        self.write(cr, uid, ids[0],{'error_codes':'\n'.join(tax_code_list_error)})
        
        tax_code_list=self._code_cleanup(tax_code_raw)[0]
        #getting and update data
        #quyet dinh: bo qua, update hay tao moi
        if len(tax_code_list) > 1: 
            self.raise_error = False
        for tax_code in tax_code_list:
            search_res = self._query_data_from_gdt(tax_code)
            if search_res:
                gdt_company = self.pool.get("gdt.companies")
                tax_code_id = gdt_company.search(cr,uid,[('tax_code','=',tax_code)])
                #search_res = self._query_data_from_gdt(tax_code)
                action = self._check_for_update(cr, uid, search_res)
                #Bo phan and ...
                if action == 'update':
                    gdt_company.write(cr,uid,tax_code_id,search_res,context)
                    tax_code_list_error.append(tax_code + ':updated')
                    self.write(cr, uid, ids[0],{'error_codes':'\n'.join(tax_code_list_error)})
                elif action == 'create':
                    gdt_company.create(cr,uid,search_res,context)
                    tax_code_list_error.append(tax_code + ':created')
                    self.write(cr, uid, ids[0],{'error_codes':'\n'.join(tax_code_list_error)})
                elif action == 'nothing':
                    #TODO
                    tax_code_list_error.append(tax_code + ':error')
                    self.write(cr, uid, ids[0],{'error_codes':'\n'.join(tax_code_list_error)})
                    continue
                else:
                    continue
            continue
        self.raise_error = True
        return True
    
    def search_for_code(self, cr, uid, ids, context):
        if ids[0]:
            return True

    def _check_for_update(self,cr, uid, values):
        """
        So sanh ket qua query va du lieu co tren database
        Neu co thay doi thi moi cap nhat.
        """
        action = 'nothing'
        if not ''.join(values.values()):#Khong lam gi khi values la dictionary rong - Kha nang khong lay duoc du lieu
            return 'nothing'
        gdt_company = self.pool.get('gdt.companies')
        tax_code_id = gdt_company.search(cr, uid,[('tax_code','=',values['tax_code'])])
        if tax_code_id:
            rec_to_comp = gdt_company.read(cr, uid, tax_code_id, ['tax_code','name','address','status'])
            for item in rec_to_comp:
                if (item.values()[0]==values[item.keys()[0]]):
                    action = 'update'
                else:
                    if (item.keys()[0]=='address'):#Voi truong hop address se kiem tra ky hon
                        if (item.values()[0].find(values[item.keys()[0]]) != -1): #Address tim kiem la mot phan cua address luu tren csdl
                            #action = 'nothing'
                            action = 'update'
                        else:
                            return 'create'
                    else:
                        return 'update'
        else:
            return 'create' 
        return action
    
    def _get_vat_code_ids(self, cr, uid, ids, name, args, context):
        """
        Lay gia tri cua cac ids
        """
        res = {}
        res[ids[0]]=[]
        codes_to_search = self.browse(cr, uid, ids[0], context).codes_to_search
        vat_codes_lst = self._code_cleanup(codes_to_search)[0]
        vat_codes_error = self._code_cleanup(codes_to_search)[1]
        #Show error vat code to form
        self.write(cr, uid, ids[0],{'error_codes':'\n'.join(vat_codes_error)})        

        #Dam bao cu phap cua lenh SQL IN
        if vat_codes_lst:
            vat_codes = ', '.join("'" + item + "'" for item in vat_codes_lst)
        else:
            vat_codes = "''"
        sql_str = """
                    SELECT id FROM gdt_companies
                    WHERE tax_code IN (%s)
                  """ %(vat_codes)
        cr.execute(sql_str)
        for vat_code_id in cr.fetchall():
            res[ids[0]].append(vat_code_id[0])

        return res
    
    _columns = {
                'codes_to_search':fields.text('Codes to Search'),
                'error_codes':fields.text('Error codes'),
                'tax_code_ids':fields.function(_get_vat_code_ids, relation='gdt.companies', type='one2many', string="Companies from GDT", method=True)
                }
    _defaults = {
                 'error_codes':'Not valid and error VAT codes will be showed here'
                 }

gdt_companies_wizard()

class gdt_companies(osv.Model):
    """
    CSDL luu tru thong tin cac cong ty tu trang web cua GDT
    """
    _name = 'gdt.companies'
    _description = 'GDT Companies'
    _rec_name = 'tax_code'
#     
    def update_data(self, cr, uid, ids, context):
        #self.pool.get("gdt.companies.wizard").raise_error = False
        tax_code = self.browse(cr, uid, ids[0], context).tax_code
        tax_code_id = self.search(cr, uid, [('tax_code','=',tax_code)])
        
        if len(ids)==1:
            search_res = self.pool.get("gdt.companies.wizard")._query_data_from_gdt(tax_code, True)
        else:
            search_res = self.pool.get("gdt.companies.wizard")._query_data_from_gdt(tax_code, False)
        if search_res:
            #gdt_company = self.pool.get("gdt.companies")
            #tax_code_id = gdt_company.search(cr,uid,[('tax_code','=',tax_code)])
            #search_res = self._query_data_from_gdt(tax_code)
            action = self.pool.get("gdt.companies.wizard")._check_for_update(cr, uid, search_res)
            if action == 'update':
                self.write(cr,uid,tax_code_id,search_res,context)
            elif action == 'create':
                self.create(cr,uid,search_res,context)
            elif action == 'nothing':
                return False
        #self.write(cr,uid,tax_code_id,data_to_update,context)
        #self.pool.get("gdt.companies.wizard").raise_error = True
        return True

    
    def gdt_link(self, cr, uid, ids, context):
        #tax_code = self.browse(cr, uid, ids[0]).tax_code
        url = 'http://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp'
        return {
                'type':'ir.actions.act_url',
                'url': url,
                'nodestroy': True,
                'target':'new'
                }
    
    def _status_desc(self, cr, uid, context):
        """
        Tra ve gia tri mo ta cua status: 00-->05 va NA
        """
        return (
                ('00','OK'),
                ('01','STOP'),
                ('02','02'),
                ('03','STOP, VAT not close'),
                ('04','OK, providing VAT'),
                ('05','PAUSE'),
                ('NA','Need Check')
                )

    _columns = {
                'tax_code':fields.char('Tax Code', size=15),
                'name':fields.char('Name',size=100),
                'address':fields.char('Address', size=100),
                'status':fields.selection(_status_desc, 'Status', size=2),
                'write_date':fields.date('Updated Date', readonly=True),
                'stop_date':fields.date('Stop Date', readonly=True),
                }
    _defaults = {
                }

gdt_companies()

                                     
        


    