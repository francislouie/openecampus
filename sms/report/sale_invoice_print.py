import time
from datetime import date
from openerp.report import report_sxw

class sale_invoice_print(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(sale_invoice_print, self).__init__(cr, uid, name, context = context)
        self.localcontext.update({
            'time': time,
            'get_user_name': self.get_user_name,
            'get_today': self.get_today,
            'get_partner':self.get_partner,
        })
        self.base_amount = 0.00

    def get_partner(self, data):
        result = []
        _acc_inv_ids = self.pool.get('account.invoice').search(self.cr ,self.uid ,[])
        _acc_inv_recs = self.pool.get('account.invoice').browse(self.cr ,self.uid ,_acc_inv_ids)
        serial_no = 0
        child_result = []
        child = ''
        for record in _acc_inv_recs:
            
            my_dict = {'s_no':'','invoice_no':'','total_amount':'','half_amount':'','number_of_install':'','install_start_date':'',
                       'inner_dict':'','child':''}
            my_dict['invoice_no'] = record.move_id.name + '--' +str(record.date_invoice)
            my_dict['total_amount'] = record.amount_untaxed
            my_dict['half_amount'] = record.amount_untaxed/2
            my_dict['number_of_install'] = str(record.no_of_instl) +  str(len(record.instalments_ids)) + 'Months'
            my_dict['install_start_date'] = record.instalment_start_date
            my_dict['child'] = str(child)
            
            for rec in record.instalments_ids:
                
                inner_dict = {'inst_1':'','inst_2':'','inst_3':'','inst_4':'','inst_5':'','inst_6':'','inst_7':'','inst_8':''}
                if rec.state == 'Paid':
                    inner_dict['inst_1'] = str(rec.amount) + str(rec.state) + str(rec.paid_on) + str(rec.name)
                else:
                    inner_dict['inst_1'] = str(rec.amount) + str(rec.state) + str(rec.name)
                if rec.state == 'Paid':
                    inner_dict['inst_2'] = str(rec.amount) + str(rec.state) + str(rec.paid_on) + str(rec.name)
                else:
                    inner_dict['inst_2'] = str(rec.amount) + str(rec.state)+ str(rec.name)
                if rec.state == 'Paid':
                    inner_dict['inst_3'] = str(rec.amount) + str(rec.state) + str(rec.paid_on) + str(rec.name)
                else:
                    inner_dict['inst_3'] = str(rec.amount) + str(rec.state)+ str(rec.name)
                if rec.state == 'Paid':
                    inner_dict['inst_4'] = str(rec.amount) + str(rec.state) + str(rec.paid_on)+ str(rec.name)
                else:
                    inner_dict['inst_4'] = str(rec.amount) + str(rec.state)+ str(rec.name)
                if rec.state == 'Paid':
                    inner_dict['inst_5'] = str(rec.amount) + str(rec.state) + str(rec.paid_on)+ str(rec.name)
                else:
                    inner_dict['inst_5'] = str(rec.amount) + str(rec.state)+ str(rec.name)
                if rec.state == 'Paid':
                    inner_dict['inst_6'] = str(rec.amount) + str(rec.state) + str(rec.paid_on)+ str(rec.name)
                else:
                    inner_dict['inst_6'] = str(rec.amount) + str(rec.state)+ str(rec.name)
                if rec.state == 'Paid':
                    inner_dict['inst_7'] = str(rec.amount) + str(rec.state) + str(rec.paid_on)+ str(rec.name)
                else:
                    inner_dict['inst_7'] = str(rec.amount) + str(rec.state)+ str(rec.name)
                if rec.state == 'Paid':
                    inner_dict['inst_8'] = str(rec.amount) + str(rec.state) + str(rec.paid_on)+ str(rec.name)
                else:
                    inner_dict['inst_8'] = str(rec.amount) + str(rec.state)+ str(rec.name)
                    
                child_result.append(inner_dict)
                my_dict['inner_dict'] = child_result
                
            serial_no = serial_no + 1
            my_dict['s_no'] = serial_no
                 
        result.append(my_dict)
        return result

    def get_user_name(self):
        user_name = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name
        return  user_name

    def get_today(self):
        today = date.today()
        return today 
       
report_sxw.report_sxw('report.sale_invoice_print_receipt', 'account.invoice', 'addons/sms/report/sale_invoice_report_print.rml', parser=sale_invoice_print, header='External')
