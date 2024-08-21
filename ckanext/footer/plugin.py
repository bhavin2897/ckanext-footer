from __future__ import annotations

import ckan.plugins as plugins
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckanext.related_resources.models.related_resources import RelatedResources as related_resources
import ckan.logic as logic

from flask import Blueprint, render_template, session , request, abort
import asyncio
from ckanext.footer.controller.display_mol_image import FooterController

import logging
import json
from typing import Any, Dict

log = logging.getLogger(__name__)
get_action = logic.get_action

local_host = '/localhost:5000'


def molecule_view():
    context = {'model': model}

    # Gather search parameters, possibly from form data or query strings
    data_dict = {
        'q': request.args.get('q', '')  # Adjust this according to how search queries are made
    }

    # Apply before_search modifications
    modified_params = FooterPlugin.before_search(data_dict)
    log.debug(modified_params)

    # Execute search (this is a placeholder, replace with your actual search call)
    try:
        search_results = logic.get_action('package_search')(context, modified_params)

        # Process results with after_search
        processed_results = FooterPlugin.after_search(search_results, modified_params)

        # Render template with processed results
        return render_template('molecule_view.html', search_results=processed_results)

    except logic.NotFound:
        abort(404)

class FooterPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IPackageController, inherit=True)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/statics', 'footer')

    def get_blueprint(self):
        blueprint = Blueprint(self.name, __name__)

        blueprint.add_url_rule('/molecule_view', 'molecule_view', molecule_view, methods=['GET', 'POST'])
        blueprint.add_url_rule('/search_bar', 'search_bar', FooterController.searchbar, methods=['GET', 'POST'])
        blueprint.add_url_rule(f'{local_host}/dataset', 'display_mol_image', FooterController.display_search_mol_image, methods=['GET', 'POST'])

        return blueprint

    # Template Helpers
    def get_helpers(self):
        return {
            'footer': FooterController.display_search_mol_image,
            'searchbar': FooterController.searchbar,
            'mol_package_list': FooterController.mol_dataset_list,
            'package_list_for_every_inchi': FooterController.package_show_dict,
            'get_molecule_data': FooterController.get_molecule_data,
            'package_list': FooterPlugin.molecule_view_search
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
        return search_results

    def molecule_view_search():
        packages_list = session.get('search_results_final', None)
        search_params = session.get('search_params', None)
        return packages_list, search_params
