from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp
from datetime import datetime, timedelta
import random, string

SKIP_DATE = 'SKIP_DATE_RECORDING'

class PentahoAuthCrypt(osv.osv):
    _name = 'pentaho.auth.crypt'
    _description = 'Pentah Auth Crypt'

    _columns = {
                'user_id':fields.many2one('res.users'),
                'value':fields.char(),
                'timestamp':fields.datetime()
    }

class res_users(osv.osv):
    _inherit = "res.users"

    def decide_on_password(self, cr, uid):
        # If we could determine if the report needs to call back, we could make this step optional and not execute every time...
        return self.create_temporary_password_pentaho(cr, uid)

    def reverse_password(self, cr, uid, password):
        self.remove_temporary_password_pentaho(cr, uid, password)

    def create_temporary_password_pentaho(self, cr, uid):

        pword = ''.join(random.choice(string.ascii_letters + string.digits + '!@#$%^&*()') for x in range(64))

        self.pool.get('pentaho.auth.crypt').create(cr, uid, {'user_id': uid,
                                          'value': pword,
                                          'timestamp': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                          })
        cr.commit()
        return pword

    def strip_password(self, cr, uid, password):
        if password[0:len(SKIP_DATE)] == SKIP_DATE:
            password = password.replace(SKIP_DATE, '')
        return password

    def check_credentials(self, cr, uid, password):
        #password = self.strip_password(cr, uid, password)
        cr.execute ('SELECT id FROM pentaho_auth_crypt WHERE user_id=%s AND value=%s', (uid, password))
        if cr.rowcount:
            return
        return
        res = super(res_users, self).check_credentials(cr, uid, password)
        #raise osv.except_osv("E","%s-%s" % (password,res))
        return res

    def remove_temporary_password_pentaho(self, cr, uid, value):
        # also get rid of tokens that are over 24 hours old...
        recs = self.pool.get('pentaho.auth.crypt').search(cr, uid, ['|', '&',
                                                 ('user_id', '=', uid),
                                                 ('value', '=', value),
                                                 ('timestamp', '<=', (datetime.now() - timedelta(hours=24)).strftime(DEFAULT_SERVER_DATETIME_FORMAT))
                                                 ])
        recs.unlink()
        cr.commit()
