from openerp.osv import fields, osv
#from openerp import tools
#from openerp import addons
#import datetime
#import xlwt
#import xlrd
#from dateutil import parser
import logging
_logger = logging.getLogger(__name__)
      
class sms_transport_location(osv.osv):
    
    """This object maintains transport locations """
    
    _name="sms.transport.location"
    _columns = {
        'name' : fields.char('Name', size=256),
        'state': fields.selection([('Active', 'Active'),('UnActive', 'UnActive')], 'State'),
            } 
    _defaults = {
                 'state': lambda*a :'Active',
                }
sms_transport_location()

class sms_transport_route(osv.osv):
    
    """This object maintains transport routes Data"""
    
    _name="sms.transport.route"
    _columns = {
        'name' : fields.char('Name', size=256),
        'transport_location':fields.many2one('sms.transport.location','Transport Location'),
        'state': fields.selection([('Active', 'Active'),('UnActive', 'UnActive')], 'State'),        
            } 
    _defaults = {
                 'state': lambda*a :'Active',
                 }
sms_transport_route()

class sms_transport_vehcile(osv.osv):
    """This object maintains transport vehciles """
    
#     def _get_vehcile_name(self, cr, uid, ids):
#         result = []
#         for rec in self.browse(cr, uid, ids):
#             result = rec.vehcile_type + ' - ' +rec.vehcile_no
#         return result
    
    _name="sms.transport.vehcile"
    _columns = {
        'name' : fields.char('Name', size=256),
        'vehcile_type': fields.selection([('Bus', 'Bus'),('Van', 'Van')], 'Vehcile Type'),
        'max_accomodation':fields.integer('Maximum Seats'),
        'current_accomodation':fields.integer('Filled Seats'),
        'transport_route':fields.many2many('sms.transport.route', 'sms_transport_route_vehcile_rel', 'sms_transport_route_id', 'sms_transport_vehcile_id','Transport Route'),
        'drivers':fields.many2many('hr.employee', 'hr_driver_vehcile_rel', 'hr_driver_id', 'sms_transport_vehcile_id','Vehcile Drivers'),
        'income_amount':fields.float('Income Amount'),
        'expanse_amount':fields.float('Expanse Amount'),
        'registered_students':fields.one2many('sms.student', 'vehcile_reg_students_id', 'Students'),
        'registered_staff':fields.one2many('hr.employee', 'vehcile_reg_employee_id', 'Employees'),
        'vehcile_no':fields.integer('Vehicle Number'), 
            } 
    _defaults = {
                 'vehcile_type': lambda*a :'Bus',
                 #'name':_get_vehcile_name,
                 }
    
sms_transport_vehcile()

