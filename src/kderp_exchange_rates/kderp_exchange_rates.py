from openerp.osv.orm import Model
from openerp.osv import osv, fields

class kderp_currency(osv.osv):
    _name = 'kderp.currency'
    _columns = {
        'cur_code': fields.char('Currency Code', size=64, required=True),
        'name': fields.char('Currency Name', size=128),
    }
kderp_currency()

class kderp_exchange_rates(osv.osv):
    _name  = 'kderp.exchange.rates'
    _description = 'Exchange Rates'
    
    def today_exrate(self, cur):
        """
        Tra ve ti gia ngay hom nay cua mot loai tien
        """
        #Getting current exrate from
        #VCB website
        import requests
        from datetime import datetime
        from bs4 import BeautifulSoup
        url = 'http://www.vietcombank.com.vn/ExchangeRates/ExrateXML.aspx'
        r = requests.get(url)
        cur_ids = {'USD':1,'JPY':2,'EUR':3}
        if (not r.raise_for_status()):
            data = BeautifulSoup(r.text)
            today = data.find("datetime").text.strip()
            #tra ve chi ngay hom nay  - khong co thoi gian
            today = datetime.strptime(today, '%m/%d/%Y %H:%M:%S %p')
            today = today.date()
            ex_data = data.find("exrate",attrs={"currencycode":cur})
            buy = float(ex_data['buy'])
            sell = float(ex_data['sell'])
            transfer = float(ex_data['transfer'])
#        today = datetime.now()
#        buy = 21000
#        sell = 20500
#        transfer = 20000 
        return {'date':today,'cur_id':cur_ids[cur],'buy':buy,'sell':sell,'tranfer':transfer}
    
    def UJE_exrate(self,cr,uid, ids=None, context=None):
        """
        Lay ti gia cua USD, JPY va EUR
        Ghi vao CSDL
        """
        from datetime import datetime
        today = datetime.now().date()
        ##Chi tao moi khi chua co du lieu cua ngay hom do
        #tim xem da co ban ghi chua
        #if (not self.search(cr, uid, [('date','=',today)])):
        self.create(cr, uid, self.today_exrate("USD")) #ti gia USD
        self.create(cr, uid, self.today_exrate("JPY")) #ti gia JPY
        self.create(cr, uid, self.today_exrate("EUR")) #ti gia EUR
       # else:
       #     return False
    
    _columns = {
        'cur_id': fields.many2one('kderp.currency', 'Currency', required=True),
        'buy': fields.float('Buy'),
        'sell': fields.float('Sell'),
        'tranfer': fields.float('Tranfer'),
        'date': fields.date('Date', size=64, required=True)       
    }

kderp_exchange_rates()