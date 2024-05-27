from __future__ import annotations
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model

from ckanext.rdkit_visuals.models.molecule_rel import MolecularRelationData as mol_relation_data

from flask import Blueprint, render_template, session
from ckanext.footer.controller.search_controller import SearchMoleculeController
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
        """
        Function to generate image in bytes code, which is later converted to an image, using the packageID
        Similar to the RDKit Visuals extension!!

        :param package_inchiKey: Receives InChIKey from the HTML which is an advanced Search & an exact Match
        :param page: page number we are in(starting from 0)
        :return: Either returns image in the format of bytecode or NONE
        """

        inchi_key = package_inchiKey

        try:
            if inchi_key:

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

            else:
                return 0

        except Exception as e:
            log.debug(f"Error in display_search_mol_image {e}")

    def get_molecule_data(package_id):
        """
        generates molecular data, that is displayed besides the molecule image, for the particular molecule

        :param package_id: receives package id from
        :return: molecule formal, exact mass and inchi are returned to display beside the image
        """

        mol_formula = []
        inchi_n = []
        # package_id_show = package_id

        molecule_formula_list = mol_relation_data.get_mol_formula_by_package_id(package_id)
        exact_mass_list = mol_relation_data.get_exact_mass_by_package_id(package_id)

        inchi = mol_relation_data.get_molecule_data_by_package_id(package_id)

        inchi_n = inchi[0][0].replace('["', '').replace('"]', '')

        # log.debug(inchi_n)
        try:
            for x in molecule_formula_list:
                mol_formula = "['']".join(x)
                exact_mass_one = exact_mass_list[0][0]
                exact_mass = '%.3f' % exact_mass_one
                return mol_formula, exact_mass, inchi_n

        except TypeError:
            return None, None, None

    def searchbar():
        """
        to render data to HTML using flask blueprint
        :return: render_template of Flask.blueprint
        """
        byte_image = session.get('byteimage', None)
        page = session.get('page', None)

        return render_template('search_bar/search_bar.html', bytename=byte_image, page=page, )

    def mol_dataset_list():
        """
        Gets the numbers of the page, and sends to the 'get_package_list' alembic method,
        to return the list of InChIKey & packageID pair

        :return: list of packages paired [InChIKey, packageID], along with 'current page', 'total pages' and
        'total datasets'.
        """
        page = toolkit.request.args.get('page', 1, type=int)
        current_page = page
        page_size = 10

        package_list_inchi_key = mol_relation_data.get_package_list_inchi_key(page_size, current_page)

        total_datasets = mol_relation_data.get_count_rows()
        total_pages = math.ceil(total_datasets / page_size)

        return package_list_inchi_key, current_page, total_pages, total_datasets

    def package_show_dict(package_ids):
        """
        List of all packages/datasets
        :return:
        """

        package_list_for_every_inchi = []
        facet_field_list = []

        try:
            if package_ids:
                package_ids_list = [package_ids]

                for package_id in package_ids_list:
                    package = toolkit.get_action('package_show')({}, {'name_or_id': package_id})
                    package_list_for_every_inchi.append(package)

        except Exception as e:
            log.exception(e)

        return package_list_for_every_inchi


    def get_facet_field_list():
        """
        Get all Facets Field in PackageSearch all!!

        :return:
        """

        facet_field_list = []
        facets_per_dataset = toolkit.get_action('package_search')({}, {'fq': '', 'facet.field': ['tags', 'organization',
                                                                                                 'measurement_technique',
                                                                                                 'license_id']})

        facet_field_list.append(facets_per_dataset)

        return facet_field_list
