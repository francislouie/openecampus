

import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_compute_salary(osv.osv_memory):

    _name ='hr.compute.salary'
    _description = 'hr compute salary'
    _columns = {
          'month_comp': fields.date('Select month to compute salary',required=True)
           }
    
    
    def compute_salary(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids)[0]['month_comp']
        print"data",data
        return self.pool.get('sms.pull.hr.machine.data').compute_attendance_holidays(cr, uid, ids ,data)
    
    
    
hr_compute_salary()
