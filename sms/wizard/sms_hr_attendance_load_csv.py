from openerp.osv import fields, osv
from openerp.tools.translate import _
import datetime
import xlrd
import logging

_logger = logging.getLogger(__name__)

class sms_import_hr_attendance_data(osv.osv_memory):
    """Use this wizard to Import Project Data from the excel file"""
    _name = "cni.import.project.data"
    _description = "Import Project Data From Excel"
    _columns = {
              'file_name': fields.char('File', size=300, required=True),
              'advanced': fields.boolean('Advanced Search'),
              'start_from': fields.integer('Start From'),
              'records': fields.integer('Number of Records'),
        }
    _defaults = {
        'file_name': '/home/shahid/table_xls.xls',
        'start_from': 1,
        'records': 0,
    }
    
    def import_data(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        start_from = current_obj[0].start_from
        records = current_obj[0].records
        advanced = current_obj[0].advanced
        
        workbook = xlrd.open_workbook(current_obj[0].file_name)
        worksheet = workbook.sheet_by_name('Sheet1')
        
        rows = worksheet.nrows - 1
        cells = worksheet.ncols - 1
        row = 1
        
        w_counter = 0
        c_counter = 0
        
        while row <= rows:
                              
            employee_id = int(worksheet.cell_value(row, 0))
            _logger.info("Employee id: %r out of %r______________________", (employee_id), (employee_id))
            hr_id = self.pool.get('hr.employee').search(cr,uid,[('attendance_id','=',employee_id)])
            
            if hr_id:
                _logger.info("Employee id: %r out of %r___>>>>>>>>>>>>>>>>_____", (hr_id), (hr_id))
                att_datetime = str(worksheet.cell_value(row, 1))
                date_formatted = datetime.datetime.strptime(att_datetime, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') 
                att_date = datetime.datetime.strptime(att_datetime, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d') 
                _logger.info("Attendance Date time.........................: %r out of %r_________", (att_date), (date_formatted))
                if row%2 == 0:
                    status = 'sign_out'
                else:
                    status = 'sign_in'
                project_id = self.pool.get('hr.attendance').create(cr, uid, {
                    'name': date_formatted,
                    #'day': '2016-01-01',
                    'employee_id': hr_id[0],
                   # 'action': status,
                    })       
            row = row + 1     
                    
        return {}

sms_import_hr_attendance_data()

