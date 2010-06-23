# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from osv import osv, fields
from osv.orm import except_orm
from tools import config
import urlparse

import os

class document_configuration_wizard(osv.osv_memory):

    _name='document.configuration.wizard'
    _description = 'Auto Directory Configuration'
    _inherit = 'res.config'   

    _columns = {
        'host': fields.char('Address', size=64,
                            help="Server address or IP and port to which users should connect to for DMS access", 
                            required=True),
    }

    _defaults = {
        'host': config.get('ftp_server_host', 'localhost') + ':' + config.get('ftp_server_port', '8021'),
    }

    def execute(self, cr, uid, ids, context=None):
        conf_id = ids and ids[0] or False
        conf = self.browse(cr, uid, conf_id, context)
        dir_pool = self.pool.get('document.directory')
        data_pool = self.pool.get('ir.model.data')
        model_pool = self.pool.get('ir.model')
        content_pool = self.pool.get('document.directory.content')
        if conf.sale_order and self.pool.get('sale.order'):
            # Sale order
            dir_data_id = data_pool._get_id(cr, uid, 'document', 'dir_sale_order_all')
            if dir_data_id:
                sale_dir_id = data_pool.browse(cr, uid, dir_data_id, context=context).res_id
            else:
                sale_dir_id = data_pool.create(cr, uid, {'name': 'Sale Orders'})
            mid = model_pool.search(cr, uid, [('model','=','sale.order')])
            dir_pool.write(cr, uid, [sale_dir_id], {
                'type':'ressource',
                'ressource_type_id': mid[0],
                'domain': '[]',
            })
            # Qutation
            dir_data_id = data_pool._get_id(cr, uid, 'document', 'dir_sale_order_quote')
            if dir_data_id:
                quta_dir_id = data_pool.browse(cr, uid, dir_data_id, context=context).res_id
            else:
                quta_dir_id = data_pool.create(cr, uid, {'name': 'Sale Quotations'})
            
            dir_pool.write(cr, uid, [quta_dir_id], {
                'type':'ressource',
                'ressource_type_id': mid[0],
                'domain': "[('state','=','draft')]",
            })
            # Sale Order Report
            order_report_data_id = data_pool._get_id(cr, uid, 'sale', 'report_sale_order')
            if order_report_data_id:
                order_report_id = data_pool.browse(cr, uid, order_report_data_id, context=context).res_id

                content_pool.create(cr, uid, {
                    'name': "Print Order",
                    'suffix': "_print",
                    'report_id': order_report_id,
                    'extension': '.pdf',
                    'include_name': 1,
                    'directory_id': sale_dir_id,
                })

                content_pool.create(cr, uid, {
                    'name': "Print Qutation",
                    'suffix': "_print",
                    'report_id': order_report_id,
                    'extension': '.pdf',
                    'include_name': 1,
                    'directory_id': quta_dir_id,
                })
            

        if conf.product and self.pool.get('product.product'):
            # Product
            dir_data_id = data_pool._get_id(cr, uid, 'document', 'dir_product')
            if dir_data_id:
                product_dir_id = data_pool.browse(cr, uid, dir_data_id, context=context).res_id
            else:
                product_dir_id = data_pool.create(cr, uid, {'name': 'Products'})
            
            mid = model_pool.search(cr, uid, [('model','=','product.product')])
            dir_pool.write(cr, uid, [product_dir_id], {
                'type':'ressource',
                'ressource_type_id': mid[0],
            })           

        if conf.project and self.pool.get('account.analytic.account'):
            # Project
            dir_data_id = data_pool._get_id(cr, uid, 'document', 'dir_project')
            if dir_data_id:
                project_dir_id = data_pool.browse(cr, uid, dir_data_id, context=context).res_id
            else:
                project_dir_id = data_pool.create(cr, uid, {'name': 'Projects'})
            
            mid = model_pool.search(cr, uid, [('model','=','account.analytic.account')])
            dir_pool.write(cr, uid, [project_dir_id], {
                'type':'ressource',
                'ressource_type_id': mid[0],
                'domain': '[]',
                'ressource_tree': 1
        })

        # Update the action for FTP browse.
        aid = objid._get_id(cr, uid, 'document_ftp', 'action_document_browse')
        aid = objid.browse(cr, uid, aid, context=context).res_id
        self.pool.get('ir.actions.url').write(cr, uid, [aid], {'url': 'ftp://'+(conf.host or 'localhost:8021')+'/'})
document_configuration_wizard()
