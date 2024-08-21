from __future__ import annotations
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model

from ckanext.rdkit_visuals.models.molecule_rel import MolecularRelationData as mol_relation_data

from flask import Blueprint, render_template, session

import requests
import math

import logging
import json
from typing import Any, Dict

log = logging.getLogger(__name__)


class SearchMoleculeController(plugins.SingletonPlugin):


    def check_and_redirect(self):
        ext_composite_type = toolkit.request.params.get('ext_composite_type')
        log.debug(ext_composite_type)
        if ext_composite_type == 'inchi_key':
            toolkit.redirct_to('/molecule_view?'+toolkit.request.query_string)
        else:
            return self.dataset_search()


    def dataset_search(self):
        return toolkit.render('dataset/search.html')