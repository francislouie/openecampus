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
    ########## Fields for Challan's Print Settings ##############################################
    'bank_name1':fields.char('Bank One Name', size=256),
    'bank_name2':fields.char('Bank Two Name', size=256),
    'bank_acctno1':fields.char('Bank One Acc.No'),
    'bank_acctno2':fields.char('Bank Two Acc.No'),
    'company_cfieldone':fields.char('Heading Line One', size=256),
    'company_cfieldtwo':fields.char('Heading Line Two', size=256),
    'company_cfieldthree':fields.char('Heading Line Three', size=256),
    'company_cfieldfour':fields.char('Footer Line One', size=256),
    'company_cfieldfive':fields.char('Footer Line Two', size=256),
    'company_cfieldsix':fields.char('Footer Line Three', size=256),
    'company_clogo':fields.binary('Challan Logo'),
    'order_of_report':fields.selection([('by_name','By Name'),('by_registration_no','By Reg No')],'Order Of Report'),
    'campus_code':fields.char('Campus Code', size=64),
    'fee_display_portal':fields.selection([('fee_unpaid','Un-Paid Fee'),('fee_paid','Paid Fee')],'Fee (Displayed on Portal)'),
    'display_refundable':fields.boolean('Display Refundable Fee'),
    
    }
    _defaults = {
                 'fee_report_type':'One_on_One',
                 'display_refundable': lambda*a : False,
                 }
res_company()



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

#******************change studnet class*******************************************************

class sms_change_student_class_new(osv.osv):
    """the objects adds fee portion in order to change student cls form sms module"""
    _name = 'sms.change.student.class.new'
    _inherit ='sms.change.student.class.new'
    _columns = {
         'applicable_fees': fields.many2many('smsfee.feetypes', 'sms_change_class_fee_rel', 'change_class_id', 'feetype_id', 'Applicable Fee', required=True),
    }
    _defaults = {
    }
sms_change_student_class_new()

#******************change studnet class*******************************************************


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
                            fee_types_ids = self.pool.get('smsfee.classes.fees.lines').search(cr,uid,[('fee_type.category','=','Academics'),('parent_fee_structure_id','=',fee.id)])
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
    
    def calc_month(self, cr, uid,ids,field_names, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = {}
            if type(field_names) is not list:
                field_names = [field_names]
            
            for key_str in field_names:
                result[f.id][key_str] = 0.0
            
            if 'month_focasted_amount' in field_names:
                sql1 = """SELECT COALESCE(sum(fee_amount),'0') from smsfee_studentfee
                         inner join smsfee_classes_fees_lines on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                        inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                               WHERE fee_month = """+str(f.id)+ """ and state = 'fee_unpaid' AND smsfee_feetypes.category='Academics'"""
                print "sql:",sql1
         
                cr.execute(sql1)
                row1 = cr.fetchone()
                print "..111....", row1[0]
                result[f.id]['month_focasted_amount'] = float(row1[0])
            
            elif 'month_collected_amout' in field_names:
                sql2 = """SELECT COALESCE(sum(paid_amount),'0') from smsfee_studentfee
                        inner join smsfee_classes_fees_lines on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                        inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                               WHERE fee_month = """+str(f.id)+ """ and state = 'fee_paid' AND smsfee_feetypes.category='Academics'"""
                cr.execute(sql2)
                row2 = cr.fetchone()
              
                print "..sql2....", sql2
                result[f.id]['month_collected_amout'] = float(row2[0])
                
            elif 'month_recovery_ratio' in field_names:
                if f.month_focasted_amount >0:
                    forcasted = f.month_focasted_amount
                else:
                    forcasted = 1
                ratio = float((f.month_collected_amout*100)/forcasted)
                print "333.....",ratio
                result[f.id]['month_recovery_ratio'] = float((f.month_collected_amout*100)/forcasted)
        return result
    
    _name = 'sms.session.months'
    _description = "stores months of a session"
    _inherit = 'sms.session.months'
    _columns = {
        'update_log': fields.char('Year',size = 50),  
        'state':fields.selection([('To_Update','To Be Updated'),('Updated','Updated')],'State'),
        'month_focasted_amount':fields.function(calc_month, multi = '1',method=True,  string='Forcasted',type='float'),
        'month_collected_amout':fields.function(calc_month,multi = '2', method=True,  string='Collection',type='float'),
        'month_recovery_ratio':fields.function(calc_month,multi = '3', method=True,  string='Ratio',type='float'),
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
    
    def start_annual_fee_structure(self, cr, uid, ids, name):
        for f in self.browse(cr, uid, ids):
            classes_list = f.applied_onclasses
            #1: -------------------- Search all fee structures in this annual revisions ------------------
#            print "number of classes selected -----",len(classes_list)
            for this_class in classes_list:                    
                #------------------- Checking fee details class by class  -----------------
                revisionline_feestructure_ids = self.pool.get('sms.revision.line.feestructure').search(cr,uid,[('parent_annaul_fs_id','=',f.id)])
                if revisionline_feestructure_ids:
                    revisionline_feestructure_objs = self.pool.get('sms.revision.line.feestructure').browse(cr,uid, revisionline_feestructure_ids)
                    for this_fs in revisionline_feestructure_objs:
                        #--------------------- Searching for every fee structure defined ------------------
                        class_fees_id = self.pool.get('smsfee.classes.fees').search(cr, uid, [('fee_structure_id','=', this_fs.name.id),('academic_cal_id','=', this_class.id)])
                        if class_fees_id:
                            #--------------------- Great, this fee structure already exists in selected class -------------------
                            #--------------------- Loop on revision.lines.fee.types, and search each fee type in classes fees lines, if exists update with new amount ----------------------
                            revision_feetype_ids = self.pool.get('sms.revision.line.feetypes').search(cr,uid,[('revisionline_fs_id','=',this_fs.id)])
                            if revision_feetype_ids:
                                rec_anfs_ftypes = self.pool.get('sms.revision.line.feetypes').browse(cr, uid, revision_feetype_ids)
                                fee_types = []
                                for this_ft in rec_anfs_ftypes:
                                    print "-----",this_ft.name.id
                                    feetype_dict = {'feetype_id':'', 'amount':''}
                                    # ---------------------- With new amount other wise create new fee type in fee lines -----------------
                                    feetype_dict['feetype_id'] = int(this_ft.name.id)
                                    feetype_dict['amount'] = this_ft.amount
                                    fee_types.append(feetype_dict)
                                
                                self.pool.get('smsfee.classes.fees').update_if_exists_or_create_ft(cr, uid, this_class.id, this_fs.name.id, fee_types)
                                    #--------------------- Call method to search classes_fee_lines for checking if fee type exist then update --------------------- 
                                    #--------------------- With new amount other wise create new fee type in fee lines -------------------------------------------------
#                                     print "updating fee structure --------",class_fees_id[0], "----->>>>",this_fs.id, "========",this_ft.name.id, "=======",this_ft.amount
#                                     self.pool.get('smsfee.classes.fees').update_if_exists_or_create_ft(cr, uid, class_fees_id[0], this_fs.name.id, this_ft.name.id, this_ft.amount)
                        else:
                            #------------  Fee structure does not exists in smsfee.classes.fees, create this fee structure in classes fees and its children in feeslines ----------------------
                            #------------ 1: Call method to create fee structure ------------------------
#                             new_fs = self.pool.get('smsfee.classes.fees').create_new_fs_in_classes_fees(self, cr, uid, this_fs.name.id, this_class.id)
                                #create its children by calling the method update_if_exists_or_create_ft
                                #loop on this revision line fstruecure nad get its its chldren i.e feetypes
                                #when revisionlnes ft are get, loop on this and call update_if_exists_or_create_ft        
                                # call method to search classes_fee_lines for checking if feetype exist then upload
                            revisionline_feetypes_ids = self.pool.get('sms.revision.line.feetypes').search(cr, uid, [('revisionline_fs_id','=', this_fs.id)])
                            if revisionline_feetypes_ids:
                                rec_anfs_ftypes = self.pool.get('sms.revision.line.feetypes').browse(cr, uid, revisionline_feetypes_ids)
                                fee_types = []
                                for this_ft in rec_anfs_ftypes:
                                    feetype_dict = {'feetype_id':'', 'amount':''}                                
                                    feetype_dict['feetype_id'] = this_ft.name.id
                                    feetype_dict['amount'] = this_ft.amount
                                    fee_types.append(feetype_dict) 
                                # ---------------------- With new amount other wise create new fee type in fee lines -----------------
                                self.pool.get('smsfee.classes.fees').update_if_exists_or_create_ft(cr, uid, this_class.id, this_fs.name.id, fee_types)
            self.write(cr, uid, f.id, {'state':'Active','effective_from':datetime.datetime.now()})                                    
        return True
        
    def close_annual_fee_structure(self, cr, uid, ids, name, args, context=None):
        for f in self.browse(cr, uid, ids, context=context):
            result = self.write(cr, uid, f.id, {'state':'Closed','effective_till':datetime.datetime.now()})
        return result
    
    _name = 'smsfee.festructure.revision'
    _columns = {
    'name':fields.function(_set_name, method=True,  string='Class Fee',type='char'),
    'session_id':fields.many2one('sms.session', 'Session'),
    'fee_str_ids':fields.one2many('sms.revision.line.feestructure','parent_annaul_fs_id','Fee Structure'),
    'applied_onclasses':fields.many2many('sms.academiccalendar','sms_academiccalendar_sms_fee_revision','academiccalendar_id','fee_revision_id','Applied On Classes', domain="[('state','=','Active')]"),
    'effective_from':fields.datetime('Effective From'),
    'effective_till':fields.datetime('Effective till'),
    'state':fields.selection([('Draft','Draft'),('Get_Session_Classes','Pick Classes'),('Active','Active'),('Closed','Closed')],'Status', readonly=True),
    }
    _defaults = {'state':'Draft'}
smsfee_festructure_revision()

class sms_revision_line_feestructure(osv.osv):
    """This object appear as child object to sms_fee_structure_revision .
       This tabl has further one child table sms_rervision_lines_feetypes"""
   
    _name = 'sms.revision.line.feestructure'
    _columns = {
    'name': fields.many2one('sms.feestructure','Fee Structure'),      
    'parent_annaul_fs_id': fields.many2one('smsfee.festructure.revision', 'Annual Fee Register', ondelete="cascade"),
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
    
    def return_count_class_defaulter_students_list(self, cr, uid,ids):
        """
        :purpose = Returns list of defaulter students for given class, or returns counted defaulter students in a given class i.e id = ids
        :param ids:class_id: Id of the class for which students will be searched
        :called by: This method is not called by any other method or field, we can use it when we need defaulter students for a given class
        :last modified 7 JAN 2017, Shahid
        """
        result = {}
        
        sql = """SELECT std_id from sms_academiccalendar_student where name= """+str(ids)
        cr.execute(sql)
        students = cr.fetchall()
        for student in students:
            my_dict = {'std_id':student[0],'amount_acadamics':'','amount_transport':'','amount_overall':''}
            my_dict['amount_acadamics'] = self.pool.get('sms.student').total_outstanding_dues(self.cr,self.uid,student[0],'Academics','fee_unpaid')
            my_dict['amount_transport'] = self.pool.get('sms.student').total_outstanding_dues(self.cr,self.uid,student[0],'Transport','fee_unpaid')
            my_dict['amount_overall'] = self.pool.get('sms.student').total_outstanding_dues(self.cr,self.uid,student[0],'Overall','fee_unpaid')
            result.append(my_dict)
        return result
        
        
        
        # for returing list of defaulter students
          
    def _calculate_class_forecasted_fee(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            total_forecasted = 0
            register_ids = self.pool.get('smsfee.classfees.register').search(cr,uid,[('academic_cal_id','=',f.id)])
            if register_ids:
                rec_register = self.pool.get('smsfee.classfees.register').browse(cr,uid,register_ids)
                for register in rec_register:
                    total_forecasted = total_forecasted + register.month_forcasted_fee 
                    result[f.id] = float(total_forecasted)
        return result  
    
    def _calculate_class_paid_fee(self, cr, uid, ids, name, args, context=None):
        #this query will be changed when function for fee reurned is included
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            total_paid = 0
            register_ids = self.pool.get('smsfee.classfees.register').search(cr,uid,[('academic_cal_id','=',f.id)])
            if register_ids:
                rec_register = self.pool.get('smsfee.classfees.register').browse(cr,uid,register_ids)
                for register in rec_register:
                    total_paid = total_paid + register.month_fee_received 
                    result[f.id] = float(total_paid)
        return result
    
    def _calculate_calculate_recovery(self, cr, uid, ids, name, args, context=None):
        #this query will be changed when function for fee reurned is included
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
#             if f.class_forcasted_fee:
#                 recovery = math.ceil((f.class_fee_received*100)/f.class_forcasted_fee)
#             else:
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
            'class_forcasted_fee':fields.float('a'),
            'class_fee_received':fields.float('a'),
            'recovery_ratio':fields.function(_calculate_calculate_recovery, method=True,  string='Recovery(%)',type='char'),
            'annaul_fs_id':fields.many2one('smsfee.festructure.revision','Annual Fee Register'),
    }
sms_academiccalendar()

class sms_student(osv.osv):
    """This object is used to add fields in sms.student"""
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        
        for f in self.browse(cr, uid, ids, context=context):
            if 'fee_type' in vals:
                
                student_history_id = self.pool.get('smsfee.structure.history').search(cr, uid, [('student_id','=', f.id)])
                student_history_obj = self.pool.get('smsfee.structure.history').browse(cr, uid, student_history_id)
                print"---------------  One Students All Records   -------------- ",student_history_obj
                if student_history_obj:
                    sql = """SELECT id FROM smsfee_structure_history WHERE student_id ="""+str(f.id)+""" order by create_date desc limit 1 """
                    cr.execute(sql)
                    target_id = cr.fetchone()[0]
                    result = self.pool.get('smsfee.structure.history').write(cr, uid, target_id, {'deallocation_date': datetime.datetime.now()}, context=context)
                    print"---------------  Target Id to Change   -------------- ",target_id
                    
                fee_type_id = self.pool.get('sms.feestructure').search(cr, uid, [('id','=', vals['fee_type'])])
                fee_type_obj = self.pool.get('sms.feestructure').browse(cr, uid, fee_type_id[0])
                print"---------------  fee fee_type_obj   -------------- ",fee_type_obj
                fee_name = fee_type_obj.name
                assigned_date = datetime.datetime.now()
                user = self.pool.get('res.users').browse(cr, uid, uid, )
                assign_person = user.login
                historyId = f.id
                result = self.pool.get('smsfee.structure.history').create(cr, uid, 
                                                                          {'student_id':historyId,
                                                                            'name':fee_name, 
                                                                           'assignment_date':assigned_date,
                                                                           'assigned_by': assign_person }, context)

        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result 
    
    
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
    
    def total_outstanding_dues(self, cr, uid, student_id,fee_category,return_choice):
        """
        This method returns total outstanding dues,total paid dues, or both of a stduent in academics section only. 
        No other function will be cereated on parser or any place to calculate dues of academics for a students, all methods in wizard report 
        or in any place will call this method
        This methods is called by
        1: Set_payebl methods which is used in f.function on sms_student
        2: Defaulter students list by passing students id
        3: return_count_class_defaulter_students () > which returns total defaulter students of a class
        Important porint:
        1) call this method only when 1) student whole fee irrespective of a class to be found (Paid,unpaid,both), this method doesnot belong to any
           class
           
        Note: this method is also called for transport fee, but this is not inside transport module, we will check its working where tranport is 
        not installed, if it works fine then the same method will be called by all other modules like hostel, mass_sms etc
        """
        if fee_category == 'Overall':
            sql= """SELECT COALESCE(sum(fee_amount),'0') as fee_amount from smsfee_studentfee
                            inner join smsfee_classes_fees_lines 
                            on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                            inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                            where smsfee_studentfee.state = 'fee_unpaid'
                            and smsfee_studentfee.student_id = """+str(student_id)
        else:
            sql= """SELECT COALESCE(sum(fee_amount),'0') as fee_amount from smsfee_studentfee
                            inner join smsfee_classes_fees_lines 
                            on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                            inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                            where smsfee_feetypes.category = '""" +fee_category+"""'
                            and smsfee_studentfee.state = 'fee_unpaid'
                            and smsfee_studentfee.student_id = """+str(student_id)
                            
        cr.execute(sql)
        rec = cr.fetchone() 
        return int(rec[0])
    
    def class_total_outstanding_dues(self, cr, uid, student_id,class_id,fee_category,return_choice):
        """
        This method returns total outstanding dues,total paid dues, or both of a stduent for a specific class . 
        No other function will be cereated on parser or any place to calculate dues , all methods in wizard report 
        or in any place will call this method
        This methods is called by
        1: Setclass_payebl methods which is used in f.function on sms_acadecmiclacalender student (thiis field is not yet created)
        2: Defaulter students list by passing students id and class_id,
        3: return_count_class_defaulter_students () > which returns total defaulter students of a class
        Important porint:
        1) call this method only when 1) student whole fee belong to a given class 
           class
           
        Note: this method is also called for transport fee, but this is not inside transport module, we will check its working where tranport is 
        not installed, if it works fine then the same method will be called by all other modules like hostel, mass_sms etc
        """
        if fee_category == 'Overall':
            sql= """SELECT COALESCE(sum(fee_amount),'0') as fee_amount from smsfee_studentfee
                            inner join smsfee_classes_fees_lines 
                            on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                            inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                            where smsfee_studentfee.state = '""" +str(return_choice)+"""'
                            and smsfee_studentfee.student_id = """+str(student_id)
        else:
            sql= """SELECT COALESCE(sum(fee_amount),'0') as fee_amount from smsfee_studentfee
                            inner join smsfee_classes_fees_lines 
                            on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                            inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                            where smsfee_feetypes.category = '""" +fee_category+"""'
                            and smsfee_studentfee.state = '""" +str(return_choice)+"""'
                            and smsfee_studentfee.student_id = """+str(student_id)
                            
        cr.execute(sql)
        rec = cr.fetchone() 
        return int(rec[0])

    
    def get_student_fees_lines(self, cr, uid, student_id,fee_category,return_choice):
        """
        --This method returns studentfeeslines(paid,unpaid or both) from table (smsfee_studentfee)
        --para, return_choice may have one of the values (fee_paid,fee_unpaid,paid_and_unpaid)
        --param fee_category: Academics, Transport,Overall   
        --called by: 1) sms_collaborator for portal
        """
        if return_choice == 'paid_and_unpaid':
            sub_query = """ and smsfee_studentfee.state in ('fee_paid','fee_unpaid') """
        else:
            sub_query = """ and smsfee_studentfee.state =  '"""+str(return_choice)+"""' """
       
#         if class_id:
#             class_query = """ and smsfee_studentfee.acad_cal_id= """+str(class_id)
#         else:
#             class_query = """ """
        if fee_category == 'Overall':
            sql= """SELECT  smsfee_studentfee.id,smsfee_feetypes.name,smsfee_studentfee.fee_amount,smsfee_studentfee.state  from smsfee_studentfee
                            inner join smsfee_classes_fees_lines 
                            on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                            inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                            where 
                             smsfee_studentfee.student_id = """+str(student_id)+sub_query
        else:
            sql= """SELECT smsfee_studentfee.id,smsfee_feetypes.name,smsfee_studentfee.fee_amount,smsfee_studentfee.state  from smsfee_studentfee
                            inner join smsfee_classes_fees_lines 
                            on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                            inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                            where smsfee_feetypes.category = '""" +fee_category+"""'
                            and smsfee_studentfee.student_id = """+str(student_id)+sub_query
                            
        print "sql::::::::",sql
        cr.execute(sql)
        rec = cr.fetchall() 
        return rec



        
    def set_paybles(self, cr, uid, ids, context={}, arg=None, obj=None):
        # temproray inner joins are used to get to fee cateogry of fee ttype, when fee strucre of student fee table is refined, one inner joiin will be removed
        result = {}
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            sql =   """SELECT  COALESCE(sum(fee_amount),'0')  FROM smsfee_studentfee
                     inner join smsfee_classes_fees_lines on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                        inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                     WHERE student_id = """+str(f.id)+""" AND smsfee_feetypes.category='Academics'  AND state='fee_unpaid'"""
            cr.execute(sql)
            amount = float(cr.fetchone()[0])
        result[f.id] = amount
        return result
    
    def set_paid_amount(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        records =  self.browse(cr, uid, ids, context)

        for f in records:
            sql =   """SELECT COALESCE(sum(fee_amount),'0')  FROM smsfee_studentfee
                     WHERE student_id ="""+str(f.id)+"""  AND state='fee_paid'"""
            cr.execute(sql)
            amount = float(cr.fetchone()[0])
        result[f.id] = amount
        return result

    def get_student_fee_views(self, cr, uid, ids, field_names, arg=None, context=None):
        """This was clients requirements to show academis and transport ,and hostel etc fee separately, we made this method to use in 
           each module, this will be called by relavent columns to show fee history of one module only, here this method shows fee
           hisotry for academics only """

        records = self.browse(cr,uid,ids)
        res = {}
        for f in records:

            sql =   """ SELECT  smsfee_studentfee.id  FROM smsfee_studentfee
                       inner join smsfee_classes_fees_lines on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                        inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                     WHERE smsfee_studentfee.student_id = """+str(f.id)+""" AND smsfee_feetypes.category='Academics' order by smsfee_feetypes.id, fee_month  """
            cr.execute(sql)
            res[f.id] = [x[0] for x in cr.fetchall()]
#         raise osv.except_osv((res), (sql))
          
        return res
    #sms_student    
    _name = 'sms.student'
    _inherit ='sms.student'
        
    _columns = {
            'discount_ids': fields.one2many('smsfee.discount', 'student_id', 'Student Discount'),
            'discount_given': fields.boolean('Give Discount'),
            'discount_reason': fields.char(string='Reason of Discount', size=100),
            'studen_fee_ids':fields.one2many('smsfee.studentfee', 'student_id','Student Fee'),
            'refundable_fee_ids':fields.one2many('smsfee.studentfee.refundable', 'student_id','Refundable Fees'),
            'view_academics_fee': fields.function(get_student_fee_views, method=True, type='one2many', relation='smsfee.studentfee', string='Academic Fee'),
            'fee_bills':fields.one2many('smsfee.receiptbook', 'student_id','Fee Bills' ),
            'latest_fee':fields.many2one('sms.session.months','Fee Register'),
            'total_paybles':fields.function(set_paybles, method=True, string='Balance', type='float'),
            'disp_cntct_prtal':fields.boolean('Display Student Contacts?'),
            'total_paid_amount':fields.function(set_paid_amount, method=True, string='Total Paid', type='float', size=300),
            'exammark_prtal':fields.boolean('Show Exam Marks?'),
            'info_portal':fields.boolean('Show Personal Information?'),
            'fee_structure_history_ids':fields.one2many('smsfee.structure.history', 'student_id', 'Fee Structure History')
          
            }
    _defaults = {
        'discount_given': False,
        }
sms_student()

# <-----  Added by Obaid  ---------->

class smsfee_structure_history(osv.osv):
    _name = 'smsfee.structure.history'
    
    _columns = {
        'student_id':fields.many2one('sms.student','Student'),
        'name': fields.char('Fee Structure Name'),
        'assignment_date': fields.date('Assignment Date'),
        'deallocation_date': fields.date('Deallocation Date'),
        'assigned_by': fields.char('Assigned By')
                }
    
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
    
    def update_if_exists_or_create_ft(self, cr, uid, academiccalendar_id, fee_structure_id, fee_types):
        #------------ Creating fee structure for class -------------------
        if type(fee_types[0]['feetype_id']) is not list:
            fee_types[0]['feetype_id'] = [fee_types[0]['feetype_id']]
        
        cls_fees_id = self.pool.get('smsfee.classes.fees').search(cr, uid, [('academic_cal_id','=', academiccalendar_id), ('fee_structure_id','=', fee_structure_id)])
        if cls_fees_id:
                #--------------- This method search for a particular fee type(smsfee.feetype.id) in smsfee_classes_fees_lines -------------
                #--------------- If record is found, updates it with new amount other wise create new fee structure, under classes_fees_id as parent -----------
            cls_fees_line_id = self.pool.get('smsfee.classes.fees.lines').search(cr,uid,[('parent_fee_structure_id','=',cls_fees_id[0]),('fee_type','in', fee_types[0]['feetype_id'])])
            #---------------- Fee type also exists, don't worry, update it with new values of revision fee structure lines fee types ---------------------
            #---------------- 2 kinds of changes, one is to change only amount , while fee type remains the same change is change fee type id, it needs more discussion, leave it to future ------------------
            if cls_fees_line_id:
                cls_fees_line_obj = self.pool.get('smsfee.classes.fees.lines').browse(cr, uid, cls_fees_line_id)
                for feetype in fee_types:
                    for child_rec in cls_fees_line_obj: 
                        if feetype['feetype_id'] == [child_rec.fee_type.id]:
                            self.pool.get('smsfee.classes.fees.lines').write(cr, uid, cls_fees_line_id, {
                                                                                                 'amount': feetype['amount']
                                                                                                 })
                        elif feetype['feetype_id'] != [child_rec.fee_type.id]:
                            cls_fee_lines_id = self.pool.get('smsfee.classes.fees.lines').search(cr,uid,[('parent_fee_structure_id','=',cls_fees_id[0]),('fee_type','=', feetype['feetype_id'])])
                            if not cls_fee_lines_id:
                                if type(feetype['feetype_id']) is list:
                                    feetype_id = feetype['feetype_id'][0]
                                else:
                                    feetype_id = feetype['feetype_id']
                                self.pool.get('smsfee.classes.fees.lines').create(cr,uid,{
                                                                                    'parent_fee_structure_id': cls_fees_id[0], #obtained from searching classes fees
                                                                                    'fee_type': feetype['feetype_id'], #obtained from revision feetypes object. new ft is added, 
                                                                                    'amount': feetype['amount'], #obtained from revision fee types object.
                                                                                    })
                            return True
            else:
                for feetype in fee_types:
                    if type(feetype['feetype_id']) is list:
                        feetype_id = feetype['feetype_id'][0]
                    else:
                        feetype_id = feetype['feetype_id']
                    self.pool.get('smsfee.classes.fees.lines').create(cr,uid,{
                                                                        'parent_fee_structure_id': cls_fees_id[0], #obtained from searching classes fees
                                                                        'fee_type': feetype_id, #obtained from revision feetypes object. new ft is added, 
                                                                        'amount': feetype['amount'], #obtained from revision fee types object.
                                                                        })
            return True
        else:
            
            print 'no fee found creating new fee'
            # this fee type does not exists in fee lines object
            # seems this fee types is newly added to fee revision object
            # now add this fee type to actual smsfee.classes.fee.lines
            parent_record_id = self.pool.get('smsfee.classes.fees').\
                                                                    create(cr, uid, {'academic_cal_id':academiccalendar_id,
                                                                                     'fee_structure_id':fee_structure_id,
                                                                                     'active':True})
            if parent_record_id:
                
                
                for feetype in fee_types:
                    if type(feetype['feetype_id']) is list:
                        feetype_id = feetype['feetype_id'][0]
                    else:
                        feetype_id = feetype['feetype_id']
                    self.pool.get('smsfee.classes.fees.lines').create(cr, uid, 
                                                                       {'parent_fee_structure_id': parent_record_id, #obtained from searching classes fees
                                                                        'fee_type': feetype_id, #obtained from revision fetypes object. new ft is added, 
                                                                        'amount': feetype['amount'], #obtained from revision fetypes object.
                                                                        })
        return True

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
        'academic_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar'),      
        'fee_structure_id': fields.many2one('sms.feestructure','Fee Structure',required = True),
        'no_of_students':fields.function(get_fs_std_qty, method=True,  string='Applies on (#Students)',type='integer'),
        'focasted_amount':fields.function(forcasted_amount, method=True,  string='Forcasted',type='float'),
        'collected_amout':fields.function(collected_amout, method=True,  string='Collection',type='float'),
    }
    _sql_constraints = [('Class_fee_unique', 'unique (academic_cal_id, fee_structure_id, fee_type_id)', """ Class Fee is already Defined Remove Duplication..""")]
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
    #smsfee_classes_fees_lines
    _name = 'smsfee.classes.fees.lines'
   
    _description = "Stores classes fee"
    _order = "fee_type"
    _columns = {
        'name':fields.function(_set_name, method=True,  string='Fee',type='char'),
        'parent_fee_structure_id': fields.many2one('smsfee.classes.fees','Fee Structure'),
        'fee_type': fields.many2one('smsfee.feetypes','Fee Type',required = True),
        'amount':fields.float('Amount'),
    }
    _sql_constraints = [('Class_fee_unique', 'unique (parent_fee_structure_id,fee_type)', """ Class Fee is already Defined Remove Duplication..""")]
smsfee_classes_fees_lines()


class smsfee_discounts(osv.osv):
    
    """ adds discounts for individual students based on  their fee structure """
    
    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)
        return result
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result
        
    def onchange_get_actual_fee(self, cr, uid, ids, student_id, fee_type, context=None):
        student = self.pool.get('sms.student').browse(cr ,uid , student_id)
        cls_fee_id = self.pool.get('smsfee.classes.fees').search(cr ,uid ,[('fee_structure_id','=',student.fee_type.id ),('academic_cal_id','=',student.current_class.id)])
        fee_id = self.pool.get('smsfee.classes.fees.lines').search(cr ,uid ,[('parent_fee_structure_id','=',cls_fee_id ),('fee_type','=',fee_type)])

        actual_fee = 0
        if (fee_id):
            rec = self.pool.get('smsfee.classes.fees.lines').browse(cr ,uid ,fee_id[0])
            actual_fee = rec.amount

        val = {'actual_fee':actual_fee}
        return {'value': val}

    def onchange_get_discounted_fee(self, cr, uid, ids, discount, actual_amount, context=None):
        if discount > 100 or discount < 0:
            warning = {
                       'title': 'Warning!',
                       'message' : 'Discount should be between 0 and 100'
                      }
            
            return {'warning': warning}

        discounted_fee = actual_amount - (discount * actual_amount/100)

        val = {'discounted_fee': discounted_fee}
        return {'value': val}

    
    _name = 'smsfee.discount'
   
    _description = "Gives discounts to the students"
    _columns = {
        'student_id': fields.many2one('sms.student', 'Student Id'),
        'fee_type': fields.many2one('smsfee.feetypes','Fee Type',required=True),
        'actual_fee': fields.float('Actual Fee'),
        'discount': fields.float('Discount (%)'),
        'discounted_fee':fields.float('Discounted Fee'),
    }
    _defaults = {
        'actual_fee': 0,
        'discount': 0,
        'discounted_fee':0,
        'student_id': lambda self, cr, uid, context: context.get('student_id', False),
    }

    _sql_constraints = [('fee_type_unique', 'unique (student_id,fee_type)', """ Fee type is already Defined Remove Duplication..""")]

smsfee_discounts()


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
        'name':fields.function(_set_name, method=True,  string='Fee',type='char'),
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
    
    #smsfee_feetypes
    _name = 'smsfee.feetypes'
    _description = "This object store fee types"
    _columns = {
        'name': fields.char(string = 'Fee Type',size = 100,required = True),
        'fs_id':fields.many2one('sms.feestructure'),      
        'description': fields.char(string = 'Description',size = 100),
        'subtype': fields.selection([('Monthly_Fee','Monthly Fee'),('at_admission','Charged at The Time of Admission'),('Promotion_Fee','Promotion Fee'),('Annual_fee','Annual Fee'),('Refundable','Refundable'),('Other','Other')],'Repetition',required = True),
        'category':fields.selection([('Academics','Academics'),('Transport','Transport'),('Hostel','Hostel'),('Stationary','Stationary'),('Portal','Portal')],'Fee Category',required=True),
        'display_sequence':fields.integer('Display Order'),
        'refundable':fields.boolean('Refundable')
    }
    _sql_constraints = [  
        ('Fee Exisits', 'unique (name)', 'Fee Already exists!')
    ] 
smsfee_feetypes()

class smsfee_studentfee(osv.osv):
        
    """ Stores student fee record
        it stores both academic and transport fees
        this obnject stores transport aslo
        """
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        #*00*************create log for updation in student fee**************************
        
        if type(ids) is list:
            _ids = ids[0]
        else:
            _ids = ids
        for k,v in vals.iteritems():
            sql = """ select """ +str(k)+ """ from smsfee_studentfee where id ="""+str(_ids)+ """
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

    def _set_std_fee(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            month_name = f.fee_month.name
            if f.generic_fee_type.subtype == 'Monthly_Fee':
                year = f.fee_month.name
                string = str(f.fee_type.name) + " (" + str(month_name) + ")"
            else:
                string = str(f.fee_type.name) + " (" + str(month_name) + ")//"
            result[f.id] = string
        return result

    def getfee_cate(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = f.fee_type.fee_type.category
        return result
    def getfee_cate(self, cr, uid, ids, fields,args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = f.generic_fee_type.category
        return result

    
    def get_student_total_paybles(self, cr, uid, ids, acad_std_id,context=None):
        
        sql = """SELECT COALESCE(sum(net_total),'0') FROM smsfee_studentfee WHERE student_id ="""+str(ids)+"""
        AND acad_cal_std_id="""+str(acad_std_id)+"""AND net_total > 0 AND state= 'fee_unpaid'"""
        cr.execute(sql)
        bal = cr.fetchone()
        print "get student total paybles",bal
        return bal[0]
    
    def insert_student_monthly_non_monthlyfee(self, cr, uid, std_id, acad_cal, fee_type_row, month):
        """This method will insert student monthly and non monthly fee 
           only when called in loop or without loop (admit student,re-admit student,student promotion and other wizards wlil call it)
           Currently called by 
           1) update_monthly_feeregister() class:sms_session_months
           2) called by admission register
           3)called by promotion process
           4) called by advance fee management
           5) adding a single student fee doesont use this method becuase it ignores fee type row
           later on we will udpate this method and we will remove use of fee_type_row if feasible, only generic fee_id will be used
           
           admin
           """
       
        fee_already_exists =  self.pool.get('smsfee.studentfee').search(cr, uid,[('acad_cal_id', '=', acad_cal), ('student_id', '=', std_id), ('fee_type', '=', fee_type_row.id), ('due_month', '=', month)])
        print "Fee Exists_____________",fee_already_exists
        if not fee_already_exists:
            print"Under the if condition "
            # at this stage is assued that fee month and dues month are same for all cases, due month may change in exceptional cases, i.e when fee of all prevoius
            #month is registered in current month against a student, this case due month for all fees will be current month to avoid fine,
            fee_month = month
            due_month = month

            fee_amount = fee_type_row.amount
         
            
            # If discount is given to the student, update the fee_amount
            sql = """SELECT discount_given FROM sms_student WHERE id ="""+str(std_id)+""""""
            cr.execute(sql)
            discount_given = cr.fetchone()[0]

            if discount_given is True:
              
                discount_fee_ids = self.pool.get('smsfee.discount').search(cr ,uid ,[('student_id','=',std_id),('fee_type','=',fee_type_row.fee_type.id)])
          
                if discount_fee_ids:

                    discount_fee = self.pool.get('smsfee.discount').browse(cr,uid, discount_fee_ids[0])
                    fee_amount = discount_fee.discounted_fee
                    full_amount = discount_fee.discounted_fee
                    print "Student id and discounted fee",str(std_id),fee_amount
                    print "Student id and Full fee",str(std_id),full_amount
            fee_dcit= {
                        'student_id': std_id,
                        'acad_cal_id': acad_cal,
                        'fee_type': fee_type_row.id,
                        'date_fee_charged':datetime.date.today(),
                        'due_month': due_month,
                        'fee_month': fee_month,
                        'paid_amount':0,
                        'fee_amount': fee_amount,  
                        'late_fee':0,
                        'discount':0,
                        'total_amount':fee_amount + 0, 
                        'reconcile':False,
                        'state':'fee_unpaid'
                     }
           
            create_fee = self.pool.get('smsfee.studentfee').create(cr, uid, fee_dcit) 
          
            if create_fee:
        
                return True
            else:
                return False
        else:
                print"False False False False False False False False False False False False"
                return False      
    
            
    def _get_total_payables(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             result[f.id] = f.late_fee + f.fee_amount
        return result
    
    def set_refundable_fee(self, cr, uid, booklines_rw):
        """ this method is called when student fee is received, this methods accepts receptbooklines reocrd full row as argument
            a) it check if the recived fee is refundable then it creates an entry in student table of refundable fees. """
#         raise osv.except_osv(('called2'), (booklines_rw))
        if booklines_rw.student_fee_id.fee_type.fee_type.refundable ==True:
            add_fee = self.pool.get('smsfee.studentfee.refundable').create(cr,uid,{
                                        'student_id':booklines_rw.student_fee_id.student_id.id,
                                        'receipt_no':booklines_rw.receipt_book_id.id,
                                        'amount_received':booklines_rw.paid_amount,
                                        'amount_paid_back':0,
                                        'student_fee_id':booklines_rw.student_fee_id.id,
                                        'state':'to_be_paid',
                    
                    })  
        return 
    
    def onchange_set_domain(self, cr, uid,ids,student_id,context):
        val = {}
        #~~~~~~~~~~~~~get class name~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if student_id:
            acd_cal_stu = self.pool.get('sms.academiccalendar.student').search(cr ,uid ,[('std_id','=',student_id)])
            clss_id = self.pool.get('sms.academiccalendar').search(cr ,uid ,[('acad_cal_students','=',acd_cal_stu),('state','=','Active')])
            if clss_id:
                rec = self.pool.get('sms.academiccalendar').browse(cr ,uid ,clss_id)[0]
                val['acad_cal_id'] = rec.id
            else:
                raise osv.except_osv(('Denied'), ('The status of the selected student class is not active.'))        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        rec = self.pool.get('sms.student').browse(cr ,uid ,context['student_id'])
        cls_fee_id = self.pool.get('smsfee.classes.fees').search(cr ,uid ,[('fee_structure_id','=',rec.fee_type.id ),('academic_cal_id','=',rec.current_class.id)])
        return {'domain': {'fee_type': [('parent_fee_structure_id', '=', cls_fee_id)]},
                'value':val }

    def onchange_get_amount(self, cr, uid,ids,fee_type):
        cls_fee = self.pool.get('smsfee.classes.fees.lines')
        rec = cls_fee.browse(cr ,uid ,fee_type)
        val = {'fee_amount':rec.amount,'state':'fee_unpaid','date_fee_charged': time.strftime('%Y-%m-%d'),}
        return {'value': val}
    def onchange_fee_month(self, cr, uid,ids,fee_month):
        print 'works_fee'
        val={}
        print('change_month',fee_month)
        months_fee = self.pool.get('sms.session.months')
        rec = months_fee.browse(cr ,uid ,fee_month)
        val['fee_month']=fee_month
        return {'value': val}

    def create(self, cr, uid, vals, context=None, check=True):
        result = super(osv.osv, self).create(cr, uid, vals, context)
        if result:
            rec = self.browse(cr ,uid ,result)
            if rec.state == False or rec.date_fee_charged == False:
                self.write(cr ,uid ,result ,{'state':'fee_unpaid','date_fee_charged': time.strftime('%Y-%m-%d')})
        return result
    _SELECTION = [
    ('Academics', 'Academics'),
    ('Transport', 'Transport'),
    ('Hostel', 'Hostel'),
    ('Stationary', 'Portal'),
    ('Portal', 'Portal')]
    
    def get_display_order(self, cr, uid, ids, name, args, context=None):
        """This method retruns the sequnece of parent class of this record. that will be use to order the list record of acad cal"""
        res = {}
        for f in self.browse(cr, uid, ids, context):
            if f.fee_type.id:
                res[f.id] = f.fee_type.fee_type.display_sequence
        return res

    #smsfee_studentfee
    _name = 'smsfee.studentfee'
    _description = "Stores student fee record"
    _order = 'display_order,due_month'
    _columns = {
        'name':fields.function(_set_std_fee, method=True,  string='Student Fee',type='char'),
        'receipt_no':fields.many2one('smsfee.receiptbook','Receipt No'),
        'student_id':fields.many2one('sms.student','Student'),
        'acad_cal_id': fields.many2one('sms.academiccalendar','Academic Calendar'),
        'acad_cal_std_id': fields.many2one('sms.academiccalendar.student','Academic Calendar Student'),  
        'date_fee_charged':fields.date('Date Fee Charged'),
        'date_fee_paid':fields.date('Date Fee Paid'),
        'fee_type':fields.many2one('smsfee.classes.fees.lines','Fee Type'),
        'category':fields.function(getfee_cate, method=True,  string='Category',type='selection', selection=[('Academics','Academics'),('Transport','Transport'),('Hostel','Hostel'),('Stationary','Stationary'),('Portal','Portal')],store=True),
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
        'verified': fields.boolean('Verified'),
        'display_order':fields.function(get_display_order, store=True, string='display order', type='integer'),
        'state':fields.selection([('fee_exemption','Fee Exemption'),('fee_unpaid','Fee Unpaid'),('fee_paid','Fee Paid'),('fee_returned','Fee Returned'),('Deleted','Deleted')],'Fee Status',readonly=True),
        'class_changed':fields.boolean('Class Changed'),
        #------------total payables---------------------------------
        'total_payable': fields.function(_get_total_payables,string = 'Total Payable',type = 'integer',method = True,store = True),
    }
     
    _defaults = {
        'reconcile': False,
        'class_changed':False,
        'student_id': lambda self, cr, uid, context: context.get('student_id', False),
    }
smsfee_studentfee()

#===== Refundabble fee objects

class smsfee_studentfee_refundable(osv.osv):
    def calculate_balance(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
            result[f.id] = int(f.amount_received - f.amount_paid_back)
        return result
    
    _name = 'smsfee.studentfee.refundable'    
    _columns = {
        'name':fields.many2one('smsfee.feetypes','Fee Type', domain="[('refundable','=',True)]"),
        'receipt_no':fields.many2one('smsfee.receiptbook','Receipt No'),
        'student_id':fields.many2one('sms.student','Student'),
        'amount_received':fields.integer('Amount Received'),
        'amount_paid_back':fields.integer('Paid Amount'),
        'paid_back_by': fields.many2one('res.users','Refunded By'),
        'date_paid_back_date': fields.datetime('Refunded On'),
        'student_fee_id': fields.many2one('smsfee.studentfee','Fee Register'),
        'balance': fields.function(calculate_balance,string = 'Balance.',type = 'integer',method = True),   
        'state':fields.selection([('to_be_paid','To be Paid Back'),('paid_back','Paid To Student'),('adjusted','Adjusted')],'Status',readonly=True),
        #------------total payables---------------------------------
    }
     
    _defaults = {
    }
smsfee_studentfee_refundable()



#==== End of refunable fee oabject




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
            
    def onchange_student(self, cr, uid, ids, std, context=None):
        result = {}
        std_rec = self.pool.get('sms.student').browse(cr, uid, std)
        print "stddddddddddd",std
        print "std rec",std_rec
        if std:
            result['fee_structure'] = std_rec.fee_type.name
            result['father_name'] = std_rec.father_name

        return {'value':result}
        

    def _set_req_no(self, cr, uid, ids, name, args, context=None):
        result = {}
        for f in self.browse(cr, uid, ids, context=context):
             ftyp = "W-"+str(ids[0])
             result[f.id] = ftyp
        return result
    
    def on_change_registration_no(self, cr, uid, ids, registration_no, context=None):
        result = {}
        rec = self.pool.get('sms.student').search(cr, uid, [('registration_no','=',registration_no)])
        if rec:
            student = self.pool.get('sms.student').browse(cr, uid, rec[0])
            result["student_id"] =  student.id
            result["student_class_id"] = student.current_class.id
            result['total_dues'] = student.total_paybles + student.total_paybles_transport
        else:
            result["student_id"] =  None
            result["student_class_id"] = None
            result['total_dues'] = None
            raise osv.except_osv(('Invalid Reg No'), ('No Student Found With Given Reg no'))
        return {'value' : result}

    _name = 'smsfee.std.withdraw'
    _description = "This object store fee types"
    _columns = {
        'name': fields.function(_set_req_no,string = 'Request No.',type = 'char',method = True,store = True),   
        'registration_no': fields.char('Registration No'),
        'request_date': fields.date('Date'),
        'request_by': fields.many2one('res.users','Decision By'),
        'decision_date': fields.date('Date'),
        'decision_by': fields.many2one('res.users','Decision By'),
        'fee_structure': fields.char(string = 'Fee Structure',size = 100),
        'student_class_id': fields.many2one('sms.academiccalendar','Class',required = True),
        'student_id': fields.many2one('sms.student','Student',required = True),
        'father_name': fields.char(string = 'Father',size = 100,readonly = True),
        'reason_withdraw':fields.text('Reason Withdraw'),
        'request_type':fields.selection([('Withdraw','Withdraw'),('admission_cancel','Admission Cancel'),('drop_out','Drop Out'),('slc','School Leaving Certificate'), ('transfer_out','Transfer Out')],'Request Type'),
        'transfer_type':fields.selection([('temporiry','Temporiry'),('permanent','Permanent')],'Transfer Type'),
        'transfer_campus': fields.many2one('sms.transfer.in', 'Campus'),
        'transfer_fee': fields.float('Transfer Fee'),
        'total_dues': fields.float('Total Dues'),
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
    
    def _set_bill_no(self, cr, uid, session_id, fee_month, module):
        #first generate sequnce no
        today = datetime.date.today()
        month = datetime.datetime.strptime(str(today), '%Y-%m-%d').strftime('%m') 
        year = datetime.datetime.strptime(str(today), '%Y-%m-%d').strftime('%Y') 
        
        """ The following query is working pefectly only when deletion is not allowed on receipbook in any case
            if dletion is allwoed, then count will generate duplicated value,"""
        sql =   """SELECT  COALESCE(count(id),'0')  FROM smsfee_receiptbook
                     WHERE session_id ="""+str(session_id)
        cr.execute(sql)
        counter1 = int(cr.fetchone()[0]) + 1
        counter = str(counter1) +"-"+str(month)+str(year)
        return counter
    
           
    def create(self, cr, uid, vals, context=None, check=True):
         
        result = super(osv.osv, self).create(cr, uid, vals, context)
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
        for f in self.browse(cr, uid, ids, context):
            
            brows =   self.browse(cr, uid, ids, context)
            unlink = self.unlink_lines(cr, uid,ids[0],None)
            student = brows[0].student_id.id
            self.onchange_student(cr, uid, ids, None)
            self.write(cr, uid, ids[0], {'student_id':student,'name':int(12)})    
           
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
        if rec[0].student_class_id.name == None:
            self.write(cr ,uid ,ids ,{'student_class_id':rec[0].student_id.current_class.id,
                                      'father_name':rec[0].student_id.father_name,
                                      'fee_structure':rec[0].student_id.fee_type.name
                                      })
        paymethod = ''
        receipt_date = ''
        for f in rec:
            stdname = self.pool.get('sms.student').browse(cr, uid, f.student_id.id).name
            paymethod = f.payment_method
            receipt_date = f.receipt_date
                
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
                           'fee_approved_by':uid,
                           'approve_date':datetime.date.today(),
                           'total_paid_amount':total_paid_amount +float(f.late_fee) ,
                           'state':'Paid',
                           })
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
            search_booklines = self.pool.get('smsfee.receiptbook.lines').search(cr, uid, [('receipt_book_id','=',ids[0])], context=context) 
            print "serarched ids to delete ",search_booklines
            if search_booklines:
               rec_booklines = self.pool.get('smsfee.receiptbook.lines').browse(cr,uid,search_booklines) 
               for booklin_id in rec_booklines:
                   if not booklin_id.reconcile:
                       self.pool.get('smsfee.receiptbook.lines').unlink(cr,uid,booklin_id.id)
                   else:
                       #call method ro record refundable fees
                       set_refund = self.pool.get('smsfee.studentfee').set_refundable_fee(cr, uid,booklin_id)
                    
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
    
    def send_for_approval(self, cr, uid, ids, context=None):
        rec = self.browse(cr, uid, ids, context)
        for f in self.browse(cr, uid, ids, context):
            print("f in send_for_approval",f)

        search_lines_id = self.pool.get('smsfee.receiptbook.lines').search(cr, uid,
                                                                               [('receipt_book_id', '=', ids[0])],
                                                                               context=context)
        lines_obj = self.pool.get('smsfee.receiptbook.lines').browse(cr, uid, search_lines_id)
        generate_receipt = False
        total_paid_amount = 0
        for line in lines_obj:

            std_fee_id = line.student_fee_id.id
            late_fee = 0

            if line.reconcile:
                total_paid_amount = total_paid_amount + line.paid_amount
                generate_receipt = True
                update_std_fee_obj = self.pool.get('smsfee.studentfee').write(cr, uid, std_fee_id, {
                    'late_fee': late_fee,
                    'paid_amount': line.paid_amount,
                    'date_fee_paid': datetime.date.today(),
                    'discount': line.discount,
                    'net_total': line.net_total,
                    'reconcile': line.reconcile,
                    'receipt_no': str(ids[0]),
                    'state': 'fee_paid',
                    'verified':True
                    })

            #-------------------------------------------------------------------
            self.write(cr, uid, ids[0], {'state':'Waiting_Approval','fee_received_by':uid,'date_receivd_onsystem':datetime.datetime.now()})
        return
    
    def send_back_for_correction(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state':'fee_calculated'})
        return
    
    
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
    
    def change_date_format(self, cr, uid, ids, context={}, arg=None, obj=None):
        #this mehod is temporarily added, this converted date formate for payment date entered by
        #user when sending challans for approvals
        result = {}
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            if f.id:
                sql = """SELECT receipt_date from smsfee_receiptbook where id= """+str(f.id)
                cr.execute(sql)
                rdate = cr.fetchone()[0]
                date_convt = datetime.datetime.strptime(str(rdate) , '%Y-%m-%d')
                date_str = str(date_convt.strftime('%d-%b-%Y'))
                result[f.id] = date_str
            else:
                result[f.id] = '--'
        return result
    
    def cancel_fee_bill(self, cr, uid, ids, context={}, arg=None, obj=None):
        result = {}
        records =  self.browse(cr, uid, ids, context)
        for f in records:
            self.write(cr, uid, f.id, {'state':'Cancel','challan_cancel_by':uid})  
        return result
    
    def check_fee_challans_issued(self, cr, uid, class_id, student_id, category, challan_type, month_ids):
        # Date 7 may 2017
        #this objects will generate challans if challans are not exists
        # the same method will be used by all modules, may be one more argument will be added, module_id e.g categoty id
        # the challan cration method of transport will be delted, transport will also call this method
        # challan category will be used in the case when separate challans tp ne printed for each category, we can keep this setting 
        # in res company wheter to print combine challans or separate (this code is not currently set for combine challans .13 may 2017)
        result = {}
        fee_ids = []
        if month_ids:
            month_str = str(tuple(month_ids))
            month_str = "AND smsfee_studentfee.fee_month in " + month_str.replace(',)', ')')
        else:
            month_str = """"""
            
        sql = """SELECT distinct smsfee_studentfee.id from smsfee_studentfee
                  inner join smsfee_classes_fees_lines on smsfee_classes_fees_lines.id = smsfee_studentfee.fee_type
                  inner join smsfee_feetypes on smsfee_feetypes.id = smsfee_classes_fees_lines.fee_type
                  where smsfee_feetypes.category = '"""+str(category)+"""'
                  and smsfee_studentfee.student_id = """+str(student_id)+ """ and smsfee_studentfee.state ='fee_unpaid'""" + month_str
        
        cr.execute(sql)
        _ids = cr.fetchall()
        print sql
        for thisfee in _ids:
            fee_ids.append(thisfee[0])
            print "transport fees found ids..............................................:",thisfee

        #fee_ids = self.pool.get('smsfee.studentfee').search(cr ,uid ,[('student_id','=',226),('state','=','fee_unpaid'),('category','=','Transport')])
#         raise osv.except_osv((_ids), (fee_ids))
        if fee_ids:
            #currenlt cancel all other challans of this student where they are with whatever amount
            #then we can enhance the code that if users asks to cancel the challans , other wise it will print old challan
            # another check will also be imposed if amount of curenlt created challans is greater than old challans, then that case , all other challans will be canceld
            challan_ids = self.pool.get('smsfee.receiptbook').search(cr, uid,
                                                                     [('student_id','=',student_id),
                                                                      ('state','=','fee_calculated'),
                                                                      ('challan_cat','=',category)])
            print "we are canceling challans:",challan_ids
            if challan_ids:
                for challan_id in challan_ids:
                    note="this fee bill is cancel by system on creation of new fee bill on date",datetime.datetime.now()
                    self.pool.get('smsfee.receiptbook').write(cr ,uid ,challan_id, {'state':'Cancel',
                                                                                    'note_at_receive':note,
                                                                                    'cancel_date':datetime.datetime.now()
                                                                                    })
                    
                #---------------------- if old_val is not equal to new_val than create reciept -----------------------------
                
            total_paybles = 0
            if type(student_id) is list:
                student_id = student_id[0]
            session_id = self.pool.get('sms.student').browse(cr, uid, student_id).current_class.acad_session_id.id
            counter = self._set_bill_no(cr, uid,session_id,None,None)
            print "priting for challan category:for parent challan",category
            receipt_id = self.pool.get('smsfee.receiptbook').create(cr ,uid , {'student_id':student_id,
                                                                              'student_class_id':class_id,
                                                                              'counter':counter,
                                                                              'challan_cat':category,
                                                                              'challan_type':challan_type,
                                                                              'state':'fee_calculated',
                                                                              'receipt_date':datetime.date.today(),
                                                                              'session_id' :session_id})
            std_unpaid_fees = self.pool.get('smsfee.studentfee').browse(cr ,uid ,fee_ids)
            print "challan created or not:",receipt_id
            if receipt_id:
                print "total  fee records found:",len(fee_ids)
                for unpaidfee in std_unpaid_fees:
                    print "creating challans for fee.................................................. ",unpaidfee
                    total_paybles = total_paybles + unpaidfee.fee_amount
                    feelinesdict = {
                    'fee_type': unpaidfee.fee_type.id,
                    'student_fee_id': unpaidfee.id,
                    'fee_month': unpaidfee.fee_month.id,
                    'receipt_book_id': receipt_id,
                    'fee_amount':unpaidfee.fee_amount,
                    'late_fee':0,
                    'total':unpaidfee.fee_amount}
                    print "book line dic ",feelinesdict
                    self.pool.get('smsfee.receiptbook.lines').create(cr ,uid,feelinesdict)
        return True
     
    #smsfee_receiptbook
    _name = 'smsfee.receiptbook'
    _description = "This object store fee types"
    _inherit = ['mail.thread']
    _order = "id desc"
    
    _columns = {
        'name': fields.char('Bill No', readonly =True,size=15), 
        'counter': fields.char('Bill No.', readonly =True,size=15),    
        'challan_cat':fields.selection([('Academics','Academics'),('Transport','Transport'),('Hostel','Hostel'),('Stationary','Stationary'),('Portal','Portal')],'Fee Category',readonly=True),
        'session_id':fields.many2one('sms.academics.session', 'Session'),
        'fee_structure': fields.char(string = 'Fee Structure',size = 100),
        'manual_recpt_no': fields.char(string = 'Manual Receipt No',size = 100),
        'student_class_id': fields.many2one('sms.academiccalendar','Class'),
        'student_id': fields.many2one('sms.student','Student',required = True),
        'father_name': fields.char(string = 'Father',size = 100),
        'payment_method':fields.selection([('Cash','Cash'),('Bank','Bank')],'Payment Method'),
        'total_paybles':fields.function(set_recvbles, string='Total', type ='float', method =True), 
        'total_paid_amount':fields.float('Paid Amount',readonly = True),
        'note_at_receive': fields.text('Note'),
        'receive_whole_amount': fields.boolean('Receive Whole Amount'),
        'state': fields.selection([('Draft', 'Draft'),('fee_calculated', 'Open'),('Waiting_Approval', 'To Be Approved'),('Paid', 'Paid'),('Cancel', 'Cancel'),('Adjusted', 'Paid(Adjusted)')], 'State', readonly = True, help='State'),
        'fee_received_by': fields.many2one('res.users', 'Received By'),
        'fee_approved_by': fields.many2one('res.users', 'Approved By'),
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
        'std_reg_no': fields.related('student_id','registration_no',type='char',relation='sms.student', string='Registration Number', readonly=True),
        'challan_type':fields.selection([('Full','Full'),('Partial','Partial')],'Challan Type'),
        'receipt_date': fields.date('Payment Date'),
        'payment_date':fields.function(change_date_format, string='Payment Date.', type ='char', method =True),
        'date_receivd_onsystem':fields.datetime('Received on', readonly =True),
        'approve_date': fields.datetime('Date Approved',readonly=True),
    }
    _sql_constraints = [  
        #('Fee Exisits', 'unique (name)', 'Fee Receipt No Must be Unique!')
    ] 
    _defaults = {
         'state':'Draft',
         'payment_method': 'Cash',
         'total_paid_amount': 0.0,
         'receipt_date':lambda *a: time.strftime('%d-%m-%Y'),
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
            result[f.id] = str(f.student_fee_id.name)
        return result

    def get_display_order(self, cr, uid, ids, name, args, context=None):
        """This method retruns the sequnece of parent class of this record. that will be use to order the list record of acad cal"""
        res = {}
        for f in self.browse(cr, uid, ids, context):
            if f.fee_type.id:
                res[f.id] = f.fee_type.fee_type.display_sequence
        return res
    
    _name = 'smsfee.receiptbook.lines'
    _rec_name = 'fee_name'
    _description = "This object store fee types"
    _order = 'display_order,fee_month'
    
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
        'display_order':fields.function(get_display_order, store=True, string='Display order', type='integer'),
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
        
        rec = self.browsle(cr, uid, ids, context)
        paymethod = ''
        receipt_date = ''
        for f in rec:
            stdname = self.pool.get('sms.student').browse(cr, uid, f.student_id.id).name
            paymethod = f.payment_method
            receipt_date = f.payment_date
                
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
        # fee_month_id=self.pool.get('smsfee.studentfee').search(cr,uid,[('student_id','=',student)]).fee_month
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
                res['hidden_parent_feestr'] = fee_line_id[0]
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
        #self.write(cr ,uid , ids ,{'state':'Receive'})
        self.write(cr ,uid , ids ,{'state':'Verification'})
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
            
            for i in self.pool.get('smsfee.receiptbook.lines').browse(cr ,uid ,receipt_lines_ids):
                self.pool.get('smsfee.receiptbook.lines').write(cr ,uid ,i.id,{
                                                                                             'paid_amount': i.total,#+rec.late_fee ,
                                                                                             'discount': 0 ,
                                                                                             'reconcile': True ,
                                                                                             })
            
            pooler_receiptbook.confirm_fee_received(cr ,uid ,[rec.challan_no.id])
            
        self.write(cr ,uid , ids ,{'state':'Confirm'})
        return True
    
    def send_for_verification(self ,cr ,uid ,ids ,context=None):
        print "send_for_verification============================="
        self.write(cr ,uid , ids ,{'state':'Receive'})
        return True    
    
    
    _name = 'smsfee.receive.challan.in.bank'
    _columns = {
        'acd_cal':fields.many2many('sms.academiccalendar', 'receive_challan_academiccalendar_rel', 'receive_challan_id', 'academiccalendar_id', 'Class'),
        'state':fields.selection([('Draft','Draft'),('Receive','Receive'),('Verification','Verification'),('Confirm','Confirm')],'State'),
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
