from openerp.osv import fields, osv
from openerp import tools
from openerp import addons
from calendar import monthrange
from datetime import date, datetime
import datetime
import time
import xlwt
import xlrd
import math

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
    'fee_report_type':fields.selection([('One_on_One','One Student Per Page'),('Two_on_One','Two Students Per Page')],'Fee Report Type'),
    'bank_name1':fields.char('Bank Name', size=256),
    'bank_name2':fields.char('Bank Name', size=256),
    'bank_acctno1':fields.integer('Account Number'),
    'bank_acctno2':fields.integer('Account Number'),
    }
    _defaults = {
    }
res_company()


class sms_fee_challan_no(osv.osv):
    """this object sore challan no of all challans in receobppk, transport challans etc."""
    _name = 'sms.fee.challan.no'
    _columns = {
    'parent_obj_id': fields.integer('Parent ID'),
    'parent_object': fields.char('Parent_obj'),
    'module': fields.char('Module'),
    'year': fields.char('Year'),
    }
    _defaults = {
    }
sms_fee_challan_no()

class sms_student_class_promotion(osv.osv):
    """the objects adds fee portion in student promotion process of sms module last update 26-8-2016"""
    _name = 'sms.student.class.promotion'
    _inherit ='sms.student.class.promotion'
    _columns = {
         'applicable_fees': fields.many2many('smsfee.feetypes', 'sms_promotion_fee_rel', 'promotion_id', 'feetype_id', 'Applicable Fee', required=True),
    }
    _defaults = {
    }
sms_student_class_promotion()



#session monnths inherited

class sms_session_months(osv.osv):
    """
    This object is inherited to keep some fields in session month related fees
    """
    def update_monthly_feeregister(self, cr, uid, ids, name):
        print "update fee register called:"
        for f in self.browse(cr, uid, ids):
            parent_session_id = f.session_id.id
            #search all classes in this session
            classes_ids = self.pool.get('sms.academiccalendar').search(cr,uid,[('session_id','=',parent_session_id)])
            print "classes found ",classes_ids
            if classes_ids:
                rec_classes = self.pool.get('sms.academiccalendar').browse(cr, uid, classes_ids)
                
                for cur_cls in rec_classes:
                    #search all fee structures in this class
                    fees_ids = self.pool.get('smsfee.classes.fees').search(cr,uid,[('academic_cal_id','=',cur_cls.id)])
                    if fees_ids:
                        rec_fees = self.pool.get('smsfee.classes.fees').browse(cr, uid, fees_ids)
                        print "class fee types ",rec_fees
                        for fee in rec_fees:
                        # search all feetypes in this fs of thi class
                            ft_list = []
                            fee_types_ids = self.pool.get('smsfee.classes.fees.lines').search(cr,uid,[('parent_fee_structure_id','=',fee.id)])
                            print "fee lines ",fee_types_ids
                            if fee_types_ids:
                                rec_fee_types = self.pool.get('smsfee.classes.fees.lines').browse(cr,uid,fee_types_ids)
                                #now search all students for this class and this fee strucutre
                                print "class ",cur_cls.id
                                print "fee str ",fee.fee_structure_id.id
                               
                                
                                students_ids = self.pool.get('sms.student').search(cr,uid,[('fee_type','=',fee.fee_structure_id.id),('current_class','=',cur_cls.id),('state','=',"Admitted")])
                                print "student found ",students_ids
                                if students_ids:
                                   for this_ft in rec_fee_types:
                                       #check if fee is monthly fee then continue
                                       if this_ft.fee_type.subtype == 'Monthly_Fee': 
                                           for this_student in students_ids:
                                               #call method to add this fee to student
                                               call = self.pool.get('smsfee.studentfee').insert_student_monthly_non_monthlyfee(cr, uid, this_student, cur_cls.id, this_ft, f.id)
                                               
                    #Update fee register object for this month 
                    # search if this month already exists then leav, otherwise create new record
                    register_id = self.pool.get('smsfee.classfees.register').search(cr,uid,[('academic_cal_id','=',cur_cls.id),('month','=',f.id)])
                    if not register_id:
                        fee_register = self.pool.get('smsfee.classfees.register').create(cr,uid,{
                                                            'academic_cal_id':cur_cls.id,                                                       
                                                            'month':f.id, 
                                                                })
            self.write(cr,uid,f.id,{'update_log':'Last update on:'+str(datetime.date.today()),'state':'Updated'})
        return 
    
    _name = 'sms.session.months'
    _description = "stores months of a session"
    _inherit = 'sms.session.months'
    _columns = {
        'update_log': fields.char('Year',size = 50),  
        'state':fields.selection([('To_Update','To Be Updated'),('Updated','Updated')],'State')
    } 
#     _sql_constraints = [('name_unique', 'unique (session_id,session_month_id)', """ Session month name must be Unique.""")]
sms_session_months()



class smsfee_festructure_revision(osv.osv):
    """This object is used to store annual fee structure. For each session there will be a fee Structure
       if 2 fs have same session, previous one will be closed"""
    
        
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            session_ = f.session_id.name.split('-')
            session_ = session_[0]
                 
            sql =   """SELECT count(*) FROM smsfee_festructure_revision
                             """
            cr.execute(sql)
            conunter = cr.fetchone()[0] +1+int(f.id)
            result[f.id] = "AFS"+str(session_) + "-"+str(conunter)
        return result
    
    def getsession_classes(self, cr, uid, ids, name):
        for f in self.browse(cr, uid, ids):
            result = self.write(cr, uid, f.id, {'state':'Get_Session_Classes'})
        return result
    
    def start_annual_fee_structure(self, cr, uid, ids,name):
        
        for f in self.browse(cr, uid, ids):
            classes_list = f.applied_onclasses
            #1: Seach all fee structures in this annual revisions
            anfs_fs_ids = self.pool.get('sms.revision.line.feestructure').search(cr,uid,[('parent_annaul_fs_id','=',f.id)])
            if anfs_fs_ids:
                rec_anfs_fs = self.pool.get('sms.revision.line.feestructure').browse(cr,uid,anfs_fs_ids)
                
                for this_fs in rec_anfs_fs:
                    for this_class in classes_list:
                        #check if this fee structure for this class is already exists
                        class_fees_id = self.pool.get('smsfee.classes.fees').search(cr,uid,[('fee_structure_id','=',this_fs.name.id),('academic_cal_id','=',this_class.id)])
                        if class_fees_id:
                            #Great, this fee structure already exists in selected class
                            # now loop on revisionlines feetypes and search each fee type in classes fees lines, if exists update with new amount
                            anfs_ftypes_ids = self.pool.get('sms.revision.line.feetypes').search(cr,uid,[('revisionline_fs_id','=',this_fs.id)])
                            if anfs_ftypes_ids:
                                rec_anfs_ftypes = self.pool.get('sms.revision.line.feetypes').browse(cr,uid,anfs_ftypes_ids)
                                for this_ft in rec_anfs_ftypes:
                                    # call method to search classes_fee_lines for checking if feetype exist then upload 
                                    # with new amount other wise create new ft in fee lines
                                    print "before call:class_fees_id[0]:",class_fees_id[0]
                                    print "fee str id:",this_ft.amount
                                    explore_ftypes = self.pool.get('smsfee.classes.fees').update_if_exists_or_create_ft(self, cr, uid, class_fees_id[0], this_ft.name.id,this_ft.amount)
                        else:
                            # fee strcuture doesenot exists in smsfee.classes.fees
                            # create this fs in classes fees
                            # and its children in feeslines
                            #1: Call method to create fs 
                            print "before call:::::"
                            print "fs id:",this_fs.name.id
                            print "class_id:", this_class.id
                            new_fs = False
