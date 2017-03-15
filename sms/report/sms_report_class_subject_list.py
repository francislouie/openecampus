
import time

from openerp.report import report_sxw

class sms_report_class_subject_list(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_report_class_subject_list, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'print_form': self.print_form,
        })
        self.base_amount = 0.00
    
    
    def print_form(self, data):
        result = []
        form = data['form']
  #      print form['session'][1],"**************",form['session']
 #       print data,"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",form
        _pooler = self.pool.get('sms.academiccalendar')
        acd_cal_ids = _pooler.search(self.cr ,self.uid ,[('acad_session_id','=',form['session'][1])])
#        print "acd_cal=========",acd_cal_ids
        
        outer_counter = 1
        for acd_cal in _pooler.browse(self.cr ,self.uid ,acd_cal_ids):
            print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            print acd_cal.name,"====std===",len(acd_cal.acad_cal_students)
            my_dict = {'outer_counter':'','acd_cal':'','tlt_student':'','subject_detail':''}
            
            my_dict['outer_counter'] = outer_counter
            my_dict['acd_cal'] = acd_cal.name
            my_dict['tlt_student'] = len(acd_cal.acad_cal_students)
             
            res = []
            s_no = 1
            for subj in acd_cal.assigned_subjects:
              #  print subj.name,"====offered as===",subj.offered_as,"====teacher====",subj.teacher_id.name
                #print subj.name,"===========",len(subj.academic_calendar.acad_cal_students)
                inner_dict = {'s_no':'','subj':'','mode':'','teacher':'','tlt_sub_student':''}
                acd_cal_std_ids = [x.id for x in subj.academic_calendar.acad_cal_students]
                #print "acd_cal_std_ids==========",acd_cal_std_ids
                std_sub = self.pool.get('sms.student.subject').search(self.cr ,self.uid ,[('student','in',acd_cal_std_ids),
                                                                                          ('subject','=',subj.id)])
                print "==============",len(std_sub)
                
                
                
                inner_dict['s_no'] = s_no
                inner_dict['subj'] = subj.name 
                inner_dict['mode'] = subj.offered_as
                inner_dict['teacher'] = subj.teacher_id.name
                inner_dict['tlt_sub_student'] = len(std_sub)
                res.append(inner_dict) 
                s_no = s_no +1
                
            my_dict['subject_detail'] = res
            result.append(my_dict)
            outer_counter = outer_counter +1
                
        return result
    
    
report_sxw.report_sxw('report.sms.report.class.subject.list', 'sms.academiccalendar', 'addons/sms/sms_report_class_subject_list_view.rml',parser = sms_report_class_subject_list, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

