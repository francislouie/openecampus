{
    'name': 'SMS',
    'version': '1.0',
    'author': 'CYME Business Technologies',
    'category': 'School Management System',
    'description': """
This Module is used for CompasManagmentSystem.
Manage Students records From their Admission Entry to Final Transcript
Manage Employee records as Teacher Round Report etc""",
    'website': 'http://www.cyme.com.pk',
    'images': ['images/sms.jpeg'],
    'depends' : ['base','account','hr','hr_contract','account_accountant','sale','purchase','hr_expense','mail'],
    'data': [
             'security/sms_security.xml',
             'security/ir.model.access.csv',
             'wizard/sms_wizard_admission_form.xml',
             'wizard/sms_wizard_student_list.xml',
             'wizard/sms_wizard_exam_entry.xml',
             'wizard/sms_wizard_exam_datesheet.xml',
             'wizard/sms_wizard_add_exam_class.xml',
             'wizard/sms_wizard_exam_students_lists.xml',
             'wizard/sms_wizard_exam_students_dmc.xml',
             'wizard/sms_wizard_exam_students_dmc_multiple.xml',
             'wizard/sms_wizard_students_subject_assignment.xml',
             'wizard/sms_wizard_students_subject_removal.xml',
             'wizard/sms_wizard_withdraw_student.xml',
             'wizard/sms_wizard_load_students.xml',
             'wizard/sms_wizard_student_promote.xml',
             'wizard/sms_wizard_failed_student_class_assignment.xml',
             'wizard/sms_wizard_student_change_section.xml',
             'wizard/sms_wizard_change_student_class.xml',
             'wizard/sms_wizard_withdraw_register.xml',
             'wizard/sms_wizard_expense_report.xml',        
             'wizard/sms_wizard_demote_student.xml',
             'wizard/sms_wizard_datesheet_list.xml',
             'wizard/sms_wizard_certificate_form.xml',
             'wizard/sms_wizard_readmit_studen.xml',
             'wizard/sms_hr_attendance_load_csv.xml',
             'wizard/sms_wizard_class_subject_list_view.xml',
             'wizard/sms_wizard_calss_subject.xml',
             'wizard/sms_wizard_sibling.xml',
             'wizard/sms_classlist.xml',
             'wizard/sms_wizard_student_transfer_in_view.xml',
             'cms_report.xml',
             'custom_sale_view.xml',
            
             'data/sms_subjects_data.xml',
             'data/sms_acadamiccal_default_data.xml',
             'data/sms_time_slot_day_data.xml',
             'data/sms_timetables_lines_default_data.xml',
             'data/sms_exam_type.xml',
             'data/sms_months.xml',
             'data/sms_grading_scheme.xml',
             'sms_view.xml',
             'sms_menus.xml',
             ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['images/sms.jpeg',],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