#                             new_fs = self.pool.get('smsfee.classes.fees').create_new_fs_in_classes_fees(self, cr, uid, this_fs.name.id, this_class.id)
                            if new_fs:
                                #create its children by calling the method update_if_exists_or_create_ft
                                #loop on this revision line fstruecure nad get its its chldren i.e feetypes
                                #when revisionlnes ft are get, loop on this and call update_if_exists_or_create_ft        
                                # call method to search classes_fee_lines for checking if feetype exist then upload
                                anfs_ftypes_ids = self.pool.get('sms.revision.line.feetypes').search(cr,uid,[('parent_annaul_fs_id','=',this_fs.id)])
                                if anfs_ftypes_ids:
                                    rec_anfs_ftypes = self.pool.get('sms.revision.line.feetypes').browse(cr,uid,anfs_fs_ids)
                                    for this_ft in rec_anfs_ftypes:
                                        # with new amount other wise create new ft in fee lnes
                                        new_ftypes = self.update_if_exists_or_create_ft(self, cr, uid, this_fs.name.id, this_ft.name.id,this_ft.amount)
        return 
    
    def close_annual_fee_structure(self, cr, uid, ids, name, args, context=None):
        print "starting method is called"
        for f in self.browse(cr, uid, ids, context=context):
            result = self.write(cr, uid, f.id, {'state':'Closed','effective_till':datetime.datetime.now()})
        return result
    
    _name = 'smsfee.festructure.revision'
    _columns = {
    'name':fields.function(_set_name, method=True,  string='Class Fee',type='char'),
    'session_id':fields.many2one('sms.session', 'Session'),
    'fee_str_ids':fields.one2many('sms.revision.line.feestructure','parent_annaul_fs_id','Fee Structure'),
    'applied_onclasses':fields.many2many('sms.academiccalendar','sms_academiccalendar_sms_fee_revision','academiccalendar_id','fee_revision_id','Applied On Classes'),
    'effective_from':fields.datetime('Effective From'),
    'effective_till':fields.datetime('Effective till'),
    'state':fields.selection([('Draft','Draft'),('Get_Session_Classes','Pick Classes'),('Active','Active'),('Closed','Closed')],'Status',readonly=True),
    }
    _defaults = {'state':'Draft'}
smsfee_festructure_revision()

class sms_revision_line_feestructure(osv.osv):
    """This object appear as child object to sms_fee_structure_revision .
       This tabl has further one child table sms_rervision_lines_feetypes"""
   
    _name = 'sms.revision.line.feestructure'
    _columns = {
    'name': fields.many2one('sms.feestructure','Fee Structure'),      
    'parent_annaul_fs_id': fields.many2one('smsfee.festructure.revision', 'Annaul Fee Register', ondelete="cascade"),
    'fee_types_ids': fields.one2many('sms.revision.line.feetypes','revisionline_fs_id','Fee Type'),
    }
    _sql_constraints = [('Class_fsunique', 'unique (name,annaul_fs_id)', """ Fee Structure is already Defined Remove Duplication..""")]
    _defaults = {
    }
sms_revision_line_feestructure()

class sms_revision_line_feetypes(osv.osv):
    """This object appear as child object to sms_revision_line_feestructure .
       """
    _name = 'sms.revision.line.feetypes'
    _columns = {
        'name': fields.many2one('smsfee.feetypes','Fee Type'),
        'revisionline_fs_id':fields.many2one('sms.revision.line.feestructure','Parent FS'), 
        'amount':fields.float('Amount')     
    }
    _sql_constraints = [('Class_ft_unique', 'unique (name,revisionline_fs_id)', """ Fee Structure is already Defined Remove Duplication..""")]
    _defaults = {
    }
sms_revision_line_feetypes()




class sms_academiccalendar(osv.osv):
    """This object is used to add fields in sms_academiccalendar"""
   
