from __future__ import annotations

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.related_resources.models.related_resources import RelatedResources as related_resources
from ckanext.footer.controller.search_controller import SearchMoleculeController
import ckan.logic as logic

from flask import Blueprint, render_template, session
import asyncio
from ckanext.footer.controller.display_mol_image import FooterController


import logging
import json
from typing import Any, Dict

log = logging.getLogger(__name__)

get_action = logic.get_action


def molecule_view():
    return render_template('molecule_view/molecule_view.html')
def searched_molecule_view():
    return render_template('molecule_view/molecule_view_self.html')


class FooterPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IRoutes,inherit=True)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/statics', 'footer')

    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)


        blueprint.add_url_rule(
            u'/molecule_view',
            u'molecule_view',
            molecule_view,
            methods=['GET', 'POST']
        )

        blueprint.add_url_rule(
            u'/search_bar',
            u'search_bar',
            FooterController.searchbar,
            methods=['GET', 'POST']
        )

        blueprint.add_url_rule(
                        '/moleculesearch',
                        'molecule_view_self',
                        FooterController.search_molecule,
                        methods=['GET', 'POST'] )

        blueprint.add_url_rule(
            u'/dataset',
            u'display_mol_image',
            FooterController.display_search_mol_image,
            methods=['GET', 'POST'])

        return blueprint

    # ITemplate Helpers
    def get_helpers(self):
        return {'footer': FooterController.display_search_mol_image,
                'searchbar': FooterController.searchbar,
                'mol_package_list': FooterController.mol_dataset_list,
                'package_list_for_every_inchi': FooterController.package_show_dict,
                'get_molecule_data': FooterController.get_molecule_data,
                'package_list': FooterPlugin.molecule_view_search,
                #'get_facet_field_list':FooterController.get_facet_field_list_sent,
                #'package_list': FooterController.molecule_view_list
               }

    @staticmethod
    def before_search(search_params: Dict[str, Any]) -> Dict[str, Any]:
        # Example modification: add a logging for debug and modify query if empty
        if search_params.get('q', '') == '':
            search_params['q'] = '*:*'  # default query if none provided
        session['initial_search_params'] = search_params
        return search_params

    @staticmethod
    def after_search(search_results: Dict[str, Any], search_params: Dict[str, Any]) -> Dict[str, Any]:
        search_params = search_params.copy()
        if search_params['q'] == '*:*':
            search_params_result = None
        else:
            search_params_result = search_params

        session['search_results_final'] = search_results
        session['search_params'] = search_params_result
        session.save()
        #log.debug("THESE ARE THE RESULTS:%s" %search_results)

        return search_results

    @staticmethod
    def molecule_view_search():
        packages_list = session.get('search_results_final', None)
        search_params = session.get('search_params', None)
        #log.debug(f'THESE ARE THE RESULTS : final {packages_list}')

        return packages_list, search_params
