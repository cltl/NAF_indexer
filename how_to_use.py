import pickle


input_folder = 'output'

sent_objs_path = f'{input_folder}/sent_objs.p'
lemma_pos2occurrences_path = f'{input_folder}/lemma_pos2occurrences.p'
lemma_mappedpos2occurrences_path = f'{input_folder}/lemma_mappedpos2occurrences.p'

sent_objs = pickle.load(open(sent_objs_path, 'rb'))
lemma_pos2occurrences = pickle.load(open(lemma_pos2occurrences_path, 'rb'))

language = 'en'
lemma = 'election'
pos = 'NOUN'
occurrences = lemma_pos2occurrences[(language, lemma, pos)]

print(f'occurrences of {lemma} {pos}')
print()
for (title, sent_id), index in occurrences:
    sent_obj = sent_objs[(title, sent_id)]
    print(f'INDEX: {index} for {language} {lemma} {pos}')
    print(sent_obj)