from openerp.osv import fields, osv
from openerp import tools
from openerp import addons
import datetime
import xlwt
import xlrd
from dateutil import parser

class student_admission_register(osv.osv):
    
    _name = "student.admission.register"
    _inherit = "student.admission.register"
    _columns = {
        'admission_mode': fields.selection([('new_admission', 'New Admission'),('transfer_in', 'Transfer In')], 'Admission Mode'),
        }
    _defaults = {'admission_mode': 'new_admission'}        
student_admission_register()
