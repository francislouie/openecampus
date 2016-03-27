from openerp.osv import fields, osv
from openerp import tools
from openerp import addons
import datetime
import time
import xlwt
import xlrd


class res_company(osv.osv):
    """This object inherits res company adds fields related to accounts ."""
    _name = 'res.company'
    _inherit ='res.company'
    _columns = {
    'enable_fm': fields.boolean('Enable Financial Management'),
    'fee_journal': fields.many2one('account.journal', 'Fee Journal', ondelete="cascade"),
    'student_fee_income_acc': fields.many2one('account.account', 'Fee Income Account', ondelete="cascade"),
    'student_fee_expense_acc': fields.many2one('account.account', 'Fee Expense Account',  ondelete="cascade"),
    'fee_reception_account_cash': fields.many2one('account.account', 'Fee Cash Account', ondelete="cascade"), 
    'fee_reception_account_bank': fields.many2one('account.account', 'Fee Bank Account', ondelete="cascade"), 
    }
    _defaults = {
    }
res_company()




class sms_academiccalendar(osv.osv):
    """This object is used to add fields in sms.student"""
    def manage_class_fee(self, cr, uid, ids, context=None):
        academic_object = self.browse(cr, uid, ids, context=context)
        for f in academic_object:
            class_id = f.class_id.id
            acad_cal_id = f.id
                 
            sql_fs = """SELECT id,name from sms_feestructure  ORDER BY name"""
            cr.execute(sql_fs)
            fs_rows =  view_res = cr.fetchall()
             
            for fee_str in fs_rows:
                fees_str_id =fee_str[0]
                
                # 1s create an entry in class fee strure object
                class_fee_str_id = self.pool.get('smsfee.classes.fees.structure').create(cr, uid, {
                                 'academic_cal_id': acad_cal_id,
                                 'fee_structure_id':fees_str_id})
                  
                print "fs id",class_fee_str_id
                if class_fee_str_id:
                    # creae all entries of fee types as one2many to fs
                
                    sql_ft = """SELECT id,name,subtype from smsfee_feetypes ORDER BY name"""
                    cr.execute(sql_ft)
                    ft_rows = cr.fetchall()
                     
                    if ft_rows:
                        for fee_type in ft_rows:
                             amount = 0
                             #sarch previous class fee
                             
                             fee_id = self.pool.get('smsfee.classes.fees.types').search(cr, uid, [
                                    ('academic_cal_id','=',acad_cal_id),
                                    ('fee_structure_id','=',class_fee_str_id),
                                    ('fee_type','=',fee_type[0])])
                             print "fee already",fee_id
                             if len(fee_id) == 0:
                        
                                 created = self.pool.get('smsfee.classes.fees.types').create(cr, uid, {
                                         'academic_cal_id':acad_cal_id,
                                         'fee_structure_id':class_fee_str_id,
                                         'fee_type': fee_type[0],
                                         'amount': 0}) 
                                 print "created",created 
                               
                    else:
                        raise osv.except_osv(('Please Define fee Types'),('Fee Types & Fee Structure both are needed for lass Fee Management'))
                                     
                   
        return                
         
#============== View of tree ===========================================================================================================         
#         cr.execute("""select id,name from ir_ui_view 
#                     where model= 'smsfee.classes.fees' 
#                     and type='tree'""")
#         view_res = cr.fetchone()
#          
#         return {
#             'domain': "[('academic_cal_id','=',"+str(acad_cal_id)+")]",
#             'name': 'Fee Management:'+academic_object[0].name,
#             'view_type': 'form',
#             'view_mode': 'tree',
#             'res_model': 'smsfee.classes.fees',
#             'view_id': view_res,
#             'type': 'ir.actions.act_window'}
    
    
    _name = 'sms.academiccalendar'
    _inherit ='sms.academiccalendar'
        
    _columns = {
            'fee_structures':fields.one2many('smsfee.classes.fees','academic_cal_id','Fee Structure'),
            #new class fee object, aobve one will be deleted
            'class_fee_structures':fields.one2many('smsfee.classes.fees.structure','academic_cal_id','Fee Structure'),
            'fee_update_till':fields.many2one('sms.session.months','Fee Updated Till'),
            'fee_register':fields.one2many('smsfee.classfees.register','academic_cal_id','Register'),
    }
       
sms_academiccalendar()

class smsfee_classes_fees_structure(osv.osv):
    
   
    
    """ all Fee Structures for an academic calendar new format """
    
    def create(self, cr, uid, vals, context=None, check=True):
         result = super(osv.osv, self).create(cr, uid, vals, context)
#          for obj in self.browse(cr, uid, context=context):
         return result
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             result[f.id] = str(f.fee_structure_id.name)
        return result
    
    _name = 'smsfee.classes.fees.structure'
   
    _description = "Stores classes fee"
    _order = "fee_structure_id"
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Class Fee',type='char'),
        'academic_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar',required = True),      
        'fee_structure_id': fields.many2one('sms.feestructure','Fee Structure',required = True),
        'fee_type_ids': fields.one2many('smsfee.classes.fees.types','fee_structure_id','Fee Type'),
        'active':fields.boolean('Active'),
    }
    _sql_constraints = [('Class_fee_unique', 'unique (academic_cal_id,fee_structure_id,fee_type_ids)', """ Class Fee is already Defined Remove Duplication..""")]
smsfee_classes_fees_structure()

class smsfee_classes_fees_types(osv.osv):
    
    """ all smsfee_classes_fees_types for an academic calendar new format """
    
    def create(self, cr, uid, vals, context=None, check=True):
         result = super(osv.osv, self).create(cr, uid, vals, context)
#          for obj in self.browse(cr, uid, context=context):
         return result
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             ftyp = f.fee_type
             result[f.id] = str(ftyp.name)
        return result
    
    _name = 'smsfee.classes.fees.types'
   
    _description = "Stores classes fee"
    _order = "fee_type"
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Class Fee',type='char'),
        'academic_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar',required = True),      
        'fee_structure_id': fields.many2one('smsfee.classes.fees.structure','Fee Structure',required = True),
        'fee_type': fields.many2one('smsfee.feetypes','Fee Type',required = True),
        'amount':fields.float('Amount'),
    }
    _sql_constraints = [('Class_fee_unique', 'unique (academic_cal_id,fee_structure_id,fee_type)', """ Class Fee is already Defined Remove Duplication..""")]
smsfee_classes_fees_types()

class sms_student(osv.osv):
    """This object is used to add fields in sms.student"""
    def action_pay_student_fee(self, cr, uid, ids, context=None):
        ctx = {}
        for f in self.pool.get('sms.student').browse(cr,uid,ids):
            if not context:
                ctx = {
                'student_id':f.id,
                'student_class_id':f.current_class.id,
                'session_id':f.current_class.acad_session_id.id,
                'fee_structure_id':f.fee_type.id
        #          'student_class_id': [(0, 0, {'product_id': product_id, 'product_qty': 1})],   
                }
            else:
                ctx = context
                ctx['student_id'] = f.id
                ctx['student_class_id'] = f.current_class.id,
                ctx['fee_structure_id'] = f.fee_type.id
                ctx['session_id'] = f.current_class.acad_session_id.id
        
        result = {
        'type': 'ir.actions.act_window',
        'name': 'Collect Fees',
        'res_model': 'smsfee.receiptbook',
        'view_type': 'form',
        'view_mode': 'form',
        'view_id': False,
        'nodestroy': True,
        'target': 'current',
        'context': ctx,
        }
        return result 
    
    def set_paybles(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        amount = '0'
        records =  self.browse(cr, uid, ids, context)
        print "ids:,",ids

        for f in records:
            sql =   """SELECT sum(fee_amount) FROM smsfee_studentfee
                     WHERE student_id ="""+str(ids[0])+"""  AND state='fee_unpaid'"""
            cr.execute(sql)
            amount = cr.fetchone()[0]
            if amount is None:
                amount = '0'   
                print "amount:m,",amount  
        result[f.id] = amount
        print "result",result
        return result
    
    def set_paid_amount(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        amount = '0'
        records =  self.browse(cr, uid, ids, context)
        print "ids:,",ids

        for f in records:
            sql =   """SELECT sum(fee_amount) FROM smsfee_studentfee
                     WHERE student_id ="""+str(ids[0])+"""  AND state='fee_paid'"""
            cr.execute(sql)
            amount = cr.fetchone()[0]
            if amount is None:
                amount = '0'   
                print "amount:m,",amount  
        result[f.id] = amount
        print "result",result
        return result
    
    _name = 'sms.student'
    _inherit ='sms.student'
        
    _columns = {
            'studen_fee_ids':fields.one2many('smsfee.studentfee', 'student_id','Student Fee'),
            'latest_fee':fields.many2one('sms.session.months','Fee Register'),
            'total_paybles':fields.function(set_paybles, method=True, string='Paybles', type='char', size=300),
            'total_paid_amount':fields.function(set_paid_amount, method=True, string='Total Paid', type='char', size=300),

    }
sms_student()


class smsfee_classes_fees(osv.osv):
    
    def get_company(self, cr, uid, ids, context=None):
        cpm_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.id
        company = self.pool.get('res.company').browse(cr,uid,uid).name
        return company
    
    """ all Fee Structures for an academic calendar
        new object (smsfee_classes_fees_structure) is associated with academic calendar
        this object will later on be deleted
        student fee will also be inserted from that object """
    
    def create(self, cr, uid, vals, context=None, check=True):
         result = super(osv.osv, self).create(cr, uid, vals, context)
#          for obj in self.browse(cr, uid, context=context):
         return result
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             ftyp = f.fee_type_id
             result[f.id] = str(ftyp.name)
        return result
    
    _name = 'smsfee.classes.fees'
    _inherit ='smsfee.classes.fees'
   
    _description = "Stores classes fee"
    _order = "fee_structure_id"
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Class Fee',type='char'),
        'academic_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar',required = True),      
        'fee_structure_id': fields.many2one('sms.feestructure','Fee Structure',required = True),
        'fee_type_id': fields.many2one('smsfee.feetypes','Fee',required = True),
        'amount':fields.integer('Amount'),
    }
    _sql_constraints = [('Class_fee_unique', 'unique (academic_cal_id,fee_structure_id,fee_type_id)', """ Class Fee is already Defined Remove Duplication..""")]
