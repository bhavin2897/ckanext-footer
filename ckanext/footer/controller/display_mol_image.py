# from flask import Blueprint, render_template, session, request, redirect, url_for
# import ckan.plugins as plugins
# import ckan.plugins.toolkit as toolkit
# import ckan.model as model
# from ckanext.rdkit_visuals.models.molecule_rel import MolecularRelationData as mol_relation_data
# from ckanext.rdkit_visuals.models.molecule_tab import Molecules as molecules_tab
# #from ckanext.footer.controller.search_controller import SearchMoleculeController
# import logging
# import json
# from PIL import Image
# import io
# import base64
# import math
#
# log = logging.getLogger(__name__)
#
# class FooterController:
#     @staticmethod
#     def display_search_mol_image(package_inchiKey, page):
#         """
#         Generates and returns the molecule image in base64 format.
#         """
#         inchi_key = package_inchiKey
#         filepath = f'/var/lib/ckan/default/storage/images/{inchi_key}.png'
#
#         try:
#             if inchi_key:
#                 with open(filepath, 'rb') as f:
#                     file = f.read()
#                 image = Image.open(io.BytesIO(file))
#                 output = io.BytesIO()
#                 image.save(output, 'PNG')
#                 output.seek(0)
#                 byteimage = base64.b64encode(output.getvalue()).decode()
#
#                 # Store byteimage and page in the Flask session
#                 session['byteimage'] = byteimage
#                 session['page'] = page
#
#                 return byteimage
#             else:
#                 return ""
#         except FileNotFoundError:
#             log.exception(f"Image file not found: {filepath}")
#             return ""
#         except Exception as e:
#             log.exception(f"Error in display_search_mol_image: {str(e)}")
#             return ""
#
#     @staticmethod
#     def get_molecule_data(package_id):
#         """
#         Generates molecular data to be displayed alongside the molecule image.
#         Returns molecule formula, exact mass, and InChI.
#         """
#         mol_formula, inchi_n = None, None
#
#         molecule_formula_list = mol_relation_data.get_mol_formula_by_package_id(package_id)
#         exact_mass_list = mol_relation_data.get_exact_mass_by_package_id(package_id)
#         inchi = mol_relation_data.get_molecule_data_by_package_id(package_id)
#
#         if inchi:
#             inchi_n = inchi[0][0].replace('["', '').replace('"]', '')
#
#         try:
#             if molecule_formula_list and exact_mass_list and inchi_n:
#                 mol_formula = "['']".join(molecule_formula_list[0])
#                 exact_mass_one = exact_mass_list[0][0]
#                 exact_mass = f'{exact_mass_one:.3f}'
#                 return mol_formula, exact_mass, inchi_n
#             else:
#                 return None, None, None
#         except TypeError:
#             return None, None, None
#
#     @staticmethod
#     def searchbar():
#         """
#         Renders the search bar snippet.
#         """
#         return render_template('snippets/ckanext_footer_molecule_search_bar.html')
#
#     @staticmethod
#     def search_molecule():
#         """
#         Unified search function to handle both InChI Key and IUPAC Name searches.
#         """
#         global results
#         params = request.args if request.method == 'GET' else request.form
#         search_query = request.args.get('search_query', '').strip()
#         log.debug(f'Search parameter given: {search_query}')
#
#         page = int(params.get('page', 1))
#         per_page = 10  # Customize as needed
#
#         if not search_query:
#             log.debug("No search query provided.")
#             return redirect(url_for('footer.molecule_view'))
#
#         # Determine if the search query is an InChI Key
#         if FooterController.is_inchi_key(search_query):
#             search_type = 'InChI Key'
#             results, total = FooterController.search_by_inchi_key(search_query, page, per_page)
#         #else:
#         #    search_type = 'IUPAC Name'
#         #    results, total = FooterController.search_by_iupac_name(search_query, page, per_page)
#
#             log.debug(f'PRINT THIS {results}')
#         # Store results in the Flask session for pagination and rendering
#             session['search_results_final'] = results
#             session['search_params'] = {
#             'search_query': search_query,
#             'search_type': search_type,
#             'page': page,
#             'per_page': per_page,
#             'total': total
#             }
#
#         return FooterController.handle_molecule_view()
#
#     @staticmethod
#     def molecule_autocomplete():
#         """
#         Provides autocomplete suggestions based on the user's input.
#         """
#         term = request.args.get('term', '').strip()
#         if not term:
#             return json.dumps([])
#
#         try:
#             molecules = FooterController.search_autocomplete_molecules(term)
#             return json.dumps(molecules['results'])
#
#         except Exception as e:
#             log.exception("Autocomplete failed.")
#             return json.dumps([])
#
#     @staticmethod
#     def is_inchi_key(query):
#         """
#         Determines if the query matches the InChI Key format.
#         InChI Keys are 27 characters long, consisting of uppercase letters and numbers, separated by hyphens.
#         Example: BSYNRYMUTXBXSQ-UHFFFAOYSA-N
#         """
#         pattern = re.compile(r'^[A-Z]{14}-[A-Z]{10}-[A-Z]$')
#         return bool(pattern.match(query))
#
#     @staticmethod
#     def search_by_inchi_key(inchi_key, page, per_page):
#         """
#         Searches molecules by InChI Key.
#         """
#         data_dict = {'q_inchi_key': inchi_key, 'page': page, 'per_page': per_page}
#         try:
#             results = FooterController.molecule_search(data_dict)
#             total = results.get('total', len(results.get('results', [])))
#             return results, total
#         except Exception as e:
#             log.exception(f"Error in search_by_inchi_key: {str(e)}")
#             return {}, 0
#
#     @staticmethod
#     def search_by_iupac_name(iupac_name, page, per_page):
#         """
#         Searches molecules by IUPAC Name.
#         """
#         data_dict = {'q_iupac_name': iupac_name, 'page': page, 'per_page': per_page}
#         try:
#             results = FooterController.molecule_search(data_dict)
#             log.debug(f'Result{results}')# Ensure this returns a dictionary
#             total = results.get('total', len(results.get('results', [])))  # `results` should be a dictionary
#             return results, total
#         except Exception as e:
#             log.exception(f"Error in search_by_iupac_name: {str(e)}")
#             return {}, 0
#
#     @staticmethod
#     def handle_molecule_view():
#         """
#         Handles rendering the molecule_view page based on session data.
#         """
#         search_results = session.get('search_results_final', None)
#         search_params = session.get('search_params', None)
#
#         if search_results and search_params:
#             packages = search_results.get('results', [])
#             search_query = search_params.get('search_query', '')
#             search_type = search_params.get('search_type', '')
#             log.debug(f"SEARCH TYPE {search_type}")
#             page = search_params.get('page', 1)
#             per_page = search_params.get('per_page', 10)
#             total = search_params.get('total', 0)
#
#             # Fetch full package dictionaries
#             packages = []
#             for result in results:
#                 package_id = result['package_id']
#                 package = toolkit.get_action('package_show')({}, {'id': package_id})
#                 #package['type'] = 'dataset'  # Ensure 'type' is set correctly
#                 #package['inchi_key'] = result['inchi_key']  # Include 'inchi_key' if needed
#                 packages.append(package)
#
#             return render_template(
#                 'molecule_view/molecule_view.html',
#                 packages=packages,
#                 search_query=search_query,
#                 search_type=search_type,
#                 page=page,
#                 per_page=per_page,
#                 total=total,
#             )
#
#         else:
#             # If no search has been performed, display the default view
#             package_list_inchi_key, current_page, total_pages, total_datasets = FooterController.mol_dataset_list()
#             log.debug(package_list_inchi_key, current_page, total_pages, total_datasets)
#             return render_template('molecule_view/molecule_view.html',
#                 mol_dataset_list=package_list_inchi_key,
#                 current_page=current_page,
#                 total_pages=total_pages,
#                 total_datasets=total_datasets
#             )
#
#     @staticmethod
#     def mol_dataset_list():
#         """
#         Retrieves the list of molecules and their associated packages for display.
#         """
#         page = request.args.get('page', 1, type=int)
#         page_size = 10
#         current_page = page
#
#         package_list_inchi_key = mol_relation_data.get_package_list_inchi_key(page_size, current_page)
#         total_datasets = mol_relation_data.get_count_rows()
#         total_pages = math.ceil(total_datasets / page_size)
#
#         return package_list_inchi_key, current_page, total_pages, total_datasets
#
#     @staticmethod
#     def package_show_dict(package_ids):
#         """
#         Retrieves detailed information for a list of package IDs.
#         """
#         package_list_for_every_inchi = []
#
#         try:
#             if package_ids:
#                 package_ids_list = [package_ids]
#
#                 for package_id in package_ids_list:
#                     package = toolkit.get_action('package_show')({}, {'name_or_id': package_id})
#                     log.debug(f"PACKAGE {package}")
#                     # Ensure package.type is 'dataset'
#                     package['type'] = 'dataset'
#
#                     package_list_for_every_inchi.append(package)
#
#         except Exception as e:
#             log.exception(f"Error in package_show_dict: {str(e)}")
#
#         return package_list_for_every_inchi
#
#     @staticmethod
#     def search_autocomplete_molecules(term):
#         """
#         Provides up to 10 autocomplete suggestions based on the user's input.
#         """
#         query = model.Session.query(molecules_tab).filter(
#             molecules_tab.inchi_key.ilike(f"%{term}%")
#         ).limit(10)
#
#         molecules = query.all()
#
#         serialized = []
#         for molecule in molecules:
#             serialized.append({
#                 'id': molecule.id,
#                 'inchi_key': molecule.inchi_key,
#                 'iupac_name': molecule.iupac_name
#             })
#
#         return {'results': serialized}
#
#     @staticmethod
#     def molecule_search(data_dict):
#         """
#         Handles searching based on either InChI Key or IUPAC Name.
#         It returns serialized results containing molecule details and associated datasets.
#         """
#         q_inchi_key = data_dict.get('q_inchi_key', '').strip()
#         q_iupac_name = data_dict.get('q_iupac_name', '').strip()
#         page = int(data_dict.get('page', 1))
#         per_page = int(data_dict.get('per_page', 10))
#
#         query = model.Session.query(molecules_tab)
#
#         # Handle case when q_inchi_key is provided
#         if q_inchi_key:
#             # Join the tables and filter based on the inchi_key condition
#             query = query.join(mol_relation_data, molecules_tab.id == mol_relation_data.molecules_id) \
#                 .filter(molecules_tab.inchi_key.ilike(f"%{q_inchi_key}%"))
#
#             # Fetch the necessary fields: package_id from mol_relation_data and inchi_key from molecules_tab
#             query = query.with_entities(
#                 mol_relation_data.package_id,
#                 molecules_tab.inchi_key
#             )
#
#             # Log the retrieved package_id and inchi_key pairs
#             dataset_ids = query.all()
#             log.debug(f"Retrieved data (package_id, inchi_key): {dataset_ids}")
#
#             # Get the total count of rows
#             total = query.count()
#             log.debug(f"Total: {total}")
#
#             # Paginate the query by using offset and limit
#             results = query.offset((page - 1) * per_page).limit(per_page).all()
#
#             # Serialize the results
#             serialized = [
#                 {
#                     'package_id': result.package_id,
#                     'inchi_key': result.inchi_key,
#                 }
#                 for result in results
#             ]
#
#             # Return serialized results and total count
#             log.debug(f"Serialized results: {serialized}")
#             return {'results': serialized, 'total': total}
#
#         # Handle the case where q_inchi_key is not provided
#         else:
#             return redirect(url_for('footer.molecule_view'))



