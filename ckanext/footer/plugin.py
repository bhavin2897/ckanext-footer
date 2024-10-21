from __future__ import annotations

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from flask import Blueprint, render_template, session

from .controller.display_mol_image import FooterController
from .logic import molecule_search, molecule_autocomplete_search
import logging
import math
import json
from typing import Any, Dict

log = logging.getLogger(__name__)


def molecule_view():
    return FooterController.handle_molecule_view()


class FooterPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IRoutes)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/statics', 'footer')

    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)

        # Define routes
        blueprint.add_url_rule(
            '/molecule_view/',
            'molecule_view',
            molecule_view,
            methods=['GET', 'POST']
        )

        blueprint.add_url_rule(
            '/search_bar',
            'search_bar',
            FooterController.searchbar,
            methods=['GET', 'POST']
        )

        blueprint.add_url_rule(
            '/display_mol_image',
            'display_mol_image',
            FooterController.display_search_mol_image,
            methods=['GET', 'POST']
        )

        blueprint.add_url_rule(
            '/moleculesearch',
            'moleculesearch',
            FooterController.search_molecule,
            methods=['GET', 'POST']
        )

        blueprint.add_url_rule(
            '/moleculeauto',
            'moleculeauto',
            FooterController.molecule_autocomplete,
            methods=['GET', 'POST']
        )


        return blueprint

    # ITemplate Helpers
    def get_helpers(self):
        return {
            'footer': FooterController.display_search_mol_image,
            'searchbar': FooterController.searchbar,
            'mol_package_list': FooterController.mol_dataset_list,
            'package_list_for_every_inchi': FooterController.package_show_dict,
            'get_molecule_data': FooterController.get_molecule_data,
            'package_list': FooterPlugin.molecule_view_search,  # Corrected to use handle_molecule_view
            'molecule_search': FooterController.molecule_search,
            #'molecule_autocomplete_search': FooterController.molecule_autocomplete_search,

        }

    # IActions
    def get_actions(self):
    #    # Import action functions
        return {
            'molecule_search': molecule_search,
            'molecule_autocomplete_search': molecule_autocomplete_search
        }

    @staticmethod
    def before_search(search_params: dict[str, Any]) -> dict[str, Any]:

        session['search_params'] = search_params
        log.debug(f"before Search {search_params}")

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
