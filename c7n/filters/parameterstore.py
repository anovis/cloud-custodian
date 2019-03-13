# # Copyright 2016-2019 Capital One Services, LLC
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# # http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.
# from __future__ import absolute_import, division, print_function, unicode_literals
#
# from c7n.utils import type_schema
# from .core import ValueFilter
#
#
# class ParameterStoreFilter(ValueFilter):
#     """Filter against tags in the parameter store that is associated with a resource."""
#
#     schema = type_schema('pstore', rinherit=ValueFilter.schema)
#
#     def get_resource_value(self, k, i):
#         # resource -> arn/type
#         # arb/type -> parameters
#         # parameters -> tags
#         # tags -> value
#         breakpoint(i)
#
#         if k.startswith('tag:'):
#             tk = k.split(':', 1)[1]
#             r = None
#             if 'TagList' in i:
#                 for t in i.get("Tags", []):
#                     if t.get('Key') == tk:
#                         r = t.get('Value')
#                         break
#             # GCP schema: 'labels': {'key': 'value'}
#             elif 'labels' in i:
#                 r = i.get('labels', {}).get(tk, None)
#             # GCP has a secondary form of labels called tags
#             # as labels without values.
#             # Azure schema: 'tags': {'key': 'value'}
#             elif 'tags' in i:
#                 r = i.get('tags', {}).get(tk, None)
#         elif k in i:
#             r = i.get(k)
#         else:
#             r = self.expr[k].search(i)
#         return r
#
#
# FilterRegistry.register('pstore', ParameterStoreFilter)
