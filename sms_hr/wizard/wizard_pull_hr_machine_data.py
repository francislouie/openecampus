from openerp.osv import fields, osv
import datetime
import xlwt
import locale
from datetime import datetime
#from osv import osv
from reportlab.pdfgen import canvas
import sys
import subprocess
import time
import urllib
#import netifaces 
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from xml.etree import ElementTree
import os

class sms_pull_hr_machine_data(osv.osv_memory):
    """
    
    """
    
    
    _name = "sms.pull.hr.machine.data"
    _description = "Pull Datat"
    _columns = {
              'pull_for_device': fields.selection([('all','Pull For All Device')],'Device'),
               }
        
    def pull_attendance_device_data(self, cr, uid, ids, data):
        result = []
        import requests
        r = requests.get('http://api.smilesn.com/attendance_pull.php?operation=pull_attendance&org_id=16&auth_key=d86ee704b4962d54227af9937a1396c3')
        read = r.json()
        print "json response",read
        for gg in read['att_records']:
            print "gg as whole",gg
            print "att_time",gg['att_time']
            print "bio_id",gg['bio_id']
            print "user_empleado_id id",['user_empleado_id']
            print "device_id id",['device_id']
        return True    
sms_pull_hr_machine_data()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: