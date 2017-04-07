from openerp.osv import fields, osv
from openerp import netsvc
logger = netsvc.Logger()
from mx import DateTime as datetime

class sms_collabrator(osv.osv):
    
    """ Servers as bridge among sms and external apps """
    _name = 'sms.collabrator'
    _columns = {}
           
    def mast_auth(self, cr, uid, ids, login, pwd):
        result = []
        my_dict = {}
        user_ids = self.pool.get('sms.student').search(cr,uid,[('login_id','=',id),('password','=',pwd),('state','=','Admitted')])

        if user_ids:
            obj = self.pool.get('sms.student').browse(cr, uid, user_ids, user_ids)
            if obj[0].state == 'Admitted':
                my_dict['registration_no']  = obj[0].registration_no
                my_dict['stdname'] = obj[0].name
                my_dict['fathername']  = obj[0].father_name,
                my_dict['current_class_id']  = obj[0].current_class.id
                my_dict['current_class']  = obj[0].current_class.name
                my_dict['pic'] = obj[0].image
                my_dict['std_id'] = obj[0].id
            
           
        else:
            my_dict['state'] = 'Invalid Username or Password'
        result.append(my_dict)
        return result
    
sms_collabrator()
