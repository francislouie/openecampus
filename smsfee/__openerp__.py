{
    'name': 'SMS Fee',
    'version': '1.0',
    'author': 'Cyme Business Technologies,Peshawar',
    'category': 'SMS Fee Management',
    'description': """This Module is used for fee management for Campus ManagmentS Solutions.""",
    'website': 'http://www.cyme.com.pk',
    'images': [''],
    'depends' : ['base','account','account_accountant','sms'],
    'data': [
             'security/smsfee_security.xml',
             'security/ir.model.access.csv',
             'wizard/smsfee_wizard_defaulter_students.xml',
             'wizard/smsfee_wizard_update_fee_register.xml',
             'wizard/smsfee_wizard_fee_reports.xml',
             'wizard/smsfee_wizard_class_fee_receipt_unpaid.xml',
             'wizard/smsfee_wizard_daily_fee_reports.xml',
             'wizard/smsfee_wizard_std_admfee_receipt_unpaid.xml',
             'wizard/wizard_singlestudent_unpaidfee_receipt.xml',
             'wizard/wizard_student_fee_collect.xml',
             'wizard/wizard_student_advancefee_collect.xml',
             # 'wizard/sms_wizard_detailed_fee_report_msexcel.xml',
             #'wizard/smsfee_wizard_student_feetype_list_view.xml',
             'smsfee_report.xml',
             'smsfee_view.xml',
             'smsfee_menus.xml',
            ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}