#     def manage_class_fee(self, cr, uid, ids, context=None):
#         fee_obj = self.pool.get('smsfee.classes.fees')
#         fee_line_obj = self.pool.get('smsfee.classes.fees.lines')
#         #get all fee structures to add with class
#         all_fee_structure_ids = self.pool.get('sms.feestructure').search(cr,uid,[])
#         #get all fee types to add with newly created class fs later on
#         all_fee_types_ids = self.pool.get('smsfee.feetypes').search(cr,uid,[])
#        
#         for f in self.browse(cr, uid, ids):
#             acad_cal_id = f.id
#                         
#             for fee_str in all_fee_structure_ids:
#                 fees_str_id =fee_str[0]
#                 #stpe1: First search if fee structure already exists
#                 fs_exists = fee_obj.check_feestructure_exists_in_class(cr, uid,acad_cal_id, fees_str_id)
#                 
#                 if not fs_exists:
#                     # step2: create an entry in smsfee.classesfees object
#                     class_fee_str_id = fee_obj.add_new_feestructure_classes_fees(cr, uid,acad_cal_id, fees_str_id)
#                   
#                     if class_fee_str_id:
#                         
#                         if all_fee_types_ids:
#                             for fee_type in all_fee_types_ids:
#                                  amount = 0
#                                  #sarch previous class fee
#                                  ft_already_exists = fee_line_obj.check_feetype_exists_in_class(cr, uid, class_fee_str_id,fee_type[0])
#     
#                                  if not ft_already_exists:
#                                      # create new fee type in classes fee lines ad child of newly created fee structure
#                                      ft_created = fee_line_obj.add_new_feetype_classfee_lines(cr, uid, class_fee_str_id,fee_type[0])
#                     
#                 else:
#                     #it means fee structure already existed, now when fee structure already exists
#                     # check all fee types if not exists with this fs, then add one
#                     for fee_type in all_fee_types_ids:
#                         # check classes fees with old few structure id and all feetypes,  
#                         ft_already_exists = fee_line_obj.check_feetype_exists_in_class(cr, uid, fs_exists[0],fee_type[0])
#                         if not ft_already_exists:
#                             # create new fee type in fees lines as child of old fee strucutre
#                             ft_created = fee_line_obj.add_new_feetype_classfee_lines(cr, uid, fs_exists[0],fee_type[0])         
#                     else:
#                         raise osv.except_osv(('Please Define fee Types'),('Fee Types & Fee Structure both are needed for lass Fee Management'))
#         return                
   
    def _calculate_class_forecasted_fee(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             total_forecasted = 0
             register_ids = self.pool.get('smsfee.classfees.register').search(cr,uid,[('academic_cal_id','=',ids)])
             if register_ids:
                 rec_register = self.pool.get('smsfee.classfees.register').browse(cr,uid,register_ids)
                 for register in rec_register:
                     total_forecasted = total_forecasted + register.month_forcasted_fee 
                 result[f.id] = total_forecasted
        return result  
    
    def _calculate_class_paid_fee(self, cr, uid, ids, name, args, context=None):
         #this query will be changed when function for fee reurned is included
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             total_paid = 0
             register_ids = self.pool.get('smsfee.classfees.register').search(cr,uid,[('academic_cal_id','=',ids)])
             if register_ids:
                 rec_register = self.pool.get('smsfee.classfees.register').browse(cr,uid,register_ids)
                 for register in rec_register:
                     total_paid = total_paid + register.month_fee_received 
                 result[f.id] = total_paid
        return result
    
    def _calculate_calculate_recovery(self, cr, uid, ids, name, args, context=None):
         #this query will be changed when function for fee reurned is included
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             if f.class_forcasted_fee:
                 recovery = math.ceil((f.class_fee_received*100)/f.class_forcasted_fee)
             else:
                 recovery = 0
             result[f.id] = str(recovery)+"%"
        return result
    
    _name = 'sms.academiccalendar'
    _inherit ='sms.academiccalendar'
    
    
    
    _columns = {
            'fee_structures':fields.one2many('smsfee.classes.fees','academic_cal_id','Fee Structure'),
            #new class fee object, aobve one will be deleted
          #  'fee_update_till':fields.many2one('sms.session.months','Fee Updated Till'),
            'fee_update_till':fields.many2one('sms.session.months',' Fee Starts From Month'),
            'fee_register':fields.one2many('smsfee.classfees.register','academic_cal_id','Register'),
            'class_forcasted_fee':fields.function(_calculate_class_forecasted_fee, method=True,  string='Fee Forecasted',type='float'),
            'class_fee_received':fields.function(_calculate_class_paid_fee, method=True,  string='Fee Received',type='float'),
            'recovery_ratio':fields.function(_calculate_calculate_recovery, method=True,  string='Recovery(%)',type='char'),
            'annaul_fs_id':fields.many2one('smsfee.festructure.revision','Annual Fee Register'),
    }
       
sms_academiccalendar()


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
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            sql =   """SELECT  COALESCE(sum(fee_amount),'0')  FROM smsfee_studentfee
                     WHERE student_id ="""+str(ids[0])+"""  AND state='fee_unpaid'"""
            cr.execute(sql)
            amount = float(cr.fetchone()[0])
        result[f.id] = amount
        return result
    
    def set_paid_amount(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        records =  self.browse(cr, uid, ids, context)

        for f in records:
            sql =   """SELECT COALESCE(sum(fee_amount),'0')  FROM smsfee_studentfee
                     WHERE student_id ="""+str(ids[0])+"""  AND state='fee_paid'"""
            cr.execute(sql)
            amount = float(cr.fetchone()[0])
        result[f.id] = amount
        return result

        
    _name = 'sms.student'
    _inherit ='sms.student'
        
    _columns = {
            'studen_fee_ids':fields.one2many('smsfee.studentfee', 'student_id','Student Fee'),
            'latest_fee':fields.many2one('sms.session.months','Fee Register'),
            'total_paybles':fields.function(set_paybles, method=True, string='Paybles', type='float', size=300),
            'total_paid_amount':fields.function(set_paid_amount, method=True, string='Total Paid', type='float', size=300),

    }
sms_student()


class smsfee_classes_fees(osv.osv):
    
    """ all Fee Structures for an academic calendar
        new object (smsfee_classes_fees_structure) is associated with academic calendar
        this object is updated according to new fee strucrure and classes"""
    
    
    def get_company(self, cr, uid, ids, context=None):
        cpm_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.id
        company = self.pool.get('res.company').browse(cr,uid,uid).name
        return company
    
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
    
    def update_if_exists_or_create_ft(self, cr, uid,ids, parent_fs, fee_type,amount):
        print "in create new ft:parent fs:",parent_fs
        print "ft:",fee_type
        print "amount",amount
        #this method search for a particular fee type(smsfee.feetype.id) in smsfee_classes_fees_lines
        # if record found, update it with new amount other wise create new ft, under classes_fees_id as parent
        #search of feetypes in classes_fees_lines begins here
        cls_fees_line_id = self.pool.get('smsfee.classes.fees.lines').search(cr,uid,[('parent_fee_structure_id','=',parent_fs),('fee_type','=',fee_type)])
        if cls_fees_line_id:
            #so fee type also exists, dont worry, update it with new values of revision fs lines feetypes
            # 2linds of changes, one is to change only amount , while fee type remains the same
            #2nd change is change fee type id, it needs more discussion, leave it to future
            update_fee_line_ft = self.pool.get('smsfee.classes.fees.lines').write(cr, uid, cls_fees_line_id[0], {'amount':amount})
        else:
            # this fee type doesnot exists in feelines object
            #seems this fee types is newly added to fee revision object
            # now add this fee type to actual smsfee.classes.fee.lines
            new_ft = self.pool.get('smsfee.classes.fees.lines').create(cr,uid,{
                    'parent_fee_structure_id': parent_fs,#obtained from searching classes fees
                    'fee_type': fee_type,#obtained from revision fetypes object. new ft is added, 
                    'amount':fee_type,#obtained from revision fetypes object.
                                                                        
                    })
            #
        
        return #result

    def forcasted_amount(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            total = 0
            lines_ids = self.pool.get('smsfee.classes.fees.lines').search(cr,uid,[('parent_fee_structure_id','=',f.id)])
            for line in lines_ids: 
                
                 sql = """SELECT COALESCE(sum(fee_amount),'0') from smsfee_studentfee
                          WHERE fee_type = """+str(line)
                 cr.execute(sql)
                 row = cr.fetchone()
                 total = total + row[0]
                 result[f.id] = total 
        return result
    
    def collected_amout(self, cr, uid,ids, name, args, context=None):
        result = {}
        total = 0
        for f in self.browse(cr, uid, ids, context=context):
            lines_ids = self.pool.get('smsfee.classes.fees.lines').search(cr,uid,[('parent_fee_structure_id','=',f.id)])
            for line in lines_ids: 
                
                 sql = """SELECT COALESCE(sum(paid_amount),'0') from smsfee_studentfee
                          WHERE fee_type = """+str(line)+""" AND reconcile = True and state = 'fee_paid'"""
                 cr.execute(sql)
                 row = cr.fetchone()
                 total = total + row[0]
            result[f.id] = total
        return result
    
    def get_fs_std_qty(self, cr, uid,ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             sql = """SELECT COALESCE(count(id),'0') from sms_student
                      WHERE current_class = """+str(f.academic_cal_id.id)+""" AND fee_type = """+str(f.fee_structure_id.id)
             cr.execute(sql)
             row = cr.fetchone()
             result[f.id] = int(row[0])
        return result 

    
    
    _name = 'smsfee.classes.fees'
    _inherit ='smsfee.classes.fees'
   
    _description = "Stores classes fee"
    _order = "fee_structure_id"
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Class Fee',type='char'),
        'fee_type_ids': fields.one2many('smsfee.classes.fees.lines','parent_fee_structure_id','Fee Type'),
        'active':fields.boolean('Active'),
        'academic_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar',required = True),      
        'fee_structure_id': fields.many2one('sms.feestructure','Fee Structure',required = True),
        'no_of_students':fields.function(get_fs_std_qty, method=True,  string='Applies on (#Students)',type='integer'),
        'focasted_amount':fields.function(forcasted_amount, method=True,  string='Forcasted',type='float'),
        'collected_amout':fields.function(collected_amout, method=True,  string='Collection',type='float'),
    }
    _sql_constraints = [('Class_fee_unique', 'unique (academic_cal_id,fee_structure_id,fee_type_id)', """ Class Fee is already Defined Remove Duplication..""")]
smsfee_classes_fees()


class smsfee_classes_fees_lines(osv.osv):
    
    """ all smsfee_classes_fees_types for an academic calendar new format
        this aject appear s one2many with smsfee.classes.fees """
    
    def create(self, cr, uid, vals, context=None, check=True):
         result = super(osv.osv, self).create(cr, uid, vals, context)
#          for obj in self.browse(cr, uid, context=context):
         return result
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        
       
        for f in self.browse(cr, uid, ids, context=context):
            
            ##################################################################################################################
            for k,v in vals.iteritems():
                print k,v
                sql = """ select """ +str(k)+ """ from  smsfee_classes_fees_lines where id="""+str(f.id)
                cr.execute(sql)
                pre_val = cr.fetchone()[0]
                self.pool.get('project.transactional.log').create_transactional_logs( cr, uid,vals,'smsfee.classes.fees.lines','write',pre_val)
            ####################################################################################################################
            if 'amount' in vals:
            
                fee_std_ids=  self.pool.get('smsfee.studentfee').search(cr,uid,[('fee_type','=',f.id),('state','=','fee_unpaid')])
                for fee in fee_std_ids:
                    update_std_fee_obj = self.pool.get('smsfee.studentfee').write(cr, uid, fee,{'fee_amount':vals['amount'] })
                    
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
    
    def _set_name(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             ftyp = f.fee_type.name
             result[f.id] = str(ftyp)
        return result
    
    
    def check_feetype_exists_in_class(self, cr, uid, ids, parent_fs_id, feetype):
        """this method check if a feetype i.e a feelines exists in a class, if it exists 
           will return true otherwise false"""
        
        ft_exists = self.search(cr,uid,[('parent_fee_structure_id','=',parent_fs_id),(('parent_fee_structure_id','=',feetype))])
        if ft_exists:
            return True
        else:
            return False
        
    def add_new_feetype_classfee_lines(self, cr, uid, ids, parent_fs_id, feetype):
        """this method add new fee type to smsfee.classes.fees.lines """
        
        new_ft = self.create(cr,uid,{'parent_fee_structure_id':parent_fs_id,'fee_type':feetype,'amount':0})
        if new_ft:
            return True
        else:
            return False
    
    _name = 'smsfee.classes.fees.lines'
   
    _description = "Stores classes fee"
    _order = "fee_type"
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Class Fee',type='char'),
        'parent_fee_structure_id': fields.many2one('smsfee.classes.fees','Fee Structure'),
        'fee_type': fields.many2one('smsfee.feetypes','Fee Type',required = True),
        'amount':fields.float('Amount'),
    }
    _sql_constraints = [('Class_fee_unique', 'unique (parent_fee_structure_id,fee_type)', """ Class Fee is already Defined Remove Duplication..""")]
smsfee_classes_fees_lines()



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
             sql = """SELECT COALESCE(sum(fee_amount),'0')  from smsfee_studentfee
                      WHERE due_month = """+str(f.month.id)+"""
                      AND acad_cal_id="""+str(f.academic_cal_id.id)
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
                      WHERE due_month = """+str(f.month.id)+"""
                      AND acad_cal_id="""+str(f.academic_cal_id.id)+"""
                      AND reconcile = True"""
             cr.execute(sql)
             amount = cr.fetchone() 
             if amount:
                 result[f.id] = float(amount[0]) 
             else:
                 result[f.id] = float(amount[0])
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
        'month_forcasted_fee':fields.function(_set_forcasted_fee, method=True,  string='Forcasted',type='float'),
        'month_fee_received':fields.function(_set_paid_fee, method=True,  string='Received',type='float'),
    }
smsfee_classfees_register()



class smsfee_feetypes(osv.osv):
    """ all Fee Types """
    
    
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
        'fs_id':fields.many2one('sms.feestructure'),      
        'description': fields.char(string = 'Description',size = 100),
        'subtype': fields.selection([('Monthly_Fee','Monthly Fee'),('at_admission','Charged at The Time of Admission'),('Promotion_Fee','Promotion Fee'),('Annual_fee','Annual Fee'),('Refundable','Refundable'),('Other','Other')],'Fee Category',required = True),
    }
    _sql_constraints = [  
        ('Fee Exisits', 'unique (name)', 'Fee Already exists!')
    ] 
smsfee_feetypes()

class smsfee_studentfee(osv.osv):
    
    
    """ Stores student fee record"""
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        #*00*************create log for updation in student fee**************************
        for k,v in vals.iteritems():
            sql = """ select """ +str(k)+ """ from smsfee_studentfee where id ="""+str(ids)+ """
            """
            cr.execute(sql)
            pre_val = cr.fetchone()[0]
            dict={k:v}
            self.pool.get('project.transactional.log').create_transactional_logs( cr, uid,dict,'smsfee_studentfee','write',pre_val)
        #-----------------------------------------------------
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
    
    def _set_std_fee(self, cr, uid, ids, fields,args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            if f.fee_type.fee_type.subtype == 'Monthly_Fee':
                month_name = f.fee_month.name.split('-')[0]
                year = f.fee_month.name.split('-')[1]
                string =  str(f.fee_type.name)+ " ("+str(month_name[:3].upper())+","+str(year)+")"
            else:
                string = f.fee_type.name
            result[f.id] = string
        return result
    
    def get_student_total_paybles(self, cr, uid, ids, acad_std_id,context=None):
        
        sql = """SELECT COALESCE(sum(net_total),'0') FROM smsfee_studentfee WHERE student_id ="""+str(ids)+"""
        AND acad_cal_std_id="""+str(acad_std_id)+"""AND net_total > 0 AND state= 'fee_unpaid'"""
        cr.execute(sql)
        bal = cr.fetchone()
        return bal[0]
    
    def insert_student_monthly_non_monthlyfee(self, cr, uid, std_id, acad_cal, fee_type_row, month):
        """This method will insert student monthly and non monthly fee 
           only when called in loop or without loop (admit student,re-admit student,student promotion and other wizards wlil call it)
           Currently called by 
           1) update_monthly_feeregister() class:sms_session_months
           2) called by admission register
           3)called by promotion process
           4) called by advance fee management
           
           admin
           """
        fee_already_exists =  self.pool.get('smsfee.studentfee').search(cr, uid,[('acad_cal_id', '=', acad_cal), ('student_id', '=', std_id), ('fee_type', '=', fee_type_row.id), ('due_month', '=', month)])
        
        if not fee_already_exists:
            # at this stage is assued that fee month and dues month are same for all cases, due month may change in exceptional cases, i.e when fee of all prevoius
            #month is registered in current month against a student, this case due month for all fees will be current month to avoid fine,
            fee_month = month
            due_month = month
            fee_dcit= {
                        'student_id': std_id,
                        'acad_cal_id': acad_cal,
                        'fee_type': fee_type_row.id,
                        'date_fee_charged':datetime.date.today(),
                        'due_month': due_month,
                        'fee_month': fee_month,
                        'paid_amount':0,
                        'fee_amount': fee_type_row.amount,  
                        'late_fee':0,  
                        'total_amount':fee_type_row.amount + 0, 
                        'reconcile':False,
                         'state':'fee_unpaid'
                        }
            
            crate_fee = self.pool.get('smsfee.studentfee').create(cr,uid,fee_dcit)  
            if crate_fee:
                return True
            else:
                return False  
    
    def add_fee_student(self ,cr ,uid ,ids ,context):
        acd_cal_stu_id = self.pool.get('sms.academiccalendar.student').search(cr ,uid ,[('name','=',context['acd_cal_id']),('std_id','=',context['student_id'] )])
        adm_regis_id = self.pool.get('student.admission.register').search(cr ,uid ,[('name','=',context['student_id']),('student_class','=',context['acd_cal_id']),('fee_structure','=',context['fee_structure'])])
        for fees_id in self.pool.get('student.admission.register').browse(cr,uid,adm_regis_id):
            for t in fees_id.fee_id:
                class_fee_id = t.stu_fee_id.parent_fee_structure_id.id
                fee_type = t.stu_fee_id.fee_type.subtype
                fee_type_id = t.stu_fee_id.fee_type.id
                amount = t.stu_fee_id.amount
        #************************************************************************#
                if class_fee_id:
                    late_fee = 0

                    if fee_type == 'Monthly_Fee':
                        insert_monthly_fee = self.pool.get('smsfee.studentfee').insert_student_monthly_fee(cr,uid,context['student_id'],acd_cal_stu_id[0],context['acd_cal_id'],context['month'],class_fee_id,fee_type_id,amount)
                    else:
                        studentfee_id = self.pool.get('smsfee.studentfee').create(cr,uid,{
                        'student_id': context['student_id'],
                        'acad_cal_id': int(context['acd_cal_id']),               
                        'acad_cal_std_id': acd_cal_stu_id[0],
                        'fee_type': class_fee_id , 
                        'generic_fee_type':fee_type_id,
                        'date_fee_charged':datetime.date.today(),
                        'due_month': context['month'],  
                        'fee_amount': amount,
                        'paid_amount':0,
                        'late_fee':0,
                        'total_amount':amount + late_fee,
                        'reconcile':False,
                        'state':'fee_unpaid'
                        })
                else:
                    raise osv.except_osv(('Alert '), ('Fee May be defined but not set for New Class.'))
        return None
        
    def _get_total_payables(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             result[f.id] = f.late_fee + f.fee_amount
        return result
    
    def onchange_set_domain(self, cr, uid,ids,fee_type):
        #********************inprogress still have to do stuff******************************************
#         rec = self.browse(cr ,uid ,ids)
#         print "rec==",rec
#         fee_struct = rec.student_id.fee_type.id  
#         cls_fee_id = self.pool.get('smsfee.classes.fees').search(cr ,uid ,[('fee_structure_id','=',fee_struct)])
#         val = [i.id for i in self.pool.get('smsfee.classes.fees').browse(cr ,uid ,cls_fee_id)]
#         print "val===",val
#         #cls_fee_lines_id = self.pool.get('smsfee.classes.fees.lines').search(cr ,uid ,[('parent_fee_structure_id','=',cls_fee_id)])
#         #print fee_struct,"******",cls_fee_id,"******",cls_fee_lines_id
#         return {'domain': {'fee_type': [('parent_fee_structure_id', 'in', cls_fee_id)]} }   
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
        'fee_type':fields.many2one('smsfee.classes.fees.lines','Fee Type'),
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
        'state':fields.selection([('fee_exemption','Fee Exemption'),('fee_unpaid','Fee Unpaid'),('fee_paid','Fee Paid'),('fee_returned','Fee Returned'),('Deleted','Deleted')],'Fee Status',readonly=True),
        #------------total payables---------------------------------
        'total_payable': fields.function(_get_total_payables,string = 'Total Payable',type = 'integer',method = True,store = True),  
    }
     
    def get_student_class(self, cr, uid,context):
        if context:
            acd_cal_stu = self.pool.get('sms.academiccalendar.student').search(cr ,uid ,[('std_id','=',context['student_id'])])
            clss_id = self.pool.get('sms.academiccalendar').search(cr ,uid ,[('acad_cal_students','=',acd_cal_stu),('state','=','Active')])
            if clss_id:
                rec = self.pool.get('sms.academiccalendar').browse(cr ,uid ,clss_id)[0]
            return rec.id
        
    _defaults = {
        'reconcile': False,
        'student_id': lambda self, cr, uid, context: context.get('student_id', False),
        'acad_cal_id':get_student_class, 
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
        self.write(cr, uid, ids[0], {'state':'Rejected','decision_by':uid,'decision_date':datetime.datetime.today()})
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
    
    
    def _set_bill_no(self, cr, uid, parent_id, parent_object, module):
        create = self.pool.get('sms.fee.challan.no').create(cr, uid, {
                   'parent_obj_id': parent_id,
                   'parent_object':parent_object,
                   'module': module,
                   'receipt_book_id':module,
                   'year':'2017',
                   }) 
        return create
    
    def _get_bill_no(self, cr, uid, parent_id, parent_object, module):
        
        sql =   """SELECT  id  FROM sms_fee_challan_no where parent_obj_id = """+str(parent_id)
        cr.execute(sql)
        no = int(cr.fetchone()[0])
        return  str(no)+"-02"+str(2017)
        
    def create(self, cr, uid, vals, context=None, check=True):
         
        vals['name'] =  'slipno'
        result = super(osv.osv, self).create(cr, uid, vals, context)
        generate_slip_no = self._set_bill_no(cr, uid, result,'smsfee.receiptbook','smsfee')
        #get_slip_no = self._get_bill_no(cr, uid, result,'smsfee.receiptbook','smsfee')
        return result
  
     
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
     
    def unlink(self, cr, uid, ids, context=None):
         result = super(osv.osv, self).unlink(cr, uid, ids, context)
         return result 
    
    def unlink_lines(self, cr, uid, ids, *args):
        line_pool = self.pool.get('smsfee.receiptbook.lines')
        idss = line_pool.search(cr,uid, [('receipt_book_id','=',ids)])
        for id in idss:
            line_pool.unlink(cr,uid,id)
        return True
    
    def load_std_fee(self, cr, uid, ids, context=None):
        brows =   self.browse(cr, uid, ids, context)
        unlink = self.unlink_lines(cr, uid,ids[0],None)
        student = brows[0].student_id.id
        self.onchange_student(cr, uid, ids, None)
        self.write(cr, uid, ids[0], {'student_id':student,})    
       
        fee_ids = self.pool.get('smsfee.studentfee').search(cr, uid, [('student_id','=',student),('reconcile','=',0)])
            
        if fee_ids:
            total_recvble = 0
            for fees in fee_ids:
                late_fee = 0
                reconcile = False
                
                    
                obj = self.pool.get('smsfee.studentfee').browse(cr, uid, fees)
                if  obj.fee_amount == 0 or obj.fee_amount+late_fee ==0:
                    reconcile = True
                if brows[0].receive_whole_amount:
                    paid_fee =  obj.fee_amount+late_fee
                    reconcile = True
                else:
                    paid_fee = 0
                    
                    if  obj.fee_amount == 0 or obj.fee_amount+late_fee ==0:
                        reconcile = True
                    else:
                        reconcile = False
                total_recvble = total_recvble + obj.fee_amount 
                create = self.pool.get('smsfee.receiptbook.lines').create(cr, uid, {
                       'acad_cal_id': obj.acad_cal_id.id,
                       'fee_type':obj.fee_type.id,
                       'fee_month': obj.fee_month.id,
                       'receipt_book_id':ids[0],
                       'student_fee_id':obj.id,
                       'fee_amount': obj.fee_amount,
                       'total': obj.fee_amount+late_fee,
                       'paid_amount':paid_fee,
                       'reconcile':reconcile
                       }) 
            self.write(cr, uid, ids[0], {'state':'fee_calculated','total_paybles':total_recvble})
        return
    
    def confirm_fee_received(self, cr, uid, ids, context=None):
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
            
    def request_for_adjustment(self, cr, uid, ids, context=None):
        
        user = self.pool.get('res.users').browse(cr,uid,uid)
        note_str = "*** Paid Fee Adjustment Details ***"
        note_str += "\n\nFee Adjustment request Entered by "+str(user.name)+ "ON"+str(datetime.datetime.now()) +" \n"
        self.write(cr, uid, ids[0], {'state':'Request_Adjustment','note_at_receive':note_str})
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
    def _set_slipno(self, cr, uid, ids, name, ):
        rec =  self.browse(cr, uid, ids)
        return rec.id
    
    
    def _get_id(self, cr, uid, context={}):
        if context:
            if 'student_id' in context:
                return context['student_id']
        return None
    
    def set_recvbles(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            sql =   """SELECT  COALESCE(sum(fee_amount),'0')  FROM smsfee_receiptbook_lines
                     WHERE receipt_book_id ="""+str(f.id)
            cr.execute(sql)
            amount = float(cr.fetchone()[0])
            result[f.id] = amount
        return result
    
    def cancel_fee_bill(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            self.write(cr, uid, f.id, {'state':'Cancel','challan_cancel_by':uid})  
        return result
    
    def check_fee_challans_issued(self, cr, uid, class_id, student_id):
        result = {}
        fee_ids = self.pool.get('smsfee.studentfee').search(cr ,uid ,[('student_id','=',student_id),('state','=','fee_unpaid')])
        if fee_ids:
            challan_ids = self.pool.get('smsfee.receiptbook').search(cr, uid,
                                                                     [('student_id','=',student_id),
                                                                      ('student_class_id','=', class_id),
                                                                      ('state','=','fee_calculated')])
            if challan_ids:
                #---------------------- Get all unpaid amount receiveable from student -------------------------------------
                receipt_total_fee = []
                std_unpaid_fees = self.pool.get('smsfee.studentfee').browse(cr ,uid ,fee_ids)
                if std_unpaid_fees:
                    current_fee_amount = 0
                    for unpaidfee in std_unpaid_fees:
                        current_fee_amount = current_fee_amount + unpaidfee.fee_amount
                #---------------------- Get Unpaid Amount Appearing in the Cuurent Fee Receipt -----------------------------
                for recipt in self.pool.get('smsfee.receiptbook').browse(cr, uid, challan_ids):
                    tlt_line_fee = 0
                    for lines in recipt.receiptbook_lines_ids:
                        tlt_line_fee =tlt_line_fee + lines.total
                    receipt_total_fee.append(tlt_line_fee)
                #---------------------- if old_val is not equal to new_val than create reciept -----------------------------
                old_val = receipt_total_fee[-1]
                if old_val <= current_fee_amount:
                    total_paybles = 0
                    if type(student_id) is list:
                        student_id = student_id[0]
                    session_id = self.pool.get('sms.student').browse(cr, uid, student_id).current_class.acad_session_id.id
                    self.pool.get('smsfee.receiptbook').write(cr ,uid ,challan_ids, {'state':'Cancel'})
                    receipt_id = self.pool.get('smsfee.receiptbook').create(cr ,uid , {'student_id':student_id,
                                                                                     'student_class_id':class_id,
                                                                                     'state':'fee_calculated',
                                                                                     'receipt_date':datetime.date.today(),
                                                                                     'session_id' :session_id})
                    std_unpaid_fees = self.pool.get('smsfee.studentfee').browse(cr ,uid ,fee_ids)
                    if receipt_id:
                        for unpaidfee in std_unpaid_fees:
                            total_paybles = total_paybles + unpaidfee.fee_amount
                            feelinesdict = {
                            'fee_type': unpaidfee.fee_type.id,
                            'student_fee_id': unpaidfee.id,
                            'fee_month': unpaidfee.fee_month.id,
                            'receipt_book_id': receipt_id,
                            'fee_amount':unpaidfee.fee_amount,
                            'late_fee':0,
                            'total':unpaidfee.fee_amount}
                            self.pool.get('smsfee.receiptbook.lines').create(cr ,uid, feelinesdict)
                    
                else:
                    print "donot create challan"
            else:
                total_paybles = 0
                if type(student_id) is list:
                    student_id = student_id[0]
                session_id = self.pool.get('sms.student').browse(cr, uid, student_id).current_class.acad_session_id.id
                receipt_id = self.pool.get('smsfee.receiptbook').create(cr ,uid , {'student_id':student_id,
                                                                                  'student_class_id':class_id,
                                                                                  'state':'fee_calculated',
                                                                                  'receipt_date':datetime.date.today(),
                                                                                  'session_id' :session_id})
                std_unpaid_fees = self.pool.get('smsfee.studentfee').browse(cr ,uid ,fee_ids)
                if receipt_id:
                    for unpaidfee in std_unpaid_fees:
                        total_paybles = total_paybles + unpaidfee.fee_amount
                        feelinesdict = {
                        'fee_type': unpaidfee.fee_type.id,
                        'student_fee_id': unpaidfee.id,
                        'fee_month': unpaidfee.fee_month.id,
                        'receipt_book_id': receipt_id,
                        'fee_amount':unpaidfee.fee_amount,
                        'late_fee':0,
                        'total':unpaidfee.fee_amount}
                        self.pool.get('smsfee.receiptbook.lines').create(cr ,uid,feelinesdict)
        return True 


    _name = 'smsfee.receiptbook'
    _description = "This object store fee types"
    _columns = {
        'name': fields.char('Receipt No.',type = 'char'),      
        'receipt_date': fields.date('Date'),
        'session_id':fields.many2one('sms.academics.session', 'Session'),
        'fee_structure': fields.char(string = 'Fee Structure',size = 100),
        'manual_recpt_no': fields.char(string = 'Manual Receipt No',size = 100),
        'student_class_id': fields.many2one('sms.academiccalendar','Class'),
        'student_id': fields.many2one('sms.student','Student',required = True),
        'father_name': fields.char(string = 'Father',size = 100),
        'payment_method':fields.selection([('Cash','Cash'),('Bank','Bank')],'Payment Method'),
        'total_paybles':fields.function(set_recvbles,string = 'Total.',type = 'float',method = True), 
        'total_paid_amount':fields.float('Paid Amount',readonly = True),
        'note_at_receive': fields.text('Note'),
        'receive_whole_amount': fields.boolean('Receive Whole Amount'),
        'state': fields.selection([('Draft', 'Draft'),('fee_calculated', 'Open'),('Paid', 'Paid'),('Cancel', 'Cancel'),('Adjusted', 'Paid(Adjusted)')], 'State', readonly = True, help='State'),
        'fee_received_by': fields.many2one('res.users', 'Received By'),
        'challan_cancel_by': fields.many2one('res.users', 'Canceled By',readonly=True),
         'cancel_date': fields.datetime('Cancel Date',readonly=True),
        #fields related to adjustment
        'receipt_book_idd': fields.one2many('smsfee.receiptbook.lines.fee.adjustment', 'receipt_book_idd', 'Fees'),
        'receiptbook_lines_ids': fields.one2many('smsfee.receiptbook.lines', 'receipt_book_id', 'Fees'),
        'voucher_date': fields.date('Voucher Date',readonly=True),
        'vouchered_by': fields.many2one('res.users', 'Voucher By',readonly=True),
        'vouchered': fields.boolean('Vouchered', readonly=True),
        'voucher_no': fields.many2one('account.move', 'Voucher No',readonly=True),
        'late_fee' : fields.float('Late Fee'),
    }
    _sql_constraints = [  
        #('Fee Exisits', 'unique (name)', 'Fee Receipt No Must be Unique!')
    ] 
    _defaults = {
         'state':'Draft',
         'payment_method': 'Cash',
         'student_id':_get_id ,
         'total_paid_amount': 0.0,
         'receipt_date':lambda *a: time.strftime('%Y-%m-%d'),
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
    
    def _set_feename(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = f.student_fee_id.name
        return result
    
    _name = 'smsfee.receiptbook.lines'
    _rec_name = 'fee_name'
    _description = "This object store fee types"
    _columns = {
        'name': fields.many2one('sms.academiccalendar','Academic Calendar'),
        'fee_name': fields.function(_set_feename,string = 'Fee.',type = 'char',method = True),      
        'fee_type': fields.many2one('smsfee.classes.fees.lines','Fee Type'),
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





#-------------------------pbject for paid fee adjustment--------------------------------------
# class smsfee_receiptbook_lines_fee_adjustment(osv.osv):
#     """ This object is created to make adjustment in paid fees.
#         it appears as on2many on receiptbook.
#         it also acts as child of receopbooklines """
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
#     _name = 'smsfee.receiptbook.lines.fee.adjustment'
#     _description = "This object store fee types"
#     _columns = {
#         'name': fields.many2one('smsfee.receiptbook.lines','Fee' ),      
#         'fee_type': fields.many2one('smsfee.classes.fees','Fee Type'),
#         'fee_month': fields.many2one('sms.session.months','Fee Month'),
#         'receipt_book_idd': fields.many2one('smsfee.receiptbook','Receipt book',required = True),
#         'paid_amount':fields.integer('Paid'),
#         'discount': fields.integer('Discount'),
#         'net_total': fields.integer('Balance'),  
#         'adjustment_decision':fields.selection([('Unchanged','No Adjustment'),('set_as_unpaid','Set as Fee Unpaid'),('change_amount','Change Amount')],'Adjustment',required = True), 
#     }
#     _sql_constraints = [  
#         ('Fee Exisits', 'unique (name)', 'This fee is already added for adjustment')
#     ] 
#     _defaults = {
#          'state':'Unchanged',
#     }
# smsfee_receiptbook_lines_fee_adjustment()
#  


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
        ftyp = None
        for f in self.browse(cr, uid, ids, context=context):
             ftyp = "R-"+str(f.id)
        return ftyp
    
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


