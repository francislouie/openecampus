
import time

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from pytz import timezone, utc
import openerp.netsvc as netsvc
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from openerp.tools.translate import _
import logging
import pytz
_logger = logging.getLogger(__name__)

DAYOFWEEK_SELECTION = [('0', 'Monday'),
                       ('1', 'Tuesday'),
                       ('2', 'Wednesday'),
                       ('3', 'Thursday'),
                       ('4', 'Friday'),
                       ('5', 'Saturday'),
                       ('6', 'Sunday'),

                       ]



class week_days(osv.Model):

    _name = 'hr.schedule.weekday'
    _description = 'Days of the Week'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'sequence': fields.integer('Sequence', required=True),
    }
class hr_public_holiday(osv.Model):

    _name = 'hr.public.holiday'
    _description = 'hr public holiday'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'holiday_date': fields.date('Public holiday'),
        'schedule_id': fields.many2one('hr.schedule', 'Schedule', required=True),
    }

class hr_schedule(osv.osv):

    _name = 'hr.schedule'
    _inherit = ['mail.thread']
    _description = 'Employee Schedule'
    
    def convert_datetime_timezone(self,dt, tz1, tz2):
        tz1 = pytz.timezone(tz1)
        tz2 = pytz.timezone(tz2)
    
        dt = datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
        dt = tz1.localize(dt)
        dt = dt.astimezone(tz2)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    
        return dt
    def create(self, cr, uid, vals, context=None):
        
        exists = self.search(cr,uid,[('department_id','=',vals['department_id']),('state','!=','locked')]) 
        if  exists:
            raise osv.except_osv(('Schedule is already in confirm state for this department'), ('First move it to lock state or remove it '))
        else:
            schedule = super(hr_schedule, self).create(cr, uid, vals, context=context)
#         empids = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',vals['department_id'])])
#         if empids:
#             
#             for emp in empids:
#                 self.create_schedule_per_emp_details(cr, uid, schedule,emp, context=context)
        return schedule
   
#     def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
#         new_date_end =0
#         new_date_start=0   
#         if 'schedule_lines_ids' in vals:
#             for value in vals['schedule_lines_ids']:
#                 rec_id=value[1]
#                 rec_date=value[2]
#                 if value[2]:
#                     if 'date_end' in value[2]:
#                         new_date_end=rec_date['date_end']
#                     if 'date_start' in value[2]:
#                         new_date_start=rec_date['date_start']
#                     if rec_date:
#                         dep_schedule_ids = self.pool.get('hr.schedule.lines').search(cr,uid, [('id','=',rec_id)])
#                         for f in self.pool.get('hr.schedule.lines').browse(cr,uid, dep_schedule_ids):
#                             
#                             dep_schedule_ids = self.pool.get('hr.schedule.detail').search(cr,uid, [('department_id','=',f.department_id.id),('day','=',f.day)])
#                             schedule_objs = self.pool.get('hr.schedule.detail').browse(cr,uid, dep_schedule_ids)
#                             for schedule in schedule_objs:
#                                 if new_date_end ==0:
#                                     new_date_end=f.date_end
#                                 if new_date_start ==0:
#                                     new_date_start=f.date_start    
#                                 if schedule:
#                                     update= self.pool.get('hr.schedule.detail').write(cr, uid, schedule.id, {'date_start':new_date_start,'date_end':new_date_end})
#                                     print"successfully updated id ",update
#                             new_date_end =0
#                             new_date_start=0 
#         result = super(osv.osv, self).write(cr, uid, ids, vals, context)
#         return True
   
    
    def _compute_alerts(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, '')
#         for obj in self.browse(cr, uid, ids, context=context):
#             alert_ids = []
#             for detail in obj.detail_ids:
#                 [alert_ids.append(a.id) for a in detail.alert_ids]
#             res[obj.id] = alert_ids
        return res

    _columns = {
        
        'name': fields.char("Description", size=64, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'template_id': fields.many2one('hr.schedule.template', 'Schedule Template', readonly=True, states={'draft': [('readonly', False)]}),
        'public_holiday_ids': fields.one2many('hr.public.holiday', 'schedule_id', 'Public Holiday'),
        'detail_ids': fields.one2many('hr.schedule.detail', 'schedule_id', 'Schedule Detail', readonly=True, states={'draft': [('readonly', False)]}),
        'schedule_lines_ids': fields.one2many('hr.schedule.lines', 'schedule_id', 'Create Schedule', readonly=True, states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', 'Department',readonly=True, states={'draft': [('readonly', False)]}),
        'alert_ids': fields.function(_compute_alerts, type='one2many', relation='hr.schedule.alert', string='Alerts', method=True, readonly=True),
        'restday_ids1': fields.many2many('hr.schedule.weekday', 'schedule_restdays_rel1', 'sched_id',
                                         'weekday_id', string='Rest Days Week 1'),
        'restday_ids2': fields.many2many('hr.schedule.weekday', 'schedule_restdays_rel2', 'sched_id',
                                         'weekday_id', string='Rest Days Week 2'),
        'restday_ids3': fields.many2many('hr.schedule.weekday', 'schedule_restdays_rel3', 'sched_id',
                                         'weekday_id', string='Rest Days Week 3'),
        'restday_ids4': fields.many2many('hr.schedule.weekday', 'schedule_restdays_rel4', 'sched_id',
                                         'weekday_id', string='Rest Days Week 4'),
        'restday_ids5': fields.many2many('hr.schedule.weekday', 'schedule_restdays_rel5', 'sched_id',
                                         'weekday_id', string='Rest Days Week 5'),
        'state': fields.selection((
            ('draft', 'Draft'), (
                'validate', 'Confirmed'),
            ('locked', 'Locked'), (
                'unlocked', 'Unlocked'),
        ), 'State', required=True, readonly=True),
    }

    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'resource.calendar', context=context)
    }

    

    
     
    def delete_details(self, cr, uid, sched_id, context=None):
 
        unlink_ids = []
        schedule = self.browse(cr, uid, sched_id, context=context)
        for detail in schedule.detail_ids:
            unlink_ids.append(detail.id)
        self.pool.get('hr.schedule.detail').unlink(
            cr, uid, unlink_ids, context=context)
        return
 
   
 
    def create_schedule_per_emp_details(self, cr, uid, sched_id,emp_id,context=None):
 
        sch_lines_ids = self.pool.get('hr.schedule.lines').search(cr,uid, [('schedule_id','=',sched_id)])
        if sch_lines_ids:
            reclines = self.pool.get('hr.schedule.lines').browse(cr,uid,sch_lines_ids)
        for line in reclines:
