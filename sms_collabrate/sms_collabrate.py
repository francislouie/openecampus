from osv import osv, fields
import netsvc
logger = netsvc.Logger()
from mx import DateTime as datetime

class collabrator(osv.osv):
    """
   Servers as bridge among cms and external apps/
    """
        
    _name = 'cms.datagrid'
    _columns = {}
    
    def mast_auth(self, cr, uid, ids, id,pwd):
        result = []
        user_ids = self.pool.get('sms.student').search(cr,uid,[('login_id','=',id),('password','=',pwd),('state','=','Admitted')])
        if user_ids:
            obj = self.pool.get('sms.student').browse(cr, uid, user_ids, user_ids)
            my_dict = {
                'registration_no':obj[0].registration_no,
                'stdname':obj[0].name,
                'fathername':obj[0].father_name,
                 'current_class_id':obj[0].current_class.id,
                'current_class':obj[0].current_class.name,
                'pic':obj[0].image,
                'std_id':obj[0].id,
            }
            result.append(my_dict)
        else:
            return 'Invalid Username or Password'
        return result
collabrator()