# class student_admission_register(osv.osv):
#     
#     def admit_student(self ,cr ,uid ,ids ,context):
#         fee_amount = 0
#         #----confirm subjects---------
#         self.confirm_student_subjects(cr ,uid ,ids,context=None)
#         #----confirm fee---------
#         for i in self.browse(cr ,uid ,ids):
#             create_stu_fee = self.pool.get('smsfee.studentfee').add_fee_student(cr ,uid ,ids,{'acd_cal_id':i.student_class.id ,
#                                                                              'student_id':i.name.id ,
#                                                                              'month':i.fee_starting_month.id, 
#                                                                              'fee_structure':i.fee_structure.id
#                                                                              })
#             for fee_sum in i.fee_id :
#                 fee_amount +=fee_sum.fee_amount
#                 
#         self.write(cr, uid, ids, {'state': 'Confirm' ,'total_fee': fee_amount })
#         return None  
#     def load_fee_subjects(self ,cr ,uid ,ids ,context):
#         #-----------write form no-------------------------------
#         #------load fee----------
#         self.load_student_fee(cr ,uid ,ids,context=None)
#         #-------load student---------
#         self.load_subjects(cr ,uid ,ids,context=None)
#         self.write(cr, uid, ids, {'state': 'waiting_approval','form_no':ids[0]})
#         return True
#     
#     def load_student_fee(self ,cr ,uid ,ids ,context):
#         for parent_id in self.browse(cr ,uid ,ids):
#             class_fee_id = self.pool.get('smsfee.classes.fees').search(cr,uid,[('academic_cal_id','=',parent_id.student_class.id),
#                                                                       ('fee_structure_id','=',parent_id.fee_structure.id)])
#             
#         if class_fee_id:
#             for class_fee in class_fee_id:
#                 obj = self.pool.get('smsfee.classes.fees').browse(cr,uid,class_fee_id[0])
#                 for fee_line in obj.fee_type_ids:
#                     adm_regis_fee = self.pool.get('admission.register.fees').create(cr ,uid ,{'name': ids[0] ,
#                                                          'stu_fee_id' : fee_line.id ,
#                                                          'fee_amount' : fee_line.amount  })
#         else:
#             print "No setting found for this feestructure"
#             raise osv.except_osv(('No Fee Structure'),('No setting found for this feestructure'))
#         return None
#     
#     """This object inherits sms_student_admission_register and adds fields related to fee."""
#     _name = 'student.admission.register'
#     _inherit ='student.admission.register'
#     _columns = {
#         'fee_id' : fields.one2many('admission.register.fees','name','Student Fee'),
#     }
#     _defaults = {  }
# student_admission_register()