smsfee_classes_fees()

class smsfee_classfees_register(osv.osv):
    
    """ Stores monthwiase fee updation historu for a class, where a class fee is updated in current month or not """
    
    def create(self, cr, uid, vals, context=None, check=True):
         result = super(osv.osv, self).create(cr, uid, vals, context)
#          for obj in self.browse(cr, uid, context=context):
         return result
   
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             result[f.id] = str(f.academic_cal_id.name)+" --- "+str(f.month.name)
        return result
    
    def _set_forcasted_fee(self, cr, uid, ids, name, args, context=None):
        result = {}
        #this query will be changed when function for fee reurned is included
        for f in self.browse(cr, uid, ids, context=context):
             sql = """SELECT sum(fee_amount) from smsfee_studentfee
                      WHERE due_month = """+str(f.month.id)+"""
                      AND acad_cal_id="""+str(f.academic_cal_id.id)
             cr.execute(sql)
             amount = cr.fetchone() 
             if amount:
                 result[f.id] = amount[0] 
             else:
                 result[f.id] = amount[0]
        return result         
             
    def _set_paid_fee(self, cr, uid, ids, name, args, context=None):
         #this query will be changed when function for fee reurned is included
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             sql = """SELECT sum(paid_amount) from smsfee_studentfee
                      WHERE due_month = """+str(f.month.id)+"""
                      AND acad_cal_id="""+str(f.academic_cal_id.id)+"""
                      AND reconcile = True"""
             cr.execute(sql)
             amount = cr.fetchone() 
             if amount:
                 result[f.id] = amount[0] 
             else:
                 result[f.id] = amount[0]
        return result                  
    
    _name = 'smsfee.classfees.register'
    _order = "month desc"
    """stores academic calendar month by month updates, user has to manually update fee register for each classs for each month. this object also sotres monthly fee received in each month.
       """
    _description = "Stores classes fee updation"
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Class Fee',type='char'),
        'academic_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar',readonly = True),      
        'month': fields.many2one('sms.session.months','Month',readonly = True),
        'month_forcasted_fee':fields.function(_set_forcasted_fee, method=True,  string='Forcasted',type='char'),
        'month_fee_received':fields.function(_set_paid_fee, method=True,  string='Received',type='char'),
    }
smsfee_classfees_register()



class smsfee_feetypes(osv.osv):
    """ all Fee Types """
    
    def onchange_feesubtype(self, cr, uid,ids,selection):
        vals = {}
        
        if selection == 'Monthly_Fee':
            vals['helptxt'] = 'Monthly Fee:\n \tUse the type for all fees that the institutes collects on monthly basis.'
        elif selection == 'at_admission': 
            vals['helptxt'] = 'Charged at The Time of Admission:\n\t Use this type of fee for all fees that the institutes want to charged at the time of new admission.\n\t Do not use for Refundable Fees.'
        elif selection == 'Refundable': 
            vals['helptxt'] = 'Refundable:\n\t Use it for all fees that are to be paid back to students.\n\t Example:\n\t\t Security Fee (At the time of admission)'
        elif selection == 'Refundable': 
            vals['helptxt'] = 'Refundable:\n\t Use it for all fees that are to be paid back to students.\n\t Example:\n\t\t Security Fee (At the time of admission)'
        elif selection == 'Annual_fee': 
            vals['helptxt'] = 'Annual Fee:\n\t Use this Fee Type for all fees that are charged at the time of students promotions to new classes.\n\t (Fees that are echanged only once within a session.).'
        elif selection == 'Other': 
            vals['helptxt'] = 'Other:\n\tUse this Option for the fee that does not match with the available options'  
        elif selection == 'Promotion_Fee': 
            vals['helptxt'] = 'Promotion Fee:\n\tFees charged at promotion'  
        update_lines = self.pool.get('smsfee.feetypes').write(cr, uid, ids, {'helptxt':vals['helptxt']})   
        return {'value':vals}
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
 
        """
         the create method of this method will auto update new fee objects of academic calendar
         the below commented code will be removed, same for fee structure object
        """
    
#     def create(self, cr, uid, vals, context=None, check=True):
#         new_feetype = super(osv.osv, self).create(cr, uid, vals, context) 
#         sql = """SELECT id,name FROM sms_feestructure"""
#         cr.execute(sql)
#         rows = cr.fetchall()
#         if rows:
#             sql = """SELECT DISTINCT sms_classes.id from sms_classes
#                   INNER JOIN sms_academiccalendar ON sms_classes.id = sms_academiccalendar.class_id"""
#             cr.execute(sql)
#             classes = cr.fetchall()
#             print "classes ",classes 
#             if classes:
#                 for class_id in classes:
#                    for ft in rows:
#                        
#                        create = self.pool.get('smsfee.generic.classes.fees').create(cr, uid, {
#                                'sms_class_id': class_id,
#                                'fee_structure_id':ft[0],
#                                'fee_type_id': new_feetype,
#                                'amount': 0})   
#          
#             return new_feetype
    
    
    _name = 'smsfee.feetypes'
    _description = "This object store fee types"
    _columns = {
        'name': fields.char(string = 'Fee Type',size = 100,required = True),      
        'description': fields.char(string = 'Description',size = 100),
        'subtype': fields.selection([('Monthly_Fee','Monthly Fee'),('at_admission','Charged at The Time of Admission'),('Promotion_Fee','Promotion Fee'),('Annual_fee','Annual Fee'),('Refundable','Refundable'),('Other','Other')],'Fee Category',required = True),
        'helptxt': fields.text('Help Text',readonly = True),
        'classes_ids': fields.one2many('smsfee.generic.classes.fees', 'fee_type_id', 'Classes'),
    }
    _sql_constraints = [  
        ('Fee Exisits', 'unique (name)', 'Fee Already exists!')
    ] 
    _defaults = {'helptxt' :'\n\nDefine Your Fee Details Here.\n\n\t1:Admission Fee, \n\t2:Monthly Fee,\n\t3: Security Fee etc.'}
smsfee_feetypes()

