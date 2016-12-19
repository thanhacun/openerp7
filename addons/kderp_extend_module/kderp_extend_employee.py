from osv import osv, fields

class hr_employee(osv.osv):
    _name = 'hr.employee'
    _description = 'Employee Working'
    _inherit = 'hr.employee'

    #Get function temple from Willow Pentaho OpenERP Report
    def report_custom_get_directorname(self, cr, uid, *param):
        """Custom data method for 'ids' report.
        'param' is a tuple where the first element is a dict with
        any report parameters (keyed by the parameter name) and
        other environmental info.
        In this example the report has a single defined parameter
        'ids' which is a list of integers.
        The 'ids' parameter will be automatically populated by the
        pentaho_reports module when the report is associated with
        the res.partner model and the report is run via the
        partners 'Print' menu. See reports.xml in this module.
        """

        #       Comment-in the line below to see the params passed
        #       from Pentaho to this method.
        #       print("***DEBUG IDS PARAMS: |%s|" % param)

        param = param[0]

        # If getFields is true then return dict of field names
        # in the result set of this method.
        if param.get('getFields'):
            return [{
                'name': {'type': 'string'},
            }]

        gdName = ''
        user_obj = self.pool.get('res.users').browse(cr, uid, uid)
        if user_obj.general_director_id:
            gdName = user_obj.general_director_id.name
        elif user_obj.company_id.general_director_id:
            gdName = user_obj.company_id.general_director_id.name

        # Build the result
        result = [{
                'name': gdName
            }]


        return result

    _columns={
              'working':fields.boolean('Working')
              }
    _defaults = {
                 'working': 1
                 }
hr_employee()