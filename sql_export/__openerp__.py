# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Akretion (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{'name': 'SQL Export',
 'version': '0.1',
 'author': 'Akretion,Odoo Community Association (OCA)',
 'website': 'http://www.akretion.com',
 'description': """
Allow to export data in csv files FROM sql requests.
There are some restrictions in the sql sql request, you can only read datas.
No update, deletion or creation are possible.
 """,
 'license': 'AGPL-3',
 'category': 'Generic Modules/Others',
 'summary': 'Export data in csv file with SQL requests',
 'depends': ['base',
             ],
 'data': [
     'sql_export_view.xml',
     'wizard/wizard_file_view.xml',
     'security/sql_export_security.xml',
     'security/ir.model.access.csv',
 ],
 'installable': True,
 }