class smsfee_studentfee(osv.osv):
    
    
    """ Stores student fee record"""
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
    
    def unlink(self, cr, uid, ids, context=None):
         done = ''
         record = self.browse(cr, uid, ids, context=context)
         for f in record:
             if f.state == 'fee_unpaid':
                result = self.write(cr, uid, f.id, {'state':'Deleted'})
             else:
                 raise osv.except_osv(('Not Allowed'), ('Only Unpaid Fees can be deleted'))
            
         return result
    
    def _set_std_fee(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             if f.state == 'fee_returned':
                 string  = 'Fee Returned'
             else:
                 if f.fee_month:
                     string = f.fee_type.name + " - "+f.fee_month.name
                 else:
                     string = f.fee_type.name 
             result[f.id] = string
        return result
    
    def get_student_total_paybles(self, cr, uid, ids, acad_std_id,context=None):
        
        sql = """SELECT sum(net_total) FROM smsfee_studentfee WHERE student_id ="""+str(ids)+"""
        AND acad_cal_std_id="""+str(acad_std_id)+"""AND net_total > 0 AND state= 'fee_unpaid'"""
        cr.execute(sql)
        bal = cr.fetchone()
        return bal[0]
    
    def insert_student_monthly_fee(self, cr, uid, ids, acad_std_id,acad_cal_id,fee_starting_month,acad_cal_fee_id):
        """This method will insert student monthly fee only when called in loop or without loop (admit student,re-admit student and other wizards wlil call it)"""
       
        acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal_id)
        class_fee_updated_till = acad_cal_obj.fee_update_till.id
       
        # Get a record frm sms acad cal classes fees, 
        acad_cal_fee = self.pool.get('smsfee.classes.fees').browse(cr,uid,acad_cal_fee_id)
        if acad_cal_fee:
            generic_fee_id = acad_cal_fee.fee_type_id.id
        
        session_months = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',acad_cal_obj.session_id.id),('id','<=',fee_starting_month)])
        print "got session months ",session_months
        if session_months:
            for month in session_months:
                print "this month",month
                fee_already_exists =  self.pool.get('smsfee.studentfee').search(cr,uid,[('acad_cal_id','=',acad_cal_id),('student_id','=',ids),('fee_type','=',acad_cal_fee_id),('fee_month','=',month)])
                
                if fee_already_exists:
                    print "fee already exists",month
                    continue
                else:
                    late_fee = 0
                    crate_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                'student_id': ids,
                                'acad_cal_id': acad_cal_id,
                                'acad_cal_std_id': acad_std_id,
                                'fee_type': acad_cal_fee_id,
                                'generic_fee_type':generic_fee_id,
                                'date_fee_charged':datetime.date.today(),
                                'due_month': fee_starting_month,
                                'fee_month': month,
                                'fee_amount': acad_cal_fee.amount,
                                'paid_amount':0,
                                'late_fee':0,
                                'total_amount':acad_cal_fee.amount + late_fee,
                                'reconcile':False,
                                 'state':'fee_unpaid'
                                })
        return  
    
    _name = 'smsfee.studentfee'
    _description = "Stores student fee record"
    _columns = {
        'name':fields.function(_set_std_fee, method=True,  string='Student Fee',type='char'),
        'receipt_no':fields.many2one('smsfee.receiptbook','Receipt No'),
        'student_id':fields.many2one('sms.student','Student'),
        'acad_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar'),
        'acad_cal_std_id': fields.many2one('sms.academiccalendar.student','Academic Calendar Student'),  
        'date_fee_charged':fields.date('Date Fee Charged'),
        'date_fee_paid':fields.date('Date Fee Paid'),
        'fee_type':fields.many2one('smsfee.classes.fees','Fee Type'),
        'generic_fee_type':fields.many2one('smsfee.feetypes','G.Feetype'),
        'fee_month':fields.many2one('sms.session.months','Fee Month'),
        'due_month':fields.many2one('sms.session.months','Payment Month'),
        'fee_amount':fields.integer('Fee'),
        'late_fee':fields.integer('Late Fee'),
        'total_amount':fields.integer('Payble'),
        'paid_amount':fields.integer('Paid Amount'),
        'returned_amount':fields.float('Returned Amount'),
        'discount': fields.integer('Discount'),
        'net_total': fields.integer('Balance'),  
        'reconcile':fields.boolean('Reconcile'), 
        'state':fields.selection([('fee_unpaid','Fee Unpaid'),('fee_paid','Fee Paid'),('fee_returned','Fee Returned'),('Deleted','Deleted')],'Fee Status',readonly=True),
    } 
    
    _defaults = {
        'reconcile': False
    }
smsfee_studentfee()

#========================================Student Withdraw process ==============================
class smsfee_std_withdraw(osv.osv):
    """ A fee receopt book, stores fee payments history of students """
    
    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)
        return result
  
     
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        print "vals parent:",vals
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
     
    def unlink(self, cr, uid, ids, context=None):
         result = super(osv.osv, self).unlink(cr, uid, ids, context)
         return result 
    
    
    
    def send_withdraw_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state':'waiting_approval','request_by':uid,})
        return
    
    def reject_std_withdraw(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state':'Rejected','decision_by':uid,'decision_date':datetime.today()})
        return
    
    def confirm_std_withdraw(self, cr, uid, ids, context=None):
        print "approve request"
        self.write(cr, uid, ids[0], {'state':'Approved','decision_by':uid,'decision_date':datetime.date.today()})
        rec = self.browse(cr, uid, ids, context)
        for f in rec:
            
            print "class:",f.student_class_id.id
            std_cls_id = self.pool.get('sms.academiccalendar.student').search(cr, uid, [('std_id','=',f.student_id.id),('name','=',f.student_class_id.id)], context=context)
            if std_cls_id:
                std_cls_rec = self.pool.get('sms.academiccalendar.student').browse(cr, uid, std_cls_id[0])
                std_subj_ids = self.pool.get('sms.student.subject').search(cr, uid, [('student','=',std_cls_id[0]),('subject_status','=','Current')], context=context)
                print "student subjects:",std_subj_ids
                if std_subj_ids:
                    if f.request_type == 'Withdraw':
                        #Withdraw student subjects
                        withdraw = self.pool.get('sms.student.subject').write(cr, uid, std_subj_ids,{'subject_status':'Withdraw'})
                        #Withdraw student class
                        std_cls_rec = self.pool.get('sms.academiccalendar.student').write(cr, uid, std_cls_id[0],{'state':'Withdraw'})
                        #update sms_student
                        sms_std = self.pool.get('sms.student').write(cr, uid, f.student_id.id,{'state':f.request_type,'date_withdraw':datetime.date.today(),'withdraw_by':uid})
                    else:
                        #suspend student subjects
                        susp = self.pool.get('sms.student.subject').write(cr, uid, std_subj_ids,{'subject_status':'Suspended'})
                        #suspend student class
                        std_cls_rec = self.pool.get('sms.academiccalendar.student').write(cr, uid, std_cls_id[0],{'state':'Suspended'})
                        #update sms_student
                        sms_std = self.pool.get('sms.student').write(cr, uid, f.student_id.id,{'state':f.request_type,'date_withdraw':datetime.date.today(),'withdraw_by':uid})
  
        return 
            
    def onchange_student(self, cr, uid,ids,std):
        result = {}
        print "std##########:",std
        if std:
             std_rec = self.pool.get('sms.student').browse(cr, uid, std)
             print "formid::",ids
             std_fs = std_rec.fee_type.name
             father_name = std_rec.father_name
             print "father::",father_name
             result['fee_structure'] = std_fs
#              result['father_name'] = father_name
# #              update_lines = self.pool.get('smsfee.receiptbook').write(cr, uid, ids, {'father_name':father_name})
             print "result:::",result
        return {'value':result}
        
#         fee_ids = self.pool.get('sms.studentfee').search(cr, uid, [('student_id','=', std)], context=context)
#         print "obj.fee_ids",fee_ids
#         for fees in fee_ids:
#             obj = self.pool.get('sms.studentfee').browse(cr, uid, fees)
#             student = obj.student_id.name
#             print "obj.acad_cal_id.id",obj.acad_cal_id.id
#             create = self.pool.get('smsfee.receiptbook.lines').create(cr, uid, {
#                        'name': obj.acad_cal_id.id,
#                        'fee_type':obj.fee_type.id,
#                        'fee_month': obj.fee_month,
#                        'receipt_book_id':pid,
#                        'fee_amount': obj.fee_amount,
#                        }) 
#             print "crert::",create
#          return {}
    def _set_req_no(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             ftyp = "W-"+str(ids[0])
             result[f.id] = ftyp
        return result
    
    _name = 'smsfee.std.withdraw'
    _description = "This object store fee types"
    _columns = {
        'name': fields.function(_set_req_no,string = 'Request No.',type = 'char',method = True,store = True),      
        'request_date': fields.date('Date'),
        'request_by': fields.many2one('res.users','Decision By'),
        'decision_date': fields.date('Date'),
        'decision_by': fields.many2one('res.users','Decision By'),
        'fee_structure': fields.char(string = 'Fee Structure',size = 100),
        'student_class_id': fields.many2one('sms.academiccalendar','Class',required = True),
        'student_id': fields.many2one('sms.student','Student',required = True),
        'father_name': fields.char(string = 'Father',size = 100,readonly = True),
        'reason_withdraw':fields.text('Reason Withdraw'),
        'request_type':fields.selection([('Withdraw','Withdraw'),('admission_cancel','Admission Cancel'),('drop_out','Drop Out'),('slc','School Leaving Certificate')],'Request Type'),
        'state': fields.selection([('Draft', 'Draft'),('waiting_approval', 'Waiting Approval'),('Approved', 'Approved'),('Rejected', 'Rejected')], 'State', readonly = True, help='State'),
        'select_return_fee_ids': fields.many2many('smsfee.studentfee', 'return_std_fee_rel', 'withdraw_req_id', 'student_fee_id','Fee To Return', domain="[('student_id','=',student_id)]"),
        
    }
    _sql_constraints = [  
        ('Fee Exisits', 'unique (name)', 'Fee Receipt No Must be Unique!')
    ] 
    _defaults = {
         'state':'Draft',
    }
smsfee_std_withdraw()


#=========================================== Student Withdraw process ENDS

class smsfee_fee_adjustment(osv.osv):
    _name= "smsfee.fee.adjustment"
    _descpription = "This is temporary object used to add those fee to the classe (selected students) which cannot be added to update fee register wizard."
    _order = "name"

    _columns = { 
        'name':fields.many2one('sms.student','Student', readonly=True),
        'student_class_id':fields.many2one('sms.academiccalendar.student','Student Academiccalendar', readonly=True),
        'fee_structure':fields.many2one('sms.feestructure','Fee Structure', readonly=True),
        'class_id':fields.many2one('sms.academiccalendar','Class', readonly=True),
        'fee_type':fields.many2one('smsfee.feetypes','Fee', readonly=True),
        'fee_subtype': fields.selection([('Monthly_Fee','Monthly Fee'),('at_admission','Charged at The Time of Admission'),('Promotion_Fee','Promotion Fee'),('Annual_fee','Annual Fee'),('Refundable','Refundable'),('Other','Other')],'Fee Category',required = True),
        'due_month': fields.many2one('sms.session.months','Due Month', readonly=True),
        'amount': fields.float('Amount'),
        'selected': fields.boolean('Included'),
        'user_id': fields.many2one('res.users','Operated By'),
        'action':fields.selection([('add_fee','Add Fee')],'Action',readonly=True),
    }
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(osv.osv, self).write(cr, uid, ids, vals, context)
        objs = self.browse(cr, uid, ids, context=context)
        fee_month = ''
        for f in self.browse(cr, uid, ids, context=context):
            if f.action == 'add_fee':
                ft_subtype = self.pool.get('smsfee.feetypes').browse(cr, uid, f.fee_type.id).subtype
                if ft_subtype == 'Monthly_Fee':
                    fee_month = f.due_month.id
                classes_fee = self.pool.get('smsfee.classes.fees').search(cr, uid, [('fee_type_id','=',f.fee_type.id),('academic_cal_id','=',f.class_id.id),('fee_structure_id','=',f.fee_structure.id)])
                if f.selected:
                    
                 	add_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                        'student_id':f.name.id,
                                        'acad_cal_id': f.class_id.id,
                                        'acad_cal_std_id': f.student_class_id.id,  
                                        'date_fee_charged':datetime.date.today(),
                                        'fee_type':classes_fee[0],
                                        'fee_month':fee_month,
                                        'due_month':f.due_month.id,
                                        'fee_amount':f.amount,
                                        'total_amount':f.amount,
                                        'reconcile':False,
                                         'state':'fee_unpaid',
                    
                    })  
                
        return {} 
       
    _defaults = {
    }
