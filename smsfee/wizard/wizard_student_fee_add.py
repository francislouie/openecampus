from openerp.osv import fields, osv
import logging
import  datetime
_logger = logging.getLogger(__name__)

class class_student_fee_collectt(osv.osv_memory):
    def getfee_cate(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = f.fee_type.fee_type.category
        return result

    def _get_student(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id

    def _get_current_class(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id = obj.id
        students = self.pool.get('sms.student').search(cr, uid,[('id','=',obj.id)])
        student=self.pool.get('sms.student').browse(cr, uid, students)
        cur_cls=1
        for std in student:
            cur_cls=std.current_class.id

        print("student",student)
        return cur_cls
    def _get_session_months(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id = obj.id
        month_ids=[]
        sql = """select id from sms_session_months where session_id=(select  a.session_id from sms_academiccalendar As a  
	             inner join sms_student As s on s.current_class=a.id
	               where s.id="""+str(std_id)+""" )"""
        cr.execute(sql)
        _ids = cr.fetchall()
        for thisfee in _ids:
            month_ids.append(thisfee[0])

        # students = self.pool.get('sms.student').search(cr, uid,[('id','=',obj.id)])
        # student=self.pool.get('sms.student').browse(cr, uid, students)
        # cur_cls=1
        # for std in student:
        #     cur_cls=std.current_class.id
        # acad_cal_search = self.pool.get('sms.academiccalendar').search(cr, uid,[('id','=',cur_cls)])
        # acad_cal = self.pool.get('sms.academiccalendar').browse(cr, uid, acad_cal_search)
        # ss_id = 1
        # for stdd in acad_cal:
        #     ss_id = stdd.session_id.id
        # print( "ss_id", ss_id)
        # print("student_id",obj.id)
        # session_months = self.pool.get('sms.session.months').search(cr, uid,[('session_id','=',ss_id)]),
        # print("session_months[0]",session_months[0],"session_months",session_months)
        print("months:",month_ids)
        return month_ids


    _name = "class.student_fee_collectt"
    _description = "Student's Fee Wizard"
    _columns = {
               'student_id': fields.many2one('sms.student', 'Student', domain="[('state','=','Admitted')]", help="Student"),
               "class_id": fields.many2one('sms.academiccalendar', 'Class',
                   domain="[('state','=','Active'),('fee_defined','=',1)]", help="Class"),
              'generic_fee_type':fields.many2one('smsfee.feetypes','Fee type'),
              'due_month': fields.many2one('sms.session.months', 'Payment Month'),
              'fee_month': fields.many2one('sms.session.months', 'Fee Month'),
              'fee_type': fields.many2one('smsfee.classes.fees.lines', 'Fee Type'),
              'fee_amount': fields.integer('Fee'),
              'late_fee': fields.integer('Late Fee'),
              'category': fields.selection( string='Category', type='selection',
                                     selection=[('Academics', 'Academics'), ('Transport', 'Transport'),
                                                ('Hostel', 'Hostel'), ('Stationary', 'Stationary'),
                                               ('Portal', 'Portal')])
               }

    _defaults = {'class_id':_get_current_class,'student_id':_get_student}

    def action_pay_student_fee(self, cr, uid, ids, context):
        domain = []
        thisform = self.read(cr, uid, ids)[0]
        # domain = [('id','>=',thisform['challan_id'][0])]
        fee_dcit = {
            'student_id':thisform['student_id'][0],
            'acad_cal_id':thisform["class_id"][0],
            'date_fee_charged': datetime.date.today(),
            'due_month':thisform['due_month'][0],
            'fee_month': thisform['fee_month'][0],
            'paid_amount': 0,
            'fee_amount': thisform['fee_amount'],
            'late_fee': thisform['late_fee'],
            'discount': 0,
            'total_amount': thisform['fee_amount'] + thisform['late_fee'],
            'reconcile': False,
            'state': 'fee_unpaid',
            'generic_fee_type':thisform['generic_fee_type'][0],
            'fee_type':thisform['fee_type'][0],
            'category':thisform['category']

        }
        add_fee = self.pool.get('smsfee.studentfee').create(cr, uid, fee_dcit)

        result = {
                'type': 'ir.actions.act_window',
                'name': 'Collect Fees',
                'res_model': 'smsfee.studentfee',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'nodestroy': True,
                'target': 'current',
                }

        return add_fee




class_student_fee_collectt()

# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
# session_months = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',new_cal_obj.session_id.id),('id','>=',std.fee_starting_month.id)])
#                                 rec_months = self.pool.get('sms.session.months').browse(cr,uid,session_months)