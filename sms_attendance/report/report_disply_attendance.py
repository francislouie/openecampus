from openerp.report import report_sxw
import pooler
import time
import datetime

class report_disply_attendance(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_disply_attendance, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'report_title': self.report_title,
            '_get_month': self._get_month,
        })
        self.base_amount = 0.00
    
    def _get_month(self,form):
        return None
    
    def report_title(self,form):  
        _pooler = self.pool.get('sms.class.attendance') 
        print "yeaaaahhhhh ......-------....... yahooooooo!!!!!!",form
        atten_ids = self.pool.get('sms.class.attendance').search(self.cr ,self.uid ,[('class_id','=',form['class_id'][0]),('state','=','submit')])
        rec = _pooler.browse(self.cr ,self.uid ,atten_ids)
        dict = {'student':'','attendance':'','child':''}
        inner_dict = {'state':''}
        result = []
        acd_id = ''
        for val in rec:
            for child in val.child_id:
             #   dict = {'student':'','father_name':'','attendance':'','child':''}
                dict = {'student':'','father_name':'','total_class':'','present':'',1:'',2:'',3:'',4:'',5:'',6:'',7:'',8:''
#                         ,9:'',10:'',
#                         11:'',12:'',13:'',14:'',15:'',16:'',17:'',18:'',19:'',20:'',
#                         21:'',22:'',23:'',24:'',25:'',26:'',27:'',28:'',29:'',30:'',
#                         31:''
                        }
                
                dict['student'] = child.student_class_id.std_id.name
                dict['father_name'] = child.student_class_id.std_id.father_name
                print  "name---",child.student_class_id.std_id.name
                
                attendance_id = self.pool.get('sms.class.attendance.lines').search(self.cr ,self.uid ,
                                                                        [('parent_id','in',atten_ids),
                                                                         ('student_name','=',child.student_class_id.std_id.id),
                                                                         ])
                res = []
                i=1
                present = 0
                for vl in self.pool.get('sms.class.attendance.lines').browse(self.cr ,self.uid ,attendance_id):
                    print vl.state[:1].upper()
                    dict[i] = vl.state[:1].upper()
                    dict['total_class'] = i
                    if vl.state[:1].upper() == 'P':
                        present +=1
                    dict['present']  = present
                    
                    res.append(dict)
                    i +=1
                result.append(dict)
        print result         
        return result
#------------------------------------------------------------------------------------------------------------------------------------------
        
report_sxw.report_sxw('report.report.disply.attendance', 
                      'sms.class.attendance', 
                      'addons/smsfee/report_disply_attendance_view.rml',
                      parser = report_disply_attendance, header='external')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

