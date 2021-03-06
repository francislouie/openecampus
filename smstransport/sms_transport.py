from openerp.osv import fields, osv
from datetime import date, datetime
import datetime
import time
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
    _sql_constraints = [
                ('unique_name_transport_location', 'unique (name)', 'Transport Location Must Unique')
                    ]
sms_transport_location()

class sms_transport_route(osv.osv):
    
    """This object maintains transport routes Data"""

    def _get_route_name(self, cr, uid, ids, fields,args, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            string =  str(rec.route_name) + ' - ' + str(rec.transport_location.name)
            result[rec.id] = string
        return result
    
    _name="sms.transport.route"
    _columns = {
        'name' : fields.function(_get_route_name, method=True, store=True, size=256, string='Route', type='char'),
        'route_name' : fields.char('Name', size=256),
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

    def _get_filled_seats(self, cr, uid, ids, fields,args, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            sql =   """SELECT COUNT(*) FROM sms_transport_registrations WHERE  
                        state = 'Registered' AND current_vehcile = """ + str(rec.id)
            cr.execute(sql)
            filled_seats = cr.fetchone()[0]
            result[rec.id] = filled_seats
        return result

    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)
        return result
    
    _name="sms.transport.vehcile"
    _columns = {
        'name' : fields.function(_get_vehcile_name, method=True, store = True, size=256, string='Code',type='char'),
        'vehcile_type': fields.selection([('Bus', 'Bus'),('Van', 'Van')], 'Vehcile Type'),
        'max_accomodation':fields.integer('Maximum Seats'),
        'driver':fields.many2one('res.partner','Driver Name', domain="[('supplier','=',True)]"),
        'current_accomodation':fields.function(_get_filled_seats, method=True, string='Filled Seats', type='integer', readonly=True),
        #---------- Ids are inverted in many2many object in sms_transport_route_vehcile_rel table. sms_transport_route_id, contains vehcile ids and sms_transport_vehcile_id, contains route id 
        'transport_route':fields.many2many('sms.transport.route', 'sms_transport_route_vehcile_rel', 'sms_transport_route_id', 'sms_transport_vehcile_id','Transport Route', required=True),
        #---------- Ids are inverted in many2many object in hr_driver_vehcile_rel table. hr_driver_id, contains vehcile ids and sms_transport_vehcile_id, contains driver ids 
        'drivers':fields.many2many('hr.employee', 'hr_driver_vehcile_rel', 'hr_driver_id', 'sms_transport_vehcile_id','Vehcile Drivers'),#groups="sms.group_sms_director,sms.group_sms_admin"),
        'transport_shifts':fields.many2many('sms.transport.shift', 'smstransport_shift_vehcile_rel', 'sms_transport_vehcile_id',  'sms_transport_shift_id', 'Vehcile Shifts', required=True),#, groups="sms.group_sms_director,sms.group_sms_admin"),
        'income_amount':fields.float('Income Amount'),
        'expanse_amount':fields.float('Expanse Amount'),
        'registered_students':fields.one2many('sms.student', 'vehcile_reg_students_id', 'Students', readonly=True),
        'registered_staff':fields.one2many('hr.employee', 'vehcile_reg_employee_id', 'Employees', readonly=True),
         'fee_register':fields.one2many('smsfee.transportfee.register','vehicle_id','Register'),
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
            string =  str(f.transport_route.name) + ' - ' + str(f.session_id.name)
            result[f.id] = string
        return result
    
    _name="sms.transport.fee.structure"
    _columns = {
        'name' : fields.function(_set_fee_structure_name, method=True, store = True, size=256, string='Code',type='char'),
        'transport_route': fields.many2one('sms.transport.route','Transport Route', required=True),
        'session_id':fields.many2one('sms.session', 'Session'),
        'monhtly_fee':fields.float('Monthly Fee'),
        'registration_fee':fields.float('Registration Fee'),
            } 
    _defaults = {}
    _sql_constraints = [
                ('unique_transport_feestructure', 'unique (transport_route,session_id)', 'Only One Fee Structure Can be Defined within a session')
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
        #this mehod permanaly registers a student along with his fee
        for record in self.browse(cr, uid, ids):
            fee_structure = self.pool.get('sms.transport.fee.registration').search(cr,uid,[('parent_id','=',record.id)])
            fee_structure = self.pool.get('sms.transport.fee.registration').browse(cr,uid,fee_structure)
            fee_amount = 0
            for rec in fee_structure:
                print'----- fee monthly transport -----', rec.fee_amount
                fee_amount = fee_amount + rec.fee_amount
                fee_month = rec.fee_month.id
            # --------- Register Person requesting to avail transport and also make entry in registration lines object. ------------
            vehcile_seats_check = self.pool.get('sms.transport.vehcile').browse(cr, uid, record.current_vehcile.id)
            if vehcile_seats_check.current_accomodation == vehcile_seats_check.max_accomodation:
                raise osv.except_osv(('Seats Filled'),('This Vehcile is full please apply for another'))
            else:
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
                        # add student fee in smsfee student fee , its fee category will be transport
                        #insert_student_monthly_non_monthlyfee(self, cr, uid, std_id, acad_cal, fee_type_row, month):
                        if registration_id:
                            student_id = self.pool.get('sms.student').search(cr,uid,[('id','=',record.student_id.id)])
                            self.pool.get('sms.student').write(cr, uid, student_id,{'transport_availed':True,'vehcile_reg_students_id':record.current_vehcile.id,'transport_reg_id':record.id})
                            #search Transport Registration fee object , coolect all fees and enter them in studentfee object of smsfee
                            # currently at the time of admission it collectes all month of a session and display them in list
                            # later on when, dta migration is completed, it will pick only months for which fee register is updated
                            fee_ids =  self.pool.get('sms.transport.fee.registration').search(cr,uid,[('parent_id','=',record.id)])
                            if fee_ids:
                                feesrec = self.pool.get('sms.transport.fee.registration').browse(cr,uid,fee_ids)
                                for trfee in feesrec:
                                    print' --- monthly fee on transport registration ----', trfee.fee_amount
                                    fee_dcit= {
                                                'student_id': record.student_id.id,
                                                'acad_cal_id': record.student_id.current_class.id,
                                                'fee_type': trfee.name.id,
                                                'date_fee_charged':datetime.date.today(),
                                                'due_month': trfee.fee_month.id,
                                                'fee_month': trfee.fee_month.id,
                                                'paid_amount':0,
                                                'fee_amount': trfee.fee_amount,  
                                                'late_fee':0,  
                                                'total_amount':trfee.fee_amount + 0, 
                                                'reconcile':False,
                                                'generic_fee_type':trfee.name.fee_type.id,
                                                 'state':'fee_unpaid'
                                                }
            
                                    crate_fee = self.pool.get('smsfee.studentfee').create(cr,uid,fee_dcit)  
    #                         current_ac
    #                         self.pool.get('sms.transport.vehcile').write(cr, uid, student_id,{'current_accomodation':True,'vehcile_reg_students_id':record.current_vehcile.id,'transport_reg_id':record.id})
        return result
    
    def withdraw_from_transprot(self, cr, uid, ids, name):
        for f in self.browse(cr,uid,ids):
            self.write(cr,uid,f.id,{'state':'Withdrawn','withdraw_by':uid})
            self.pool.get('sms.student').write(cr, uid, [f.student_id.id],{'transport_availed':False,'vehcile_reg_students_id':None})
        
        
        return
    
    def load_transport_fee(self, cr, uid, ids, context):
        for record in self.browse(cr, uid, ids):
            fee_structure_ids = self.pool.get('sms.transport.fee.structure').search(cr, uid, [('transport_route','=',record.transport_route.id)])
            fee_structure_obj = self.pool.get('sms.transport.fee.structure').browse(cr, uid, fee_structure_ids)
            if not fee_structure_obj:
                raise osv.except_osv(('Fee structure does not exist'),('Please define transport fee structure first'))
            else:
                #search for fee_type tansport in classes fee lines
                #this is temp slon, this will be replaced when studentfee is directly linked with feetypes
                fee_types_ids = self.pool.get('smsfee.classes.fees.lines').search(cr,uid,[('parent_fee_structure_id','=',record.id)])
                sql = """SELECT smsfee_classes_fees_lines.id from smsfee_classes_fees_lines
                                        inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                                        where smsfee_feetypes.category =  'Transport'"""
                cr.execute(sql)
                feetypid = cr.fetchone()
                if not feetypid:
                    raise osv.except_osv(('Transport Fee Not Found'),('Transport fee is not defined in any class, Goto fee management of any class and add transport under any fee structure.'))
                
                for rec in fee_structure_obj:
                    print'------ monthly Transport Fee -------', rec.monhtly_fee
                    fiscalyear_months_id = self.pool.get('sms.session.months').search(cr, uid, [('session_id','=',rec.session_id.id)])
                    fiscalyear_months_obj = self.pool.get('sms.session.months').browse(cr, uid, fiscalyear_months_id)
                    for obj in fiscalyear_months_obj:
                        self.pool.get('sms.transport.fee.registration').create(cr ,uid ,{
                                                                          'name': feetypid[0],
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
            check_studentregis_trans_sql = """SELECT id FROM sms_transport_registrations WHERE student_id = """ + str(student_id[0]) + """"""
            cr.execute(check_studentregis_trans_sql)
            trans_regis_id = cr.fetchone()
            if trans_regis_id:         
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

    _name="sms.transport.registrations"
    _columns = {
        'name' : fields.function(_set_registration_name, method=True, store = True, size=256, string='Registration',type='char'),
        'registration_type':fields.selection([('Employee', 'Employee'),('Student', 'Student')], 'Registration For', required=True),
        'registration_no':fields.related('student_id', 'registration_no', type='char', string='Registration No'),  
        'employee_id':fields.many2one('hr.employee','Employee'),
        'student_id':fields.many2one('sms.student','Student'),
        'withdraw_by':fields.many2one('res.users','Withdraw By'),
        'student_reg_no':fields.char('Search Student(Reg No)', size=256),
        'shift':fields.many2one('sms.transport.shift','Transport Shift', required=True),
        'reg_start_date': fields.date('Start Date'),
        'reg_end_date': fields.date('End Date'),
        'transport_route': fields.many2one('sms.transport.route','Destination', required=True),
        'current_vehcile':fields.many2one('sms.transport.vehcile','Vehicle', domain="[('transport_route','=',transport_route)]", required=True),
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
        'name':fields.many2one('smsfee.classes.fees.lines','Fee Type'),
        'parent_id':fields.many2one('sms.transport.registrations','Transport Register'),
        'fee_month':fields.many2one('sms.session.months','Fee Month'),
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
        'state':fields.selection([('Draft', 'Draft'),('waiting_approval', 'Waiting Approval'),('Registered', 'Registered'),('Withdrawn', 'Withdrawn'),('Withdrawn', 'Withdrawn')], 'State'),
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
    
    
    def _get_bill_no(self, cr, uid, parent_id, parent_object, module):
        sql =   """SELECT  id  FROM sms_fee_challan_no where parent_obj_id = """+str(parent_id)
        cr.execute(sql)
        res = cr.fetchone()
        if not res:
            from random import randint
            res = [randint(0,9)]
        no = int(res[0])
        return  str(no)+"-03"+str(2017)
        
    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)
        vals['receipt_no'] = self._set_bill_no(cr, uid, result, 'sms.transportfee.challan.book', 'smstransport')
        return result
    
    _name="sms.transport.fee.payments"
    _columns = {
        'name' : fields.function(_set_transport_fee, method=True, store=True, size=256, string='Fee', type='char'),
        'receipt_no': fields.char('Receipt No.',type = 'char'),      
        'registeration_id' :fields.many2one('sms.transport.registrations','Transport Registration'),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'student_id':fields.many2one('sms.student','Student'),
        'acad_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar'),
        'fee_amount':fields.float('Fee'),
        'fee_discount':fields.float('Discount'),
        'date_fee_charged':fields.date('Date Fee Charged'),
        'date_fee_paid':fields.date('Date Fee Paid'),
        'late_fee':fields.float('Late Fee'),
        'net_total':fields.float('Net Total'),
        'paid_amount':fields.float('Paid Amount'),
        'fee_month': fields.many2one('sms.session.months','Fee Month'),
        'due_month':fields.many2one('sms.session.months','Due Month'),
        'is_reconcile': fields.boolean('Reconciled'),
        'state':fields.selection([('Draft', 'Draft'),('fee_calculated', 'Fee Unpaid'),('Paid', 'Paid'),('Cancel', 'Cancel'),('Adjusted', 'Paid(Adjusted)')], 'Fee Status'),
            }
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
        'transport_availed':fields.boolean('Transport Availed?',readonly = True),
        'transport_regis_id':fields.many2one('sms.transport.registrations','Transport Registration'),
        'transport_fee_payment_ids':fields.one2many('sms.transport.fee.payments','employee_id','Transport Payments'),
        }
hr_employee()

class sms_student(osv.osv):
    
    """This object is used to add fields in sms.student for transport"""
    def get_student_fee_views(self, cr, uid, ids, field_names, arg=None, context=None):
        """This was clients requirements to show academis and transport ,and hostel etc fee separately, we made this method to use in 
           each module, this will be called by relavent columns to show fee history of one module only, here this method shows fee
           hisotry for transport only """
        records = self.browse(cr,uid,ids)
        res = {}
        for f in records:
            sql =   """ SELECT  smsfee_studentfee.id  FROM smsfee_studentfee
                      inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_studentfee.generic_fee_type
                     WHERE smsfee_studentfee.student_id = """+str(f.id)+""" AND smsfee_feetypes.category='Transport' order by fee_month """
            cr.execute(sql)
            res[f.id] = [x[0] for x in cr.fetchall()]
        return res
    
    def set_paybles_transport(self, cr, uid, ids, context={}, arg=None, obj=None):
        # temproray inner joins are used to get to fee cateogry of fee ttype, when fee strucre of student fee table is refined, one inner joiin will be removed
        result = {}
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            sql =   """ SELECT  COALESCE(sum(fee_amount),'0')  FROM smsfee_studentfee
                       inner join smsfee_classes_fees_lines on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                        inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                     WHERE student_id = """+str(f.id)+""" AND smsfee_feetypes.category='Transport'  AND state='fee_unpaid'"""
            cr.execute(sql)
            amount = float(cr.fetchone()[0])
        result[f.id] = amount
        return result
    
    _name = 'sms.student'
    _inherit ='sms.student'
        
    _columns = {

            'vehcile_reg_students_id':fields.many2one('sms.transport.vehcile','Vehicle',readonly = True),

            'view_transport_fee': fields.function(get_student_fee_views, method=True, type='one2many', relation='smsfee.studentfee', string='Transport Fee'),
            'transport_availed':fields.boolean('Transport Availed?',readonly = True),
            'transport_fee_history':fields.float('Fee History',readonly = True),
            'total_paybles_transport':fields.function(set_paybles_transport, method=True, string='Balance(Transport)', type='float'),
            'transport_reg_id':fields.many2one('sms.transport.registrations','Transport Registration',readonly = True),
            'transport_fee_payment_ids':fields.one2many('sms.transport.fee.payments','student_id','Transport Payments'),
            
                }
sms_student()


class smsfee_receiptbook(osv.osv):
    
    def confirm_fee_received(self, cr, uid, ids, context=None):
        result = super(smsfee_receiptbook, self).confirm_fee_received(cr, uid, ids, context)
        print "transport method of confimation is called"
        return result
    _name = 'smsfee.receiptbook'
    _description = "This object store fee types"
    _inherit = 'smsfee.receiptbook'
    
    columns = {}

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
                        self.pool.get('sms.transport.fee.challan.lines').create(cr ,uid, feelinesdict)
        return True 

    def _get_id(self, cr, uid, context={}):
        if context:
            if 'student_id' in context:
                return context['student_id']
        return None

    def cancel_fee_bill(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            self.write(cr, uid, f.id, {'state':'Cancel','challan_cancel_by':uid})  
        return result
    
    def recive_fee_send_2approve(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            self.write(cr, uid, f.id, {'state':'waiting_approval','challan_cancel_by':uid})  
        return result

    _name = 'sms.transportfee.challan.book'
    _description = "This object contains the challan issued to transport availers."
    _columns = {
            'name' : fields.char('Name', size=256),
            'student_id' : fields.many2one('sms.student','Student'),
            'student_class_id': fields.many2one('sms.academiccalendar','Class'),
            'father_name':fields.char('Father Name', size=256),
            'payment_method':fields.char('Payment Method', size=256),
            'manual_recpt_no': fields.char('Manual Receipt No', size=100),
            'total_payables':fields.integer('Total Payable'),
            'total_paid':fields.integer('Total Paid'),
            'receipt_date': fields.date('Date'),
            'receive_whole_amount': fields.boolean('Received Whole Amount'),
            'fee_received_by': fields.many2one('res.users', 'Received By',readonly=True),
            'challan_cancel_by': fields.many2one('res.users', 'Canceled By',readonly=True),            
            'note_at_receive': fields.text('Note'),
            'late_fee' : fields.float('Late Fee'),
            'voucher_date': fields.date('Voucher Date',readonly=True),
            'vouchered_by': fields.many2one('res.users', 'Voucher By',readonly=True),
            'vouchered': fields.boolean('Vouchered', readonly=True),
            'voucher_no': fields.many2one('account.move', 'Voucher No',readonly=True),
            'state': fields.selection([('Draft', 'Draft'),('waiting_approval', 'Waiting Approval'),('fee_calculated', 'Open'),('Paid', 'Paid'),('Cancel', 'Cancel'),('Adjusted', 'Paid(Adjusted)')], 'State', readonly=True, help='State'),
            'transport_challan_lines_ids': fields.one2many('sms.transport.fee.challan.lines', 'receipt_book_id', 'Transport Challan'),
    }
    _sql_constraints = [] 
    _defaults = {
                 'state':'Draft',
                 'payment_method': 'Cash',
                 'student_id':_get_id ,
                 'total_paid': 0.0,
                 'receipt_date':lambda *a: time.strftime('%Y-%m-%d'),
                 }

    def unlink_transportlines(self, cr, uid, ids, *args):
        line_pool = self.pool.get('sms.transport.fee.challan.lines')
        idss = line_pool.search(cr,uid, [('receipt_book_id','=',ids)])
        for id in idss:
            line_pool.unlink(cr, uid, id)
        return True

    def onchange_student(self, cr, uid, ids, std):
        result = {}
        if std:
            f = self.pool.get('sms.student').browse(cr, uid, std)
            std_class = self.pool.get('sms.academiccalendar').browse(cr, uid, f.current_class.id)
            result['student_class_id'] = f.current_class.id
            result['session_id'] = std_class.acad_session_id.id
            sql =   """SELECT SUM(fee_amount) FROM sms_transport_fee_payments
                        WHERE student_id ="""+str(std)+""" AND is_reconcile =False"""
            cr.execute(sql)
            amount = cr.fetchone()[0]
            if amount is None:
                amount = '0'   
            result['total_payables'] = amount
            self.pool.get('sms.transportfee.challan.book').write(cr, uid, ids, result)
        return {'value':result}
        
    def load_student_transportfee(self, cr, uid, ids, context=None):
        brows = self.browse(cr, uid, ids, context)
        self.unlink_transportlines(cr, uid, ids[0], None)
        student = brows[0].student_id.id
        student_fathername = brows[0].student_id.father_name 
        self.onchange_student(cr, uid, ids, None)
        self.write(cr, uid, ids[0], {'student_id':student, 'father_name':student_fathername})    
        fee_ids = self.pool.get('sms.transport.fee.payments').search(cr, uid, [('student_id','=',student), ('is_reconcile','=', 0)])
        if fee_ids:
            total_receiveable = 0
            for fees in fee_ids:
                late_fee = 0
                reconcile = False
                obj = self.pool.get('sms.transport.fee.payments').browse(cr, uid, fees)
                if obj.fee_amount == 0 or obj.fee_amount + late_fee==0:
                    reconcile = True
                if brows[0].receive_whole_amount:
                    paid_fee    = obj.fee_amount+late_fee
                    reconcile   = True
                else:
                    paid_fee = 0
                    if obj.fee_amount == 0 or obj.fee_amount+late_fee==0:
                        reconcile = True
                    else:
                        reconcile = False
                total_receiveable = total_receiveable + obj.fee_amount 
                self.pool.get('sms.transport.fee.challan.lines').create(cr, uid, {
                        'fee_month': obj.fee_month.id,
                        'receipt_book_id':ids[0],
                        'student_fee_id':obj.id,
                        'fee_amount': obj.fee_amount,
                        'total': total_receiveable + late_fee,
                        'paid_amount':paid_fee,
                        'is_reconcile':reconcile,
                        'late_fee':0,
                       }) 
            self.write(cr, uid, ids[0], {'state':'fee_calculated','total_payables':total_receiveable})
        return
    
    def receive_transportfee(self, cr, uid, ids, context=None):
        sqluser = """ select res_groups.name from res_groups inner join res_groups_users_rel 
                              on res_groups.id=res_groups_users_rel.gid where res_groups_users_rel.uid=""" + str(uid)
        cr.execute(sqluser)
        group_name = cr.fetchall()
        for s in group_name:
            print('sss', s[0])
            IsItTransportManager = True
            if 'SMS Transport Manager' in s:
                IsItTransportManager=False
        if IsItTransportManager:
            raise osv.except_osv(('Transport Challans'), ('Only Transport Manager is allowed to Approve Challans'))

        self.onchange_student(cr, uid, ids, None)
        rec = self.browse(cr, uid, ids, context)
        paymethod = ''
        receipt_date = ''
        for f in rec:
            stdname = self.pool.get('sms.student').browse(cr, uid, f.student_id.id).name
            paymethod = f.payment_method
            receipt_date = f.receipt_date
            
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id.enable_fm:
            
            fee_income_acc = user.company_id.student_fee_income_acc
            fee_expense_acc = user.company_id.student_fee_expense_acc
            fee_journal = user.company_id.fee_journal
            period_id = self.pool.get('account.move')._get_period(cr, uid, context)
            if paymethod=='Cash':
                fee_reception_acc = user.company_id.fee_reception_account_cash
                if not fee_reception_acc:
                    raise osv.except_osv(('Cash Account'), ('No Account is defined for Payment method:Cash'))
            elif paymethod=='Bank':
                fee_reception_acc = user.company_id.fee_reception_account_bank
                if not fee_reception_acc:
                    raise osv.except_osv(('Bank Account'), ('No Account is defined for Payment method:Bank'))
            
            if not fee_income_acc:
                raise osv.except_osv(('Accounts'), ('Please define Fee Income Account'))
            if not fee_expense_acc:
                raise osv.except_osv(('Accounts'), ('Please define Fee Expense Account'))
            if not fee_journal:
                raise osv.except_osv(('Accounts'), ('Please Define A Fee Journal'))
            if not period_id:
                raise osv.except_osv(('Financial Period'), ('Financial Period is not defined in Fiscal Year.'))
        
        search_lines_id = self.pool.get('sms.transport.fee.challan.lines').search(cr, uid, [('receipt_book_id','=',ids[0])], context=context)
        lines_obj = self.pool.get('sms.transport.fee.challan.lines').browse(cr, uid, search_lines_id)
        generate_receipt = False
        total_paid_amount = 0 
        for line in lines_obj:
            std_fee_id = line.student_fee_id.id
            late_fee = 0
            if line.is_reconcile:
                total_paid_amount = total_paid_amount+ line.received_amount
                generate_receipt = True
                self.pool.get('sms.transport.fee.payments').write(cr, uid, std_fee_id, {
                           'late_fee':late_fee,
                           'paid_amount':line.received_amount,
                           'date_fee_paid':date.today(),
#                           'fee_discount':line.discount,
                           'net_total':line.total,
                           'is_reconcile':line.is_reconcile,
                           'receipt_no':str(ids[0]),
                           'state':'Paid',
                           })
        if generate_receipt:
            self.write(cr, uid, ids[0],{
                           'fee_received_by':uid,
                           'total_paid':total_paid_amount,
                           'state':'Paid',
                           })
            if user.company_id.enable_fm:
                account_move_dict= {
                                'ref':'Income:Student Fee:',
                                'journal_id':fee_journal.id,
                                'type':'journal_voucher',
                                'narration':'Pay/'+str(ids[0]) +'--'+ receipt_date}
                
                move_id=self.pool.get('account.move').create(cr, uid, account_move_dict, context)
                account_move_line_dict=[
                    {
                         'name': 'Fee Received: '+stdname,
                         'debit':0.00,
                         'credit':total_paid_amount,
                         'account_id':fee_income_acc.id,
                         'move_id':move_id,
                         'journal_id':fee_journal.id,
                         'period_id':period_id
                     },
                    {
                         'name': 'Fee Received: '+stdname,
                         'debit':total_paid_amount,
                         'credit':0.00,
                         'account_id':fee_reception_acc.id,
                         'move_id':move_id,
                         'journal_id':fee_journal.id,
                         'period_id':period_id
                     }]
                context.update({'journal_id': fee_journal.id, 'period_id': period_id})
                for move in account_move_line_dict:
                    self.pool.get('account.move.line').create(cr, uid, move, context)
                self.write(cr, uid, ids[0],{
                       'vouchered':True,
                       'vouchered_by':uid,
                       'voucher_date':datetime.date.today(),
                       'voucher_no':move_id
                       })
            search_booklines = self.pool.get('sms.transport.fee.challan.lines').search(cr, uid, [('receipt_book_id','=',ids[0]),('is_reconcile','=',False)], context=context) 
            print "Challan Lines to Be deleted --- ",search_booklines
            if search_booklines:
                for del_id in search_booklines:
                    self.pool.get('sms.transport.fee.challan.lines').unlink(cr,uid,del_id)
        else:
            raise osv.except_osv(('No Fee Paid'),('Paid amount or Discount should not be 0'))
        return True

sms_transportfee_challan_book()

class sms_transport_fee_challan_lines(osv.osv):

    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)
        return result
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result

    def unlink(self, cr, uid, ids, context=None):
        result = super(osv.osv, self).unlink(cr, uid, ids, context)
        return result 

    def onchange_amount(self, cr, uid, ids, total, received_amount):
        vals = {}
        if received_amount > total:
            vals['paid_amount']     = 0
            vals['discount']        = 0
            vals['total']           = total
            vals['is_reconcile']    = False
        elif received_amount == total: 
            vals['paid_amount']     = received_amount
            vals['discount']        = 0
            vals['total']           = total-received_amount
            vals['is_reconcile']    = True
        elif received_amount < total:
            vals['paid_amount']     = received_amount
            vals['discount']        = total - received_amount
            vals['total']           = total - (received_amount + vals['discount'])
            vals['is_reconcile']    = True
        self.pool.get('sms.transport.fee.challan.lines').write(cr, uid, ids, 
                       {'paid_amount'   :vals['paid_amount'],
                       'discount'       :vals['discount'],
                       'total'          :vals['total'],
                       'is_reconcile'   :vals['is_reconcile']
                       })   
        return {'value':vals}
    
    def onchange_discount(self, cr, uid, ids, total, discount):
        vals = {}
        if discount > total:
            vals['paid_amount']     = 0
            vals['discount']        = 0
            vals['total']           = total
            vals['is_reconcile']    = False
        elif discount == total: 
            vals['paid_amount']     = 0
            vals['total']           = total- discount
            vals['is_reconcile']    = True
            vals['discount']        = discount
        elif  discount < total:
            vals['paid_amount']     = total - discount
            vals['total']           = total - (discount+vals['paid_amount'])
            vals['discount']        = discount
            vals['is_reconcile']    = True         
        self.pool.get('sms.transport.fee.challan.lines').write(cr, uid, ids, {
                       'paid_amount':vals['paid_amount'],
                       'discount':vals['discount'],
                       'total':vals['total'],
                       'is_reconcile':vals['is_reconcile']
                       })   
        return {'value':vals}
    
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
            'late_fee':fields.integer('Late Fee'),
            'total':fields.integer('Payable'),
            'paid_amount':fields.integer('Paid Amount'),
            'discount':fields.float('Discount'),
            'received_amount':fields.integer('Received Amount'),
            'fee_month': fields.many2one('sms.session.months','Fee Month'),
            'is_reconcile': fields.boolean('Reconciled'),
            'receipt_book_id': fields.many2one('sms.transportfee.challan.book','Transport Challan'),
                }
    _sql_constraints = [] 
    _defaults = {                
                 'discount':0,
                 'paid_amount':0,
                }
sms_transport_fee_challan_lines()

class sms_session_months(osv.osv):
    
    """ This object is inherited to Apply Transport Fees on Students """
    def update_monthly_feeregister_transport(self, cr, uid, ids, name):
        print "UPdate monthly fee Register is called"
        """This method now getting transport fee from smsfee classes fees lines, but when the fee structure is change for smsfee_studentfee
           then it will directly pick the transport fee id from smsfee_feetypes while its amount will be picked from rout or destination , 
           the transport fee str is also not necesarry to be defined for every session and every rout
           """
        for f in self.browse(cr, uid, ids):
            parent_session_id = f.session_id.id
            #search all classes in this session
                        # search all feetypes in this fs of thi class
            ft_list = []
            sql = """SELECT smsfee_classes_fees_lines.id from smsfee_classes_fees_lines
                                    inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                                    where smsfee_feetypes.category =  'Transport'"""
            cr.execute(sql)
            feetypid = cr.fetchone()[0]
            print"Fee type id-----",feetypid
            if not feetypid:
                raise osv.except_osv(('Transport Fee Not Found'),('Transport fee is not defined in any class, Goto fee management of any class and add transport under any fee structure.'))
            ftrow = self.pool.get('smsfee.classes.fees.lines').browse(cr,uid,feetypid)  
            vehcle_ids = self.pool.get('sms.transport.vehcile').search(cr,uid,[])
            if vehcle_ids:
                veh_rec = self.pool.get('sms.transport.vehcile').browse(cr,uid,vehcle_ids)
                for this_veh in veh_rec:
                        students_ids = this_veh.registered_students

                        for this_student in students_ids:
                            if this_student.transport_availed and this_student.state == 'Admitted':
                                #call method to add this fee to student
                                ses_id = self.pool.get('sms.academiccalendar').browse(cr, uid,this_student.current_class.id)

                                if ses_id.session_id.id==f.session_id.id:
                                    print " Done a id ", ses_id.session_id.id, "b id", f.session_id.id
                                    call = self.pool.get('smsfee.studentfee').insert_student_monthly_non_monthlyfee(cr, uid, this_student.id, this_student.current_class.id,ftrow.name.fee_type.id, ftrow.amount, f.id)
                                else:
                                    print "dublicate fee for tranpsort will raise here ", ses_id.session_id.id, "b id", f.session_id.id
                                           
                        #Update fee register object for this month 
                        # search if this month already exists then leav, otherwise create new record
                        register_id = self.pool.get('smsfee.transportfee.register').search(cr,uid,[('vehicle_id','=',this_veh.id),('month','=',f.id)])
                        if not register_id:
                            fee_register = self.pool.get('smsfee.transportfee.register').create(cr,uid,{
                                                                'vehicle_id':this_veh.id,                                                       
                                                                'month':f.id, 
                                                                    })
            self.write(cr,uid,f.id,{'transport_update_log':'Last update on:'+str(datetime.date.today())})
        return 
    
    _name = 'sms.session.months'
    _description = "Stores months of a session"
    _inherit = 'sms.session.months'
    _columns = {
                 'transport_update_log': fields.char('Last Update',size = 50),  
                } 
    
sms_session_months()

class smsfee_transportfee_register(osv.osv):
    
    """ Store monthly fee history of all vehicles, when month fee register is updated, new record is inserted in this objects """
    
    def create(self, cr, uid, vals, context=None, check=True):
         result = super(osv.osv, self).create(cr, uid, vals, context)
#          for obj in self.browse(cr, uid, context=context):
         return result
   
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             result[f.id] = str(f.vehicle_id.name)+" --- "+str(f.month.name)
        return result
    
    def _set_forcasted_fee(self, cr, uid, ids, name, args, context=None):
        result = {}
        #this query will be changed when function for fee reurned is included
        for f in self.browse(cr, uid, ids, context=context):
             sql = """SELECT COALESCE(sum(fee_amount),'0')  from smsfee_studentfee
                      WHERE due_month = """+str(f.month.id)+"""
                      """
             cr.execute(sql)
             amount = cr.fetchone() 
             if amount:
                 result[f.id] = float(amount[0]) 
             else:
                 result[f.id] = float(amount[0])
        return result         
             
    def _set_paid_fee(self, cr, uid, ids, name, args, context=None):
         #this query will be changed when function for fee reurned is included
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             sql = """SELECT COALESCE(sum(paid_amount),'0') from smsfee_studentfee
                      WHERE  reconcile = True"""
             cr.execute(sql)
             amount = cr.fetchone() 
             if amount:
                 result[f.id] = float(amount[0]) 
             else:
                 result[f.id] = float(amount[0])
        return result                  
    
    _name = 'smsfee.transportfee.register'
    _order = "month desc"
    """stores academic calendar month by month updates, user has to manually update fee register for each classs for each month. this object also sotres monthly fee received in each month.
       """
    _description = "Stores transport fee register"
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Fee',type='char'),
        'vehicle_id': fields.many2one('sms.transport.vehcile','Van',readonly = True),      
        'month': fields.many2one('sms.session.months','Month',readonly = True),
        'month_forcasted_fee':fields.function(_set_forcasted_fee, method=True,  string='Forcasted',type='float'),
        'month_fee_received':fields.function(_set_paid_fee, method=True,  string='Received',type='float'),
    }
smsfee_transportfee_register()

class res_company(osv.osv):
    """This object is used to add fields in company ."""
    _name = 'res.company'
    _inherit ='res.company'
    _columns = {
            ########## Fields for Transport Challan's Print Settings ##############################################
            'bank_name1_trans':fields.char('Bank Name', size=256),
            'bank_name2_trans':fields.char('Bank Name', size=256),
            'bank_acctno1_trans':fields.integer('Account Number'),
            'bank_acctno2_trans':fields.integer('Account Number'),
            'company_cfieldone_trans':fields.char('Transport Challan Heading One', size=256),
            'company_cfieldtwo_trans':fields.char('Transport Challan Heading Two', size=256),
            'company_cfieldthree_trans':fields.char('Transport Challan Heading Three', size=256),
            'company_cfieldfour_trans':fields.char('Transport Challan Footer One', size=256),
            'company_cfieldfive_trans':fields.char('Transport Challan Footer two', size=256),
            'company_cfieldsix_trans':fields.char('Field Six', size=256),
            'company_cfieldseven_trans':fields.char('Field Seven', size=256),
            'company_cfieldeight_trans':fields.char('Field Eight', size=256),
            'company_clogo_trans':fields.binary('Transport Challan Logo'),
                }
    _defaults = {                
                }
    
res_company()              

