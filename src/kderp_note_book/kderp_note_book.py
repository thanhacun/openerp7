import netsvc
from openerp.osv import osv, fields

class book_author(osv.osv):
    _name = 'book.author'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'birthdate': fields.date('Birthday'),
        'gender' : fields.boolean('Gender'),
        'country' : fields.char('Country', size=32),
    }
    _defaults = {
    }
book_author()
 
class book_publisher(osv.osv):
    _name = 'book.publisher'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'address': fields.char('Address', size=128),
    }
    _defaults = {
    }
book_publisher()
 
class kderp_readers_line(osv.osv):
    _name='kderp.readers.line'    
    _description='Customize Detail of Advance Payment for Kinden'

    _columns={
                'readers':fields.char('Readers',size=256,required=True),
                'date_lend':fields.date('Date Lend'),
                'date_receive_expected':fields.date('Date Rev Expected'),
                'date_receive_fact':fields.date('Date Rev Fact'),
                'readers_id':fields.many2one('kderp.note.book','Readers',required=True,ondelete='cascade')
              }
kderp_readers_line()

class kderp_note_book(osv.osv):
    _name  = "kderp.note.book"
    _description = "Simple Notebook"
    _order = "book_number desc"
#    _rec_name = ""
    STATE_SELECTION=[('draft', 'New'),
                     ('open', 'Accepted'),
                     ('cancel', 'Refused'),
                     ('close', 'Done')]
    def _get_total(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for notebook in self.browse(cr, uid, ids,context):
            res[notebook.id]= notebook.price+notebook.discount
        return res
               
    def create(self, cr, uid, vals, context=None):
        if vals.get('book_number','/')== "/":
            vals['book_number'] = self.pool.get('ir.sequence').get(cr, uid, 'kderp.note.book') or "/"
        new_obj=super(kderp_note_book, self).create(cr, uid, vals, context=context)
        return new_obj
#    def _get_name(self, cr, uid, ids, name=None, args=None, context=None):#        if context == None:
#            context = {}
#        res = {}
#        for var in self.browse(cr, uid, ids, context=context):
#            res[var.id] = "%s - %s" % (var.book_number,var.name)
#        return res

    _columns = {
#        'full_name': fields.function(_get_name,  type='char', string='Full Name', store={
#                                                                                         'kderp.note.book':(lambda self, cr, uid, ids, c={}: ids, ['book_number','name'], 50)}),
        'book_number': fields.char('Book Number', size=64, required=True),       
        'name': fields.char('Name', size=64, required=True),
        'author': fields.many2one('book.author', 'Author', required=True),
        'publisher': fields.many2one('book.publisher', 'Publisher', required=True),
        'publish_date': fields.date('Publish Date'),
        'height': fields.float('Height'),
        'width': fields.float('Width'),
        'weight': fields.float('Weight'),
        'price' : fields.float('Price'),
        'discount' : fields.float('Discount'),
        'description' : fields.text('Description'),
        'total': fields.function(_get_total, 'Total'),
        'readers_line':fields.one2many('kderp.readers.line','readers_id','Readers'),
        'state':fields.selection(STATE_SELECTION,"Status",select=1)
        }
    _defaults = {'state':lambda *x: 'draft',
                 'book_number': lambda obj, cr, uid, context : "/"}

    def notebook_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def notebook_open(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    def notebook_close(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)

    def notebook_draft(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    
    def wkf_action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for adv_id in ids:
            wf_service.trg_create(uid, 'kderp.note.book', adv_id, cr)
        return True
    
    def wkf_action_done_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for adv_id in ids:
            wf_service.trg_create(uid, 'kderp.note.book', adv_id, cr)
        return True
kderp_note_book()