#             date_start =self.pool.get('hr.schedule').convert_datetime_timezone(line.date_start, "UTC", "Asia/Karachi")
#             date_end =self.pool.get('hr.schedule').convert_datetime_timezone(line.date_end, "UTC", "Asia/Karachi")
            mysch =self.pool.get('hr.schedule.detail').create(cr, uid, {
                            'employee_id':emp_id,
                            'date_end':line.date_end,
                            'date_start':line.date_start,
                            'name':line.name,
                            'state':line.state,
                            'schedule_id':sched_id,
                            'dayofweek':line.dayofweek,
                            'natureofday':line.natureofday,
                            'department_id':line.department_id.id,
                            'day':'2018-03-07',
                            },context=context)        
        return True
 
    
 
    def create_mass_schedule(self, cr, uid, context=None):
        '''Creates tentative schedules for all employees based on the
        schedule template attached to their contract. Called from the scheduler.'''
 
        sched_obj = self.pool.get('hr.schedule')
        ee_obj = self.pool.get('hr.employee')
 
        # Create a two-week schedule beginning from Monday of next week.
        
        dt = datetime.today()
        days = 7 - dt.weekday()
        dt += relativedelta(days=+days)
        dStart = dt.date()
        dEnd = dStart + relativedelta(weeks=+2, days=-1)
 
        # Create schedules for each employee in each department
        #
        dept_ids = self.pool.get('hr.department').search(cr, uid, [],
                                                         context=context)
        for dept in self.pool.get('hr.department').browse(cr, uid, dept_ids, context=context):
            ee_ids = ee_obj.search(cr, uid, [
                ('department_id', '=', dept.id),
            ], order="name", context=context)
            if len(ee_ids) == 0:
                continue
 
            for ee in ee_obj.browse(cr, uid, ee_ids, context=context):
 
                if not ee.contract_id or not ee.contract_id.schedule_template_id:
                    continue
 
                sched = {
                    'name': ee.name + ': ' + dStart.strftime('%Y-%m-%d') + ' Wk ' + str(dStart.isocalendar()[1]),
                    'employee_id': ee.id,
                    'template_id': ee.contract_id.schedule_template_id.id,
                    'date_start': dStart.strftime('%Y-%m-%d'),
                    'date_end': dEnd.strftime('%Y-%m-%d'),
                }
                sched_obj.create(cr, uid, sched, context=context)
 
    def deletable(self, cr, uid, sched_id, context=None):
 
        sched = self.browse(cr, uid, sched_id, context=context)
        if sched.state not in ['draft', 'unlocked']:
            return False
        for detail in sched.detail_ids:
            if detail.state not in ['draft', 'unlocked']:
                return False
 
        return True
 
    def unlink(self, cr, uid, ids, context=None):
 
        detail_obj = self.pool.get('hr.schedule.detail')
 
        if isinstance(ids, (int, long)):
            ids = [ids]
 
        schedule_ids = []
        for schedule in self.browse(cr, uid, ids, context=context):
            # Do not remove schedules that are not in draft or unlocked state
            if not self.deletable(cr, uid, schedule.id, context):
                continue
 
            # Delete the schedule details associated with this schedule
            #
            detail_ids = []
            [detail_ids.append(detail.id) for detail in schedule.detail_ids]
            if len(detail_ids) > 0:
                detail_obj.unlink(cr, uid, detail_ids, context=context)
 
            schedule_ids.append(schedule.id)
 
        return super(hr_schedule, self).unlink(cr, uid, schedule_ids, context=context)
 
    def _workflow_common(self, cr, uid, ids, signal, next_state, context=None):
 
        wkf = netsvc.LocalService('workflow')
        for sched in self.browse(cr, uid, ids, context=context):
            for detail in sched.detail_ids:
                wkf.trg_validate(
                    uid, 'hr.schedule.detail', detail.id, signal, cr)
                wkf.trg_validate(
                    uid, 'hr.schedule.lines', detail.id, signal, cr)
#             self.write(
#                 cr, uid, sched.id, {'state': next_state}, context=context)
            sql_query = """Update hr_schedule_lines set state ='validate' where schedule_id ="""+str(sched.id)+""""""
            cr.execute(sql_query)
            sql_query = """Update hr_schedule set state ='validate' where id ="""+str(sched.id)+""""""
            cr.execute(sql_query)
        return True
 
    def workflow_validate(self, cr, uid, ids, context=None):
        return self._workflow_common(cr, uid, ids, 'signal_validate', 'validate', context=context)
 
    def details_locked(self, cr, uid, ids, context=None):
 
        for sched in self.browse(cr, uid, ids, context=context):
            for detail in sched.detail_ids:
                if detail.state != 'locked':
                    return False
 
        return True
    def Schedule_lines_Rec_lock(self, cr, uid, ids, context=None):
        for sched in self.browse(cr, uid, ids, context=context):
            for sched_lines in sched.schedule_lines_ids:
                sql_query = """Update hr_schedule_lines set state ='locked' where id ="""+str(sched_lines.id)+""""""
                cr.execute(sql_query)
            if sched_lines.state != 'locked':
                    return False       
 
        return True
    def Schedule_Rec_lock(self, cr, uid, ids, context=None):
        '''This method is use to lock  hr schedule and schedule lines record.'''
        all_locked = True
        for sched in self.browse(cr, uid, ids, context=context):
            if self.Schedule_lines_Rec_lock(cr, uid, [sched.id], context):
                sql_query = """Update hr_schedule set state ='locked' where id ="""+str(sched.id)+""""""
                cr.execute(sql_query)
            else:
                all_locked = False
        return all_locked           
 
    def Schedule_lines_backto_confirm(self, cr, uid, ids, context=None):
        for sched in self.browse(cr, uid, ids, context=context):
            for sched_lines in sched.schedule_lines_ids:
                sql_query = """Update hr_schedule_lines set state ='validate' where id ="""+str(sched_lines.id)+""""""
                cr.execute(sql_query)
            if sched_lines.state != 'validate':
                    return False       
 
        return True
    def Schedule_backto_confirm(self, cr, uid, ids, context=None):
        '''This method is use to lock  hr schedule and schedule lines record.'''
        all_locked = True
        for sched in self.browse(cr, uid, ids, context=context):
            
            exists = self.search(cr,uid,[('department_id','=',sched.department_id.id),('state','=','validate')]) 
            if  exists:
                raise osv.except_osv(('Schedule is already in confirm state for this department'), ('First move it to lock state or remove it '))
            else:
                if self.Schedule_lines_backto_confirm(cr, uid, [sched.id], context):
                    print"schedule id",sched.id
                    sql_query = """Update hr_schedule set state ='validate' where id ="""+str(sched.id)+""""""
                    cr.execute(sql_query)
                else:
                    all_locked = False
        return all_locked
 
    def workflow_lock(self, cr, uid, ids, context=None):
        '''Lock the Schedule Record. Expects to be called by its schedule detail
        records as they are locked one by one.  When the last one has been locked
        the schedule will also be locked.'''
 
        all_locked = True
        for sched in self.browse(cr, uid, ids, context=context):
            if self.details_locked(cr, uid, [sched.id], context):
                self.write(cr, uid, sched.id, {
                           'state': 'locked'}, context=context)
            else:
                all_locked = False
 
        return all_locked
 
    def workflow_unlock(self, cr, uid, ids, context=None):
        '''Unlock the Schedule Record. Expects to be called by its schedule detail
        records as they are unlocked one by one.  When the first one has been unlocked
        the schedule will also be unlocked.'''
 
        all_locked = True
        for sched in self.browse(cr, uid, ids, context=context):
            if not self.details_locked(cr, uid, [sched.id], context):
                self.write(
                    cr, uid, sched.id, {'state': 'unlocked'}, context=context)
            else:
                all_locked = False
 
        return all_locked == False

