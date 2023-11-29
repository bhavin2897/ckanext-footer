[![Tests](https://github.com/TIB/ckanext-footer/workflows/Tests/badge.svg?branch=main)](https://github.com/TIB/ckanext-footer/actions)

# ckanext-footer

Extension for following Static page and views on Frontend for NFDI4Chem Search Service
1. Footer Info
2. Header Page and Page navigation 
3. Help Page 
4. About Page
5. Molecule View Page 
6. Imprint and Datenschutz 


The Extension mostly provides functionality for designing the Molecule_View CKAN template page.
Molecule_View displays Datasets and image for every Molecule present in the Search Service.  

For every Molecule InChIKey search, the molecule_view gives the User to visualize image and their dataset. 
****************************************************************
## Requirements

**CKAN Extensions prerequisites:**
- ckanext-search-tweaks (https://github.com/bhavin2897/ckanext-search-tweaks)
- ckanext-rdkit-visuals (https://github.com/bhavin2897/ckanext-rdkit-visuals)

If your extension works across different versions you can add the following table:

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.8             | not tested    |
| 2.9             | Yes    |

********************************


## Installation

To install ckanext-footer:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/TIB/ckanext-footer.git
    cd ckanext-footer
    pip install -e .
	pip install -r requirements.txt

3. Add `footer` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings

None at present

## Developer installation

To install ckanext-footer for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/TIB/ckanext-footer.git
    cd ckanext-footer
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## Releasing a new version of ckanext-footer

If ckanext-footer should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `setup.py` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

2. Make sure you have the latest version of necessary packages:

    pip install --upgrade setuptools wheel twine

3. Create a source and binary distributions of the new version:

       python setup.py sdist bdist_wheel && twine check dist/*

   Fix any errors you get.

4. Upload the source distribution to PyPI:

       twine upload dist/*

5. Commit any outstanding changes:

       git commit -a
       git push

6. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:

       git tag 0.0.1
       git push --tags

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
