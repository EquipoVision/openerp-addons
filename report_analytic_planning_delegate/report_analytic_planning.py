##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: sale.py 1005 2005-07-25 08:41:42Z Fabien Pinckaers $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields,osv

def _get_delegated_ids(self, cr, uid, dt_from, dt_to):

class delegated_field(fields.one2many):
	def set(self, cr, obj, id, field, values, user=None, context=None):
		pass
	def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
		result = {}
		for planing in obj.browse(cr, user, ids, context):
			cr.execute('''select
					l.id 
				from
					report_account_analytic_planning_line l
				left join
					report_account_analytic_planning p on (l.planning_id=p.id)
				where
					l.delegate_id=%d and 
					l.user_id is NULL and
					p.date_from<=%s and
					p.date_to>=%s''', (planing.user_id.id, planing.date_from, planing.date_to))
			result[planing.id] = map(lambda x: x[0], cr.fetchall())
		return result

class report_account_analytic_planning(osv.osv):
	_inherit = "report_account_analytic.planning"
	_columns = {
		'delegated_ids': delegated_field('report_account_analytic.planning.line', 'planning_id', readonly=True)
	}
	_defaults = {
		'delegate_ids': lambda self,cr, uid, ctx:
	}
report_account_analytic_planning()

class report_account_analytic_planning_line(osv.osv):
	_inherit = "report_account_analytic.planning.line"
	_columns = {
		'delegate_id': fields.many2one('res.users', 'Delegate To'),
	}
report_account_analytic_planning_line()

