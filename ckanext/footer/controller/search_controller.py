from __future__ import annotations
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckanext.rdkit_visuals.models.molecule_rel import MolecularRelationData as mol_relation_data
from ckan.common import request

from flask import Blueprint, render_template, session

import requests
import math

import logging
import json
from typing import Any, Dict

log = logging.getLogger(__name__)


class SearchMoleculeController(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController)

    def before_search(self, query_dict):
        dataset_type = request.environ.get('CKAN_CURRENT_URL_TYPE')  # e.g. 'molecule' or 'dataset'
        if dataset_type == 'molecule':
            query_dict['rows'] = int(config.get('ckanext.footer.molecule_per_page', 10))
        return query_dict

    def check_and_redirect(self):
        ext_composite_type = toolkit.request.params.get('ext_composite_type')
        log.debug(ext_composite_type)
        if ext_composite_type == 'inchi_key':
            toolkit.redirct_to('/molecule_view?'+toolkit.request.query_string)
        else:
            return self.dataset_search()

    #def dataset_search(self):
    #    return toolkit.render('package/search.html')