
from ckan.lib.base import abort

"""
Handles searching based on either InChI Key or IUPAC Name. 
It returns serialized results containing molecule details and associated datasets.
"""

def molecule_search(context, data_dict):
    model = context['model']
    session = context['session']

    q_inchi_key = data_dict.get('q_inchi_key', '').strip()
    q_iupac_name = data_dict.get('q_iupac_name', '').strip()
    page = int(data_dict.get('page', 1))
    per_page = int(data_dict.get('per_page', 10))

    query = session.query(model.Molecule)

    if q_inchi_key:
        query = query.filter(model.Molecule.inchi_key.ilike(f"%{q_inchi_key}%"))
    elif q_iupac_name:
        query = query.filter(model.Molecule.iupac_name.ilike(f"%{q_iupac_name}%"))
    else:
        abort(400, 'No search parameter provided.')

    total = query.count()
    molecules = query.offset((page - 1) * per_page).limit(per_page).all()

    # Serialize the results
    serialized = []
    for molecule in molecules:
        serialized.append({
            'id': molecule.id,
            'inchi_key': molecule.inchi_key,
            'iupac_name': molecule.iupac_name,
            'datasets': [dataset.to_dict() for dataset in molecule.datasets]
        })

    return {'results': serialized, 'total': total}
