from openerp.osv import fields, osv
import datetime
from openerp import tools

class update_fee_register(osv.osv_memory):
    
    """
    This is an attempt to show student attendance summary on a runtime view ,but current result shows all columns have same value, this may be enhanced nex
    time, last update on 13-12-2017
    
    """

    _name = "update.fee.register"
    _description = "Update monthly class register"
    _columns = {
              'commenced_classes':fields.integer('Total Days'),      
              'total_present': fields.integer('Present'),
              "total_absent": fields.integer('Absent'),
              'total_leaves':fields.integer('Leaves'),
              'percent':fields.integer('Percent'),
               }
   
    
    def _select(self):
        select_str = """
             select count(parent.id) as commenced_classes,
                count(child.present) as total_present,
                count(child.absent) as total_absent, 
                count(child.leave) as total_leaves           
                
                        """
        return select_str

    def _from(self):
        from_str = """
                sms_class_attendance as parent
                left join sms_class_attendance_lines as child on parent.id = child.parent_id
                where child.student_name = 59

                 """
        return from_str

#     def init(self, cr):
#         # self._table = hr_timesheet_report
#         tools.drop_view_if_exists(cr, self._table)
#         cr.execute("""CREATE or REPLACE VIEW %s as (
#             %s
#             FROM ( %s )
#             %s
#             )""" % (self._table, self._select(), self._from())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: