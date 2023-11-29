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


from PIL import Image
import io
import base64


log = logging.getLogger(__name__)


class FooterController(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController, inherit=True)

    @staticmethod
    def display_search_mol_image(package_inchiKey, page):

        inchi_key = package_inchiKey

        filepath = '/var/lib/ckan/default/storage/images/' + str(inchi_key) + '.png'
        file = open(filepath, 'rb').read()
        image = Image.open(io.BytesIO(file))
        output = io.BytesIO()
        image.save(output, 'PNG')
        output.seek(0)
        byteimage = base64.b64encode(output.getvalue()).decode()

        # Store byteimage in the session
        session['byteimage'] = byteimage
        session['page'] = page

        return byteimage


    def get_molecule_data(package_id):

        mol_formula = []
        #exact_mass = []

        molecule_formula_list = mol_relation_data.get_mol_formula_by_package_id(package_id)
        exact_mass_list = mol_relation_data.get_exact_mass_by_package_id(package_id)

        try:
            for x in molecule_formula_list:
                mol_formula = "['']".join(x)

        except TypeError:
            pass

        exact_mass_one = exact_mass_list[0][0]
        exact_mass = '%.3f' % exact_mass_one
        return mol_formula, exact_mass


    def searchbar():
        byte_image = session.get('byteimage', None)
        page = session.get('page', None)

        return render_template('search_bar/search_bar.html', bytename=byte_image, page=page, )


    def mol_dataset_list():
        page = toolkit.request.args.get('page', 1, type=int)
        current_page = page
        page_size = 10

        package_list_inchi_key = mol_relation_data.get_package_list_inchi_key(page_size, current_page)

        total_datasets = mol_relation_data.get_count_rows()
        total_pages = math.ceil(total_datasets / page_size)
        
        return package_list_inchi_key, current_page, total_pages, total_datasets



    def package_show_dict(package_ids):

        package_list_for_every_inchi = []
        try:
            if package_ids:
                package_ids_list = [package_ids]

                for package_id in package_ids_list:
                    package = toolkit.get_action('package_show')({}, {'name_or_id': package_id})
                    package_list_for_every_inchi.append(package)
                    # log.debug(f'{package_list_for_every_inchi}')
        except Exception as e:
            log.debug(e)

        return package_list_for_every_inchi

