{
    'name': 'SMS Attendance',
    'version': '1.0',
    'author': 'Inovtec Solutions',
    'category': 'SMS Attendance Management',
    'description': """This Module is used for attendance management for Compas Managment System.""",
    'website': 'http://www.inovtec.com.pk',
    'images': [''],
    'depends' : ['base','account','account_accountant','sms'],
    'data': [
             'security/sms_attendance_security.xml',
             'security/ir.model.access.csv',
             'wizard/sms_attendance_blank_attendancesheet.xml',
             'wizard/sms_attendance_filled_attendancesheet.xml',
             'wizard/sms_attendance_daily_attendancesheet.xml',
             'wizard/sms_attendance_total_absent_attendancesheet.xml',
             'sms_attendance_view.xml',
             'sms_attendance_report.xml',             
             'sms_attendance_menu.xml',
            ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}
