{
    'name': 'SMS Transport',
    'version': '1.0',
    'author': 'Inovtec Solutions',
    'category': 'School Management System',
    'description': """This Module serves the purpose of managing transport
                      system for a school""",
    'website': 'http://www.inovtec.com.pk',
    'depends' : ['base','account','account_accountant','sms'],
    'data': ['security/smstransport_security.xml',
             'security/ir.model.access.csv',
             'wizard/smstransport_class_fee_receipt_unpaid.xml',
             'smstransport_view.xml',
             'smstransport_report.xml',
             'smstransport_menus.xml',],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
