#this is the final wizard code used to create academics and transporet challans
#currently this is used for generation of class wise challans
# will soon be used for indivudual sutdents challans from student form, both for academics and transport or any other
#last udpate: 18oct

from openerp.osv import fields, osv
import datetime
import logging
_logger = logging.getLogger(__name__)

class class_fee_receipts_unpaid(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
#         thisform = self.read(cr, uid, ids)[0]
        obj = self.browse(cr, uid, ids['active_id'])
#         print'---- obj id ----', thisform
#         std_id =  int(thisform['class_id'])
        std_id = obj.id
        return std_id
    
    def _get_amount(self, cr, uid, ids):
        amount = 200
#         thisform = self.read(cr, uid, ids)[0]
#         class_id = thisform['class_id']
#         if class_id:
#             acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,class_id)
#             amount =  acad_cal_obj.class_id.acad_session_id.late_fee_amount
        return amount
    
    def _get_total_pending(self, cr, uid, ids):
        total_pending = 0
        class_ids = self._get_class(cr, uid, ids)
        print'------ Class Id ------', class_ids
        pending_amount = self.pool.get('sms.academiccalendar').get_open_pending_receipts(cr, uid, class_ids, 'Waiting_Approval', 'Academics')
        if pending_amount:
            total_pending = pending_amount
        return total_pending
    
    def _get_total_open(self, cr, uid, ids):
        total_pending = 0
        class_ids = self._get_class(cr, uid, ids)
        print'------ Class Id ------', class_ids
        pending_amount = self.pool.get('sms.academiccalendar').get_open_pending_receipts(cr, uid, class_ids, 'fee_calculated', 'Academics')
        if pending_amount:
            total_pending = pending_amount
        return total_pending
    
    def onchange_get_open_pending(self, cr, uid, ids, cat, class_id):
        print'------ on change mehtod --------', cat, class_id

        open_amount = self.pool.get('sms.academiccalendar').get_open_pending_receipts(cr, uid, class_id, 'fee_calculated', cat)
        waiting_amount = self.pool.get('sms.academiccalendar').get_open_pending_receipts(cr, uid, class_id, 'Waiting_Approval', cat)
        
        print'--------- return value from this --------', open_amount, waiting_amount

        return {'value': {'total_pending':waiting_amount,'total_open':open_amount}}
   

    _name = "class.fee.receipts.unpaid"
    _description = "admits student in a selected class"
    _columns = {
            "Dublicate": fields.boolean('Duplicate Fee Bill'),
              'class_id': fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active'),('fee_defined','=',1)]", help="Class"),
              'due_date': fields.date('Due Date', required=True),
              'total_pending': fields.text('Pending Challans', readonly=True),
              'total_open': fields.text('Open Challans', readonly=True),
              'amount_after_due_date': fields.integer('Fine After Due Date',readonly=True),
               'category':fields.selection([('Academics','Academics'),('Transport','Transport')],'Fee Bill Category',required=True),
               }
    
    _defaults = {'class_id':_get_class,
                 'amount_after_due_date':_get_amount,
                'total_pending': _get_total_pending,
                'total_open': _get_total_open,
                'category': 'Academics'
                 }
    
    def create_unpaid_challans(self, cr, uid, class_id,due_date,category):
        print "create upaid challans"
        # create unpaid challans for category academic when called for academics, or crete for transp[ort when called for transpoert
        
        _logger.warning("Deprecated, usle c............................................................................")
        student_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',class_id[0]),('state','=','Current')])
        if student_ids:
            print 'student_ids',student_ids
            recstudent = self.pool.get('sms.academiccalendar.student').browse(cr,uid,student_ids)
            for student in recstudent:
                #----------Passing 'Full' as an argument. Since this challan is for whole class so we don't need to pass the option of Partial here ----- 
                self.pool.get('smsfee.receiptbook').check_fee_challans_issued(cr, uid, class_id[0], student.std_id.id, category, 'Full',due_date, None)
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
    
    def print_fee_report_challan(self, cr, uid, ids, data):
        thisform = self.read(cr, uid, ids)[0]
        print ("dublicate vate",thisform['Dublicate'])
        
        thisform = self.read(cr, uid, ids)[0]
        checking_challan = self.check_challan_print_type(cr, uid, thisform)
        if thisform['category'] == 'Academics':
            if checking_challan == 'print_three_on_one':
                report = 'smsfee_print_three_student_per_page'
                thisform = self.read(cr, uid, ids)[0]
                print "dublicate vate",thisform['Dublicate']
                if thisform['Dublicate']==False:

                    self.create_unpaid_challans(cr, uid, thisform['class_id'],thisform['due_date'],'Academics')
                
            elif checking_challan == 'print_one_on_one':
                report = 'smsfee_print_one_student_per_page'
                thisform = self.read(cr, uid, ids)[0]
                if thisform['Dublicate'] == False:
                    self.create_unpaid_challans(cr, uid, thisform['class_id'],thisform['due_date'],'Academics')
                
                
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
            #then also called the parser of academics challan 
            #comenting the code that calls parser of transport module
            #becuase one parser will be called by all challan single student or whole class, transport or academics, all will call same parser
            if checking_challan == 'print_three_on_one':  
                #report = 'smstransport_print_three_student_per_page'
                report = 'smsfee_print_three_student_per_page' #here parser of academics also called for transport, threee students one page
                thisform = self.read(cr, uid, ids)[0]
                if thisform['Dublicate'] == False:
                    self.create_unpaid_challans(cr, uid, thisform['class_id'],thisform['due_date'],'Transport')
        
            elif checking_challan == 'print_one_on_one':  
                #report = 'smstransport_print_one_student_per_page'
                report = 'smsfee_print_one_student_per_page'
                thisform = self.read(cr, uid, ids)[0]
                if thisform['Dublicate'] == False:
                    self.create_unpaid_challans(cr, uid, thisform['class_id'],thisform['due_date'],'Transport')
            
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
            if thisform['Dublicate'] == False:
                self.create_unpaid_challans(cr, uid, thisform['class_id'],thisform['due_date'])
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