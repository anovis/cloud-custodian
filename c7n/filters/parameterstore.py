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


from .core import ValueFilter, ValuesFrom, OPERATORS
from c7n.utils import local_session


class ParameterStoreFilter(ValueFilter):
    """Filter against tags in the parameter store that is associated with a resource."""

    schema = {
        'type': 'object',
        'required': ['type', 'param_key'],
        'properties': {
            'type': {'enum': ['pstore']},
            'key': {'type': 'string'},
            'param_key': {'oneOf': [
                {'type': 'array'},
                {'type': 'string'}]}
        },
        'default': {'type': 'object'},
        'value_from': ValuesFrom.schema,
        'value': {'oneOf': [
            {'type': 'array'},
            {'type': 'string'},
            {'type': 'boolean'},
            {'type': 'number'},
            {'type': 'null'}]},
        'op': {'enum': list(OPERATORS.keys())}}

    def get_parameter_key(self, i):
        param_key_input = self.data['param_key']
        if isinstance(param_key_input, str):
            parameter_key = param_key_input
        if isinstance(param_key_input, list):
            parameter_key = ""
            for pk in param_key_input:
                if pk == 'self.resource':  # make programmatic
                    parameter_key = parameter_key + '/' + self.manager.type
                else:
                    parameter_key = parameter_key + '/' + ValueFilter.get_resource_value(self, pk, i)

        return parameter_key

    def get_tag_list(self, parameter_key):
        client = local_session(self.manager.session_factory).client('ssm')
        try:
            resp = client.list_tags_for_resource(ResourceType='Parameter', ResourceId=parameter_key)
            return resp.get('TagList', [])
        except:
            return []

    def get_parameter_value(self, parameter_key, key):
        client = local_session(self.manager.session_factory).client('ssm')
        try:
            resp = client.get_parameter(Name=parameter_key)
            return resp.get('Parameter', {}).get(key)
        except:
            return None

    def get_resource_value(self, k, i):
        parameter_key = self.get_parameter_key(i)

        if k.startswith('tag:'):
            tk = k.split(':', 1)[1]
            r = None
            tag_list = self.get_tag_list(parameter_key)
            for t in tag_list:
                if t.get('Key') == tk:
                    r = t.get('Value')
                    break
        else:
            r = self.get_parameter_value(parameter_key, k)
        return r