smsfee_fee_adjustment()





class smsfee_receiptbook(osv.osv):
    """ A fee receopt book, stores fee payments history of students """
    
    def create(self, cr, uid, vals, context=None, check=True):
        
        rec =  self.pool.get('sms.student').browse(cr,uid,vals['student_id'])
        vals['student_class_id'] = rec.current_class.id,
        vals['fee_structure_id'] = rec.fee_type.id
        vals['session_id'] =  rec.current_class.acad_session_id.id,
        
        result = super(osv.osv, self).create(cr, uid, vals, context)
        return result
  
     
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        print "vals parent:",vals
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
     
    def unlink(self, cr, uid, ids, context=None):
         result = super(osv.osv, self).unlink(cr, uid, ids, context)
         return result 
    
    def unlink_lines(self, cr, uid, ids, *args):
        line_pool = self.pool.get('smsfee.receiptbook.lines')
        print "idssssssss:",ids
        idss = line_pool.search(cr,uid, [('receipt_book_id','=',ids)])
        for id in idss:
            line_pool.unlink(cr,uid,id)
        print "idssssssss:",ids   
        return True
    
    def load_std_fee(self, cr, uid, ids, context=None):
        brows =   self.browse(cr, uid, ids, context)
        unlink = self.unlink_lines(cr, uid,ids[0],None)
        student = brows[0].student_id.id
        self.onchange_student(cr, uid, ids, None)
        self.write(cr, uid, ids[0], {'student_id':student,})    
       
        fee_ids = self.pool.get('smsfee.studentfee').search(cr, uid, [('student_id','=',student),('reconcile','=',0)])
            
        if fee_ids:
            for fees in fee_ids:
                late_fee = 0
                reconcile = False
                
                    
                obj = self.pool.get('smsfee.studentfee').browse(cr, uid, fees)
                if  obj.fee_amount == 0 or obj.fee_amount+late_fee ==0:
                    reconcile = True
                create = self.pool.get('smsfee.receiptbook.lines').create(cr, uid, {
                       'acad_cal_id': obj.acad_cal_id.id,
                       'fee_type':obj.fee_type.id,
                       'fee_month': obj.fee_month.id,
                       'receipt_book_id':ids[0],
                       'student_fee_id':obj.id,
                       'fee_amount': obj.fee_amount,
                       'total': obj.fee_amount+late_fee,
                       'reconcile':reconcile
                       }) 
            self.write(cr, uid, ids[0], {'state':'fee_calculated'})
        return
    
    def confirm_fee_received(self, cr, uid, ids, context=None):
        self.onchange_student(cr, uid, ids, None)
        rec = self.browse(cr, uid, ids, context)
        paymethod = ''
        receipt_date = ''
        for f in rec:
            stdname = self.pool.get('sms.student').browse(cr, uid, f.student_id.id).name
            clsname = self.pool.get('sms.academiccalendar').browse(cr, uid,f.student_class_id.id).name
            paymethod = f.payment_method
            receipt_date = f.receipt_date
                
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id.enable_fm:
            print "enabled fm:"
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
        
        
        
        search_lines_id = self.pool.get('smsfee.receiptbook.lines').search(cr, uid, [('receipt_book_id','=',ids[0])], context=context)
        lines_obj = self.pool.get('smsfee.receiptbook.lines').browse(cr, uid, search_lines_id)
        generate_receipt = False
        total_paid_amount = 0 
        for line in lines_obj:
             
            std_fee_id = line.student_fee_id.id
            late_fee = 0
             
            if line.reconcile:
                total_paid_amount = total_paid_amount+ line.paid_amount
                generate_receipt = True
                update_std_fee_obj = self.pool.get('smsfee.studentfee').write(cr, uid, std_fee_id,{
                           'late_fee':late_fee,
                           'paid_amount':line.paid_amount,
                           'date_fee_paid':datetime.date.today(),
                           'discount':line.discount,
                           'net_total':line.net_total,
                           'reconcile':line.reconcile,
                           'receipt_no':str(ids[0]),
                           'state':'fee_paid',
                           })
             
        if generate_receipt:
            update_receiptbook = self.write(cr, uid, ids[0],{
                           'fee_received_by':uid,
                           'total_paid_amount':total_paid_amount,
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
                         'name': 'Fee Received:'+stdname,
                         'debit':0.00,
                         'credit':total_paid_amount,
                         'account_id':fee_income_acc.id,
                         'move_id':move_id,
                         'journal_id':fee_journal.id,
                         'period_id':period_id
                     },
                    {
                         'name': 'Fee Received:'+stdname,
                         'debit':total_paid_amount,
                         'credit':0.00,
                         'account_id':fee_reception_acc.id,
                         'move_id':move_id,
                         'journal_id':fee_journal.id,
                         'period_id':period_id
                     }]
                context.update({'journal_id': fee_journal.id, 'period_id': period_id})
                for move in account_move_line_dict:
                    print "move:",move
                    result=self.pool.get('account.move.line').create(cr, uid, move, context)
                    
                update_receiptbook2 = self.write(cr, uid, ids[0],{
                       'vouchered':True,
                       'vouchered_by':uid,
                       'voucher_date':datetime.date.today(),
                       'voucher_no':move_id
                       })
            search_booklines = self.pool.get('smsfee.receiptbook.lines').search(cr, uid, [('receipt_book_id','=',ids[0]),('reconcile','=',False)], context=context) 
            print "serarched ids to delete ",search_booklines
            if search_booklines:
               for del_id in search_booklines:
                   print "found ids to delte ",del_id
                   self.pool.get('smsfee.receiptbook.lines').unlink(cr,uid,del_id)
        else:
            raise osv.except_osv(('No Fee Paid'),('Paid amount or Discount should not be 0'))
#         for np in lines_obj :
#             if not np.reconcile:
#                 #Delete those record from lines which are not paid 
#                 sql = """DELETE FROM smsfee_receiptbook_lines WHERE id = """+str(np.id)+"""AND receipt_book_id="""+str(ids[0])
#                 cr.execute(sql) 
#                 cr.commit()  
        return 
            
    def onchange_student(self, cr, uid,ids,std):
        result = {}
        print "std##########:",std
        if std:
             f = self.pool.get('sms.student').browse(cr, uid, std)
             std_class = self.pool.get('sms.academiccalendar').browse(cr,uid,f.current_class.id)

             std_fs = f.fee_type.name
             father_name = f.father_name
             result['fee_structure'] = f.fee_type.name
             result['father_name'] = father_name
             result['student_class_id'] = f.current_class.id
             result['session_id'] = std_class.acad_session_id.id
             
             sql =   """SELECT sum(fee_amount) FROM smsfee_studentfee
                     WHERE student_id ="""+str(std)+"""  AND reconcile=False"""
             cr.execute(sql)
             amount = cr.fetchone()[0]
             if amount is None:
                amount = '0'   
             result['total_paybles'] = amount
             update_data = self.pool.get('smsfee.receiptbook').write(cr, uid, ids, result)
        return {'value':result}
        
