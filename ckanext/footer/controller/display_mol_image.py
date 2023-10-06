import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, render_template, session

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from PIL import Image
import io
import base64



class FooterController():

    @staticmethod
    def display_search_mol_image(package_inchiKey,page):

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


    def searchbar():


        byte_image = session.get('byteimage', None)
        page = session.get('page', None)

        return render_template('search_bar/search_bar.html', bytename=byte_image, page=page)


