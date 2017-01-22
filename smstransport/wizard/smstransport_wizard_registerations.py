from openerp.osv import fields, osv
import datetime
import logging
_logger = logging.getLogger(__name__)

class class_smstransport_registrations(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "class.smstransport_registrations"
    _description = "Details of People Registered in Transport Section"
    _columns = {
              'class_filter':   fields.boolean('Filter on Class'),
              'class_id'    :   fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active')]"),   
              'vehcile_filter'  : fields.boolean('Filter on Vehicle'),
              'vehcile_id'    :   fields.many2one('sms.transport.vehcile', 'Vehcile'),   
              'route_filter'    : fields.boolean('Filter on Route'),
              'route_id'    :   fields.many2one('sms.transport.route', 'Route'),   
              'display_phone':   fields.boolean('Display Phone?'),
              'display_email':   fields.boolean('Display Email?'),
              'display_class':   fields.boolean('Display Class?'),
              'display_address':   fields.boolean('Display Address?'),
               }
    _defaults = {
                 'class_filter': lambda*a :True,
                 'vehcile_filter': lambda*a :False,
                 'route_filter': lambda*a :False,
#                 'class_id':_get_class
                 }
    
    def print_transport_registered_entries(self, cr, uid, ids, data):
        
        thisform = self.read(cr, uid, ids)[0]
        report = 'smstransport_registered_entries'
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'sms.transport.registrations',
             'form': thisform,
             }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
            }
        
class_smstransport_registrations()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: