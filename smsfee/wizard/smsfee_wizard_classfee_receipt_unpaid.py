from openerp.osv import fields, osv
import datetime
import logging
_logger = logging.getLogger(__name__)

class class_fee_receipts_unpaid(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "class.fee.receipts.unpaid"
    _description = "admits student in a selected class"
    _columns = {
              "class_id": fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active'),('fee_defined','=',1)]", help="Class"),
              'due_date': fields.date('Due Date', required=True),
              'amount_after_due_date': fields.integer('Payment After Due Date'),
               'category':fields.selection([('Academics','Academics'),('Transport','Transport')],'Fee Bill Category'),
               }
    _defaults = {'class_id':_get_class}
    
    def create_unpaid_challans(self, cr, uid, class_id,category):
        # create unpaid challans for category academic
        _logger.warning("Deprecated, usle c............................................................................")
        student_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',class_id[0]),('state','=','Current')])
        if student_ids:
            recstudent = self.pool.get('sms.academiccalendar.student').browse(cr,uid,student_ids)
            for student in recstudent:
                #----------Passing 'Full' as an argument. Since this challan is for whole class so we don't need to pass the option of Partial here ----- 
                self.pool.get('smsfee.receiptbook').check_fee_challans_issued(cr, uid, class_id[0], student.std_id.id, category, 'Full', None)
        return True

    def check_challan_print_type(self, cr, uid, thisform):
        challan_type = self.pool.get('res.company').search(cr, uid, [])
        challan_type = self.pool.get('res.company').browse(cr, uid, challan_type)
        for obj in challan_type:
            if obj.fee_report_type == 'One_on_One':
                return 'print_one_on_one'
            else:
                return 'print_three_on_one'
        return True
    
    def check_trans_challan_print_type(self, cr, uid, thisform):
        challan_type = self.pool.get('res.company').search(cr, uid, [])
        challan_type = self.pool.get('res.company').browse(cr, uid, challan_type)
        for obj in challan_type:
            if obj.fee_report_type_trans == 'One_on_One':
                return 'print_one_on_one'
            else:
                return 'print_three_on_one'
        return True
    
    def print_fee_report_challan(self, cr, uid, ids, data):
        
        thisform = self.read(cr, uid, ids)[0]
        checking_challan = self.check_challan_print_type(cr, uid, thisform)
        checking_trans_challan = self.check_trans_challan_print_type(cr, uid, thisform)
        if thisform['category'] == 'Academics':
            if checking_challan == 'print_three_on_one':
                report = 'smsfee_print_three_student_per_page'
                thisform = self.read(cr, uid, ids)[0]
                self.create_unpaid_challans(cr, uid, thisform['class_id'],'Academics')
                
            elif checking_challan == 'print_one_on_one':
                report = 'smsfee_print_one_student_per_page'
                thisform = self.read(cr, uid, ids)[0]
                self.create_unpaid_challans(cr, uid, thisform['class_id'],'Academics')
                
                
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
            
        if thisform['category'] == 'Transport':
            if checking_trans_challan == 'print_three_on_one':  
                report = 'smstransport_print_three_student_per_page'
                thisform = self.read(cr, uid, ids)[0]
                self.create_unpaid_challans(cr, uid, thisform['class_id'],'Transport')
        
            elif checking_trans_challan == 'print_one_on_one':  
                report = 'smstransport_print_one_student_per_page'
                thisform = self.read(cr, uid, ids)[0]
                self.create_unpaid_challans(cr, uid, thisform['class_id'],'Transport')  
            
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
        else:
            thisform = self.read(cr, uid, ids)[0]
            self.create_unpaid_challans(cr, uid, thisform['class_id'])
            report = 'smsfee_print_one_student_per_page'        
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
class_fee_receipts_unpaid()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: