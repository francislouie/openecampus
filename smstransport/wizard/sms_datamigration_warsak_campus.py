from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)
from xlrd import open_workbook

class class_data_migration(osv.osv_memory):
    
    _name = "class.data_migration"
    _description = "Used To Print Transport Fee Challans"
    _columns = {
              "class_id": fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active'),('fee_defined','=',1)]", help="Class"),
               }
    
    def import_student_data(self, cr, uid, ids, data):
        thisform = self.read(cr, uid, ids)[0]        
        class_obj = self.pool.get('sms.academiccalendar').browse(cr, uid, [thisform['class_id'][0]])
        for obj in class_obj:
            
            excel_sheets = open_workbook('/home/masood/Downloads/iiui data_warsak.xls')
            sheet = excel_sheets.sheet_by_name(obj.class_id.name)
            
            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
            print keys
            print sheet.nrows
            print sheet.ncols

            dict_list = []
            for row_index in xrange(1, sheet.nrows):
                d = {keys[col_index]: sheet.cell(row_index, col_index).value 
                     for col_index in xrange(sheet.ncols)}
                dict_list.append(d)
                
            for item in dict_list:
                student_name = item['Student Name']                       
                father_name =  item['Father Name']                       
                registration_no = item['Admission No']                       
                f_nic = item['Father CNIC']                       
                cell_no =  item['Cell-No']                       
                if item['Phone'] and item['Email']:
                    phone = item['Phone']
                    email = item['Email']
                                           
                cur_address = item['Current Address']                       
                nationality = item['Nationality']                       
                current_class = item['Current Class']                       
                admiss_status = item['New/Promoted']                       
                admiss_fee = item['Admission Fee']                       
                security_fee = item['Security Fee \n(New and promoted)']                       
                tuition_fee_effect_from = item['Tuition Fee \nStarts From']                       
                tuition_fee_paid_till = item['Tuition Fee \nPaid Till']                       
                fee_structure = item['Fee Stucture ']
                
                std_admission_id = self.pool.get('student.admission.register').\
                                                    create(cr, uid, {'name':uid,                                              
                                                                    'registration_no':'',
                                                                    'father_name':'',
                                                                    'student_class':obj.id,
                                                                    'group':'',
                                                                    'state':'Draft',
                                                                    'gender':'',
                                                                    'father_nic':obj.id,
                                                                    'cell_no':'',
                                                                    'permanent_address':'',
                                                                         })
                                                    
                print ('-'*30)
                    
        return True
class_data_migration()
