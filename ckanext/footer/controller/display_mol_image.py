from flask import Blueprint, render_template, session, request, redirect, url_for
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckanext.rdkit_visuals.models.molecule_rel import MolecularRelationData as mol_relation_data
from ckanext.rdkit_visuals.models.molecule_tab import Molecules as molecules_tab
#from ckanext.footer.controller.search_controller import SearchMoleculeController
import logging
import json
import re
from PIL import Image
import io
import base64
import math

log = logging.getLogger(__name__)

class FooterController:
    @staticmethod
    def display_search_mol_image(package_inchiKey, page):
        """
        Generates and returns the molecule image in base64 format.
        """
        inchi_key = package_inchiKey
        filepath = f'/var/lib/ckan/default/storage/images/{inchi_key}.png'
        log.debug(f"Generating molecule image: {inchi_key}")
        try:
            if inchi_key:
                with open(filepath, 'rb') as f:
                    file = f.read()
                image = Image.open(io.BytesIO(file))
                output = io.BytesIO()
                image.save(output, 'PNG')
                output.seek(0)
                byteimage = base64.b64encode(output.getvalue()).decode()

                # Store byteimage and page in the Flask session
                session['byteimage'] = byteimage
                session['page'] = page

                return byteimage
            else:
                return ""
        except FileNotFoundError:
            log.exception(f"Image file not found: {filepath}")
            return ""
        except Exception as e:
            log.exception(f"Error in display_search_mol_image: {str(e)}")
            return ""

    @staticmethod
    def get_molecule_data(package_id):
        """
        Generates molecular data to be displayed alongside the molecule image.
        Returns molecule formula, exact mass, and InChI.
        """
        mol_formula, inchi_n = None, None

        molecule_formula_list = mol_relation_data.get_mol_formula_by_package_id(package_id)
        exact_mass_list = mol_relation_data.get_exact_mass_by_package_id(package_id)
        inchi = mol_relation_data.get_molecule_data_by_package_id(package_id)

        if inchi:
            inchi_n = inchi[0][0].replace('["', '').replace('"]', '')

        try:
            if molecule_formula_list and exact_mass_list and inchi_n:
                mol_formula = "['']".join(molecule_formula_list[0])
                exact_mass_one = exact_mass_list[0][0]
                exact_mass = f'{exact_mass_one:.3f}'
                return mol_formula, exact_mass, inchi_n
            else:
                return None, None, None
        except TypeError:
            return None, None, None

    @staticmethod
    def searchbar():
        """
        Renders the search bar snippet.
        """
        return render_template('snippets/ckanext_footer_molecule_search_bar.html')

    @staticmethod
    def search_molecule():
        """
        Unified search function to handle both InChI Key and IUPAC Name searches.
        """
        global results
        params = request.args if request.method == 'GET' else request.form
        search_query = request.args.get('search_query', '').strip()
        log.debug(f'Search parameter given: {search_query}')

        page = int(params.get('page', 1))
        per_page = 10  # Customize as needed

        if not search_query:
            log.debug("No search query provided.")
            return redirect(url_for('footer.molecule_view'))

        # Determine if the search query is an InChI Key
        if FooterController.is_inchi_key(search_query):
            search_type = 'InChI Key'
            results, total = FooterController.search_by_inchi_key(search_query, page, per_page)
        #else:
        #    search_type = 'IUPAC Name'
        #    results, total = FooterController.search_by_iupac_name(search_query, page, per_page)

            log.debug(f'PRINT THIS {results}')
        # Store results in the Flask session for pagination and rendering
            session['search_results_final'] = results
            session['search_params'] = {
            'search_query': search_query,
            'search_type': search_type,
            'page': page,
            'per_page': per_page,
            'total': total
            }

        return FooterController.handle_molecule_view()

    @staticmethod
    def molecule_autocomplete():
        """
        Provides autocomplete suggestions based on the user's input.
        """
        term = request.args.get('term', '').strip()
        if not term:
            return json.dumps([])

        try:
            molecules = FooterController.search_autocomplete_molecules(term)
            return json.dumps(molecules['results'])

        except Exception as e:
            log.exception("Autocomplete failed.")
            return json.dumps([])

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
    def search_by_inchi_key(inchi_key, page, per_page):
        """
        Searches molecules by InChI Key.
        """
        data_dict = {'q_inchi_key': inchi_key, 'page': page, 'per_page': per_page}
        try:
            results = FooterController.molecule_search(data_dict)
            total = results.get('total', len(results.get('results', [])))
            return results, total
        except Exception as e:
            log.exception(f"Error in search_by_inchi_key: {str(e)}")
            return {}, 0

    @staticmethod
    def search_by_iupac_name(iupac_name, page, per_page):
        """
        Searches molecules by IUPAC Name.
        """
        data_dict = {'q_iupac_name': iupac_name, 'page': page, 'per_page': per_page}
        try:
            results = FooterController.molecule_search(data_dict)
            log.debug(f'Result{results}')# Ensure this returns a dictionary
            total = results.get('total', len(results.get('results', [])))  # `results` should be a dictionary
            return results, total
        except Exception as e:
            log.exception(f"Error in search_by_iupac_name: {str(e)}")
            return {}, 0

    @staticmethod
    def handle_molecule_view():
        """
        Handles rendering the molecule_view page based on session data.
        """
        search_results = session.get('search_results_final', None)
        search_params = session.get('search_params', None)

        if search_results and search_params:
            packages = search_results.get('results', [])
            search_query = search_params.get('search_query', '')
            search_type = search_params.get('search_type', '')
            log.debug(f"SEARCH TYPE {search_type}")
            page = search_params.get('page', 1)
            per_page = search_params.get('per_page', 10)
            total = search_params.get('total', 0)

            log.debug(molecules,
                search_query,
                search_type,
                page,
                per_page,
                total)

            return render_template('molecule_view/molecule_view.html',
                packages=packages,
                search_query=search_query,
                search_type=search_type,
                page=page,
                per_page=per_page,
                total=total,

            )
        else:
            # If no search has been performed, display the default view
            package_list_inchi_key, current_page, total_pages, total_datasets = FooterController.mol_dataset_list()
            log.debug(package_list_inchi_key, current_page, total_pages, total_datasets)
            return render_template('molecule_view/molecule_view.html',
                mol_dataset_list=package_list_inchi_key,
                current_page=current_page,
                total_pages=total_pages,
                total_datasets=total_datasets
            )

    @staticmethod
    def mol_dataset_list():
        """
        Retrieves the list of molecules and their associated packages for display.
        """
        page = request.args.get('page', 1, type=int)
        page_size = 10
        current_page = page

        package_list_inchi_key = mol_relation_data.get_package_list_inchi_key(page_size, current_page)
        total_datasets = mol_relation_data.get_count_rows()
        total_pages = math.ceil(total_datasets / page_size)

        return package_list_inchi_key, current_page, total_pages, total_datasets

    @staticmethod
    def package_show_dict(package_ids):
        """
        Retrieves detailed information for a list of package IDs.
        """
        package_list_for_every_inchi = []

        try:
            if package_ids:
                package_ids_list = [package_ids]

                for package_id in package_ids_list:
                    package = toolkit.get_action('package_show')({}, {'name_or_id': package_id})

                    package_list_for_every_inchi.append(package)

        except Exception as e:
            log.exception(f"Error in package_show_dict: {str(e)}")

        return package_list_for_every_inchi

    @staticmethod
    def search_autocomplete_molecules(term):
        """
        Provides up to 10 autocomplete suggestions based on the user's input.
        """
        query = model.Session.query(molecules_tab).filter(
            molecules_tab.inchi_key.ilike(f"%{term}%")
        ).limit(10)

        molecules = query.all()

        serialized = []
        for molecule in molecules:
            serialized.append({
                'id': molecule.id,
                'inchi_key': molecule.inchi_key,
                'iupac_name': molecule.iupac_name
            })

        return {'results': serialized}

    @staticmethod
    def molecule_search(data_dict):
        """
        Handles searching based on either InChI Key or IUPAC Name.
        It returns serialized results containing molecule details and associated datasets.
        """
        q_inchi_key = data_dict.get('q_inchi_key', '').strip()
        q_iupac_name = data_dict.get('q_iupac_name', '').strip()
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
                    'package_id': result.package_id,
                    'inchi_key': result.inchi_key,
                }
                for result in results
            ]

            # Return serialized results and total count
            log.debug(f"Serialized results: {serialized}")
            return {'results': serialized, 'total': total}

        # Handle the case where q_inchi_key is not provided
        else:
            return redirect(url_for('footer.molecule_view'))