#         fee_ids = self.pool.get('sms.studentfee').search(cr, uid, [('student_id','=', std)], context=context)
#         print "obj.fee_ids",fee_ids
#         for fees in fee_ids:
#             obj = self.pool.get('sms.studentfee').browse(cr, uid, fees)
#             student = obj.student_id.name
#             print "obj.acad_cal_id.id",obj.acad_cal_id.id
#             create = self.pool.get('smsfee.receiptbook.lines').create(cr, uid, {
#                        'name': obj.acad_cal_id.id,
#                        'fee_type':obj.fee_type.id,
#                        'fee_month': obj.fee_month,
#                        'receipt_book_id':pid,
#                        'fee_amount': obj.fee_amount,
#                        }) 
#             print "crert::",create
#          return {}
    def _set_slipno(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            sql = """SELECT max(id) FROM smsfee_receiptbook WHERE state ='Paid'
                     """
            cr.execute(sql)
            counted = cr.fetchone() 
            result[f.id] = counted[0]
        return result
    
    
    def _get_id(self, cr, uid, context={}):
        if context:
            if 'student_id' in context:
                return context['student_id']
        return None
    
    _name = 'smsfee.receiptbook'
    _description = "This object store fee types"
    _columns = {
        'name': fields.function(_set_slipno,string = 'Receipt No.',type = 'char',method = True,store = True),      
        'receipt_date': fields.date('Date'),
        'session_id':fields.many2one('sms.academics.session', 'Session'),
        'fee_structure': fields.char(string = 'Fee Structure',size = 100),
        'manual_recpt_no': fields.char(string = 'Manual Receipt No',required = True,size = 100),
        'student_class_id': fields.many2one('sms.academiccalendar','Class'),
        'student_id': fields.many2one('sms.student','Student',required = True),
        'father_name': fields.char(string = 'Father',size = 100),
        'payment_method':fields.selection([('Cash','Cash'),('Bank','Bank')],'Payment Method'),
        'total_paybles':fields.float('Paybles',readonly = True),
        'total_paid_amount':fields.float('Paid Amount',required = True),
        'note_at_receive': fields.text('Note'),
        'state': fields.selection([('Draft', 'Draft'),('fee_calculated', 'Calculated'),('Paid', 'Paid')], 'State', readonly = True, help='State'),
        'fee_received_by': fields.many2one('res.users', 'Received By'),
        'receiptbook_lines_ids': fields.one2many('smsfee.receiptbook.lines', 'receipt_book_id', 'Fees'),
        'voucher_date': fields.date('Voucher Date',readonly=True),
        'vouchered_by': fields.many2one('res.users', 'Voucher By',readonly=True),
        'vouchered': fields.boolean('Vouchered', readonly=True),
        'voucher_no': fields.many2one('account.move', 'Voucher No',readonly=True),
    }
    _sql_constraints = [  
        #('Fee Exisits', 'unique (name)', 'Fee Receipt No Must be Unique!')
    ] 
    _defaults = {
         'state':'Draft',
         'payment_method': 'Cash',
         'student_id':_get_id ,
         'total_paid_amount': 0.0,
    }
smsfee_receiptbook()

class smsfee_receiptbook_lines(osv.osv):
    """ A fee receopt book, stores fee payments history of students """
    
    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)
        return result
  
     
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
     
    def unlink(self, cr, uid, ids, context=None):
        result = super(osv.osv, self).unlink(cr, uid, ids, context)
        return result 
    
    def onchange_amount(self, cr, uid, ids,total,paid_amount):
        vals = {}
        
        print "ids::",ids
        if paid_amount > total:
            vals['paid_amount'] = 0
            vals['discount'] = 0
            vals['net_total'] = total
            vals['reconcile'] = False
        elif paid_amount == total: 
            vals['paid_amount'] = paid_amount
            vals['discount'] = 0
            vals['net_total'] = total-paid_amount
            vals['reconcile'] = True
        elif  paid_amount < total:
            vals['paid_amount'] = paid_amount
            vals['discount'] = total - paid_amount
            vals['net_total'] = total- (paid_amount+vals['discount'])
            vals['reconcile'] = True         
        update_lines = self.pool.get('smsfee.receiptbook.lines').write(cr, uid, ids, {
                       'paid_amount':vals['paid_amount'],
                       'discount':vals['discount'],
                       'net_total':vals['net_total'],
                       'reconcile':vals['reconcile']
                       })   
        return {'value':vals}
    
    def onchange_discount(self, cr, uid, ids,total,discount):
        vals = {}
        
        print "ids disc::",ids
        if discount > total:
            vals['paid_amount'] = 0
            vals['discount'] = 0
            vals['net_total'] = total
            vals['reconcile'] = False
        elif discount == total: 
            vals['paid_amount'] = 0
            vals['net_total'] = total- discount
            vals['reconcile'] = True
            vals['discount'] = discount
        elif  discount < total:
            vals['paid_amount'] = total - discount
            vals['net_total'] = total- (discount+vals['paid_amount'])
            vals['discount'] = discount
            vals['reconcile'] = True         
        update_lines = self.pool.get('smsfee.receiptbook.lines').write(cr, uid, ids, {
                       'paid_amount':vals['paid_amount'],
                       'discount':vals['discount'],
                       'net_total':vals['net_total'],
                       'reconcile':vals['reconcile']
                       })   
        return {'value':vals}
    
    _name = 'smsfee.receiptbook.lines'
    _description = "This object store fee types"
    _columns = {
        'name': fields.many2one('sms.academiccalendar','Academic Calendar'),      
        'fee_type': fields.many2one('smsfee.classes.fees','Fee Type'),
        'student_fee_id': fields.many2one('smsfee.studentfee','Student Fee Id'),
        'fee_month': fields.many2one('sms.session.months','Fee Month'),
        'receipt_book_id': fields.many2one('smsfee.receiptbook','Receipt book',required = True),
        'fee_amount':fields.integer('Fee'),
        'late_fee':fields.integer('late Fee'),
        'total':fields.integer('Payble'),
        'paid_amount':fields.integer('Paid'),
        'discount': fields.integer('Discount'),
        'net_total': fields.integer('Balance'),  
        'reconcile':fields.boolean('Reconcile',readonly = True), 
    }
    _sql_constraints = [  
        ('Fee Exisits', 'unique (receipt_no)', 'Fee Receipt No Must be Unique!')
    ] 
    _defaults = {
                 'discount':0,
                 'paid_amount':0,
                 
                 
    }
smsfee_receiptbook_lines()