class smsfee_paid_unpaid_adjustments(osv.osv):
        
    def cancel_fee_change(self, cr, uid, ids, context=None):
        rec = self.browse(cr ,uid ,ids)[0]
        _pool = self.pool.get('smsfee.paid.fee.adjustment')
        if rec.unpaid_fee != []:
            _pool = self.pool.get('smsfee.unpaid.fee.adjustment')
            
        _ids = _pool.search(cr ,uid , [('name','=',ids[0])]) 
        if _ids :
            unlink = _pool.unlink(cr ,uid ,_ids )
            
        self.write(cr ,uid ,ids ,{'state' : 'Draft'})
        return True

    def apply_fee_change(self, cr, uid, ids, context=None):
        rec = self.browse(cr ,uid ,ids)[0]
        _pooler_stu_fee = self.pool.get('smsfee.studentfee')
        
        if rec.unpaid_fee != []:
            #------if user wants to adjust unpaid_fee-----------------
            for change_amount in rec.unpaid_fee:
                if change_amount.decision == "charge_amount" :
                    change_fee = _pooler_stu_fee.write(cr ,uid ,change_amount.fee_id.id ,{'fee_amount': change_amount.new_amount 
                                                                             })
                elif change_amount.decision == "fee_exemption" :
                    fee_exempted = _pooler_stu_fee.write(cr ,uid ,change_amount.fee_id.id ,{'fee_amount': change_amount.new_amount ,
                                                                             'state':'fee_exemption' ,
                                                                             'reconcile': True,
                                                                             })
                
        else :
            #------if user wants to adjust paid_fee-----------------
            for check in rec.paid_fee:
                if check.decision == "set_as_unpaid" :
                    set_unpaid_fee = _pooler_stu_fee.write(cr ,uid ,check.fee_id.id ,{'paid_amount': check.actual_amount , 
                                                                                      'reconcile': False,
                                                                                      'state' : 'fee_unpaid'
                                                                                      })
                elif check.decision == "change_amount" :
                    set_unpaid_fee = _pooler_stu_fee.write(cr ,uid ,check.fee_id.id ,{'paid_amount': check.actual_amount  
                                                                                      })
                elif check.decision == "return_fee" :
                    print "return amount",check.actual_amount
                    return_fee = _pooler_stu_fee.write(cr ,uid ,check.fee_id.id ,{#'paid_amount': check.actual_amount,
                                                                                      'state' : 'fee_returned',
                                                                                      'reconcile': False,
                                                                                      'returned_amount' : check.actual_amount
                                                                                      }) 
            print "id of reciptbook=",rec.receipt_no.id,rec.receipt_no.name,rec.receipt_no.state
            self.pool.get('smsfee.receiptbook').write(cr ,uid ,rec.receipt_no.id ,{'state' : 'Adjusted'})
            print "state of reciptbook=",rec.receipt_no.state
            
        self.write(cr ,uid ,ids ,{'state' : 'fee_adjusted'})
        return True
            
    def load_fee(self, cr, uid, ids, context=None):
        rec = self.browse(cr ,uid ,ids)[0]
        _pooler_stu_fee = self.pool.get('smsfee.studentfee')
        
        if rec.action == 'unpaid_fee_adjustment':
            unpaid_fee_id = _pooler_stu_fee.search(cr ,uid , [('student_id','=',rec.student.id),('state','=','fee_unpaid')])
            fee_rec = _pooler_stu_fee.browse(cr ,uid ,unpaid_fee_id)
            for i in fee_rec:
                unpaid_id = self.pool.get('smsfee.unpaid.fee.adjustment').create(cr ,uid ,{'name': ids[0],
                                                                                           'fee_id': i.id,
                                                                                            'current_amount': i.fee_amount ,
                                                                                            })
                
        else:
            paid_fee_id = _pooler_stu_fee.search(cr ,uid , [('student_id','=',rec.student.id),('state','=','fee_paid'),('receipt_no','=',rec.receipt_no.id)])
            if paid_fee_id:
                fee_rec = _pooler_stu_fee.browse(cr ,uid ,paid_fee_id)
                for i in fee_rec:
                    paid_id = self.pool.get('smsfee.paid.fee.adjustment').create(cr ,uid ,{'name': ids[0],
                                                                                            'fee_id': i.id,
                                                                                                })
            else:
                raise osv.except_osv(('Enter valid receipt no '),('The receipt number that you have entered is invalid'))
        
        #--------------calculate fee adjustment number-------------------------------------
        sql = """SELECT count(*) from  smsfee_paid_unpaid_adjustments"""
        cr.execute(sql)
        adjust_no = cr.fetchone()
            
        self.write(cr ,uid ,ids ,{'state' : 'waiting_approve','name':adjust_no[0]})
        return True
 
    def onchange_set_domain(self, cr, uid, ids, student):
        receipt_id = self.pool.get('smsfee.receiptbook').search(cr ,uid , [('student_id','=',student)])
        return {'domain': {'receipt_no': [('id', 'in', receipt_id)]} ,
                'value':{}}

       
    """This object performs fee adjustment of student's paid and unpaid fee """
    _name = 'smsfee.paid.unpaid.adjustments'
    _columns = {
        'name' : fields.char('Fee Adjustment No' ,size=256),
        'class' : fields.many2one('sms.academiccalendar' , 'Class' ,required=True ),
        'student' : fields.many2one('sms.student' , 'Student Name' ,required=True , domain="[('current_class','=',class)]"),
        'date': fields.date("Date" ,required=True),
        'receipt_no':fields.many2one('smsfee.receiptbook','Receipt No'),
        'action':fields.selection([('paid_fee_adjustment','Paid Fee Adjustment'),('unpaid_fee_adjustment','Unpaid Fee Adjustment')],'Action' ,required=True ),
        'state': fields.selection([('Draft', 'Draft'),('waiting_approve', 'Waiting Approve'),('fee_adjusted', 'Fee Adjusted')], 'State', readonly = True ,required=True),
        'unpaid_fee' : fields.one2many('smsfee.unpaid.fee.adjustment','name','Unpaid Fee Adjustment'),
        'paid_fee' : fields.one2many('smsfee.paid.fee.adjustment','name','Paid Fee Adjustment'),
    }
    _defaults = { 'state' : 'Draft',   }  
      