class schedule_lines(osv.osv):
    _name = "hr.schedule.lines"
    _description = "Schedule lines"

    def _day_compute(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = time.strftime(
                '%Y-%m-%d', time.strptime(obj.date_start, '%Y-%m-%d %H:%M:%S'))
        return res

    def _get_ids_from_sched(self, cr, uid, ids, context=None):
        res = []
        for sched in self.pool.get('hr.schedule').browse(cr, uid, ids, context=context):
            for detail in sched.detail_ids:
                res.append(detail.id)
        return res
    
    
    
    _columns = { 
        'name': fields.char("Name", size=64, required=True),
        'dayofweek': fields.selection(DAYOFWEEK_SELECTION, 'Day of Week', required=True, select=True),
        'natureofday':fields.selection((('Wording_day', 'Wording day'), ('holiday', 'Holiday')), 'Day Nature'),
        'date_start': fields.datetime('Start Date and Time', required=True),
        'date_end': fields.datetime('End Date and Time', required=True),
        'day': fields.date('Day',select=1),

        'schedule_id': fields.many2one('hr.schedule', 'Schedule', required=True),

        'department_id': fields.related('schedule_id', 'department_id', type='many2one',
                                        relation='hr.department', string='Department', store=True),
        'employee_id': fields.many2one('hr.employee', 'employee'),
#         'employee_id': fields.related('schedule_id', 'employee_id', type='many2one',
#                                       relation='hr.employee', string='Employee', store=True),
        'alert_ids': fields.one2many('hr.schedule.alert', 'sched_detail_id', 'Alerts', readonly=True),
        'state': fields.selection((
            ('draft', 'Draft'), (
                'validate', 'Confirmed'),
            ('locked', 'Locked'), (
                'unlocked', 'Unlocked'),
        ), 'State', required=True, readonly=True),
    }

    _order = 'schedule_id, date_start, dayofweek'

    _defaults = {
        'dayofweek': '0',
        'natureofday': 'Wording_day',
        'state': 'draft',
    }

class hr_employee(osv.osv):
    _inherit="hr.employee"

    def create(self, cr, uid, vals, context=None):
        employee_id =  super(hr_employee, self).create(cr, uid, vals, context=context)
       
        dep_schedule_ids = self.pool.get('hr.schedule').search(cr,uid, [('department_id','=',vals['department_id'])])
        if dep_schedule_ids:
            self.create_schedule_per_emp_details(cr, uid, dep_schedule_ids[0],employee_id, context=context)
            
        return employee_id    
    _columns = {
       
    }

hr_employee()


class schedule_detail(osv.osv):
    _name = "hr.schedule.detail"
    _description = "Schedule Detail"

    def _day_compute(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = time.strftime(
                '%Y-%m-%d', time.strptime(obj.date_start, '%Y-%m-%d %H:%M:%S'))
        return res

    def _get_ids_from_sched(self, cr, uid, ids, context=None):
        res = []
        for sched in self.pool.get('hr.schedule').browse(cr, uid, ids, context=context):
            for detail in sched.detail_ids:
                res.append(detail.id)
        return res
    
    
    
    _columns = { 
        'name': fields.char("Name", size=64, required=True),
        'dayofweek': fields.selection(DAYOFWEEK_SELECTION, 'Day of Week', required=True, select=True),
        'natureofday':fields.selection((('Wording_day', 'Wording day'), ('holiday', 'Holiday')), 'Day Nature'),
#         'date_start': fields.datetime('Start Date and Time', required=True),
#         'date_end': fields.datetime('End Date and Time', required=True),
        'date_start': fields.char('Start Date and Time', required=True),
        'date_end': fields.char('End Date and Time', required=True),
        'day': fields.date('Day', select=1),

        'schedule_id': fields.many2one('hr.schedule', 'Schedule', required=True),

        'department_id': fields.related('schedule_id', 'department_id', type='many2one',
                                        relation='hr.department', string='Department', store=True),
        'employee_id': fields.many2one('hr.employee', 'employee'),
#         'employee_id': fields.related('schedule_id', 'employee_id', type='many2one',
#                                       relation='hr.employee', string='Employee', store=True),
        'alert_ids': fields.one2many('hr.schedule.alert', 'sched_detail_id', 'Alerts', readonly=True),
        'state': fields.selection((
            ('draft', 'Draft'), (
                'validate', 'Confirmed'),
            ('locked', 'Locked'), (
                'unlocked', 'Unlocked'),
        ), 'State', required=True, readonly=True),
    }

    _order = 'schedule_id, date_start, dayofweek'

    _defaults = {
        'dayofweek': '0',
        'state': 'draft',
    }

    def _detail_date(self, cr, uid, ids, context=None):
        for detail in self.browse(cr, uid, ids, context=context):
            cr.execute('SELECT id \
                FROM hr_schedule_detail \
                WHERE (date_start <= %s and %s <= date_end) \
                    AND schedule_id=%s \
                    AND id <> %s', (detail.date_end, detail.date_start, detail.schedule_id.id, detail.id))
            if cr.fetchall():
                return False
        return True


#     _constraints = [
#         (_detail_date, 'You cannot have scheduled days that overlap!',
#          ['date_start', 'date_end']),
#     ]


    def scheduled_hours_on_day(self, cr, uid, employee_id, contract_id, dt, context=None):

        dtDelta = timedelta(seconds=0)
        shifts = self.scheduled_begin_end_times(cr, uid, employee_id,
                                                contract_id, dt, context=context)
        for start, end in shifts:
            dtDelta += end - start

        return float(dtDelta.seconds / 60) / 60.0

    def scheduled_begin_end_times(self, cr, uid, employee_id, contract_id, dt, context=None):
        '''Returns a list of tuples containing shift start and end times for the day'''

        res = []
        detail_ids = self.search(cr, uid, [
            ('schedule_id.employee_id.id', '=', employee_id),
            ('day', '=', dt.strftime(
                '%Y-%m-%d')),
        ],
            order='date_start',
            context=context)
        if len(detail_ids) > 0:
            sched_details = self.browse(cr, uid, detail_ids, context=context)
            for detail in sched_details:
                res.append((
                    datetime.strptime(
                        detail.date_start, '%Y-%m-%d %H:%M:%S'),
                    datetime.strptime(
                        detail.date_end, '%Y-%m-%d %H:%M:%S'),
                ))

        return res

    def scheduled_hours_on_day_from_range(self, d, range_dict):

        dtDelta = timedelta(seconds=0)
        shifts = range_dict[d.strftime(OE_DFORMAT)]
        for start, end in shifts:
            dtDelta += end - start

        return float(dtDelta.seconds / 60) / 60.0

    def scheduled_begin_end_times_range(
        self, cr, uid, employee_id, contract_id,
            dStart, dEnd, context=None):
        '''Returns a dictionary with the dates in range dtStart - dtEnd as keys and
        a list of tuples containing shift start and end times during those days as values'''

        res = {}
        d = dStart
        while d <= dEnd:
            res.update({d.strftime(OE_DFORMAT): []})
            d += timedelta(days=+1)

        detail_ids = self.search(cr, uid, [
            ('schedule_id.employee_id.id', '=', employee_id),
            ('day', '>=', dStart.strftime(
                '%Y-%m-%d')),
            ('day', '<=', dEnd.strftime(
                '%Y-%m-%d')),
        ],
            order='date_start',
            context=context)
        if len(detail_ids) > 0:
            sched_details = self.browse(cr, uid, detail_ids, context=context)
            for detail in sched_details:
                res[detail.day].append((
                    datetime.strptime(
                        detail.date_start, '%Y-%m-%d %H:%M:%S'),
                    datetime.strptime(
                        detail.date_end, '%Y-%m-%d %H:%M:%S'),
                ))

        return res

    def _remove_direct_alerts(self, cr, uid, ids, context=None):
        '''Remove alerts directly attached to the schedule detail and return a unique
        list of tuples of employee id and schedule detail date.'''

        if isinstance(ids, (int, long)):
            ids = [ids]

        alert_obj = self.pool.get('hr.schedule.alert')

        # Remove alerts directly attached to these schedule details
        #
        alert_ids = []
        scheds = []
        sched_keys = []
        for sched_detail in self.browse(cr, uid, ids, context=context):

            [alert_ids.append(alert.id) for alert in sched_detail.alert_ids]

            # Hmm, creation of this record triggers a workflow action that tries to
            # write to it. But it seems that computed fields aren't available at
            # this stage. So, use a fallback and compute the day ourselves.
            day = sched_detail.day
            if not sched_detail.day:
                day = time.strftime('%Y-%m-%d', time.strptime(
                    sched_detail.date_start, '%Y-%m-%d %H:%M:%S'))
            key = str(sched_detail.schedule_id.employee_id.id) + day
            if key not in sched_keys:
                scheds.append((sched_detail.schedule_id.employee_id.id, day))
                sched_keys.append(key)

        if len(alert_ids) > 0:
            alert_obj.unlink(cr, uid, alert_ids, context=context)

        return scheds

    def _recompute_alerts(self, cr, uid, attendances, context=None):
        '''Recompute alerts for each record in schedule detail.'''

        alert_obj = self.pool.get('hr.schedule.alert')

        # Remove all alerts for the employee(s) for the day and recompute.
        #
        for ee_id, strDay in attendances:

            # Today's records will be checked tomorrow. Future records can't
            # generate alerts.
            if strDay >= fields.date.context_today(self, cr, uid, context=context):
                continue

            # XXX - Someone who cares about DST should fix this
            #
            data = self.pool.get('res.users').read(
                cr, uid, uid, ['tz'], context=context)
            dt = datetime.strptime(strDay + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            lcldt = timezone(data['tz']).localize(dt, is_dst=False)
            utcdt = lcldt.astimezone(utc)
            utcdtNextDay = utcdt + relativedelta(days=+1)
            strDayStart = utcdt.strftime('%Y-%m-%d %H:%M:%S')
            strNextDay = utcdtNextDay.strftime('%Y-%m-%d %H:%M:%S')

            alert_ids = alert_obj.search(cr, uid, [('employee_id', '=', ee_id),
                                                   '&', (
                                                       'name', '>=', strDayStart),
                                                   ('name', '<', strNextDay)],
                                         context=context)
            alert_obj.unlink(cr, uid, alert_ids, context=context)
            alert_obj.compute_alerts_by_employee(
                cr, uid, ee_id, strDay, context=context)

#     def create(self, cr, uid, vals, context=None):
# 
#         if 'day' not in vals and 'date_start' in vals:
#             # XXX - Someone affected by DST should fix this
#             #
#             user = self.pool.get('res.users').browse(
#                 cr, uid, uid, context=context)
#             local_tz = timezone(user.tz)
#             dtStart = datetime.strptime(vals['date_start'], OE_DTFORMAT)
#             locldtStart = local_tz.localize(dtStart, is_dst=False)
#             utcdtStart = locldtStart.astimezone(utc)
#             dDay = utcdtStart.astimezone(local_tz).date()
#             vals.update({'day': dDay})
# 
#         res = super(schedule_detail, self).create(
#             cr, uid, vals, context=context)
# 
#         obj = self.browse(cr, uid, res, context=context)
#         attendances = [
#             (obj.schedule_id.employee_id.id, fields.date.context_today(self, cr, uid, context=context))]
#         self._recompute_alerts(cr, uid, attendances, context=context)
# 
#         return res

    def unlink(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        detail_ids = []
        for detail in self.browse(cr, uid, ids, context=context):
            if detail.state in ['draft', 'unlocked']:
                detail_ids.append(detail.id)

        # Remove alerts directly attached to the schedule details
        #
        attendances = self._remove_direct_alerts(
            cr, uid, detail_ids, context=context)

        res = super(schedule_detail, self).unlink(
            cr, uid, detail_ids, context=context)

        # Remove all alerts for the employee(s) for the day and recompute.
        #
        self._recompute_alerts(cr, uid, attendances, context=context)

        return res

    def write(self, cr, uid, ids, vals, context=None):

        # Flag for checking wether we have to recompute alerts
#         trigger_alert = False
#         for k, v in vals.iteritems():
#             if k in ['date_start', 'date_end']:
#                 trigger_alert = True
# 
#         if trigger_alert:
#             # Remove alerts directly attached to the attendances
#             #
#             attendances = self._remove_direct_alerts(
#                 cr, uid, ids, context=context)

        res = super(schedule_detail, self).write(
            cr, uid, ids, vals, context=context)

#         if trigger_alert:
#             # Remove all alerts for the employee(s) for the day and recompute.
#             #
#             self._recompute_alerts(cr, uid, attendances, context=context)

        return res

    def workflow_lock(self, cr, uid, ids, context=None):

        wkf = netsvc.LocalService('workflow')
        for detail in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [detail.id], {
                       'state': 'locked'}, context=context)
            wkf.trg_validate(
                uid, 'hr.schedule', detail.schedule_id.id, 'signal_lock', cr)

        return True

    def workflow_unlock(self, cr, uid, ids, context=None):

        wkf = netsvc.LocalService('workflow')
        for detail in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [detail.id], {
                       'state': 'unlocked'}, context=context)
            wkf.trg_validate(
                uid, 'hr.schedule', detail.schedule_id.id, 'signal_unlock', cr)

        return True


class hr_schedule_request(osv.osv):

    _name = 'hr.schedule.request'
    _description = 'Change Request'

    _inherit = ['mail.thread']

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'date': fields.date('Date', required=True),
        'type': fields.selection((
            ('missedp', 'Missed Punch'),
            ('adjp', 'Punch Adjustment'),
            ('absence', 'Absence'),
            ('schedadj', 'Schedule Adjustment'),
            ('other', 'Other'),
        ), 'Type', required=True),
        'message': fields.text('Message'),
        'state': fields.selection((
            ('pending', 'Pending'),
            ('auth', 'Authorized'),
            ('denied', 'Denied'),
            ('cancel', 'Cancelled'),
        ), 'State', required=True, readonly=True),
    }

    _defaults = {
        'state': 'pending',
    }


class hr_schedule_alert(osv.osv):

    _name = 'hr.schedule.alert'
    _description = 'Attendance Exception'

    _inherit = ['mail.thread', 'resource.calendar']

    def _get_employee_id(self, cr, uid, ids, field_name, arg, context=None):

        res = {}
        for alert in self.browse(cr, uid, ids, context=context):
            if alert.punch_id:
                res[alert.id] = alert.punch_id.employee_id.id
            elif alert.sched_detail_id:
                res[alert.id] = alert.sched_detail_id.schedule_id.employee_id.id
            else:
                res[alert.id] = False

        return res

    _columns = {
        'name': fields.datetime('Date and Time', required=True, readonly=True),
        'rule_id': fields.many2one('hr.schedule.alert.rule', 'Alert Rule', required=True, readonly=True),
        'punch_id': fields.many2one('hr.attendance', 'Triggering Punch', readonly=True),
        'sched_detail_id': fields.many2one('hr.schedule.detail', 'Schedule Detail', readonly=True),
        'employee_id': fields.function(_get_employee_id, type='many2one', obj='hr.employee',
                                       method=True, store=True, string='Employee', readonly=True),
        'department_id': fields.related('employee_id', 'department_id', type='many2one', store=True,
                                        relation='hr.department', string='Department', readonly=True),
        'severity': fields.related('rule_id', 'severity', type='char', string='Severity',
                                   store=True, readonly=True),
        'state': fields.selection((
            ('unresolved', 'Unresolved'),
            ('resolved', 'Resolved'),
        ), 'State', readonly=True),
    }

    _defaults = {
        'state': 'unresolved',
    }

    _sql_constraints = [
        ('all_unique', 'UNIQUE(punch_id,sched_detail_id,name,rule_id)', 'Duplicate Record!')]

    _track = {
        'state': {
            'hr_schedule.mt_alert_resolved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'resolved',
            'hr_schedule.mt_alert_unresolved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'unresolved',
        },
    }

    def check_for_alerts(self, cr, uid, context=None):
        '''Check the schedule detail and attendance records for yesterday
        against the scheduling/attendance alert rules. If any rules match create a 
        record in the database.'''

        dept_obj = self.pool.get('hr.department')
        detail_obj = self.pool.get('hr.schedule.detail')
        attendance_obj = self.pool.get('hr.attendance')
        rule_obj = self.pool.get('hr.schedule.alert.rule')

        # XXX - Someone who cares about DST should fix ths
        #
        data = self.pool.get('res.users').read(
            cr, uid, uid, ['tz'], context=context)
        dtToday = datetime.strptime(
            datetime.now().strftime('%Y-%m-%d') + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        lcldtToday = timezone(data['tz'] and data['tz'] or 'UTC').localize(
            dtToday, is_dst=False)
        utcdtToday = lcldtToday.astimezone(utc)
        utcdtYesterday = utcdtToday + relativedelta(days=-1)
        strToday = utcdtToday.strftime('%Y-%m-%d %H:%M:%S')
        strYesterday = utcdtYesterday.strftime('%Y-%m-%d %H:%M:%S')

        dept_ids = dept_obj.search(cr, uid, [], context=context)
        for dept in dept_obj.browse(cr, uid, dept_ids, context=context):
            for employee in dept.member_ids:

                # Get schedule and attendance records for the employee for the day
                #
                sched_detail_ids = detail_obj.search(
                    cr, uid, [('schedule_id.employee_id', '=', employee.id),
                              '&',
                              ('date_start', '>=', strYesterday),
                              ('date_start', '<', strToday),
                              ],
                    order='date_start',
                    context=context)
                attendance_ids = attendance_obj.search(
                    cr, uid, [('employee_id', '=', employee.id),
                              '&',
                              ('name', '>=', strYesterday),
                              ('name', '<', strToday),
                              ],
                    order='name',
                    context=context)

                # Run the schedule and attendance records against each active rule, and
                # create alerts for each result returned.
                #
                rule_ids = rule_obj.search(
                    cr, uid, [('active', '=', True)], context=context)
                for rule in rule_obj.browse(cr, uid, rule_ids, context=context):
                    res = rule_obj.check_rule(cr, uid, rule,
                                              detail_obj.browse(
                                                  cr, uid, sched_detail_ids, context=context),
                                              attendance_obj.browse(
                                                  cr, uid, attendance_ids, context=context),
                                              context=context)

                    for strdt, attendance_id in res['punches']:
                        # skip if it has already been triggered
                        ids = self.search(
                            cr, uid, [('punch_id', '=', attendance_id),
                                      ('rule_id', '=', rule.id),
                                      ('name', '=', strdt),
                                      ],
                            context=context)
                        if len(ids) > 0:
                            continue

                        self.create(cr, uid, {'name': strdt,
                                              'rule_id': rule.id,
                                              'punch_id': attendance_id},
                                    context=context)

                    for strdt, detail_id in res['schedule_details']:
                        # skip if it has already been triggered
                        ids = self.search(
                            cr, uid, [('sched_detail_id', '=', detail_id),
                                      ('rule_id', '=', rule.id),
                                      ('name', '=', strdt),
                                      ],
                            context=context)
                        if len(ids) > 0:
                            continue

                        self.create(cr, uid, {'name': strdt,
                                              'rule_id': rule.id,
                                              'sched_detail_id': detail_id},
                                    context=context)

    def _get_normalized_attendance(self, cr, uid, employee_id, utcdt, att_ids, context=None):

        att_obj = self.pool.get('hr.attendance')
        attendances = att_obj.browse(cr, uid, att_ids, context=context)
        strToday = utcdt.strftime(OE_DTFORMAT)

        # If the first punch is a punch-out then get the corresponding punch-in
        # from the previous day.
        #
        if len(attendances) > 0 and attendances[0].action != 'sign_in':
            strYesterday = (utcdt - timedelta(days=1)).strftime(OE_DTFORMAT)
            ids = att_obj.search(cr, uid, [('employee_id', '=', employee_id),
                                           '&', ('name', '>=', strYesterday),
                                           ('name', '<', strToday),
                                           ],
                                 order='name', context=context)
            att2 = att_obj.browse(cr, uid, ids, context=context)
            if len(att2) > 0 and att2[-1].action == 'sign_in':
                att_ids = [att2[-1].id] + att_ids
            else:
                att_ids = att_ids[1:]

        # If the last punch is a punch-in then get the corresponding punch-out
        # from the next day.
        #
        if len(attendances) > 0 and attendances[-1].action != 'sign_out':
            strTommorow = (utcdt + timedelta(days=1)).strftime(OE_DTFORMAT)
            ids = att_obj.search(cr, uid, [('employee_id', '=', employee_id),
                                           '&', ('name', '>=', strToday),
                                           ('name', '<', strTommorow),
                                           ],
                                 order='name', context=context)
            att2 = att_obj.browse(cr, uid, ids, context=context)
            if len(att2) > 0 and att2[0].action == 'sign_out':
                att_ids = att_ids + [att2[0].id]
            else:
                att_ids = att_ids[:-1]

        return att_ids

    def compute_alerts_by_employee(self, cr, uid, employee_id, strDay, context=None):
        '''Compute alerts for employee on specified day.'''

        detail_obj = self.pool.get('hr.schedule.detail')
        attendance_obj = self.pool.get('hr.attendance')
        rule_obj = self.pool.get('hr.schedule.alert.rule')

        # XXX - Someone who cares about DST should fix ths
        #
        data = self.pool.get('res.users').read(
            cr, uid, uid, ['tz'], context=context)
        dt = datetime.strptime(strDay + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        lcldt = timezone(data['tz']).localize(dt, is_dst=False)
        utcdt = lcldt.astimezone(utc)
        utcdtNextDay = utcdt + relativedelta(days=+1)
        strToday = utcdt.strftime('%Y-%m-%d %H:%M:%S')
        strNextDay = utcdtNextDay.strftime('%Y-%m-%d %H:%M:%S')

        # Get schedule and attendance records for the employee for the day
        #
        sched_detail_ids = detail_obj.search(
            cr, uid, [('schedule_id.employee_id', '=', employee_id),
                      '&',
                      ('day', '>=', strToday),
                      ('day', '<', strNextDay),
                      ],
            order='date_start',
            context=context)
        attendance_ids = attendance_obj.search(
            cr, uid, [('employee_id', '=', employee_id),
                      '&',
                      ('name', '>=', strToday),
                      ('name', '<', strNextDay),
                      ],
            order='name',
            context=context)
        attendance_ids = self._get_normalized_attendance(
            cr, uid, employee_id, utcdt,
            attendance_ids, context)

        # Run the schedule and attendance records against each active rule, and
        # create alerts for each result returned.
        #
        rule_ids = rule_obj.search(
            cr, uid, [('active', '=', True)], context=context)
        for rule in rule_obj.browse(cr, uid, rule_ids, context=context):
            res = rule_obj.check_rule(cr, uid, rule,
                                      detail_obj.browse(
                                          cr, uid, sched_detail_ids, context=context),
                                      attendance_obj.browse(
                                          cr, uid, attendance_ids, context=context),
                                      context=context)

            for strdt, attendance_id in res['punches']:
                # skip if it has already been triggered
                ids = self.search(cr, uid, [('punch_id', '=', attendance_id),
                                            ('rule_id', '=', rule.id),
                                            ('name', '=', strdt),
                                            ],
                                  context=context)
                if len(ids) > 0:
                    continue

                self.create(cr, uid, {'name': strdt,
                                      'rule_id': rule.id,
                                      'punch_id': attendance_id},
                            context=context)

            for strdt, detail_id in res['schedule_details']:
                # skip if it has already been triggered
                ids = self.search(
                    cr, uid, [('sched_detail_id', '=', detail_id),
                              ('rule_id', '=', rule.id),
                              ('name', '=', strdt),
                              ],
                    context=context)
                if len(ids) > 0:
                    continue

                self.create(cr, uid, {'name': strdt,
                                      'rule_id': rule.id,
                                      'sched_detail_id': detail_id},
                            context=context)


class hr_schedule_alert_rule(osv.osv):

    _name = 'hr.schedule.alert.rule'
    _description = 'Scheduling/Attendance Exception Rule'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=10, required=True),
        'severity': fields.selection((
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ), 'Severity', required=True),
        'grace_period': fields.integer('Grace Period', help='In the case of early or late rules, the amount of time before/after the scheduled time that the rule will trigger.'),
        'window': fields.integer('Window of Activation'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
        'severity': 'low',
    }

    def check_rule(self, cr, uid, rule, sched_details, punches, context=None):
        '''Identify if the schedule detail or attendance records trigger any rule. If
        they do return the datetime and id of the record that triggered it in one of
        the appropriate lists.  All schedule detail and attendance records are expected
        to be in sorted order according to datetime.'''

        res = {'schedule_details': [], 'punches': []}

        if rule.code == 'MISSPUNCH':
            prev = False
            for punch in punches:
                if not prev:
                    prev = punch
                    if punch.action != 'sign_in':
                        res['punches'].append((punch.name, punch.id))
                elif prev.action == 'sign_in':
                    if punch.action != 'sign_out':
                        res['punches'].append((punch.name, punch.id))
                elif prev.action == 'sign_out':
                    if punch.action != 'sign_in':
                        res['punches'].append((punch.name, punch.id))
                prev = punch
            if len(punches) > 0 and prev.action != 'sign_out':
                res['punches'].append((punch.name, punch.id))
        elif rule.code == 'UNSCHEDATT':
            for punch in punches:
                if punch.action == 'sign_in':
                    isMatch = False
                    dtPunch = datetime.strptime(
                        punch.name, '%Y-%m-%d %H:%M:%S')
                    for detail in sched_details:
                        dtSched = datetime.strptime(
                            detail.date_start, '%Y-%m-%d %H:%M:%S')
                        difference = 0
                        if dtSched >= dtPunch:
                            difference = abs((dtSched - dtPunch).seconds) / 60
                        else:
                            difference = abs((dtPunch - dtSched).seconds) / 60
                        if difference < rule.window:
                            isMatch = True
                            break
                    if not isMatch:
                        res['punches'].append((punch.name, punch.id))
        elif rule.code == 'MISSATT':
            if len(sched_details) > len(punches):
                for detail in sched_details:
                    isMatch = False
                    dtSched = datetime.strptime(
                        detail.date_start, '%Y-%m-%d %H:%M:%S')
                    for punch in punches:
                        if punch.action == 'sign_in':
                            dtPunch = datetime.strptime(
                                punch.name, '%Y-%m-%d %H:%M:%S')
                            difference = 0
                            if dtSched >= dtPunch:
                                difference = (dtSched - dtPunch).seconds / 60
                            else:
                                difference = (dtPunch - dtSched).seconds / 60
                            if difference < rule.window:
                                isMatch = True
                                break
                    if not isMatch:
                        res['schedule_details'].append(
                            (detail.date_start, detail.id))
        elif rule.code == 'UNSCHEDOT':
            actual_hours = 0
            sched_hours = 0
            for detail in sched_details:
                dtStart = datetime.strptime(
                    detail.date_start, '%Y-%m-%d %H:%M:%S')
                dtEnd = datetime.strptime(detail.date_end, '%Y-%m-%d %H:%M:%S')
                sched_hours += float((dtEnd - dtStart).seconds / 60) / 60.0

            dtStart = False
            for punch in punches:
                if punch.action == 'sign_in':
                    dtStart = datetime.strptime(
                        punch.name, '%Y-%m-%d %H:%M:%S')
                elif punch.action == 'sign_out':
                    dtEnd = datetime.strptime(punch.name, '%Y-%m-%d %H:%M:%S')
                    actual_hours += float(
                        (dtEnd - dtStart).seconds / 60) / 60.0
                    if actual_hours > 8 and sched_hours <= 8:
                        res['punches'].append((punch.name, punch.id))
        elif rule.code == 'TARDY':
            for detail in sched_details:
                isMatch = False
                dtSched = datetime.strptime(
                    detail.date_start, '%Y-%m-%d %H:%M:%S')
                for punch in punches:
                    if punch.action == 'sign_in':
                        dtPunch = datetime.strptime(
                            punch.name, '%Y-%m-%d %H:%M:%S')
                        difference = 0
                        if dtPunch > dtSched:
                            difference = (dtPunch - dtSched).seconds / 60
                        if difference < rule.window and difference > rule.grace_period:
                            isMatch = True
                            break
                if isMatch:
                    res['punches'].append((punch.name, punch.id))
        elif rule.code == 'LVEARLY':
            for detail in sched_details:
                isMatch = False
                dtSched = datetime.strptime(
                    detail.date_end, '%Y-%m-%d %H:%M:%S')
                for punch in punches:
                    if punch.action == 'sign_out':
                        dtPunch = datetime.strptime(
                            punch.name, '%Y-%m-%d %H:%M:%S')
                        difference = 0
                        if dtPunch < dtSched:
                            difference = (dtSched - dtPunch).seconds / 60
                        if difference < rule.window and difference > rule.grace_period:
                            isMatch = True
                            break
                if isMatch:
                    res['punches'].append((punch.name, punch.id))
        elif rule.code == 'INEARLY':
            for detail in sched_details:
                isMatch = False
                dtSched = datetime.strptime(
                    detail.date_start, '%Y-%m-%d %H:%M:%S')
                for punch in punches:
                    if punch.action == 'sign_in':
                        dtPunch = datetime.strptime(
                            punch.name, '%Y-%m-%d %H:%M:%S')
                        difference = 0
                        if dtPunch < dtSched:
                            difference = (dtSched - dtPunch).seconds / 60
                        if difference < rule.window and difference > rule.grace_period:
                            isMatch = True
                            break
                if isMatch:
                    res['punches'].append((punch.name, punch.id))
        elif rule.code == 'OUTLATE':
            for detail in sched_details:
                isMatch = False
                dtSched = datetime.strptime(
                    detail.date_end, '%Y-%m-%d %H:%M:%S')
                for punch in punches:
                    if punch.action == 'sign_out':
                        dtPunch = datetime.strptime(
                            punch.name, '%Y-%m-%d %H:%M:%S')
                        difference = 0
                        if dtPunch > dtSched:
                            difference = (dtPunch - dtSched).seconds / 60
                        if difference < rule.window and difference > rule.grace_period:
                            isMatch = True
                            break
                if isMatch:
                    res['punches'].append((punch.name, punch.id))
        elif rule.code == 'OVRLP':
            leave_obj = self.pool.get('hr.holidays')
            for punch in punches:
                if punch.action == 'sign_in':
                    dtStart = datetime.strptime(
                        punch.name, '%Y-%m-%d %H:%M:%S')
                elif punch.action == 'sign_out':
                    dtEnd = datetime.strptime(punch.name, '%Y-%m-%d %H:%M:%S')
                    leave_ids = leave_obj.search(
                        cr, uid, [('employee_id', '=', punch.employee_id.id),
                                  ('type', '=', 'remove'),
                                  ('date_from', '<=', dtEnd.strftime(
                                      OE_DTFORMAT)),
                                  ('date_to', '>=', dtStart.strftime(
                                      OE_DTFORMAT)),
                                  ('state', 'in', ['validate', 'validate1'])],
                        context=context)
                    if len(leave_ids) > 0:
                        res['punches'].append((punch.name, punch.id))
                        break

        return res


class hr_schedule_template(osv.osv):

    _name = 'hr.schedule.template'
    _description = 'Employee Working Schedule Template'

    _columns = {
        'name': fields.char("Name", size=64, required=True),
        'company_id': fields.many2one('res.company', 'Company', required=False),
        'worktime_ids': fields.one2many('hr.schedule.template.worktime', 'template_id', 'Working Time'),
        'restday_ids': fields.many2many('hr.schedule.weekday', 'schedule_template_restdays_rel', 'sched_id',
                                        'weekday_id', string='Rest Days'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'resource.calendar', context=context)
    }

    def get_rest_days(self, cr, uid, t_id, context=None):
        '''If the rest day(s) have been explicitly specified that's what is returned, otherwise
        a guess is returned based on the week days that are not scheduled. If an explicit
        rest day(s) has not been specified an empty list is returned. If it is able to figure
        out the rest days it will return a list of week day integers with Monday being 0.'''

        res = []
        tpl = self.browse(cr, uid, t_id, context=context)
        if tpl.restday_ids:
            res = [rd.sequence for rd in tpl.restday_ids]
        else:
            weekdays = ['0', '1', '2', '3', '4', '5', '6']
            scheddays = []
            scheddays = [
                wt.dayofweek for wt in tpl.worktime_ids if wt.dayofweek not in scheddays]
            res = [int(d) for d in weekdays if d not in scheddays]
            # If there are no work days return nothing instead of *ALL* the
            # days in the week
            if len(res) == 7:
                res = []

        return res

    def get_hours_by_weekday(self, cr, uid, tpl_id, day_no, context=None):
        ''' Return the number working hours in the template for day_no.
        For day_no 0 is Monday.'''

        delta = timedelta(seconds=0)
        tpl = self.browse(cr, uid, tpl_id, context=context)
        for worktime in tpl.worktime_ids:
            if int(worktime.dayofweek) != day_no:
                continue

            fromHour, fromSep, fromMin = worktime.hour_from.partition(':')
            toHour, toSep, toMin = worktime.hour_to.partition(':')
            if len(fromSep) == 0 or len(toSep) == 0:
                raise osv.except_osv(
                    'Invalid Data', 'Format of working hours is incorrect')

            delta += datetime.strptime(toHour + ':' + toMin, '%H:%M') - datetime.strptime(
                fromHour + ':' + fromMin, '%H:%M')

        return float(delta.seconds / 60) / 60.0


class hr_schedule_working_times(osv.osv):

    _name = "hr.schedule.template.worktime"
    _description = "Work Detail"

    _columns = {
        'name': fields.char("Name", size=64, required=True),
        'dayofweek': fields.selection(DAYOFWEEK_SELECTION, 'Day of Week', required=True, select=True),
        'hour_from': fields.char('Work From', size=5, required=True, select=True),
        'hour_to': fields.char("Work To", size=5, required=True),
        'template_id': fields.many2one('hr.schedule.template', 'Schedule Template', required=True),
    }

    _order = 'dayofweek, name'

    _sql_constraints = [
        ('unique_template_day_from',
         'UNIQUE(template_id, dayofweek, hour_from)', 'Duplicate Records!'),
        ('unique_template_day_to',
         'UNIQUE(template_id, dayofweek, hour_to)', 'Duplicate Records!'),
    ]

    _defaults = {
        'dayofweek': '0'
    }


class contract_init(osv.Model):

    _inherit = 'hr.contract.init'

    _columns = {
        'sched_template_id': fields.many2one('hr.schedule.template', 'Schedule Template',
                                             readonly=True, states={
                                                 'draft': [('readonly', False)]}),
    }


class hr_contract(osv.osv):

    _name = 'hr.contract'
    _inherit = 'hr.contract'

    _columns = {
        'schedule_template_id': fields.many2one('hr.schedule.template', 'Working Schedule Template', required=True),
    }

    def _get_sched_template(self, cr, uid, context=None):

        res = False
        init = self.get_latest_initial_values(cr, uid, context=context)
        if init != None and init.sched_template_id:
            res = init.sched_template_id.id
        return res

    _defaults = {
        'schedule_template_id': _get_sched_template,
    }


class hr_attendance(osv.osv):

    _name = 'hr.attendance'
    _inherit = 'hr.attendance'

    _columns = {
        'alert_ids': fields.one2many('hr.schedule.alert', 'punch_id', 'Exceptions', readonly=True),
    }

    def _remove_direct_alerts(self, cr, uid, ids, context=None):
        '''Remove alerts directly attached to the attendance and return a unique
        list of tuples of employee ids and attendance dates.'''

        alert_obj = self.pool.get('hr.schedule.alert')

        # Remove alerts directly attached to the attendances
        #
        alert_ids = []
        attendances = []
        attendance_keys = []
        for attendance in self.browse(cr, uid, ids, context=context):
            [alert_ids.append(alert.id) for alert in attendance.alert_ids]
            key = str(attendance.employee_id.id) + attendance.day
            if key not in attendance_keys:
                attendances.append((attendance.employee_id.id, attendance.day))
                attendance_keys.append(key)

        if len(alert_ids) > 0:
            alert_obj.unlink(cr, uid, alert_ids, context=context)

        return attendances

    def _recompute_alerts(self, cr, uid, attendances, context=None):
        '''Recompute alerts for each record in attendances.'''

        alert_obj = self.pool.get('hr.schedule.alert')

        # Remove all alerts for the employee(s) for the day and recompute.
        #
        for ee_id, strDay in attendances:

            # Today's records will be checked tomorrow. Future records can't
            # generate alerts.
            if strDay >= fields.date.context_today(self, cr, uid, context=context):
                continue

            # XXX - Someone who cares about DST should fix this
            #
            data = self.pool.get('res.users').read(
                cr, uid, uid, ['tz'], context=context)
            dt = datetime.strptime(strDay + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            lcldt = timezone(data['tz']).localize(dt, is_dst=False)
            utcdt = lcldt.astimezone(utc)
            utcdtNextDay = utcdt + relativedelta(days=+1)
            strDayStart = utcdt.strftime('%Y-%m-%d %H:%M:%S')
            strNextDay = utcdtNextDay.strftime('%Y-%m-%d %H:%M:%S')

            alert_ids = alert_obj.search(cr, uid, [('employee_id', '=', ee_id),
                                                   '&', (
                                                       'name', '>=', strDayStart),
                                                   ('name', '<', strNextDay)],
                                         context=context)
            alert_obj.unlink(cr, uid, alert_ids, context=context)
            alert_obj.compute_alerts_by_employee(
                cr, uid, ee_id, strDay, context=context)

    def create(self, cr, uid, vals, context=None):

        res = super(hr_attendance, self).create(cr, uid, vals, context=context)

        obj = self.browse(cr, uid, res, context=context)
        attendances = [
            (obj.employee_id.id, fields.date.context_today(self, cr, uid, context=context))]
        self._recompute_alerts(cr, uid, attendances, context=context)

        return res

    def unlink(self, cr, uid, ids, context=None):

        # Remove alerts directly attached to the attendances
        #
        attendances = self._remove_direct_alerts(cr, uid, ids, context=context)

        res = super(hr_attendance, self).unlink(cr, uid, ids, context=context)

        # Remove all alerts for the employee(s) for the day and recompute.
        #
        self._recompute_alerts(cr, uid, attendances, context=context)

        return res

    def write(self, cr, uid, ids, vals, context=None):

        # Flag for checking wether we have to recompute alerts
        trigger_alert = False
        for k, v in vals.iteritems():
            if k in ['name', 'action']:
                trigger_alert = True

        if trigger_alert:
            # Remove alerts directly attached to the attendances
            #
            attendances = self._remove_direct_alerts(
                cr, uid, ids, context=context)

        res = super(hr_attendance, self).write(
            cr, uid, ids, vals, context=context)

        if trigger_alert:
            # Remove all alerts for the employee(s) for the day and recompute.
            #
            self._recompute_alerts(cr, uid, attendances, context=context)

        return res


class hr_holidays(osv.Model):

    _inherit = 'hr.holidays'

    def holidays_validate(self, cr, uid, ids, context=None):

        res = super(hr_holidays, self).holidays_validate(
            cr, uid, ids, context=context)

        if isinstance(ids, (int, long)):
            ids = [ids]

        unlink_ids = []
        det_obj = self.pool.get('hr.schedule.detail')
        for leave in self.browse(cr, uid, ids, context=context):
            if leave.type != 'remove':
                continue

            det_ids = det_obj.search(
                cr, uid, [(
                    'schedule_id.employee_id', '=', leave.employee_id.id),
                    ('date_start', '<=', leave.date_to),
                    ('date_end', '>=', leave.date_from)],
                order='date_start', context=context)
            for detail in det_obj.browse(cr, uid, det_ids, context=context):

                # Remove schedule details completely covered by leave
                if leave.date_from <= detail.date_start and leave.date_to >= detail.date_end:
                    if detail.id not in unlink_ids:
                        unlink_ids.append(detail.id)

                # Partial day on first day of leave
                elif leave.date_from > detail.date_start and leave.date_from <= detail.date_end:
                    dtLv = datetime.strptime(leave.date_from, OE_DTFORMAT)
                    if leave.date_from == detail.date_end:
                        if detail.id not in unlink_ids:
                            unlink_ids.append(detail.id)
                        else:
                            dtSchedEnd = dtLv + timedelta(seconds=-1)
                            det_obj.write(
                                cr, uid, detail.id, {
                                    'date_end': dtSchedEnd.strftime(OE_DTFORMAT)},
                                context=context)

                # Partial day on last day of leave
                elif leave.date_to < detail.date_end and leave.date_to >= detail.date_start:
                    dtLv = datetime.strptime(leave.date_to, OE_DTFORMAT)
                    if leave.date_to != detail.date_start:
                        dtStart = dtLv + timedelta(seconds=+1)
                        det_obj.write(
                            cr, uid, detail.id, {
                                'date_start': dtStart.strftime(OE_DTFORMAT)},
                            context=context)

        det_obj.unlink(cr, uid, unlink_ids, context=context)

        return res

    def holidays_refuse(self, cr, uid, ids, context=None):

        res = super(hr_holidays, self).holidays_refuse(
            cr, uid, ids, context=context)

        if isinstance(ids, (int, long)):
            ids = [ids]

        sched_obj = self.pool.get('hr.schedule')
        for leave in self.browse(cr, uid, ids, context=context):
            if leave.type != 'remove':
                continue

            dLvFrom = datetime.strptime(leave.date_from, OE_DTFORMAT).date()
            dLvTo = datetime.strptime(leave.date_to, OE_DTFORMAT).date()
            sched_ids = sched_obj.search(
                cr, uid, [('employee_id', '=', leave.employee_id.id),
                          ('date_start', '<=', dLvTo.strftime(
                              OE_DFORMAT)),
                          ('date_end', '>=', dLvFrom.strftime(OE_DFORMAT))])

            # Re-create affected schedules from scratch
            for sched_id in sched_ids:
                sched_obj.delete_details(cr, uid, sched_id, context=context)
                sched_obj.create_details(cr, uid, sched_id, context=context)

        return res


class hr_term(osv.Model):

    _inherit = 'hr.employee.termination'

    def create(self, cr, uid, vals, context=None):

        res = super(hr_term, self).create(cr, uid, vals, context=context)

        det_obj = self.pool.get('hr.schedule.detail')
        term = self.browse(cr, uid, res, context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if user and user.tz:
            local_tz = timezone(user.tz)
        else:
            local_tz = timezone('Africa/Addis_Ababa')
        dt = datetime.strptime(term.name + ' 00:00:00', OE_DTFORMAT)
        utcdt = (local_tz.localize(dt, is_dst=False)).astimezone(utc)
        det_ids = det_obj.search(
            cr, uid, [('schedule_id.employee_id', '=', term.employee_id.id),
                      ('date_start', '>=', utcdt.strftime(OE_DTFORMAT))],
            order='date_start', context=context)
        det_obj.unlink(cr, uid, det_ids, context=context)

        return res

    def _restore_schedule(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        sched_obj = self.pool.get('hr.schedule')
        for term in self.browse(cr, uid, ids, context=context):
            d = datetime.strptime(term.name, OE_DFORMAT).date()
            sched_ids = sched_obj.search(
                cr, uid, [('employee_id', '=', term.employee_id.id),
                          ('date_start', '<=', d.strftime(
                              OE_DFORMAT)),
                          ('date_end', '>=', d.strftime(OE_DFORMAT))])

            # Re-create affected schedules from scratch
            for sched_id in sched_ids:
                sched_obj.delete_details(cr, uid, sched_id, context=context)
                sched_obj.create_details(cr, uid, sched_id, context=context)

        return

    def state_cancel(self, cr, uid, ids, context=None):

        self._restore_schedule(cr, uid, ids, context=context)
        res = super(hr_term, self).state_cancel(cr, uid, ids, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):

        self._restore_schedule(cr, uid, ids, context=context)
        res = super(hr_term, self).unlink(cr, uid, ids, context=context)
        return res