#-------------------------- Unpaid Fee Adjustment ---------------------------------------------------------------
# 
# class smsfee_unpaid_fee_adjustment(osv.osv):
#     """ Unapid fee Adjustment """
#     
#     def create(self, cr, uid, vals, context=None, check=True):
#         result = super(osv.osv, self).create(cr, uid, vals, context)
#         return result
#   
#      
#     def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
#         print "vals parent:",vals
#         result = super(osv.osv, self).write(cr, uid, ids, vals, context)
#         return result
#      
#     def unlink(self, cr, uid, ids, context=None):
#          result = super(osv.osv, self).unlink(cr, uid, ids, context)
#          return result 
#     
#     def unlink_lines(self, cr, uid, ids, *args):
#         line_pool = self.pool.get('smsfee.receiptbook.lines')
#         print "idssssssss:",ids
#         idss = line_pool.search(cr,uid, [('receipt_book_id','=',ids)])
#         for id in idss:
#             line_pool.unlink(cr,uid,id)
#         print "idssssssss:",ids   
#         return True
#     
#     def load_std_fee(self, cr, uid, ids, context=None):
#         brows =   self.browse(cr, uid, ids, context)
#         unlink = self.unlink_lines(cr, uid,ids[0],None)
#         student = brows[0].student_id.id
#         self.onchange_student(cr, uid, ids, None)
#         self.write(cr, uid, ids[0], {'student_id':student,})    
#        
#         fee_ids = self.pool.get('smsfee.studentfee').search(cr, uid, [('student_id','=',student),('reconcile','=',0)])
#             
#         if fee_ids:
#             for fees in fee_ids:
#                 late_fee = 0
#                 reconcile = False
#                 
#                     
#                 obj = self.pool.get('smsfee.studentfee').browse(cr, uid, fees)
#                 if  obj.fee_amount == 0 or obj.fee_amount+late_fee ==0:
#                     reconcile = True
#                 create = self.pool.get('smsfee.receiptbook.lines').create(cr, uid, {
#                        'acad_cal_id': obj.acad_cal_id.id,
#                        'fee_type':obj.fee_type.id,
#                        'fee_month': obj.fee_month.id,
#                        'receipt_book_id':ids[0],
#                        'student_fee_id':obj.id,
#                        'fee_amount': obj.fee_amount,
#                        'total': obj.fee_amount+late_fee,
#                        'reconcile':reconcile
#                        }) 
#             self.write(cr, uid, ids[0], {'state':'fee_calculated'})
#         return
#     
#     def confirm_fee_received(self, cr, uid, ids, context=None):
#         self.onchange_student(cr, uid, ids, None)
#         rec = self.browse(cr, uid, ids, context)
#         paymethod = ''
#         receipt_date = ''
#         for f in rec:
#             stdname = self.pool.get('sms.student').browse(cr, uid, f.student_id.id).name
#             clsname = self.pool.get('sms.academiccalendar').browse(cr, uid,f.student_class_id.id).name
#             paymethod = f.payment_method
#             receipt_date = f.receipt_date
#                 
#         user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
#         if user.company_id.enable_fm:
#             print "enabled fm:"
#             fee_income_acc = user.company_id.student_fee_income_acc
#             fee_expense_acc = user.company_id.student_fee_expense_acc
#             fee_journal = user.company_id.fee_journal
#             period_id = self.pool.get('account.move')._get_period(cr, uid, context)
#             if paymethod=='Cash':
#                 fee_reception_acc = user.company_id.fee_reception_account_cash
#                 if not fee_reception_acc:
#                     raise osv.except_osv(('Cash Account'), ('No Account is defined for Payment method:Cash'))
#             elif paymethod=='Bank':
#                 fee_reception_acc = user.company_id.fee_reception_account_bank
#                 if not fee_reception_acc:
#                     raise osv.except_osv(('Bank Account'), ('No Account is defined for Payment method:Bank'))
#             
#             if not fee_income_acc:
#                 raise osv.except_osv(('Accounts'), ('Please define Fee Income Account'))
#             if not fee_expense_acc:
#                 raise osv.except_osv(('Accounts'), ('Please define Fee Expense Account'))
#             if not fee_journal:
#                 raise osv.except_osv(('Accounts'), ('Please Define A Fee Journal'))
#             if not period_id:
#                 raise osv.except_osv(('Financial Period'), ('Financial Period is not defined in Fiscal Year.'))
#         
#         
#         
#         search_lines_id = self.pool.get('smsfee.receiptbook.lines').search(cr, uid, [('receipt_book_id','=',ids[0])], context=context)
#         lines_obj = self.pool.get('smsfee.receiptbook.lines').browse(cr, uid, search_lines_id)
#         generate_receipt = False
#         total_paid_amount = 0 
#         for line in lines_obj:
#              
#             std_fee_id = line.student_fee_id.id
#             late_fee = 0
#              
#             if line.reconcile:
#                 total_paid_amount = total_paid_amount+ line.paid_amount
#                 generate_receipt = True
#                 update_std_fee_obj = self.pool.get('smsfee.studentfee').write(cr, uid, std_fee_id,{
#                            'late_fee':late_fee,
#                            'paid_amount':line.paid_amount,
#                            'date_fee_paid':datetime.date.today(),
#                            'discount':line.discount,
#                            'net_total':line.net_total,
#                            'reconcile':line.reconcile,
#                            'receipt_no':str(ids[0]),
#                            'state':'fee_paid',
#                            })
#              
#         if generate_receipt:
#             update_receiptbook = self.write(cr, uid, ids[0],{
#                            'fee_received_by':uid,
#                            'total_paid_amount':total_paid_amount,
#                            'state':'Paid',
#                            })
#             if user.company_id.enable_fm:
#                 account_move_dict= {
#                                 'ref':'Income:Student Fee:',
#                                 'journal_id':fee_journal.id,
#                                 'type':'journal_voucher',
#                                 'narration':'Pay/'+str(ids[0]) +'--'+ receipt_date}
#                 
#                 move_id=self.pool.get('account.move').create(cr, uid, account_move_dict, context)
#                 account_move_line_dict=[
#                     {
#                          'name': 'Fee Received:'+stdname,
#                          'debit':0.00,
#                          'credit':total_paid_amount,
#                          'account_id':fee_income_acc.id,
#                          'move_id':move_id,
#                          'journal_id':fee_journal.id,
#                          'period_id':period_id
#                      },
#                     {
#                          'name': 'Fee Received:'+stdname,
#                          'debit':total_paid_amount,
#                          'credit':0.00,
#                          'account_id':fee_reception_acc.id,
#                          'move_id':move_id,
#                          'journal_id':fee_journal.id,
#                          'period_id':period_id
#                      }]
#                 context.update({'journal_id': fee_journal.id, 'period_id': period_id})
#                 for move in account_move_line_dict:
#                     print "move:",move
#                     result=self.pool.get('account.move.line').create(cr, uid, move, context)
#                     
#                 update_receiptbook2 = self.write(cr, uid, ids[0],{
#                        'vouchered':True,
#                        'vouchered_by':uid,
#                        'voucher_date':datetime.date.today(),
#                        'voucher_no':move_id
#                        })
#             search_booklines = self.pool.get('smsfee.receiptbook.lines').search(cr, uid, [('receipt_book_id','=',ids[0]),('reconcile','=',False)], context=context) 
#             print "serarched ids to delete ",search_booklines
#             if search_booklines:
#                for del_id in search_booklines:
#                    print "found ids to delte ",del_id
#                    self.pool.get('smsfee.receiptbook.lines').unlink(cr,uid,del_id)
#         else:
#             raise osv.except_osv(('No Fee Paid'),('Paid amount or Discount should not be 0'))
# #         for np in lines_obj :
# #             if not np.reconcile:
# #                 #Delete those record from lines which are not paid 
# #                 sql = """DELETE FROM smsfee_receiptbook_lines WHERE id = """+str(np.id)+"""AND receipt_book_id="""+str(ids[0])
# #                 cr.execute(sql) 
# #                 cr.commit()  
#         return 
#             
#     def onchange_student(self, cr, uid,ids,std):
#         result = {}
#         print "std##########:",std
#         if std:
#              std_rec = self.pool.get('sms.student').browse(cr, uid, std)
#              std_fs = std_rec.fee_type.name
#              father_name = std_rec.father_name
#              result['fee_structure'] = std_fs
#              result['father_name'] = father_name
#              
#              sql =   """SELECT sum(fee_amount) FROM smsfee_studentfee
#                      WHERE student_id ="""+str(std)+"""  AND reconcile=False"""
#              cr.execute(sql)
#              amount = cr.fetchone()[0]
#              if amount is None:
#                 amount = '0'   
#              result['total_paybles'] = amount
#              update_data = self.pool.get('smsfee.receiptbook').write(cr, uid, ids, {'father_name':father_name,'total_paybles':amount})
#         return {'value':result}
#         
# #         fee_ids = self.pool.get('sms.studentfee').search(cr, uid, [('student_id','=', std)], context=context)
# #         print "obj.fee_ids",fee_ids
# #         for fees in fee_ids:
# #             obj = self.pool.get('sms.studentfee').browse(cr, uid, fees)
# #             student = obj.student_id.name
# #             print "obj.acad_cal_id.id",obj.acad_cal_id.id
# #             create = self.pool.get('smsfee.receiptbook.lines').create(cr, uid, {
# #                        'name': obj.acad_cal_id.id,
# #                        'fee_type':obj.fee_type.id,
# #                        'fee_month': obj.fee_month,
# #                        'receipt_book_id':pid,
# #                        'fee_amount': obj.fee_amount,
# #                        }) 
# #             print "crert::",create
# #          return {}
#     def _set_slipno(self, cr, uid, ids, name, args, context=None):
#         result = {}
#         for f in self.browse(cr, uid, ids, context=context):
#             sql = """SELECT max(id) FROM smsfee_receiptbook WHERE state ='Paid'
#                      """
#             cr.execute(sql)
#             counted = cr.fetchone() 
#             result[f.id] = counted[0]
#         return result
#     
#     def _get_active_session(self, cr, uid, context={}):
#         ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
#         if ssn:
#             return ssn[0]
#         else:
#             return []
#     
#     _name = 'smsfee.unpaid.fee.adjustment'
#     _description = "This object store fee types"
#     _columns = {
#         'name': fields.function(_set_slipno,string = 'Receipt No.',type = 'char',method = True,store = True),      
#         'class_id': fields.many2one('sms.academiccalendar','Class',required = True,domain="[('state!','=','Closed')]"),
#         'receipt_date': fields.date('Date'),
#         'fee_structure': fields.char(string = 'Fee Structure',size = 100),
#         'student_id': fields.many2one('sms.student','Student',required = True),
#         'payment_method':fields.selection([('Cash','Cash'),('Bank','Bank')],'Payment Method'),
#         'total_paybles_before_adjustment':fields.float('Paybles Before Adjustment',readonly = True),
#         'total_paybles_after_adjustment':fields.float('Paybles After Ajustment',readonly = True),
#         'filter_on_fee_structure': fields.boolean('Filter On Fee Structure'),
#         'note': fields.text('Note'),
#         'state': fields.selection([('Draft', 'Draft'),('Waiting_Approval', 'Waiting Approval'),('Fee_Adjusted', 'Fee Adjusted'),('Cancelled', 'Cancelled')], 'State', readonly = True, help='State'),
#         'requested_by': fields.many2one('res.users', 'Requested By'),
#         'approved_by': fields.many2one('res.users', 'Requested By'),
#         'adjustment_lines_ids': fields.one2many('smsfee.unpaid.feeadjustment.lines', 'parent_adjustment_id', 'Adjustments'),
#         'voucher_date': fields.date('Voucher Date',readonly=True),
#         'vouchered_by': fields.many2one('res.users', 'Voucher By',readonly=True),
#         'vouchered': fields.boolean('Vouchered', readonly=True),
#         'voucher_no': fields.many2one('account.move', 'Voucher No',readonly=True),
#     }
#     _sql_constraints = [  
#         #('Fee Exisits', 'unique (name)', 'Fee Receipt No Must be Unique!')
#     ] 
#     _defaults = {
#          'state':'Draft',
#          'payment_method': 'Cash',
#          'session_id':_get_active_session ,
#          'total_paid_amount': 0.0,
#     }
# smsfee_unpaid_fee_adjustment()
# 
# class smsfee_unpaid_fee_adjustmentlines(osv.osv):
#     """ A fee receopt book, stores fee payments history of students """
#     
#     def create(self, cr, uid, vals, context=None, check=True):
#         result = super(osv.osv, self).create(cr, uid, vals, context)
#         return result
#   
#      
#     def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
#         result = super(osv.osv, self).write(cr, uid, ids, vals, context)
#         return result
#      
#     def unlink(self, cr, uid, ids, context=None):
#         result = super(osv.osv, self).unlink(cr, uid, ids, context)
#         return result 
#     
#     def onchange_amount(self, cr, uid, ids,total,paid_amount):
#         vals = {}
#         
#         print "ids::",ids
#         if paid_amount > total:
#             vals['paid_amount'] = 0
#             vals['discount'] = 0
#             vals['net_total'] = total
#             vals['reconcile'] = False
#         elif paid_amount == total: 
#             vals['paid_amount'] = paid_amount
#             vals['discount'] = 0
#             vals['net_total'] = total-paid_amount
#             vals['reconcile'] = True
#         elif  paid_amount < total:
#             vals['paid_amount'] = paid_amount
#             vals['discount'] = total - paid_amount
#             vals['net_total'] = total- (paid_amount+vals['discount'])
#             vals['reconcile'] = True         
#         update_lines = self.pool.get('smsfee.receiptbook.lines').write(cr, uid, ids, {
#                        'paid_amount':vals['paid_amount'],
#                        'discount':vals['discount'],
#                        'net_total':vals['net_total'],
#                        'reconcile':vals['reconcile']
#                        })   
#         return {'value':vals}
#     
#     def onchange_discount(self, cr, uid, ids,total,discount):
#         vals = {}
#         
#         print "ids disc::",ids
#         if discount > total:
#             vals['paid_amount'] = 0
#             vals['discount'] = 0
#             vals['net_total'] = total
#             vals['reconcile'] = False
#         elif discount == total: 
#             vals['paid_amount'] = 0
#             vals['net_total'] = total- discount
#             vals['reconcile'] = True
#             vals['discount'] = discount
#         elif  discount < total:
#             vals['paid_amount'] = total - discount
#             vals['net_total'] = total- (discount+vals['paid_amount'])
#             vals['discount'] = discount
#             vals['reconcile'] = True         
#         update_lines = self.pool.get('smsfee.receiptbook.lines').write(cr, uid, ids, {
#                        'paid_amount':vals['paid_amount'],
#                        'discount':vals['discount'],
#                        'net_total':vals['net_total'],
#                        'reconcile':vals['reconcile']
#                        })   
#         return {'value':vals}
#     
#     _name = 'smsfee.unpaid.fee.adjustmentlines'
#     _description = "This object store fee types"
#     _columns = {
#         'name': fields.many2one('sms.academiccalendar','Academic Calendar'),      
#         'fee_type': fields.many2one('smsfee.classes.fees','Fee Type'),
#         'student_fee_id': fields.many2one('smsfee.studentfee','Student Fee Id'),
#         'fee_month': fields.many2one('sms.session.months','Fee Month'),
#         'receipt_book_id': fields.many2one('smsfee.receiptbook','Receipt book',required = True),
#         'fee_amount':fields.integer('Fee'),
#         'late_fee':fields.integer('late Fee'),
#         'total':fields.integer('Payble'),
#         'paid_amount':fields.integer('Paid'),
#         'discount': fields.integer('Discount'),
#         'net_total': fields.integer('Balance'),  
#         'reconcile':fields.boolean('Reconcile',readonly = True), 
#     }
#     _sql_constraints = [  
#         ('Fee Exisits', 'unique (receipt_no)', 'Fee Receipt No Must be Unique!')
#     ] 
#     _defaults = {
#                  'discount':0,
#                  'paid_amount':0,
#                  
#                  
#     }
# smsfee_unpaid_fee_adjustmentlines()



