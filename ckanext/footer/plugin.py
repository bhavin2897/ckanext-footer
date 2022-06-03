import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, render_template

def help():
    return render_template('help.html')

def imprint():
    return render_template('imprint.html')

def dataprotection():
    return render_template('data_protection.html')


class FooterPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IRoutes, inherit=True)


    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
            'footer')

    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.add_url_rule(
            u'/help',
            u'help',
            help,
            methods=['GET']
        )

        blueprint.add_url_rule(
            u'/imprint',
            u'imprint',
            imprint,
            methods = ['GET']
        )

        blueprint.add_url_rule(
            u'/data_protection',
            u'data_protection',
            dataprotection,
            methods=['GET']
        )
        return blueprint

    def before_map(self, map):
        org_controller = 'ckan.controllers.organization:OrganizationController'
        with SubMapper(map, controller = org_controller) as m:
            m.connect('repository_index', '/repository', action='index')
            m.connect('/repository/list', action='list')
            m.connect('/repository/new', action='new')
            m.connect('/repository/{action}/{id}',
                      requirements=dict(action='|'.join([
                          'delete',
                          'admins',
                          'member_new',
                          'member_delete',
                          'history'
                      ])))
            m.connect('repository_activity', '/repository/activity/{id}',
                      action='activity', ckan_icon='time')
            m.connect('repository_read', '/repository/{id}', action='read')
            m.connect('repository_about', '/repository/about/{id}',
                      action='about', ckan_icon='info-sign')
            m.connect('repository_read', '/repository/{id}', action='read',
                      ckan_icon='sitemap')
            m.connect('repository_edit', '/repository/edit/{id}',
                      action='edit', ckan_icon='edit')
            m.connect('repository_members', '/repository/edit_members/{id}',
                      action='members', ckan_icon='group')
            m.connect('repository_bulk_process',
                      '/repository/bulk_process/{id}',
                      action='bulk_process', ckan_icon='sitemap')

        map.redirect('/api/{ver:1|2|3}/rest/repository',
                     '/api/{ver}/rest/group')
        map.redirect('/api/rest/repository', '/api/rest/group')
        map.redirect('/api/{ver:1|2|3}/rest/repository/{url:.*}',
                     '/api/{ver}/rest/group/{url:.*}')
        map.redirect('/api/rest/repository/{url:.*}',
                     '/api/rest/group/{url:.*}')

        map.connect('repository_members_read', '/repository/members/{id}',
                    controller='ckanext.iati.controllers.repository:repositoryController',
                    action='members_read', ckan_icon='group')

        return map

    def after_map(self,map):
        return map