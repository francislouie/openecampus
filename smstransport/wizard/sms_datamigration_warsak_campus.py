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
        excel_sheets = open_workbook('/home/masood/Downloads/iiui data_warsak.xls')
        for sheet in excel_sheets.sheets():
            num_cols = sheet.ncols   # Number of columns
            for row_idx in range(0, sheet.nrows):    # Iterate through rows
                print ('-'*40)
                for col_idx in range(0, num_cols):  # Iterate through columns
                    cell_obj = sheet.cell(row_idx, col_idx)  # Get cell object by row, col
                    print ('Column: [%s] cell_obj: [%s]' % (col_idx, cell_obj))
            break                
        
        thisform = self.read(cr, uid, ids)[0]
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'sms.academiccalendar',
             'form': self.read(cr, uid, ids)[0],
             }
        
class_data_migration()
