from __future__ import annotations
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, render_template, session

import requests
import math

import logging
import json
from typing import Any, Dict

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from PIL import Image
import io
import base64

from rdkit.Chem import inchi
from rdkit.Chem import rdmolfiles
from rdkit.Chem import Draw
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors

log = logging.getLogger(__name__)


DB_HOST = "localhost"
DB_USER = "ckan_default"
DB_NAME = "ckan_default"
DB_pwd = "123456789"

# # Sample search values used for testing sample_search_q = 'BWFYMIDEWZXNAH-BNEYPBHNSA-N' sample_q = 'inchi_key:* AND
# +inchi_key:("' + sample_search_q + '")' sample_search_q_val =
# 'ext_composite_value=ZPPQIOUITZSYAO-UHFFFAOYSA-O&ext_composite_negation=&ext_composite_type=inchi_key
# &ext_composite_junction=AND&sort=score+desc%2C+metadata_modified+desc',

# This controller, finds the relavent image when search through InChiKey.
# And sends the bytes of the image to front-end template

class FooterController(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController, inherit=True)

    @staticmethod
    def display_search_mol_image(package_inchiKey, page):
        global mol_formula, iupacName
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

        try:
        # Get Molecular Formula using PubChem
            r = requests.get(
                f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/{inchi_key}/property/MolecularFormula,IUPACName/JSON').json()
            mol_formula = r['PropertyTable']['Properties'][0]['MolecularFormula']

        # Get IUPAC name using PubChem
            iupacName = r['PropertyTable']['Properties'][0]['IUPACName']
        except Execption as e:
            log.debug(e)

        return byteimage, mol_formula, iupacName

    def searchbar():
        byte_image = session.get('byteimage', None)
        page = session.get('page', None)

        return render_template('search_bar/search_bar.html', bytename=byte_image, page=page, )

    def mol_dataset_list():
        # List of datasets which have inchi_key as molecular Image.
        page = toolkit.request.args.get('page', 1, type=int)
        current_page = page

        page_size = 20

        package_list_inchi_key = []

        con = psycopg2.connect(user=DB_USER,
                               host=DB_HOST,
                               password=DB_pwd,
                               dbname=DB_NAME)

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Cursor
        cur = con.cursor()
        cur2 = con.cursor()
        #cur.execute("SELECT DISTINCT ON (molecules_id) package_id FROM molecule_rel_data LIMIT %s OFFSET (%s - 1) * %s", (page_size, current_page, page_size))

        cur.execute("SELECT m.inchi_key, a.package_ids FROM (SELECT molecules_id, STRING_AGG(package_id::text, ', ') AS "
                    "package_ids FROM molecule_rel_data GROUP BY molecules_id) a JOIN molecules m ON a.molecules_id = m.id"
                    " LIMIT %s OFFSET (%s - 1) * %s", (page_size, current_page, page_size))

        cur2.execute("SELECT COUNT(*) FROM (SELECT DISTINCT ON (molecules_id) package_id FROM molecule_rel_data) AS distinct_rows")
        dataset_id_list = cur.fetchall()


        #type = dataset_id_list.type

        #log.debug(f'Molecule ID : {dataset_id_list}')
        #log.debug(f'package IDs : {dataset_id_list[1]}')

        total_datasets = cur2.fetchone()[0]

        #log.debug(f'nr of dataset {dataset_id_list}')

        # commit cursor
        con.commit()
        # close cursor
        cur.close()
        # close connection
        con.close()

        #for dataset_id in dataset_id_list:
         #   package = toolkit.get_action('package_show')({}, {'name_or_id': dataset_id})
        #  package_list_inchi_key.append(package)

        package_list_inchi_key = dataset_id_list

        total_pages = math.ceil(total_datasets/page_size)

        return package_list_inchi_key, current_page, total_pages, total_datasets


    def package_show_dict(package_ids):

        package_list_for_every_inchi =[]
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
