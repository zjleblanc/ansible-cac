#!/usr/bin/python
import yaml

class FilterModule(object):
    ASSET_TYPES_W_SCHEDULE = ['inventory_sources', 'job_templates', 'workflow_job_templates']

    def filters(self):
        return {
            'process_assets': self.do_process_assets,
            'parse_credentials': self.do_parse_credentials,
            'parse_inventories': self.do_parse_inventories,
            'parse_inventory_sources': self.do_parse_inventory_sources,
            'parse_job_templates': self.do_parse_job_templates,
            'parse_workflow_job_templates': self.do_parse_workflow_job_templates,
            'parse_projects': self.do_parse_projects,
        }

    ## filters ##

    def do_process_assets(self, assets):
        assets.pop('schedules', None)
        for asset_type in self.ASSET_TYPES_W_SCHEDULE:
            for asset in assets.get(asset_type, []):
              asset['related'].pop('schedules', None)

        return assets
    
    def do_parse_credentials(self, credentials):
      for cred in credentials:
        cred.pop('natural_key', None)
        cred.pop('user', None)
        cred.pop('team', None)
        if not cred.get('organization', None):
          cred['organization'] = 'Autodotes'
        for input in cred.get('inputs', {}).keys():
          if cred['inputs'][input] == '$encrypted$':
            cred['inputs'][input] = 'REPLACE_ME'

      return {"controller_credentials": credentials}
    
    def do_parse_inventories(self, inventories):
      for inv in inventories:
        inv.pop('natural_key', None)

      return {"controller_inventories": inventories}
    
    def do_parse_inventory_sources(self, inventory_sources):
      for src in inventory_sources:
        src.pop('natural_key', None)
        src.pop('related', None)
        self.__get_name_or_pop(src, 'inventory')
        self.__get_name_or_pop(src, 'credential')
        self.__get_name_or_pop(src, 'source_project')
        self.__get_name_or_pop(src, 'execution_environment')
        self.__load_vars_or_empty(src, 'source_vars')

      return {"controller_inventory_sources": inventory_sources}
    
    def do_parse_job_templates(self, job_templates):
      for jt in job_templates:
        jt.pop('natural_key', None)
        self.__get_name_or_pop(jt, 'inventory')
        self.__get_name_or_pop(jt, 'project')
        self.__get_name_or_pop(jt, 'execution_environment')
        self.__load_vars_or_empty(jt, 'extra_vars')

        jt['credentials'] = list(map(lambda cred: cred['name'], jt.get('related', {}).get('credentials', [])))
        jt['survey_spec'] = jt.get('related', {}).get('survey_spec', False)
        jt.pop('related', None)

        self.__drop_defaults(jt)

      return {"controller_templates": job_templates}
    
    def do_parse_workflow_job_templates(self, workflow_job_templates):
      for wjt in workflow_job_templates:
        wjt.pop('natural_key', None)
        self.__get_name_or_pop(wjt, 'organization')
        self.__get_name_or_pop(wjt, 'inventory')
        self.__get_name_or_pop(wjt, 'project')
        self.__get_name_or_pop(wjt, 'execution_environment')
        self.__load_vars_or_empty(wjt, 'extra_vars')

        wjt['credentials'] = list(map(lambda cred: cred['name'], wjt.get('related', {}).get('credentials', [])))
        wjt['survey_spec'] = wjt.get('related', {}).get('survey_spec', False)
        wjt['workflow_nodes'] = wjt.get('related', {}).get('workflow_nodes', False)
        wjt.pop('related', None)

        self.__process_workflow_node(wjt['workflow_nodes'])
        self.__drop_defaults(wjt)

      return {"controller_workflows": workflow_job_templates}
    
    def do_parse_projects(self, projects):
      for proj in projects:
        proj.pop('natural_key', None)
        self.__get_name_or_pop(proj, 'credential')
        self.__get_name_or_pop(proj, 'organization')
        self.__get_name_or_pop(proj, 'default_environment')
        proj.pop('related', None)
        proj.pop('local_path', None)
        self.__drop_defaults(proj)

      return {"controller_projects": projects}
    
    ## private helpers ##'

    def __process_workflow_node(self, workflow_nodes):
      for node in workflow_nodes:
        node.pop('natural_key', None)
        self.__get_name_or_pop(node, 'inventory')
        self.__get_name_or_pop(node, 'execution_environment')
        self.__load_vars_or_empty(node, 'extra_data')
        self.__process_related_nodes(node)
        self.__drop_defaults(node.get('related', {}))
        self.__drop_defaults(node)

    def __process_related_nodes(self, node):
      if node.get('related', None):
        node.pop('workflow_job_template', None)
        node['related']['always_nodes'] = list(map(lambda rn: {"identifier": rn['identifier']}, node['related'].get('always_nodes', [])))
        node['related']['success_nodes'] = list(map(lambda rn: {"identifier": rn['identifier']}, node['related'].get('success_nodes', [])))
        node['related']['failure_nodes'] = list(map(lambda rn: {"identifier": rn['identifier']}, node['related'].get('failure_nodes', [])))

    def __drop_defaults(self, resource):
      for field in list(resource):
        if not resource[field]:
          resource.pop(field)
        elif isinstance(resource[field], (int, bool, str)) and not resource[field]:
          resource.pop(field)
        elif isinstance(resource[field], (dict, list)) and not len(resource):
          resource.pop(field)
        else:
          continue

    def __get_name_or_pop(self, resource: dict, key: str, name_key='name'):
      if resource.get(key, None):
        resource[key] =  resource[key][name_key]
      else:
        resource.pop(key, None)

    def __load_vars_or_empty(self, resource, key):
      if resource.get(key, None):
        try:
          resource[key] = yaml.safe_load(resource[key])
        except:
          resource[key] = {}