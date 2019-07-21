"""
Represent a folder of NAF (version 3) files

Usage:
  represent_naf.py --input_folder=<input_folder> --output_folder=<output_folder> \
  --languages=<languages> --verbose=<verbose> [--pos_mapping_file=<pos_mapping_file>]

Options:
    --input_folder=<input_folder>
    --output_folder=<output_folder>
    --languages=<languages> languages separated by -, e.g., "en" or "en-it"
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout
    [pos_mapping_file] if provided, created mapping between
    (lemma, mapped_pos) -> [sent_obj, index of lemma, mapped_pos in tokens)

    example of mapping (only keys in mapping file are used, rest is ignored):
    {
      'NOUN' : 'n':
      'VERB' : 'v',
      'ADJ' : 'a'
    }

Example:
    python represent_naf.py --input_folder="example_files" --output_folder="output" --languages="en" --verbose=1
"""
import shutil
import json
import pickle
from collections import defaultdict
from glob import glob
from path import Path

from naf_classes import Sent, Token
from lxml import etree
from docopt import docopt


# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

input_folder = arguments['--input_folder']
languages = set(arguments['--languages'].split('-'))
verbose = int(arguments['--verbose'])
output_folder = Path(arguments['--output_folder'])
if output_folder.exists():
    shutil.rmtree(str(output_folder))
output_folder.mkdir()

if arguments['--pos_mapping_file']:
    pos_mapping = json.load(open(arguments['--pos_mapping_file']))
    if verbose:
        print('loaded pos mapping')
        print(pos_mapping)
else:
    pos_mapping = {}


sent_id2sent_obj = {}
num_tokens = 0

paths = glob(f'{input_folder}/*naf')
paths_loaded = 0
for naf_file in paths:
    doc = etree.parse(naf_file)
    root = doc.getroot()
    lang = root.get('{http://www.w3.org/XML/1998/namespace}lang')

    # title
    file_desc_el = root.find('nafHeader/fileDesc')
    title = file_desc_el.get('title')

    if lang not in languages:
        if verbose >= 2:
            print(f'skipping {title} because language {lang} not in chosen languages {languages}')
        continue

    paths_loaded += 1
    if verbose >= 2:
        print()
        print(f'processing {title}')

    w_els = doc.xpath('text/wf')
    t_els = doc.xpath('terms/term')

    assert len(w_els) == len(t_els), f'{title} mismatch in number of w_els and t_els'
    num_tokens += len(w_els)

    for w_el, t_el in zip(w_els, t_els):
        sent_number = w_el.get('sent')
        sent_id = (title, sent_number)
        token_obj = Token(sent_id, w_el, t_el)

        if sent_id not in sent_id2sent_obj:
            sent_obj = Sent(sent_id, lang)
            sent_id2sent_obj[sent_id] = sent_obj
        else:
            sent_obj = sent_id2sent_obj[sent_id]

        # update dicts
        sent_obj.tokens.append(token_obj)


# do some checks
num_tokens_in_classes = sum([len(sent_obj.tokens)
                             for sent_obj in sent_id2sent_obj.values()])
assert num_tokens_in_classes == num_tokens, f'mismatch between number of wf els in files and in tokenid2token_obj'


# stats
if verbose:
    print()
    print(f'looped over {paths_loaded} files')
    print(f'found {len(sent_id2sent_obj)} sentences')
    print(f'found {num_tokens_in_classes} tokens')

# load index of lemma,pos to occurrences
lemma_pos2occurrences = defaultdict(list)
lemma_mappedpos2occurrences = defaultdict(list)

for sent_id, sent_obj in sent_id2sent_obj.items():

    lang = sent_obj.lang

    for index, token_obj in enumerate(sent_obj.tokens):
        lemma = token_obj.lemma
        pos = token_obj.pos

        lemma_pos2occurrences[(lang, lemma, pos)].append((sent_id, index))

        if pos in pos_mapping:
            mapped_pos = pos_mapping[pos]
            lemma_pos2occurrences[(lang, lemma, mapped_pos)].append((sent_id, index))

# to file
sent_objs_path = f'{output_folder}/sent_objs.p'
lemma_pos2occurrences_path = f'{output_folder}/lemma_pos2occurrences.p'
to_file = [(sent_objs_path, sent_id2sent_obj),
           (lemma_pos2occurrences_path, lemma_pos2occurrences)]

if pos_mapping:
    lemma_mappedpos2occurrences_path = f'{output_folder}/lemma_mappedpos2occurrences.p'
    to_file.append((lemma_mappedpos2occurrences_path,
                    lemma_mappedpos2occurrences))

for path, obj_ in to_file:
    with open(path, 'wb') as outfile:
        pickle.dump(obj_, outfile)