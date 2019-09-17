"""
Represent a folder of NAF (version 3) files
"""
import json
from glob import glob
from lxml import etree
import naf_classes

input_folder = 'example_files'
paths = glob(f'{input_folder}/*naf')
verbose=2

# this is optional
pos_mapping =  json.load(open('example_files/pos_mapping.json'))

# create NAF_collection class instance
naf_coll_obj = naf_classes.NAF_collection()
naf_coll_obj.add_naf_documents(paths, verbose=verbose)

# load distributions per file: terms
for naf_obj in naf_coll_obj.documents:
    naf_obj.set_terms_attribute(pos_mapping)

# merge all distributions at the collection level
naf_coll_obj.merge_distributions('terms')

# show top n items
df = naf_coll_obj.distribution_as_df('terms')
print(df.head(10))

# show occurrences
#occurrences = naf_coll_obj.print_occurrences('terms', 'en', 'wedding---N')