smsfee_paid_unpaid_adjustments()

class smsfee_unpaid_fee_adjustment(osv.osv):
    
    def onchange_decision_on_amount(self, cr, uid, ids, new_amount ,decision):
        val ={}
#         if new_amount == 0 and decision == False:
#             val['decision'] = 'no_adjustment'
            
        if  decision == 'no_adjustment' :
            val['new_amount'] = 0.00
        
        if  decision == 'charge_amount':
            if  new_amount == 0:
                raise osv.except_osv(('Enter new amount'),('Inorder to charge fee  enter New Amount'))
            
        elif  decision == 'fee_exemption':
            if  new_amount != 0:
                raise osv.except_osv(('Fee Exemption Denied'),('For fee exemption new amount should be zero'))
        
        return {'value':val}     
    
    """This is child object of smsfee.paid.unpaid.adjustments resolving unpaid fee"""
    _name = 'smsfee.unpaid.fee.adjustment'
    _columns = {
        'name' : fields.many2one('smsfee.paid.unpaid.adjustments','parent_id' ),
        'fee_id' : fields.many2one('smsfee.studentfee' , 'Fee Type'),
        'current_amount' : fields.integer('Current Amount'),
        'new_amount' : fields.integer('New Amount'),
        'decision': fields.selection([('no_adjustment', 'No Adjustment'),('charge_amount', 'Charge Amount'),('fee_exemption', 'Fee Exemption')], 'decision' ),
    }
    _defaults = { }  
    _sql_constraints = [('parent_fee_id', 'unique (name,fee_id)', """ Parent and fee id should be unique..""")]     