#-------------------------Unpaid fee Adjutment ENDS --------------------------------------------------------


class smsfee_return_paid_fee(osv.osv):
    """ this objects returns students fee paid by student. """
    
    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)
        return result
  
     
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        print "vals parent:",vals
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
     
    def unlink(self, cr, uid, ids, context=None):
         result = super(osv.osv, self).unlink(cr, uid, ids, context)
         return result 
    
    def unlink_lines(self, cr, uid, ids, *args):
        line_pool = self.pool.get('smsfee.receiptbook.lines')
        print "idssssssss:",ids
        idss = line_pool.search(cr,uid, [('receipt_book_id','=',ids)])
        for id in idss:
            line_pool.unlink(cr,uid,id)
        print "idssssssss:",ids   
        return True
    
    def load_std_fee(self, cr, uid, ids, context=None):
        brows =   self.browse(cr, uid, ids, context)
        unlink = self.unlink_lines(cr, uid,ids[0],None)
        student = brows[0].student_id.id
        self.write(cr, uid, ids[0], {'student_id':student,})    
       
        fee_ids = self.pool.get('smsfee.studentfee').search(cr, uid, [('student_id','=',student),('reconcile','=',0)])
            
        if fee_ids:
            for fees in fee_ids:
                late_fee = 0
                reconcile = False
                
                    
                obj = self.pool.get('smsfee.studentfee').browse(cr, uid, fees)
                if  obj.fee_amount == 0 or obj.fee_amount+late_fee ==0:
                    reconcile = True
                create = self.pool.get('smsfee.receiptbook.lines').create(cr, uid, {
                       'acad_cal_id': obj.acad_cal_id.id,
                       'fee_type':obj.fee_type.id,
                       'fee_month': obj.fee_month.id,
                       'receipt_book_id':ids[0],
                       'student_fee_id':obj.id,
                       'fee_amount': obj.fee_amount,
                       'total': obj.fee_amount+late_fee,
                       'reconcile':reconcile
                       }) 
            self.write(cr, uid, ids[0], {'state':'fee_calculated'})
        return
    
    def confirm_fee_received(self, cr, uid, ids, context=None):
        
        rec = self.browse(cr, uid, ids, context)
        paymethod = ''
        receipt_date = ''
        for f in rec:
            stdname = self.pool.get('sms.student').browse(cr, uid, f.student_id.id).name
            clsname = self.pool.get('sms.academiccalendar').browse(cr, uid,f.student_class_id.id).name
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
        
        
        
        search_lines_id = self.pool.get('smsfee.receiptbook.lines').search(cr, uid, [('receipt_book_id','=',ids[0])], context=context)
        lines_obj = self.pool.get('smsfee.receiptbook.lines').browse(cr, uid, search_lines_id)
        generate_receipt = False
        total_paid_amount = 0 
        for line in lines_obj:
             
            std_fee_id = line.student_fee_id.id
            late_fee = 0
             
            if line.reconcile:
                total_paid_amount = total_paid_amount+ line.paid_amount
                generate_receipt = True
                update_std_fee_obj = self.pool.get('smsfee.studentfee').write(cr, uid, std_fee_id,{
                           'late_fee':late_fee,
                           'paid_amount':line.paid_amount,
                           'date_fee_paid':datetime.date.today(),
                           'discount':line.discount,
                           'net_total':line.net_total,
                           'reconcile':line.reconcile,
                           'receipt_no':str(ids[0]),
                           'state':'fee_paid'
                           })
             
        if generate_receipt:
            update_receiptbook = self.write(cr, uid, ids[0],{
                           'fee_received_by':uid,
                           'total_paid_amount':total_paid_amount,
                           'state':'Paid',
                           'name':'Pay/'+str(ids[0])})
            if user.company_id.enable_fm:
                account_move_dict= {
                                'ref':'Income:Student Fee:',
                                'journal_id':fee_journal.id,
                                'type':'journal_voucher',
                                'narration':'Pay/'+str(ids[0]) +'--'+ receipt_date}
                
                move_id=self.pool.get('account.move').create(cr, uid, account_move_dict, context)
                account_move_line_dict=[
                    {
                         'name': 'Fee Received:'+stdname,
                         'debit':0.00,
                         'credit':total_paid_amount,
                         'account_id':fee_income_acc.id,
                         'move_id':move_id,
                         'journal_id':fee_journal.id,
                         'period_id':period_id
                     },
                    {
                         'name': 'Fee Received:'+stdname,
                         'debit':total_paid_amount,
                         'credit':0.00,
                         'account_id':fee_reception_acc.id,
                         'move_id':move_id,
                         'journal_id':fee_journal.id,
                         'period_id':period_id
                     }]
                context.update({'journal_id': fee_journal.id, 'period_id': period_id})
                for move in account_move_line_dict:
                    print "move:",move
                    result=self.pool.get('account.move.line').create(cr, uid, move, context)
                    
                update_receiptbook2 = self.write(cr, uid, ids[0],{
                       'vouchered':True,
                       'vouchered_by':uid,
                       'voucher_date':time.strftime('%Y-%m-%d'),
                       'voucher_no':move_id
                       })
             
        else:
            raise osv.except_osv(('No Fee Paid'),('Paid amount or Discount should not be 0'))
