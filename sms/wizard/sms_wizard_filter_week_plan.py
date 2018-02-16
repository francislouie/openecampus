
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp import netsvc
class sms_filter_week_plan(osv.osv_memory):
    """Use this wizard to filter_week_plan"""

    _name = "sms.filter.week.plan"
    _description = "sms_filter_week_plan"
  
    def filter_week_plan(self, cr, uid, ids, context=None):
        week_p = self.pool.get('sms.weekly.plan')
        cr.execute("""select id,job_id from hr_employee where resource_id =(select id from resource_resource where user_id =""" + str(uid) + """  )""")
        emp_obj = cr.fetchone()
        tea_emp_id = emp_obj[0]
        tea_job_id = emp_obj[1]
     
        ids = week_p.search(cr, uid, [('teacher','=',tea_emp_id)], context=context)

        if tea_job_id ==1:
            domain = "[('id','in',["+','.join(map(str, ids))+"])]"
        else:
            domain = "[]"
        print"domain",domain
        value = {
            'domain': domain,
            'name': _('Week Plan'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sms.weekly.plan',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
        if len(ids) == 1:
            value['res_id'] = ids[0]
        return value

sms_filter_week_plan()