smsfee_unpaid_fee_adjustment()

class smsfee_paid_fee_adjustment(osv.osv):
    
    def set_fee(self, cr, uid, ids, fields, arg, context):
        res = {}
        records =  self.browse(cr, uid, ids, context)
        
        for f in records:
            res[f.id] = str(f.fee_id.paid_amount) +'/'+ str(f.fee_id.fee_amount)
        return res
    
    def onchange_decision(self, cr, uid, ids, actual_amount ,decision):
        val ={}
        
        if  decision == 'set_as_unpaid':
            if  actual_amount != 0:
                raise osv.except_osv(('Request Denied'),('Inorder to set fee as unpaid Actual Amount should be zero.'))

        if  decision == 'return_fee':
            val['actual_amount'] = 0

        if  decision == 'change_amount':
            if  actual_amount == 0:
                raise osv.except_osv(('Request Denied'),('Enter value in Actual amount'))

        
        return {'value':val}     
    
    """This is child object of smsfee.paid.unpaid.adjustments resolving unpaid fee"""
    _name = 'smsfee.paid.fee.adjustment'
    _columns = {
        'name' : fields.many2one('smsfee.paid.unpaid.adjustments','parent_id'),
        'fee_id' : fields.many2one('smsfee.studentfee' , 'Fee Type'),
        'fee_received' : fields.function(set_fee, method=True, string='Paid Fee/Actual Fee', type='char', size=150),
        'actual_amount' : fields.integer('Actual Amount'),
        'decision': fields.selection([('change_amount', 'Change Amount'),('set_as_unpaid', 'Set As Unpaid'),('return_fee', 'Return Fee')], 'decision'),
    }
    _defaults = {   }  
       
