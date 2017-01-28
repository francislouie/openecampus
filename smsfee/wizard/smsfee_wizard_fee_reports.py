from openerp.osv import fields, osv
import datetime

class fee_reports(osv.osv_memory):

    def _get_active_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
        if ssn:
            return ssn[0]
    
    def _get_user_group(self, cr, uid, context={}):
        # 'report_type': 'annaul_report_all_classes','annaul_report_single_class','monthly_report_all_classes',
        # 'officer_type':'student_paid_fee_report','defaulter_list_annual','defaulter_student_list','monthly_feestructure_report_all_classes'
        if uid:
            return uid 
    
    _name = "fee.reports"
    _description = "admits student in a selected class"
    _columns = {
              "session": fields.many2one('sms.session', 'Session', help="Select A session , you can also print reprts from previous session."),
              "class_id": fields.many2one('sms.academiccalendar', 'Class', domain="[('session_id','=',session),('fee_defined','=',1)]", help="Select A class to load its subjects."),
#               'report_type': fields.selection([('annaul_report_all_classes','1:\tAnnual Fee Collection Report (All Classes)'),
#                                                ('annaul_report_single_class','2:\tAnnual Fee Collection Report (Single Class)'),
#                                                ('monthly_report_all_classes','3:\tMonthly Fee Collection Report (All Classes)'),
#                                                ('student_paid_fee_report','4:\tStudents Paid Fee Report'),
#                                                ('defaulter_list_annual','5:\tDefaulter Student list (Whole Session)'),
#                                                ('defaulter_student_list','6:\Defaulter Student list'),
# 											   ('monthly_feestructure_report_all_classes','7:\tMonthly Fee Structure Wise Collection Report (All Classes)'),
#                                                ],'Report Type',required = True),
              'report_type': fields.selection([('annaul_report_all_classes','1:\tAnnual Fee Collection Report (All Classes)'),
                                               ('annaul_report_single_class','2:\tAnnual Fee Collection Report (Single Class)'),
                                               ('monthly_report_all_classes','3:\tMonthly Fee Collection Report (All Classes)'),
                                               ],'Report Type'),
                
                
              'officer_type': fields.selection([
                                               ('student_paid_fee_report','1:\tStudents Paid Fee Report'),
                                               ('defaulter_list_annual','2:\tDefaulter Student list (Whole Session)'),
                                               ('defaulter_student_list','3:\Defaulter Student list'),
                                               ('monthly_feestructure_report_all_classes','4:\tMonthly Fee Structure Wise Collection Report (All Classes)'),
                                               ],'Report Type'),                
                
			  'from_date': fields.date('From'),
              'to_date': fields.date('To'),
              'month': fields.many2one('sms.session.months','Month',domain="[('session_id','=',session)]"),
              'helptext':fields.text('Help Text'),
              'user_id':fields.many2one('res.users', 'User Group'),
               }
    _defaults = {
                 'session':_get_active_session,
                 'user_id':_get_user_group,
                 'helptext':'Print Fee Reports:\n Annual Fee Collection Report, Monthly Fee Collection,Monthly Fee Strucuture Wise Collection,Annual & Monthly Defaulter students..Many More '
           }
    
    def print_fee_report(self, cr, uid, ids, data):
        result = []
        thisform = self.read(cr, uid, ids)[0]
        
        reporttype = thisform['report_type']
        if thisform['officer_type'] !=False:
            reporttype = thisform['officer_type']
        
        if reporttype =='annaul_report_all_classes':
            report = 'smsfee.annaul.allclasses.name'
        elif reporttype =='annaul_report_single_class':
            report = 'smsfee.annaul.singleclass.name'
        elif reporttype =='monthly_report_all_classes':
            report = 'smsfee.monthlyfeecollection.allclasses.name'
            
        elif reporttype =='student_paid_fee_report':
            report = 'smsfee_students_paidfee_report_name'
        elif reporttype =='defaulter_student_list':
            report = 'smsfee_defaulter_studnent_list_name'
        elif reporttype =='defaulter_list_annual':
            report = 'smsfee_annaul_defaulter_list_name'        
        elif reporttype =='monthly_feestructure_report_all_classes':
            report = 'smsfee.monthly.feestructure.collections.allclasses.name'
                
        
 
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.register',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
        }
                
fee_reports()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: