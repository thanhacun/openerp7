from osv import osv
from tools.translate import _

class AdditionalDiscountable(object):

    _line_column = 'order_line'
    _tax_column = 'tax_id'

    def record_currency(self, record):
        """Return currency browse record from a browse record.

        Default implementation is for sale/purchase order.
        """
        return record.pricelist_id.currency_id


    def _amount_all_generic(self, cls, cr, uid, ids, field_name, arg,
                            context=None):
        """Generic overload of the base method to add discount infos

        This is a generic version that needs to be passed the caller class (for
        super).
        For now it can be applied to sale.order, purchase.order and
        account.invoice, using the methods and attrs of AdditionalDiscountable
        """
        cur_obj = self.pool.get('res.currency')
        if not context:
            context = {}
         
        disc_type =context.get('disc_type','percent') 
        
        res = super(cls, self)._amount_all(cr, uid, ids, field_name, arg, context)
        
        for record in self.browse(cr, uid, ids, context=context):
            # Taxes are applied line by line, we cannot apply a
            # discount on taxes that are not proportional
            if not all(t.type == 'percent'
                       for line in getattr(record, self._line_column)
                       for t in getattr(line, self._tax_column)):
                raise osv.except_osv(_('Discount error'),
                                     _('Unable (for now) to compute a global '
                                       'discount with non percent-type taxes'))
            o_res = res[record.id]

            cur = self.record_currency(record)
            def cur_round(value,disc_type='percent'):
                """Round value according to currency."""
                return cur_obj.round(cr, uid, cur, value)

            # add discount
            amount_untaxed = sum(line.price_subtotal
                                 for line in getattr(record, self._line_column))
            if disc_type=='percent':
                add_disc = record.add_disc
                add_disc_amt = cur_round(amount_untaxed * add_disc / 100)
                o_res['add_disc_amt'] = add_disc_amt
            else:
                add_disc_amt = record.add_disc_amt
                if not amount_untaxed:
                    add_disc = 0.0
                else:
                    add_disc = cur_round(add_disc_amt/amount_untaxed * 100.0)
                o_res['add_disc'] = add_disc
                
            o_res['amount_net'] = o_res['amount_untaxed'] - add_disc_amt

            # we apply a discount on the tax as well.
            # We might have rounding issue
            o_res['amount_tax'] = cur_round(
                o_res['amount_tax'] * (100.0 - (add_disc or 0.0))/100.0)
            o_res['amount_total'] = o_res['amount_net'] + o_res['amount_tax']

        return res

