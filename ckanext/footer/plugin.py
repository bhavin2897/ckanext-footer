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
