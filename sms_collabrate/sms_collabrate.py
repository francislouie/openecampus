from openerp.osv import fields, osv
from openerp import netsvc
logger = netsvc.Logger()
from mx import DateTime as datetime

class sms_collabrator(osv.osv):
    
    """ Servers as bridge among sms and external apps """
    _name = 'sms.collabrator'
    _columns = {}
    
    def mast_auth(self, cr, uid, ids, id,pwd):
        result = []
        user_ids = self.pool.get('sms.student').search(cr,uid,[('','',''),('state','=','Admitted')])
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
    
sms_collabrator()