from __future__ import annotations
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
import re


from ckanext.rdkit_visuals.models.molecule_rel import MolecularRelationData as mol_relation_data
#from ckanext.rdkit_visuals.models.molecule_rel import MolecularRelationData as mol_relation_data
from ckanext.rdkit_visuals.models.molecule_tab import Molecules as molecules_tab

from rapidfuzz import process, fuzz

from flask import Blueprint, render_template, session, request, redirect, url_for
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



# def get_facet_field_list(package_ids):
#
#     package_to_facet = [row[1] for row in package_ids]
#
#     fq = " OR ".join(f"id:{pkg_id}" for pkg_id in package_to_facet)
#
#
#
#     facets_per_dataset = toolkit.get_action('package_search')({},
#                                                               {'fq': '196793-29-0-dept416', 'facet.field': ['tags', 'organization',
#                                                                                                  'measurement_technique',
#                                                                                                  'license_id'],
#                                                                'facet': True,
#                                                                'rows': 0})
#
#     return facets_per_dataset


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

        inchi,iupac_name = mol_relation_data.get_molecule_data_by_package_id(package_id)

        inchi_n = inchi[0][0].replace('["', '').replace('"]', '')

        # log.debug(inchi_n)
        try:
            for x in molecule_formula_list:
                mol_formula = "['']".join(x)
                exact_mass_one = exact_mass_list[0][0]
                exact_mass = '%.3f' % exact_mass_one
                return mol_formula, exact_mass, inchi_n,iupac_name[0][0]

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

    @staticmethod
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

        # if package_list_inchi_key:
            # facet_field_list = get_facet_field_list(package_list_inchi_key)
            # session['facet_field_list_final'] = facet_field_list

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
        log.debug(f'It reach till here {package_ids}')
        try:
            if isinstance(package_ids,list):
                package_ids_list = package_ids
            else:
                package_ids_list = [package_ids]

            for package_id in package_ids_list:
                package = toolkit.get_action('package_show')({}, {'name_or_id': package_id})
                package_list_for_every_inchi.append(package)

        except Exception as e:
            log.exception(e)

        #log.debug(f'package_list_for_every_inchi: {package_list_for_every_inchi}')
        return package_list_for_every_inchi


    # def get_facet_field_list_sent():
    #     """
    #     Get all Facets Field in PackageSearch all!!
    #
    #     :return:
    #     """
    #
    #     facets_list = session.get('facet_field_list_final', None)
    #     #log.debug(facets_list)
    #     return facets_list

    def search_molecule():
        params = request.args if request.method == 'GET' else request.form
        search_query = request.args.get('search_query', '').strip()
        log.debug(f'Search parameter given: {search_query}')

        page = int(params.get('page', 1))
        per_page = 10  # Customize as needed

        if not search_query:
            log.debug("No search query provided.")
            return redirect(url_for('footer.molecule_view'))

        if FooterController.is_inchi_key(search_query):
            results, total = FooterController.search_by_inchi_key(search_query, page, per_page)
        else:
            # Try searching by IUPAC Name
            results, total = FooterController.search_by_iupac_name(search_query, page, per_page)
            if total == 0:
                # If no results, search by alternate_names with fuzzy matching
                results, total = FooterController.search_by_alternate_name(search_query, page, per_page)

        if total > 0:
            package_ids = [result['id'] for result in results['results']]
            display = {'results': FooterController.package_show_dict(package_ids)}
            # log.debug(f"DISPLAY RESULTS :{display}")
            return render_template('molecule_view/molecule_view_self.html', packages=display)
        else:
            log.debug("No results found for search query.")
            return redirect(url_for('footer.molecule_view'))


    @staticmethod
    def search_by_inchi_key(inchi_key, page, per_page):
            """
            Searches molecules by InChI Key.
            """
            log.debug("Search based on InChI Key")
            data_dict = {'q_inchi_key': inchi_key, 'page': page, 'per_page': per_page}

            try:
                results = FooterController.molecule_search(data_dict)
                total = results.get('total', len(results.get('results', [])))
                return results, total
            except Exception as e:
                log.exception(f"Error in search_by_inchi_key: {str(e)}")
                return {}, 0

    @staticmethod
    def is_inchi_key(query):
            """
            Determines if the query matches the InChI Key format.
            InChI Keys are 27 characters long, consisting of uppercase letters and numbers, separated by hyphens.
            Example: BSYNRYMUTXBXSQ-UHFFFAOYSA-N
            """
            pattern = re.compile(r'^[A-Z]{14}-[A-Z]{10}-[A-Z]$')
            return bool(pattern.match(query))

    @staticmethod
    def molecule_search(data_dict):
            """
            Handles searching based on either InChI Key or IUPAC Name.
            It returns serialized results containing molecule details and associated datasets.
            """
            q_inchi_key = data_dict.get('q_inchi_key', '').strip()
            q_iupac_name = data_dict.get('q_iupac_name', '').strip()
            q_alternate_name = data_dict.get('q_alternate_name', '').strip()
            page = int(data_dict.get('page', 1))
            per_page = int(data_dict.get('per_page', 10))

            query = model.Session.query(molecules_tab)

            # Handle case when q_inchi_key is provided
            if q_inchi_key:
                # Join the tables and filter based on the inchi_key condition
                query = query.join(mol_relation_data, molecules_tab.id == mol_relation_data.molecules_id) \
                    .filter(molecules_tab.inchi_key.ilike(f"%{q_inchi_key}%"))

                # Fetch the necessary fields: package_id from mol_relation_data and inchi_key from molecules_tab
                query = query.with_entities(
                    mol_relation_data.package_id,
                    molecules_tab.inchi_key
                )

                # Log the retrieved package_id and inchi_key pairs
                dataset_ids = query.all()
                log.debug(f"Retrieved data (package_id, inchi_key): {dataset_ids}")

                # Get the total count of rows
                total = query.count()
                log.debug(f"Total: {total}")

                # Paginate the query by using offset and limit
                results = query.offset((page - 1) * per_page).limit(per_page).all()

                # Serialize the results
                serialized = [
                    {
                        'id': result.package_id,
                        'inchi_key': result.inchi_key,
                    }
                    for result in results
                ]

                # Return serialized results and total count
                return {'results': serialized, 'total': total}

            elif q_iupac_name:
                query = query.join(
                    mol_relation_data, molecules_tab.id == mol_relation_data.molecules_id
                ).filter(
                    molecules_tab.iupac_name.ilike(f"%{q_iupac_name}%")
                )

                # Fetch the necessary fields: package_id from mol_relation_data and iupac_name from molecules_tab
                query = query.with_entities(
                    mol_relation_data.package_id,
                    molecules_tab.iupac_name
                )

                # Log the retrieved package_id and iupac_name pairs
                dataset_ids = query.all()
                log.debug(f"Retrieved data (package_id, iupac_name): {dataset_ids}")

                # Get the total count of rows
                total = query.count()
                log.debug(f"Total: {total}")

                # Paginate the query by using offset and limit
                results = query.offset((page - 1) * per_page).limit(per_page).all()

                # Serialize the results
                serialized = [
                    {
                        'id': result.package_id,
                        'iupac_name': result.iupac_name,
                    }
                    for result in results
                ]

                # Return serialized results and total count
                return {'results': serialized, 'total': total}

            # Alternate Name ssearch
            elif q_alternate_name:

                # Fetch molecules where alternate_names is not null
                query = query.join(
                    mol_relation_data, molecules_tab.id == mol_relation_data.molecules_id
                ).filter(
                    molecules_tab.alternate_names.isnot(None)
                )

                # Fetch necessary fields
                query = query.with_entities(
                    mol_relation_data.package_id,
                    molecules_tab.alternate_names
                )

                # Execute the query
                results = query.all()

                # Build a list of all alternate names with their associated package IDs
                alternate_name_mapping = []
                for result in results:
                    package_id = result.package_id
                    alternate_names = result.alternate_names

                    if alternate_names:
                        # Parse the alternate_names field
                        try:
                            # Assuming alternate_names is stored as JSON array
                            names_list = json.loads(alternate_names)
                        except (TypeError, json.JSONDecodeError):
                            # If not JSON, treat it as a comma-separated string
                            names_list = [name.strip() for name in alternate_names.split(',')]

                        # Add each alternate name to the mapping
                        for name in names_list:
                            alternate_name_mapping.append({
                                'package_id': package_id,
                                'alternate_name': name
                            })

                # Perform fuzzy matching using rapidfuzz
                search_names = [item['alternate_name'] for item in alternate_name_mapping]
                matches = process.extract(q_alternate_name, search_names, scorer=fuzz.WRatio, limit=1000)

                # Filter matches based on a similarity threshold
                threshold = 80  # Adjust as needed
                matched_packages = []
                for match in matches:
                    name, score, index = match
                    if score >= threshold:
                        package_info = alternate_name_mapping[index]
                        matched_packages.append({
                            'id': package_info['package_id'],
                            'alternate_name': name,
                            'similarity': score
                        })

                # Remove duplicates while keeping the highest similarity score
                unique_matched_packages = {}
                for item in matched_packages:
                    key = item['id']
                    if key not in unique_matched_packages or item['similarity'] > unique_matched_packages[key][
                        'similarity']:
                        unique_matched_packages[key] = item

                # Convert back to list
                matched_packages = list(unique_matched_packages.values())

                # Get total count
                total = len(matched_packages)
                log.debug(f"Total matched packages: {total}")

                # Paginate results
                start = (page - 1) * per_page
                end = start + per_page
                paginated_results = matched_packages[start:end]

                # Return serialized results and total count
                return {'results': paginated_results, 'total': total}

            # Handle the case where q_inchi_key is not provided
            else:
                return redirect(url_for('footer.molecule_view'))

    @staticmethod
    def search_by_iupac_name(iupac_name, page, per_page):
        """
        Searches molecules by IUPAC Name.
        """

        log.debug("Search based on iupac name" )
        data_dict = {'q_iupac_name': iupac_name, 'page': page, 'per_page': per_page}

        try:
            results = FooterController.molecule_search(data_dict)
            total = results.get('total', len(results.get('results', [])))  # `results` should be a dictionary
            return results, total
        except Exception as e:
            log.exception(f"Error in search_by_iupac_name: {str(e)}")
            return {}, 0

    @staticmethod
    def search_by_alternate_name(alternate_name, page, per_page):

        log.debug("Search based on Alternate name")
        data_dict = {'q_alternate_name': alternate_name, 'page': page, 'per_page': per_page}

        try:
            results = FooterController.molecule_search(data_dict)
            total = results.get('total', len(results.get('results', [])))  # `results` should be a dictionary
            return results, total
        except Exception as e:
            log.exception(f"Error in search_by_iupac_name: {str(e)}")
            return {}, 0