
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp import netsvc
class sms_filter_subject_open(osv.osv_memory):
    """Use this wizard to filter subject"""

    _name = "sms.filter.subject.open"
    _description = "sms_filter_subject_open"
  
    def filter_subject(self, cr, uid, ids, context=None):
       
        ts = self.pool.get('sms.academiccalendar.subjects')
        if context is None:
            context = {}
        view_type =  'tree,form'

        user_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        if not len(user_ids):
            raise osv.except_osv(_('Error!'), _('Please create an employee and associate it with this user.'))
        cr.execute("""select id from hr_employee where resource_id =(select id from resource_resource where user_id =""" + str(uid) + """  )""")
        tea_id = cr.fetchone()[0]
        
        ids = ts.search(cr, uid, [('teacher_id','=',tea_id)], context=context)

        if len(ids) > 1:
            view_type = 'tree,form'
            domain = "[('id','in',["+','.join(map(str, ids))+"])]"
        elif len(ids)==1:
            domain = "[('id', '=', ["+''.join(map(str, ids))+"])]"
        else:
            domain = "[('id', '=', ["+''.join(map(str, ids))+"])]"
        print"domain",domain
        value = {
            'domain': domain,
            'name': _('My Sbject'),
            'view_type': 'form',
            'view_mode': view_type,
            'res_model': 'sms.academiccalendar.subjects',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
        if len(ids) == 1:
            value['res_id'] = ids[0]
        return value
            
            
       

sms_filter_subject_open()