smsfee_paid_fee_adjustment()

class student_admission_register(osv.osv):
    """This object serves as a tree view for sms_student_admission_register for fee purpose """
    def set_fee_amount(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        amount = '0'
        records =  self.browse(cr, uid, ids, context)

        for f in records:
            sql =   """SELECT COALESCE(sum(amount),'0')  FROM admission_register_student_fees
                     WHERE parent_id ="""+str(f.id)
            cr.execute(sql)
            amount = cr.fetchone()[0]
        result[f.id] = amount
        return result
    
    _name = 'student.admission.register'
    _inherit = 'student.admission.register'
    _columns = {
        'fee_ids':fields.one2many('admission.register.student.fees','parent_id','Fee'),
        'total_fee_applicable':fields.function(set_fee_amount, method=True, string='Total Fee',type='float'),
        'store_fee_ids':fields.char('Fee Ids',size = 150)
    }
    _defaults = {    }    
student_admission_register()

class admission_register_student_fees(osv.osv):
    """This object serves as a tree view for sms_student_admission_register for fee purpose """
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(admission_register_student_fees, self).default_get(cr, uid, fields, context)
        if context.get('parent_id'):
            rec_admin_reg = self.pool.get('student.admission.register').browse(cr ,uid ,context['parent_id'])
            #get class id and fs id to search via this in class fess lines to get lin id
            class_id = rec_admin_reg.student_class.id
            fs_id = rec_admin_reg.fee_structure.id
            fee_line_id = self.pool.get('smsfee.classes.fees').search(cr ,uid ,[('academic_cal_id','=',class_id),('fee_structure_id','=',fs_id)])
            if fee_line_id:
                 print "found parent fs id ",fee_line_id[0]
                 res['hidden_parent_feestr'] = fee_line_id[0]
        print "res ",res
        return res
    
    _name = 'admission.register.student.fees'
    _columns = {
        'name':fields.many2one('smsfee.classes.fees.lines','Fee'),
        'parent_id':fields.many2one('student.admission.register','Admission Register'),
        'fee_month':fields.many2one('sms.session.months','Fee Month'),
        'amount':fields.float('Amount'),
        'hidden_parent_feestr':fields.integer('Hidden classes Fees id'),
    }
    _sql_constraints = [('Fee_ex-tinsts', 'unique (name,parent_id,fee_month)', """ Fee is already inculded""")]

    _defaults = {    }    
admission_register_student_fees()



#$$$$--
class smsfee_receive_challan_in_bank(osv.osv):
    """This object enter detail about fee challan that in received by bank """

    def load_challan_details(self, cr, uid, ids, name):
        record = self.browse(cr, uid, ids)
        pooler_receiptbook = self.pool.get('smsfee.receiptbook')
        
        if record[0].challan_type == 'class_challan':
            for acd_cal in record[0].acd_cal:
                for std in acd_cal.acad_cal_students:
                   
                    challan_id = pooler_receiptbook.search(cr ,uid ,[('state','=','fee_calculated'),('student_id','=',std.std_id.id),
                                                                                      ('student_class_id','=',acd_cal.id)])
                    for challan in pooler_receiptbook.browse(cr ,uid ,challan_id):
                        self.pool.get('smsfee.receive.challan.in.bank.lines').create(cr ,uid ,{'parent_id':record[0].id,
                                                                                                             'challan_no':challan.id,
                                                                                                             #'due_date':,
                                                                                                             'student_name':std.std_id.id,
                                                                                                             'amount':challan.total_paybles,
                                                                                                            # 'late_fee':,
                                                                                                            # 'received':,
                                                                                                             'challan_produced_by_bank':True,
                                                                                                             })
        else:
            year = int(record[0].session_month.session_year)
            month = int(record[0].session_month.session_month_id.code)
            
            begin = date(year, month, 1)
            end = date(year, month, monthrange(year, month)[1])   
            challan_id = pooler_receiptbook.search(cr ,uid ,[('state','=','fee_calculated'),
                                                             ('receipt_date','>=',begin),('receipt_date','<=',end)])
            for challan in pooler_receiptbook.browse(cr ,uid ,challan_id):
                print "**create open challans****",self.pool.get('smsfee.receive.challan.in.bank.lines').create(cr ,uid ,{'parent_id':record[0].id,
                                                                                                     'challan_no':challan.id,
                                                                                                     #'due_date':,
                                                                                                     'student_name':challan.student_id.id,
                                                                                                     'amount':challan.total_paybles,
                                                                                                     'challan_produced_by_bank':True,
                                                                                                     })
        if not challan_id:
            raise osv.except_osv(('Define Challans'),('No open challans found'))            
        self.write(cr ,uid , ids ,{'state':'Receive'})
        return True
    
    def confirm_challan_receive_from_bank(self ,cr ,uid ,ids ,context=None):
        _pooler = self.pool.get('smsfee.receive.challan.in.bank.lines')
        pooler_receiptbook = self.pool.get('smsfee.receiptbook')
        sql = """ SELECT smsfee_receive_challan_in_bank_lines.id from smsfee_receive_challan_in_bank_lines
                    INNER JOIN smsfee_receive_challan_in_bank ON smsfee_receive_challan_in_bank_lines.parent_id =smsfee_receive_challan_in_bank.id 
                    WHERE smsfee_receive_challan_in_bank.id = """ +str(ids[0])+ """
                          AND smsfee_receive_challan_in_bank_lines.received = True
        """
        cr.execute(sql)
        record = cr.fetchall()
        for id  in record:
            rec = _pooler.browse(cr ,uid ,id[0])
            
            #--------------update smsfee.receiptbook.lines--------------------
            receipt_lines_ids = self.pool.get('smsfee.receiptbook.lines').search(cr ,uid , [('receipt_book_id','=',rec.challan_no.id)])
            self.pool.get('smsfee.receiptbook.lines').write(cr ,uid ,receipt_lines_ids,{
                                                                                                                         'paid_amount': rec.amount,#+rec.late_fee ,
                                                                                                                         'discount': 0 ,
                                                                                                                         'reconcile': True ,
                                                                                                                         })
            
            pooler_receiptbook.confirm_fee_received(cr ,uid ,[rec.challan_no.id])
        self.write(cr ,uid , ids ,{'state':'Confirm'})
        return True
    
    _name = 'smsfee.receive.challan.in.bank'
    _columns = {
        'acd_cal':fields.many2many('sms.academiccalendar', 'receive_challan_academiccalendar_rel', 'receive_challan_id', 'academiccalendar_id', 'Class'),
        'state':fields.selection([('Draft','Draft'),('Receive','Receive'),('Confirm','Confirm')],'State'),
        'challan_type':fields.selection([('open_challan','Months'),('class_challan','Class')],'Load On' ,required=True),
        'session_month':fields.many2one('sms.session.months','Month'),
        'receive_challan_by_bank':fields.one2many('smsfee.receive.challan.in.bank.lines','parent_id','Challan Received By Bank')
    }
    _sql_constraints = []

    _defaults = { 'state':'Draft','challan_type':'class_challan'   }    
smsfee_receive_challan_in_bank()

class smsfee_receive_challan_in_bank_lines(osv.osv):
    """Child object of smsfee_receive_challan_in_bank  """
    _name = 'smsfee.receive.challan.in.bank.lines'
    _columns = {
        'parent_id':fields.many2one('smsfee.receive.challan.in.bank', 'Parent Id'),
        'challan_no':fields.many2one('smsfee.receiptbook', 'Challan No'),
        'due_date':fields.date('Due Date'),
        'student_name':fields.many2one('sms.student', 'Student'),
        'amount':fields.integer('Amount'),
        'late_fee':fields.integer('Late Fee'),
        'received':fields.boolean('Received'),
        'challan_produced_by_bank':fields.boolean('Challan By Bank'),
        

    }
    _sql_constraints = []

    _defaults = { }    
smsfee_receive_challan_in_bank_lines()
