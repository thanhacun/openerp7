# # -*- coding: utf-8 -*-
# ##############################################################################
# #
# #    OpenERP, Open Source Management Solution
# #    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
# #
# #    This program is free software: you can redistribute it and/or modify
# #    it under the terms of the GNU Affero General Public License as
# #    published by the Free Software Foundation, either version 3 of the
# #    License, or (at your option) any later version.
# #
# #    This program is distributed in the hope that it will be useful,
# #    but WITHOUT ANY WARRANTY; without even the implied warranty of
# #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #    GNU Affero General Public License for more details.
# #
# #    You should have received a copy of the GNU Affero General Public License
# #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# #
# ##############################################################################
#
# from openerp.osv.osv import object_proxy
#
# class kderp_object_proxy(object_proxy):
#
#     # def execute_cr(self, cr, uid, model, method, *args, **kw):
#     #     fct_src = super(kderp_object_proxy, self).execute_cr
#     #     if method=='search':
#     #         def subfinder(mylist, pattern):
#     #             i = False
#     #             for i in range(len(mylist)):
#     #                 if mylist[i] == pattern[0] and mylist[i:i+len(pattern)] == pattern:
#     #                     return i
#     #             return i
#     #         context = filter(lambda arg: type(arg) == type({}) and arg.get('new_domain',False), args)
#     #         context = context[0] if context else {}
#     #         newSDomain = context.get('new_domain', [])
#     #         if context and newSDomain and type(newSDomain) == type([]):
#     #             # import ipdb
#     #             # ipdb.set_trace()
#     #             args[0].insert(subfinder(args[0], newSDomain) - 1 ,'|')
#     #     return fct_src(cr, uid, model, method, *args, **kw)
#
#     # def _check_number(self,value):
#     #     try:
#     #         return float(value)
#     #     except:
#     #         return False
#     #
#     # def _check_date(self,value):
#     #     #import time
#     #     from time import *
#     #     date = value
#     #     try:
#     #         if len(date)==10:
#     #             valid_date = strptime(date, '%d/%m/%Y')
#     #         else:
#     #             valid_date = strptime(date, '%d/%m/%y')
#     #     except:
#     #         try:
#     #             if len(date)==10:
#     #                 valid_date = strptime(date, '%Y/%m/%d')
#     #             else:
#     #                 valid_date = strptime(date, '%y/%m/%d')
#     #         except:
#     #             return False
#     #
#     #     return strftime('%Y/%m/%d',valid_date)
#
#
# kderp_object_proxy()