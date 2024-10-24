from __future__ import annotations

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.related_resources.models.related_resources import RelatedResources as related_resources
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
            u'/localhost:5000/dataset',
            u'display_mol_image',
            FooterController.display_search_mol_image,
            methods=['GET', 'POST']
        )
        return blueprint

    # ITemplate Helpers
    def get_helpers(self):
        return {'footer': FooterController.display_search_mol_image,
                'searchbar': FooterController.searchbar,
                'mol_package_list': FooterController.mol_dataset_list,
                'package_list_for_every_inchi': FooterController.package_show_dict,
                'get_molecule_data': FooterController.get_molecule_data,
                'package_list': FooterPlugin.molecule_view_search,
                'get_facet_field_list':FooterController.get_facet_field_list_sent,
               }


    @staticmethod
    def before_search(search_params: dict[str, Any]) -> dict[str, Any]:

        session['search_params'] = search_params

        return search_params

    @staticmethod
    def after_search(search_results: dict[str, Any], search_params: dict[str, Any]) -> dict[str, Any]:

        # search_params = search_params.copy()

        if search_params['q'] == '*:*':
            search_params_result = None
        else:
            search_params_result = search_params

        session['search_results_final'] = search_results
        session['search_params'] = search_params_result

        return search_results

    def molecule_view_search():
        packages_list = session.get('search_results_final', None)
        search_params = session.get('search_params', None)

        return packages_list, search_params

    # IRoutes implementation
    def before_map(self, map):
        # Redirect from /dataset to /molecule_view
        map.redirect('/dataset', '/molecule_view', _redirect_code='301')
        # Ensure /molecule_view is handled by a specific controller or function
        map.connect('molecule_view',
                    '/molecule_view',
                    controller= FooterController ,
                    action='handle_molecule_view',
                    conditions=dict(method=['GET']))

        return map