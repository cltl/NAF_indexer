"""
Represent a folder of NAF (version 3) files
"""
import json
import pickle
from glob import glob
import naf_classes

input_folder = 'example_files'
paths = glob(f'{input_folder}/*naf')
verbose=3

# this is optional
pos_mapping =  json.load(open('example_files/pos_mapping.json'))

# create NAF_collection class instance
naf_coll_obj = naf_classes.NAF_collection()
for path in paths:
    naf_coll_obj.add_naf_document(path,
                                  load_distributions=True,
                                  pos_mapping=pos_mapping,
                                  verbose=verbose)

# merge all distributions at the collection level
naf_coll_obj.merge_distributions('terms')
naf_coll_obj.merge_distributions('predicates')

# show top n items
term_df = naf_coll_obj.distribution_as_df('terms')
print(term_df.head(10))

predicate_df = naf_coll_obj.distribution_as_df('predicates')
print(predicate_df.head(10))

# show occurrences
occurrences = naf_coll_obj.print_occurrences('terms', 'en', 'wedding---N')
occurrences = naf_coll_obj.print_occurrences('predicates', 'en', 'Forming_relationships')

print(naf_coll_obj)

with open('output/example.p', 'wb') as outfile:
    pickle.dump(naf_coll_obj, outfile)