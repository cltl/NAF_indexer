import naf_classes
from glob import glob


input_folder = 'example_files'
paths = glob(f'{input_folder}/*naf')
verbose=2

naf_coll_obj_one = naf_classes.NAF_collection()
for path in paths:
    naf_coll_obj_one.add_naf_document(path, verbose=verbose)

naf_coll_obj_two = naf_classes.NAF_collection()
naf_coll_obj_two.add_naf_objects(naf_coll_obj_one.documents, verbose=verbose)

print(naf_coll_obj_two)