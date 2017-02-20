from openerp.osv import fields, osv
from datetime import datetime
from datetime import date
import logging
from lxml import etree
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
    _sql_constraints = [
                ('unique_name_transport_location', 'unique (name)', 'Transport Location Must Unique')
                    ]
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
    _sql_constraints = [
                ('unique_name_transport_route', 'unique (name, transport_location)', 'Transport Route Can be Entered Once Only')
                    ]
sms_transport_route()

class sms_transport_shift(osv.osv):
    
    """This object maintains transport shifts """
    
    _name="sms.transport.shift"
    _columns = {
        'name' : fields.char('Name', size=256),
        'desc': fields.char('Description', size=256),
            } 
    _defaults = {}
    _sql_constraints = []
    
sms_transport_shift()

class sms_transport_vehcile(osv.osv):
    """This object maintains transport vehciles """

    def _get_vehcile_name(self, cr, uid, ids, fields,args, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            string =  str(rec.vehcile_type) + ' - ' + str(rec.vehcile_no)
            result[rec.id] = string
        return result
    
    _name="sms.transport.vehcile"
    _columns = {
        'name' : fields.function(_get_vehcile_name, method=True, store = True, size=256, string='Code',type='char'),
        'vehcile_type': fields.selection([('Bus', 'Bus'),('Van', 'Van')], 'Vehcile Type'),
        'max_accomodation':fields.integer('Maximum Seats'),
        'current_accomodation':fields.integer('Filled Seats'),
        #---------- Ids are inverted in many2many object in sms_transport_route_vehcile_rel table. sms_transport_route_id, contains vehcile ids and sms_transport_vehcile_id, contains route id 
        'transport_route':fields.many2many('sms.transport.route', 'sms_transport_route_vehcile_rel', 'sms_transport_route_id', 'sms_transport_vehcile_id','Transport Route'),
        #---------- Ids are inverted in many2many object in hr_driver_vehcile_rel table. hr_driver_id, contains vehcile ids and sms_transport_vehcile_id, contains driver ids 
        'drivers':fields.many2many('hr.employee', 'hr_driver_vehcile_rel', 'hr_driver_id', 'sms_transport_vehcile_id','Vehcile Drivers'),
        'transport_shifts':fields.many2many('sms.transport.shift', 'smstransport_shift_vehcile_rel', 'sms_transport_vehcile_id',  'sms_transport_shift_id', 'Vehcile Shifts'),
        'income_amount':fields.float('Income Amount'),
        'expanse_amount':fields.float('Expanse Amount'),
        'registered_students':fields.one2many('sms.student', 'vehcile_reg_students_id', 'Students', readonly=True),
        'registered_staff':fields.one2many('hr.employee', 'vehcile_reg_employee_id', 'Employees', readonly=True),
        'vehcile_no':fields.integer('Vehicle Number'), 
            } 
    _defaults = {
                 'vehcile_type': lambda*a :'Bus',
                 }
    
sms_transport_vehcile()

class sms_transport_fee_structure(osv.osv):
    
    """This object maintains transport vehciles """

    def _set_fee_structure_name(self, cr, uid, ids, fields,args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            string =  str(f.transport_route.name) + ' - ' + str(f.fiscal_year.name)
            result[f.id] = string
        return result
    
    _name="sms.transport.fee.structure"
    _columns = {
        'name' : fields.function(_set_fee_structure_name, method=True, store = True, size=256, string='Code',type='char'),
        'transport_route': fields.many2one('sms.transport.route','Transport Route', required=True),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'fiscal_year':fields.many2one('account.fiscalyear', 'Fiscal Year'),
        'monhtly_fee':fields.float('Monthly Fee'),
        'registration_fee':fields.float('Registration Fee'),
            } 
    _defaults = {}
    _sql_constraints = [
                ('unique_transport_feestructure', 'unique (transport_route)', 'Only One Fee Structure Can be Defined For A Vehcile')
                    ]
    
sms_transport_fee_structure()

class sms_transport_registrations(osv.osv):
    """This object maintains transport registrations """

    def _set_registration_name(self, cr, uid, ids, fields,args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            if f.registration_type == 'Student':
                string =  str(f.id) +'-'+ str(f.student_id.name)  
            else:
                string =  str(f.id) +'-'+ str(f.employee_id.name)
            result[f.id] = string
        return result

    def register_person(self, cr, uid, ids, name):
        for record in self.browse(cr, uid, ids):
            fee_structure = self.pool.get('sms.transport.fee.registration').search(cr,uid,[('parent_id','=',record.id)])
            fee_structure = self.pool.get('sms.transport.fee.registration').browse(cr,uid,fee_structure)
            fee_amount = 0
            for rec in fee_structure:
                fee_amount = fee_amount + rec.fee_amount            
            # --------- Register Person requesting to avail transport and also make entry in registration lines object. ------------
            result = self.write(cr,uid,record.id,{'state':'Registered'})
            if result:
                if record.registration_type == 'Employee':
                    registration_id = self.pool.get('sms.transport.registrations.lines').create(cr,uid,
                                                                             {
                                                                            'registeration_id': record.id,
                                                                            'state': record.state, 
                                                                            'current_vehcile':record.current_vehcile.id,
                                                                            'employee_id':record.employee_id.id,
                                                                            })
                    if registration_id:
                        employee_id = self.pool.get('hr.employee').search(cr,uid,[('id','=',record.employee_id.id)])
                        self.pool.get('hr.employee').write(cr, uid, employee_id,{'transport_availed':True,
                                                                               'vehcile_reg_employee_id':record.current_vehcile.id
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
                                                                'state': 'fee_calculated', 
                                                                'student_id':record.student_id.id,
                                                                'fee_amount':fee_amount
                                                                })
#                         current_ac
#                         self.pool.get('sms.transport.vehcile').write(cr, uid, student_id,{'current_accomodation':True,'vehcile_reg_students_id':record.current_vehcile.id,'transport_reg_id':record.id})
        return result

    def load_transport_fee(self, cr, uid, ids, context):
        for record in self.browse(cr, uid, ids):
            fee_structure_ids = self.pool.get('sms.transport.fee.structure').search(cr, uid, [('transport_route','=',record.transport_route.id)])
            fee_structure_obj = self.pool.get('sms.transport.fee.structure').browse(cr, uid, fee_structure_ids)
            if not fee_structure_obj:
                raise osv.except_osv(('Fee structure does not exist'),('Please define transport fee structure first'))
            for rec in fee_structure_obj:
                fiscal_year_session_id = self.pool.get('sms.fiscalyear.session').search(cr, uid, [('fiscal_year_id','=',rec.fiscal_year.id)])
                fiscalyear_months_id = self.pool.get('sms.fiscalyearsession.months').search(cr, uid, [('fiscalyear_session_id','=',fiscal_year_session_id)])
                fiscalyear_months_obj = self.pool.get('sms.fiscalyearsession.months').browse(cr, uid, fiscalyear_months_id)
                for obj in fiscalyear_months_obj:
                    self.pool.get('sms.transport.fee.registration').create(cr ,uid ,{
                                                                      'name': rec.id,
                                                                      'parent_id': record.id,
                                                                      'fee_month': obj.id,
                                                                      'fee_amount': rec.monhtly_fee
                                                                      }) 
            self.write(cr,uid,record.id,{'state':'waiting_approval'})
        return True

    def onchange_load_student(self, cr, uid, ids, std_reg_no):
        result = {}
        search_student_sql = """SELECT id FROM sms_student WHERE registration_no like '%""" + str(std_reg_no) + """%'"""
        cr.execute(search_student_sql)
        student_id = cr.fetchone()
        if student_id:
            if self.browse(cr, uid, student_id[0]):         
                raise osv.except_osv(('Record Exists'),('Student is already registered.'))         
            else:
                result['student_id'] = student_id
        else:
            result['student_id'] = ''
        return {'value':result}

    def onchange_vehcile_load_shift(self, cr, uid, ids, vechile_id):
        result = {}
        search_shift_sql = """SELECT sms_transport_shift_id FROM smstransport_shift_vehcile_rel WHERE sms_transport_vehcile_id= """ + str(vechile_id) + """"""
        cr.execute(search_shift_sql)
        shift_id = cr.fetchone()
        if shift_id:
            result['shift'] = shift_id
        else:
            result['shift'] = ''
        return {'value':result}

    def set_transportfee_amount(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        amount = '0'
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            sql =   """SELECT COALESCE(sum(fee_amount),'0') FROM sms_transport_fee_registration
                     WHERE parent_id =""" + str(f.id)
            cr.execute(sql)
            amount = cr.fetchone()[0]
        result[f.id] = amount
        return result

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(sms_transport_registrations,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'tree':
            if context.get('registration_type', '1') is 'Employee':
                for node in doc.xpath("//field[@name='employee_id']"):
                    doc.remove(node)
            if context.get('registration_type', '1') is 'Student':
                for node in doc.xpath("//field[@name='student_id']"):
                    doc.remove(node)
            res['arch'] = etree.tostring(doc)
        return res    
    
    _name="sms.transport.registrations"
    _columns = {
        'name' : fields.function(_set_registration_name, method=True, store = True, size=256, string='Registration',type='char'),
        'registration_type':fields.selection([('Employee', 'Employee'),('Student', 'Student')], 'Registration For', required=True),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'student_id':fields.many2one('sms.student','Student'),
        'student_reg_no':fields.char('Search Student(Reg No)', size=256),
        'shift':fields.many2one('sms.transport.shift','Transport Shift', required=True),
        'reg_start_date': fields.date('Start Date'),
        'reg_end_date': fields.date('End Date'),
        'transport_route': fields.many2one('sms.transport.route','Transport Route', required=True),
        'current_vehcile':fields.many2one('sms.transport.vehcile','Vechile', domain="[('transport_route','=',transport_route)]", required=True),
        'state':fields.selection([('Draft', 'Draft'),('waiting_approval', 'Waiting Approval'),('Registered', 'Registered'),('Withdrawn', 'Withdrawn')], 'State'),
        'picture':fields.related('student_id', 'image', type='binary', string='Image'),
        'registered_lines':fields.one2many('sms.transport.registrations.lines','registeration_id','Registered Candidates'),
        'transportfee_ids':fields.one2many('sms.transport.fee.registration','parent_id','Fee'),
        'total_fee_applicable':fields.function(set_transportfee_amount, method=True, string='Total Fee',type='float'),
            }
    _sql_constraints = [('Unique_registration', 'unique (name)', """Person Can be Registered Only Once """)]
    _defaults = {
                 'state': lambda*a :'Draft',
                 'registration_type': 'Student',                 
                 }
sms_transport_registrations()

class sms_transport_fee_registration(osv.osv):
    
    _name="sms.transport.fee.registration"
    _columns = {
        'name':fields.many2one('sms.transport.fee.structure','Transport Fee Structure'),
        'parent_id':fields.many2one('sms.transport.registrations','Transport Register'),
        'fee_month':fields.many2one('sms.fiscalyearsession.months','Fee Month'),
        'fee_amount':fields.float('Amount'),
            }
    _defaults = {}
    
sms_transport_fee_registration()

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
            string =  "Transport Fee - " + str(f.fee_month.session_month_id.name)
            result[f.id] = string
        return result
    
    _name="sms.transport.fee.payments"
    _columns = {
        'name' : fields.function(_set_transport_fee, method=True, store = True, size=256, string='Code',type='char'),
        'receipt_no': fields.char('Receipt No.',type = 'char'),      
        'registeration_id' :fields.many2one('sms.transport.registrations','Transport Registration'),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'student_id':fields.many2one('sms.student','Student'),
        'acad_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar'),
        'fee_amount':fields.float('Fee Amount'),
        'fee_discount':fields.float('Discount'),
        'date_fee_charged':fields.date('Date Fee Charged'),
        'date_fee_paid':fields.date('Date Fee Paid'),
        'paid_amount':fields.float('Paid Amount'),
        'fee_month':fields.many2one('sms.fiscalyearsession.months','Fee Month'),
        'due_month':fields.many2one('sms.fiscalyearsession.months','Due Month'),
        'is_reconcile': fields.boolean('Reconciled'),
        'state':fields.selection([('Draft', 'Draft'),('fee_calculated', 'Un-Paid'),('Paid', 'Paid'),('Cancel', 'Cancel'),('Adjusted', 'Paid(Adjusted)')], 'State'),
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
    
    def create(self, cr, uid, vals, context=None, check=True):
#        slipno = self._set_slipno(self, cr, uid, None)
#        vals['name'] =  slipno
        result = super(osv.osv, self).create(cr, uid, vals, context)
        return result
    
    def check_transportfee_challans_issued(self, cr, uid, class_id, student_id):
        if type(student_id) is list:
            student_id = student_id[0]
        fee_ids = self.pool.get('sms.transport.fee.payments').search(cr ,uid ,[('student_id','=',student_id),('state','=','fee_calculated')])
        if fee_ids:
            challan_ids = self.pool.get('sms.transportfee.challan.book').search(cr, uid,[
                                                                                         ('student_id','=',student_id),
                                                                                         ('student_class_id','=', class_id),
                                                                                         ('state','=','fee_calculated')
                                                                                         ])
            if challan_ids:
                #---------------------- Get all unpaid amount receive able from student -------------------------------------
                receipt_total_fee = []
                std_unpaid_fees = self.pool.get('sms.transport.fee.payments').browse(cr ,uid ,fee_ids)
                if std_unpaid_fees:
                    current_fee_amount = 0
                    for unpaidfee in std_unpaid_fees:
                        current_fee_amount = current_fee_amount + unpaidfee.fee_amount
                #---------------------- Get Unpaid Amount Appearing in the Current Fee Receipt -----------------------------
                for recipt in self.pool.get('sms.transportfee.challan.book').browse(cr, uid, challan_ids):
                    tlt_line_fee = 0
                    for lines in recipt.transport_challan_lines_ids:
                        tlt_line_fee =tlt_line_fee + lines.total
                    receipt_total_fee.append(tlt_line_fee)
                #---------------------- if old_val is not equal to new_val than create receipt -----------------------------
                old_val = receipt_total_fee[-1]
                if old_val <= current_fee_amount:
                    total_paybles = 0
                    self.pool.get('sms.transportfee.challan.book').write(cr ,uid ,challan_ids, {'state':'Cancel'})
                    receipt_id = self.pool.get('sms.transportfee.challan.book').create(cr ,uid , {
                                                                                                  'student_id':student_id,
                                                                                                  'student_class_id':class_id,
                                                                                                  'state':'fee_calculated',
                                                                                                  'receipt_date':date.today()
                                                                                                  })
                    std_unpaid_fees = self.pool.get('sms.transport.fee.payments').browse(cr ,uid ,fee_ids)
                    if receipt_id:
                        for unpaidfee in std_unpaid_fees:
                            total_paybles = total_paybles + unpaidfee.fee_amount
                            self.pool.get('sms.transportfee.challan.book').write(cr ,uid ,receipt_id, {'total_payables':total_paybles})
                            feelinesdict = {
#                                            'fee_type': unpaidfee.fee_type.id,
                                            'student_fee_id': unpaidfee.id,
                                            'fee_month': unpaidfee.fee_month.id,
                                            'receipt_book_id': receipt_id,
                                            'fee_amount':unpaidfee.fee_amount,
                                            'late_fee':0,
                                            'total':unpaidfee.fee_amount
                                            }
                            self.pool.get('sms.transport.fee.challan.lines').create(cr ,uid, feelinesdict)
                    
                else:
                    print "donot create challan"
            else:
                total_paybles = 0
                receipt_id = self.pool.get('sms.transportfee.challan.book').create(cr ,uid , {
                                                                                              'student_id':student_id,
                                                                                              'student_class_id':class_id,
                                                                                              'state':'fee_calculated',
                                                                                              'receipt_date':date.today()
                                                                                              })
                std_unpaid_fees = self.pool.get('sms.transport.fee.payments').browse(cr ,uid ,fee_ids)
                if receipt_id:
                    for unpaidfee in std_unpaid_fees:
                        total_paybles = total_paybles + unpaidfee.fee_amount
                        self.pool.get('sms.transportfee.challan.book').write(cr ,uid ,receipt_id, {'total_payables':total_paybles})
                        feelinesdict = {
 #                                       'fee_type': unpaidfee.fee_type.id,
                                        'student_fee_id': unpaidfee.id,
                                        'fee_month': unpaidfee.fee_month.id,
                                        'receipt_book_id': receipt_id,
                                        'fee_amount':unpaidfee.fee_amount,
                                        'late_fee':0,
                                        'total':unpaidfee.fee_amount
                                        }
                        self.pool.get('sms.transport.fee.challan.lines').create(cr ,uid,feelinesdict)
        return True 

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
    
    def _set_feename(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = str(f.student_fee_id.name)
        return result
    
    _name = 'sms.transport.fee.challan.lines'
    _columns = {
            'name':fields.function(_set_feename, method=True, store = True, size=256, string='Fee Name',type='char'),
            'student_fee_id':fields.many2one('sms.transport.fee.payments','Fee Name'),
            'fee_type': fields.many2one('sms.transport.fee.structure','Fee Type'),
            'fee_amount':fields.integer('Amount'),
            'late_fee':fields.integer('late Fee'),
            'total':fields.integer('Payable'),
            'discount_offered':fields.integer('Discount'),
            'received_amount':fields.integer('Received Amount'),
            'fee_month': fields.many2one('sms.fiscalyearsession.months','Fee Month'),
            'receipt_book_id': fields.many2one('sms.transportfee.challan.book','Transport Challan'),
                }
    _sql_constraints = [] 
    _defaults = {}
    
sms_transport_fee_challan_lines()

class sms_fiscalyearsession_months(osv.osv):
    """ This object is inherited to Apply Transport Fees on Students """
    def apply_transport_fee_student(self, cr, uid, ids, name):
        """Method Servers the purpose of applying transport fees on student, in unpaid status. Currently called by 
           1) 
           2)
           3)
           """
        for rec in self.browse(cr, uid, ids):
            student_ids = self.pool.get('sms.transport.registrations').search(cr, uid, [('state','=','Registered')])
            student_recs = self.pool.get('sms.transport.registrations').browse(cr, uid, student_ids)
            
            for student_rec in student_recs:
                monthly_fee_sql = """SELECT monhtly_fee FROM sms_transport_fee_structure WHERE 
                                        fiscal_year = """ + str(rec.fiscalyear_session_id.fiscal_year_id.id) + """
                                        AND transport_route = """ +str(student_rec.transport_route.id) + """"""
                cr.execute(monthly_fee_sql)
                monthly_fee = cr.fetchone()
                fee_already_exists =  self.pool.get('sms.transport.fee.payments').search(cr,uid,[('student_id','=',student_rec.student_id.id),('due_month','=',rec.session_month_id.id)])
                if not fee_already_exists:
                    fee_month = rec.session_month_id.id
                    due_month = rec.session_month_id.id
                    fee_dict= {
                        'student_id': student_rec.student_id.id,
                        'registeration_id': student_rec.id,
                        'fee_amount': monthly_fee[0],
                        'due_month': due_month,
                        'fee_month': fee_month,
                        'late_fee':0,
                        'total_fees':0,
                        'date_fee_charged':date.today(),
                        'state':'fee_calculated'
                        }
                    create_trans_fee = self.pool.get('sms.transport.fee.payments').create(cr,uid,fee_dict)  
                    if create_trans_fee:
                        self.write(cr, uid, rec.id, {'update_log':'Last update on:'+str(date.today()),'state':'Updated'})
                else:
                    print 'rec exists'
            return True
    _name = 'sms.fiscalyearsession.months'
    _description = "stores months of a session"
    _inherit = 'sms.fiscalyearsession.months'
    _columns = {
            'update_log': fields.char('Year', size=50),  
            'state':fields.selection([('To_Update','To Be Updated'),('Updated','Updated')],'State')
                } 
sms_fiscalyearsession_months()

class res_company(osv.osv):
    """This object is used to add fields in company ."""
    _name = 'res.company'
    _inherit ='res.company'
    _columns = {
                 'one_on_one':fields.boolean('1 on 1'),
                 'three_on_one':fields.boolean('3 on 1'),
                 }
res_company()              


