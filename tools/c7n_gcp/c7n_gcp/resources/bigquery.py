# Copyright 2018 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import jmespath

from c7n.utils import type_schema, local_session, chunks
from c7n_gcp.query import QueryResourceManager, TypeInfo
from c7n_gcp.provider import resources
from c7n_gcp.actions.core import MethodAction


@resources.register('bq-dataset')
class DataSet(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'bigquery'
        version = 'v2'
        component = 'datasets'
        enum_spec = ('list', 'datasets[]', None)
        scope = 'project'
        scope_key = 'projectId'
        get_requires_event = True
        id = "id"

        @staticmethod
        def get(client, event):
            # dataset creation doesn't include data set name in resource name.
            _, method = event['protoPayload']['methodName'].split('.')
            if method not in ('insert', 'update'):
                raise RuntimeError("unknown event %s" % event)
            expr = 'protoPayload.serviceData.dataset{}Response.resource.datasetName'.format(
                method.capitalize())
            ref = jmespath.search(expr, event)
            return client.execute_query('get', verb_arguments=ref)

    def augment(self, resources):
        client = self.get_client()
        results = []
        for r in resources:
            ref = r['datasetReference']
            results.append(
                client.execute_query(
                    'get', verb_arguments=ref))
        return results


@resources.register('bq-job')
class BigQueryJob(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'bigquery'
        version = 'v2'
        component = 'jobs'
        enum_spec = ('list', 'jobs[]', {'allUsers': True})
        scope = 'project'
        scope_key = 'projectId'
        id = 'id'

        @staticmethod
        def get(client, resource_info):
            return client.execute_query('get', {
                'projectId': resource_info['project_id'],
                'jobId': resource_info['job_id']
            })


@resources.register('bq-project')
class BigQueryProject(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'bigquery'
        version = 'v2'
        component = 'projects'
        enum_spec = ('list', 'projects[]', None)
        scope = 'global'
        id = 'id'


@resources.register('bq-capacity-commitment')
class BigQueryCapacityCommitment(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'bigqueryreservation'
        version = 'v1'
        component = 'projects.locations.capacityCommitments'
        enum_spec = ("list", 'capacityCommitments[]', None)
        scope = 'project'
        scope_key = 'parent'
        scope_template = "projects/{}/locations/{region}"
        id = 'name'


@BigQueryProject.action_registry.register('create-capacity-commitment')
class CreateCapacity(MethodAction):

    schema = type_schema(
        'create-capacity-commitment',
        required=['slotCount','plan'],
        slotCount={"type": "number", "min": 100},
        plan={"type": "string", "enum":["FLEX","TRIAL","MONTHLY","ANNUAL"]}
    )
    method_spec = {'op': 'create'}

    def get_resource_params(self, model, resource):
        body_params = {
            'slotCount':self.data['slotCount'],
            'plan':self.data['plan']
            }
        region = local_session(self.manager.session_factory).get_default_region()
        return {'body': body_params, 'parent': 'projects/{}/locations/{}'.format(resource['id'], region)}

    def process(self, resources):
        if self.attr_filter:
            resources = self.filter_resources(resources)
        m = BigQueryCapacityCommitment.resource_type
        session = local_session(self.manager.session_factory)
        client = self.get_client(session, m)
        for resource_set in chunks(resources, self.chunk_size):
            self.process_resource_set(client, m, resource_set)


@BigQueryCapacityCommitment.action_registry.register('delete')
class DeleteCapacity(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_resource_params(self, model, resource):
        return {'name': resource['name']}