class sms_transport_fee_structure(osv.osv):
    """This object maintains transport vehciles """
    
    _name="sms.transport.fee.structure"
    _columns = {
        'name' : fields.char('Name', size=256),
        'transport_route': fields.many2one('sms.transport.route','Transport Route'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'fiscal_year':fields.many2one('account.fiscalyear', 'Fiscal Year'),
        'monhtly_fee':fields.float('Monthly Fee'),
        'registration_fee':fields.float('Registration Fee'),
            } 
    _defaults = {}
    
sms_transport_fee_structure()

class sms_transport_registrations(osv.osv):
    """This object maintains transport registrations """
    
    def _set_registration_name(self, cr, uid, ids, fields,args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            if f.registration_type == 'Student':
                string =  'Std: ' + str(f.student_id.name)
            else:
                string =  'Emp: ' + str(f.employee_id.name)
            result[f.id] = string
        return result

    def register_person(self, cr, uid, ids, name):
        fee_structure = self.pool.get('sms.transport.fee.structure').search(cr,uid,[])
        fee_structure = self.pool.get('sms.transport.fee.structure').browse(cr,uid,fee_structure)
        for rec in fee_structure:
            registration_fee = rec.registration_fee
            
        for record in self.browse(cr, uid, ids):
            # --------- Register Person requesting to avail transport and also make entry in registration lines object. ------------
            result = self.write(cr,uid,record.id,{'state':'Registered'})
            if result:
                if record.registration_type == 'Employee':
                    registration_id = self.pool.get('sms.transport.registrations.lines').create(cr,uid,
                                                                            {
                                                                            'registeration_id': record.id,
                                                                            'state': record.state, 
                                                                            'current_vehcile':record.current_vehcile,
                                                                            'employee_id':record.employee_id.id,
                                                                            })
                    if registration_id:
                        self.pool.get('hr.employee').write(cr, uid, record.employee_id.id,{'transport_availed':True,
                                                                                   'vehcile_reg_students_id':record.current_vehcile
                                                                                    })
                        
                elif record.registration_type == 'Student':
                    registration_id = self.pool.get('sms.transport.registrations.lines').create(cr,uid,
                                                                             {
                                                                            'registeration_id': record.id,
                                                                            'state': record.state, 
                                                                            'current_vehcile':record.current_vehcile.id,
                                                                            'student_id':record.student_id.id,
                                                                            })
                    if registration_id:
                        student_id = self.pool.get('sms.student').search(cr,uid,[('id','=',record.student_id.id)])
                        self.pool.get('sms.student').write(cr, uid, student_id,{'transport_availed':True,'vehcile_reg_students_id':record.current_vehcile.id,'transport_reg_id':record.id})
                        self.pool.get('sms.transport.fee.payments').\
                                                                create(cr,uid,
                                                                {
                                                                'registeration_id': record.id,
                                                                'state': 'Unpaid', 
                                                                'student_id':record.student_id.id,
                                                                'registration_fee':registration_fee
                                                                })
#                         current_ac
#                         self.pool.get('sms.transport.vehcile').write(cr, uid, student_id,{'current_accomodation':True,'vehcile_reg_students_id':record.current_vehcile.id,'transport_reg_id':record.id})
                                                                
                                                                
        return result
    
    _name="sms.transport.registrations"
    _columns = {
#        'name' : fields.function(_set_registration_name, method=True,  string='Transport Fee',type='char', store=True),
        'name' : fields.char('Name', size=256),
        'registration_type':fields.selection([('Employee', 'Employee'),('Student', 'Student')], 'Registration For'),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'student_id':fields.many2one('sms.student','Student'),
        'reg_start_date': fields.date('Start Date'),
        'reg_end_date': fields.date('End Date'),
        'current_vehcile':fields.many2one('sms.transport.vehcile','Vechile'),
        'state':fields.selection([('Draft', 'Draft'),('Registered', 'Registered'),('Withdrawn', 'Withdrawn'),('Withdrawn', 'Withdrawn')], 'State'),
        'registered_lines':fields.one2many('sms.transport.registrations.lines','registeration_id','Registered Candidates'),
        #current dues ff
            }
    _sql_constraints = [('Unique_registration', 'unique (name)', """Person Can bE Registered Only Once""")]
    _defaults = {
                 'state': lambda*a :'Draft',                 
                 }
    
sms_transport_registrations()

class sms_transport_registrations_lines(osv.osv):
    """This object record of transport registrations vehciles """
    
    _name="sms.transport.registrations.lines"
    _columns = {
        'name' : fields.char('Name', size=256),
        'registeration_id' :fields.many2one('sms.transport.registrations','Transport Reg:'),
        'current_vehcile':fields.many2one('sms.transport.vehcile','Vehcile'),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'student_id':fields.many2one('sms.student','Student'),
        'date_of_reg': fields.date('Registration Date'),
        'date_of_withdrawl': fields.date('With Drawn Date'),
        'state':fields.selection([('Draft', 'Draft'),('Registered', 'Registered'),('Withdrawn', 'Withdrawn'),('Withdrawn', 'Withdrawn')], 'State'),
            } 
    _defaults = {
                 'state': lambda*a :'Draft',                 
                 }
    
sms_transport_registrations_lines()

class sms_transport_fee_payments(osv.osv):
    """This object maintains the record of payments made to transport department """

    def _set_transport_fee(self, cr, uid, ids, fields,args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            string =  "Transport Fee- " + str(f.fee_month.session_month_id.name) + str(f.registeration_id)
            result[f.id] = string
        return result
    
    def apply_transport_fee_student(self, cr, uid, std_id,transport_reg_id,month):
#    def apply_transport_fee_student(self, cr, uid, std_id,trans_fee_structure): Use this definition if transport fee structure comes into play
        """Method Servers the purpose of applying transport fees on student, in unpaid status.
           Currently called by 
           1) update_monthly_feeregister() class:sms_session_months
           2)
           3)
           admin
           """
        fee_already_exists =  self.pool.get('sms.transport.fee.payments').search(cr,uid,[('student_id','=',std_id),('due_month','=',month)])
        
        if not fee_already_exists:
            fee_structure = self.pool.get('sms.transport.fee.structure').search(cr,uid,[])
            fee_structure = self.pool.get('sms.transport.fee.structure').browse(cr,uid,fee_structure)
            for rec in fee_structure:
                month_fee =  rec.monhtly_fee
            
            fee_month = month
            due_month = month
            fee_dict= {
                        'student_id': std_id,
                        'registeration_id': transport_reg_id,
                        'fee_amount': month_fee,
                        'due_month': due_month,
                        'fee_month': fee_month,
                        'late_fee':0,
                        'total_fees':0,
                        'state':'Unpaid'
                        }
            
            create_trans_fee = self.pool.get('sms.transport.fee.payments').create(cr,uid,fee_dict)  
            if create_trans_fee:
                return True
            else:
                return False  
    
    _name="sms.transport.fee.payments"
    _columns = {
        'name' : fields.char('Name', size=256),
#        'name' : fields.function(_set_transport_fee, method=True,  string='Transport Fee',type='char', store=True),
        'registeration_id' :fields.many2one('sms.transport.registrations','Transport Registration'),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'student_id':fields.many2one('sms.student','Student'),
        'fee_amount':fields.float('Fee Amount'),
        'date_fee_charged':fields.date('Date Fee Charged'),
        'date_fee_paid':fields.date('Date Fee Paid'),
        'fee_month':fields.many2one('sms.session.months','Fee Month'),
        'due_month':fields.many2one('sms.session.months','Payment Month'),
        'late_fee':fields.float('Late Fee Charges'),
        'total_fees':fields.float('Total Fee'),
        'registration_fee':fields.float('Registration Fee'),
        'state':fields.selection([('Draft', 'Draft'),('Paid', 'Paid'),('Unpaid', 'Unpaid'),('Exemption', 'Exemption')], 'State'),
            }
#    _sql_constraints = [('Fee_Payment_Unique', 'unique (name)', """ Only One Entry Can be Made""")]
    _defaults = {
                 'state': lambda*a :'Draft',
                 }
    
sms_transport_fee_payments()

class hr_employee(osv.osv):
    
    """This object is used to add fields in employee"""
    _name = 'hr.employee'
    _inherit ='hr.employee'
        
    _columns = {
        'vehcile_reg_employee_id': fields.many2one('sms.transport.vehcile','Vehcile Registration'),
        'transport_availed':fields.boolean('Transport Availed?'),
        'transport_regis_id':fields.many2one('sms.transport.registrations','Transport Registration'),
        'transport_fee_payment_ids':fields.one2many('sms.transport.fee.payments','employee_id','Transport Payments'),
        }
hr_employee()

class sms_student(osv.osv):
    
    """This object is used to add fields in sms.student"""
    
    _name = 'sms.student'
    _inherit ='sms.student'
        
    _columns = {
            'vehcile_reg_students_id':fields.many2one('sms.transport.vehcile','Vechile Registration'),
            'transport_availed':fields.boolean('Transport Availed?'),
            'transport_fee_history':fields.float('Fee History'),
            'transoprt_amount':fields.float('Transport Amount'),
            'transport_reg_id':fields.many2one('sms.transport.registrations','Transport Registration'),
            'transport_fee_payment_ids':fields.one2many('sms.transport.fee.payments','student_id','Transport Payments'),
                }
sms_student()

class sms_transportfee_challan_book(osv.osv):
    
    _name = 'sms.transportfee.challan.book'
    _description = "This object contains the challan issued to transport availers."
    _columns = {
            'name' : fields.char('Name', size=256),
            'student_id' : fields.many2one('sms.student','Student'),
            'student_class_id': fields.many2one('sms.academiccalendar','Class'),
            'father_name':fields.char('Father Name', size=256),
            'payment_method':fields.char('Payment Method', size=256),
            'total_payables':fields.integer('Total Payable'),
            'total_paid':fields.integer('Total Paid'),
            'receipt_date': fields.date('Date'),
            'state': fields.selection([('Draft', 'Draft'),('fee_calculated', 'Open'),('Paid', 'Paid'),('Cancel', 'Cancel'),('Adjusted', 'Paid(Adjusted)')], 'State', readonly=True, help='State'),
            'transport_challan_lines_ids': fields.one2many('sms.transport.fee.challan.lines', 'receipt_book_id', 'Transport Challan'),
    }
    _sql_constraints = [] 
    _defaults = {
    }
sms_transportfee_challan_book()

class sms_transport_fee_challan_lines(osv.osv):
    
#     def _set_feename(self, cr, uid, ids, name, args, context=None):
#         result = {}
#         for f in self.browse(cr, uid, ids, context=context):
#             result[f.id] = f.student_fee_id.name
#         return result
    
    _name = 'sms.transport.fee.challan.lines'
    _columns = {
            'name':fields.char('Name', size=256),
            'student_fee_id':fields.many2one('sms.transport.fee.payments','Fee Name'),
            'fee_type': fields.many2one('sms.transport.fee.structure','Fee Type'),
            'fee_amount':fields.integer('Amount'),
            'late_fee':fields.integer('late Fee'),
            'total':fields.integer('Payable'),
            'discount_offered':fields.integer('Discount'),
            'received_amount':fields.integer('Received Amount'),
            'fee_month': fields.many2one('sms.session.months','Fee Month'),
            'receipt_book_id': fields.many2one('sms.transportfee.challan.book','Transport Challan'),
                }
    _sql_constraints = [] 
    _defaults = {}
    
sms_transport_fee_challan_lines()

class sms_session_months(osv.osv):
    """
    This object is inherited to Apply Transport Fees oN Students 
    """
    def update_monthly_feeregister(self, cr, uid, ids, name):
        super(sms_session_months, self).update_monthly_feeregister(cr, uid, ids, name)
        for f in self.browse(cr, uid, ids):
            students_ids = self.pool.get('sms.student').search(cr,uid,[('state','=',"Admitted"),('transport_availed','=',True)])
            print "Registered Students in Transport Department",students_ids
            student_recs = self.pool.get('sms.student').browse(cr,uid,students_ids)
            for rec in student_recs:
#                 print rec.id
#                 trans_fee_structure_ids = self.pool.get('sms.transport.fee.structure').search(cr,uid,[('start_date','>=',rec.transport_reg_id.reg_start_date),('end_date','<=',rec.transport_reg_id.reg_end_date)])
#                 trans_fee_structure_recs = self.pool.get('sms.transport.fee.structure').browse(cr,uid,trans_fee_structure_ids)
#                 if trans_fee_structure_recs:
#                     print 'success'
#                 else:
#                     raise osv.except_osv(('Please Define fee Structure'),('Define transport fee structure according to the registration date of student in transport department'))
                self.pool.get('sms.transport.fee.payments').apply_transport_fee_student(cr, uid, rec.id,rec.transport_reg_id.id,f.id)
        return 
    
    _name = 'sms.session.months'
    _description = "stores months of a session"
    _inherit = 'sms.session.months'
    _columns = {} 
    
sms_session_months()

class res_company(osv.osv):
    """This object is used to add fields in company ."""
    _name = 'res.company'
    _inherit ='res.company'
    _columns = {
                 'one_on_one':fields.boolean('1 on 1'),
                 'three_on_one':fields.boolean('3 on 1'),
                 }
res_company()              