#         for np in lines_obj :
#             if not np.reconcile:
#                 #Delete those record from lines which are not paid 
#                 sql = """DELETE FROM smsfee_receiptbook_lines WHERE id = """+str(np.id)+"""AND receipt_book_id="""+str(ids[0])
#                 cr.execute(sql) 
#                 cr.commit()  
        return 
            
    def _set_slipno(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             ftyp = "PAY/"+str(ids[0])
             result[f.id] = ftyp
        return result
    
    def _get_active_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
        if ssn:
            return ssn[0]
        else:
            return []
        
        
    
    _name = 'smsfee.return.paid.fee'
    _description = "This object store fee types"
    _columns = {
        'name': fields.function(_set_slipno,string = 'Receipt No.',type = 'char',method = True,store = True),      
        'receipt_date': fields.date('Date'),
        'session_id':fields.many2one('sms.session', 'session'),
        'fee_structure': fields.char(string = 'Fee Structure',size = 100),
        'class_id': fields.many2one('sms.academiccalendar','Class',required = True,domain="[('session_id','=',session_id)]"),
        'student_id': fields.many2one('sms.student','Student',required = True),
        'father_name': fields.many2one('sms.student','Father',readonly = True),
        'payment_method':fields.selection([('Cash','Cash'),('Bank','Bank')],'Payment Method'),
        'total_paid_amount':fields.float('Paid Amount',required = True),
        'state':fields.selection([('Draft', 'Draft'),('fee_calculated', 'Calculated'),('Fee_Return', 'Fee Return')], 'State', readonly = True, help='State'),
        'fee_paid_by': fields.many2one('res.users', 'Received By'),
        'fee_return_lines_ids': fields.one2many('smsfee.feereturn.lines', 'receipt_book_id', 'Fees'),
        'voucher_date': fields.date('Voucher Date',readonly=True),
        'vouchered_by': fields.many2one('res.users', 'Voucher By',readonly=True),
        'vouchered': fields.boolean('Vouchered', readonly=True),
        'voucher_no': fields.many2one('account.move', 'Voucher No',readonly=True),
    }
    _sql_constraints = [  
        #('Fee Exisits', 'unique (name)', 'Fee Receipt No Must be Unique!')
    ] 
    _defaults = {
         'state':'Draft',
         'payment_method': 'Cash',
         'session_id':_get_active_session ,
         'name': 'Draft',
         'total_paid_amount': 0.0,
         'receipt_date': lambda * a: time.strftime('%Y-%m-%d'),
    }
smsfee_return_paid_fee()

class smsfee_feereturn_lines(osv.osv):
    """ A fee receopt book, stores fee payments history of students """
    
    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)
        return result
  
     
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
     
    def unlink(self, cr, uid, ids, context=None):
        result = super(osv.osv, self).unlink(cr, uid, ids, context)
        return result 
    
    def onchange_amount(self, cr, uid, ids,total,paid_amount):
        vals = {}
        
        print "ids::",ids
        if paid_amount > total:
            vals['paid_amount'] = 0
            vals['discount'] = 0
            vals['net_total'] = total
            vals['reconcile'] = False
        elif paid_amount == total: 
            vals['paid_amount'] = paid_amount
            vals['discount'] = 0
            vals['net_total'] = total-paid_amount
            vals['reconcile'] = True
        elif  paid_amount < total:
            vals['paid_amount'] = paid_amount
            vals['discount'] = total - paid_amount
            vals['net_total'] = total- (paid_amount+vals['discount'])
            vals['reconcile'] = True         
        update_lines = self.pool.get('smsfee.receiptbook.lines').write(cr, uid, ids, {
                       'paid_amount':vals['paid_amount'],
                       'discount':vals['discount'],
                       'net_total':vals['net_total'],
                       'reconcile':vals['reconcile']
                       })   
        return {'value':vals}
    
    def onchange_discount(self, cr, uid, ids,total,discount):
        vals = {}
        
        print "ids disc::",ids
        if discount > total:
            vals['paid_amount'] = 0
            vals['discount'] = 0
            vals['net_total'] = total
            vals['reconcile'] = False
        elif discount == total: 
            vals['paid_amount'] = 0
            vals['net_total'] = total- discount
            vals['reconcile'] = True
            vals['discount'] = discount
        elif  discount < total:
            vals['paid_amount'] = total - discount
            vals['net_total'] = total- (discount+vals['paid_amount'])
            vals['discount'] = discount
            vals['reconcile'] = True         
        update_lines = self.pool.get('smsfee.receiptbook.lines').write(cr, uid, ids, {
                       'paid_amount':vals['paid_amount'],
                       'discount':vals['discount'],
                       'net_total':vals['net_total'],
                       'reconcile':vals['reconcile']
                       })   
        return {'value':vals}
    
    _name = 'smsfee.feereturn.lines'
    _description = "This object store fee types"
    _columns = {
        'name': fields.many2one('smsfee.receiptbook','Paid Receipt No'),
        'parent_obj_id': fields.many2one('smsfee.return.paid.fee','Parent'),      
        'paid_fee_type': fields.many2one('smsfee.studentfee','Student Fee Id'),
        'fee_month': fields.many2one('sms.session.months','Fee Month'),
        'receipt_book_id': fields.many2one('smsfee.receiptbook','Receipt book',required = True),
        'paid_amount':fields.integer('Fee Paid'),
        'return_amount':fields.integer('late Fee'),
        'total':fields.integer('Net'),
    }
    _sql_constraints = [  
        ('Fee Exisits', 'unique (parent_obj_id)', 'Fee Receipt No Must be Unique!')
    ] 
    _defaults = {}
smsfee_receiptbook_lines()
##########
class smsfee_student_return_fee(osv.osv):
    """This object defines students' return fee process."""
 
    def set_no(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        count = 0
        records =  self.browse(cr, uid, ids, context)
        
        for f in records:
            sql =   """SELECT count(*) FROM smsfee_student_return_fee where state !='Draft'
                     """
            cr.execute(sql)
            count = cr.fetchone()[0]
            if count is None:
                count = int(count) + 1   
                 
        result[f.id] = count
        return result
    
    def submit_request(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            self.write(cr, uid, ids, {'state':'Waiting_Approval','request_by':uid})
        return result
    
    def approve_request(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            std_cls_id = self.pool.get('sms.academiccalendar.student').search(cr, uid, [('std_id','=',f.student.id),('name','=',f.student_class.id)]) 
            if std_cls_id:
                return_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                            'student_id':f.student.id,
                                            'acad_cal_id': f.student_class.id,
                                            'acad_cal_std_id': std_cls_id[0],  
                                            'date_fee_charged':datetime.date.today(),
                                            'returned_amount':f.return_amount,
                                            'state':'fee_returned',
                                            'reconcile':True})
                
                if return_fee:
                    self.write(cr, uid, ids, {'state':'Approved','return_date':datetime.date.today(),'approved_by':uid})
        return result
    
    def reject_request(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            self.write(cr, uid, ids, {'state':'Rejected','return_date':datetime.date.today(),'approved_by':uid})
        return result
    
    def set_to_draft(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            self.write(cr, uid, ids, {'state':'Draft'})
        return result
    

    def onchange_student(self, cr, uid,ids,student_id):
        result = {}
        print "student_id##########:" ,student_id
        
        if student_id:

            sql =   """SELECT sum(fee_amount) FROM smsfee_studentfee
                     WHERE student_id ="""+str(student_id)+"""  AND reconcile=True"""
            cr.execute(sql)
            paid_amount = cr.fetchone()[0]
            if paid_amount is None:
                paid_amount = '0'
            else:       
                result['total_paid'] = paid_amount
            update_data = self.pool.get('smsfee.student.return.fee').write(cr, uid, ids, {'total_paid':paid_amount})
        else:
            
            warning = {
                       'title': 'Warning!',
                       'message' : 'You must select a student!'
                      }
            
            return {'warning': warning}
        return {'value':result}

    def onchange_total_return(self, cr, uid, ids,return_amount,total_paid):
        result = {}
        print "ids::",ids
        
        if return_amount > total_paid:
            result['return_amount'] = 0
            warning = {
                       'title': 'Warning!',
                       'message' : 'Amount To Return cannot exceed Total Amount Paid!'
                      }
            self.pool.get('smsfee.student.return.fee').write(cr, uid, ids, {'return_amount':0})#this line will ensure that when warning is prompted the value of return_amount will still be 0
            return {'warning': warning, 'value':result}
        
        else: 
            result['return_amount'] = return_amount
                    
        update_data = self.pool.get('smsfee.student.return.fee').write(cr, uid, ids, {
                       'return_amount':result['return_amount'],
                       })   
        return {'value':result}
    
    _name = 'smsfee.student.return.fee'
    _description = "defines return fee process"
    _columns = {
        'name':fields.function(set_no, method=True, string='No.', store=True, type='char', size=300),
        'student_class':fields.many2one('sms.academiccalendar','Class', required = True,),      
        'student': fields.many2one('sms.student','Student', domain="[('current_class','=',student_class),('state','in',['Admitted','admission_cancel','drop_out','slc'])]", required=True),
        'total_paid': fields.float('Total Amount Paid', readonly=True),
        'request_date': fields.date('Date'),
        'request_by': fields.many2one('res.users','Requested By'),
        'approved_by': fields.many2one('res.users','Aprov/Reject By'),
        'return_amount': fields.float('Amount to Return',required=True),
        'return_reason': fields.text('Reason',required=True),
        'return_date': fields.date('Date', required=True),
        'state': fields.selection([('Draft', 'Draft'),('Waiting_Approval', 'Waiting Approval'),('Approved', 'Approved'),('Rejected', 'Rejected')], 'State', required=True, readonly=True),
        'counter': fields.integer('Counter'),
    } 
    _defaults = {
                 'state':'Draft'
                  }
        

smsfee_student_return_fee()


