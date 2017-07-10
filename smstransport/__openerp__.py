{
    'name': 'SMS Transport',
    'version': '1.0',
    'author': 'Inovtec Solutions',
    'category': 'School Management System',
    'description': """This Module serves the purpose of managing transport
                      system for a school""",
    'website': 'http://www.inovtec.com.pk',
    'depends' : ['base','account','account_accountant','sms','smsfee'],
    'data': ['security/smstransport_security.xml',
             'security/ir.model.access.csv',
             'wizard/smstransport_class_fee_receipt_unpaid.xml',
             'wizard/smstransport_wizard_registerations.xml',
             'wizard/wizard_singlestudent_unpaidftransportee_receipt.xml',
             'wizard/wizard_student_transportfee_collect.xml',
             'wizard/wizard_student_transportfee_receipt_exist_challans.xml',
             'wizard/sms_datamigration_warsak_campus.xml',
             'smstransport_view.xml',
             'smstransport_report.xml',
             'smstransport_menus.xml',
             ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
