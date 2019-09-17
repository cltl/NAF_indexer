from collections import defaultdict, Counter
from lxml import etree
import pandas

def perc_it(value, total, decimal_points=2):
    if not value:
        return 0

    perc = 100 * (value / total)
    return round(perc, decimal_points)

def get_span_tids(el):
    """

    :param el:
    :return:
    """
    has_references_child = el.find('references') is not None

    if has_references_child:
        query_path = 'references/span/target'
    else:
        query_path = 'span/target'

    t_ids = []
    for target_el in el.xpath(query_path):
        t_id = target_el.get('id')
        t_ids.append(t_id)

    return t_ids

el = etree.fromstring("""<predicate id="pr6" uri="Forming_relationships">
      <span>
        <target id="t44"/>
      </span>
    </predicate>""")
assert get_span_tids(el) == ['t44']

el = etree.fromstring("""<entity id="e2" type="UNK">
      <references>
        <span>
          <!--D u k e   o f   E d i n b u r g h-->
          <target id="t36"/>
          <target id="t37"/>
          <target id="t38"/>
        </span>
      </references>
      <externalReferences>
        <externalRef reference="http://en.wikipedia.org/wiki/Duke_of_Edinburgh" resource="Wikipedia"/>
        <externalRef reference="http://it.wikipedia.org/wiki/Duca_di_Edimburgo" resource="Wikipedia"/>
        <externalRef reference="http://nl.wikipedia.org/wiki/Hertog_van_Edinburgh" resource="Wikipedia"/>
      </externalReferences>
    </entity>""")
assert get_span_tids(el) == ['t36', 't37', 't38']




class NAF_collection:
    """

    """
    def __init__(self):
        self.documents = []
        self.lang_title2naf_obj = {}

        self.supported = {'terms', 'predicates'}


    def __str__(self):
        info = []
        info.append(f'number of documents: {len(self.documents)}')
        lang_distr = Counter([lang
                              for lang, title in self.lang_title2naf_obj])
        info.append(f'language distribution: {lang_distr}')

        return '\n'.join(info)

    def add_naf_objects(self, naf_objects, verbose=0):
        """
        add instances of class NAF_documents
        (you might use this if you merge different instances of NAF_collection objects)

        :param naf_objects:
        :return:
        """
        added = 0
        total = len(naf_objects)
        for naf_object in naf_objects:
            key = (naf_object.language,
                   naf_object.title)
            if key not in self.lang_title2naf_obj:
                self.lang_title2naf_obj[key] = naf_object
                self.documents.append(naf_object)
                added += 1

        assert len(self.documents) == len(self.lang_title2naf_obj)

        if verbose >= 2:
            print(f'added {added} naf object out of the {total} provided')

    def add_naf_document(self, path, load_distributions=False, pos_mapping={}, verbose=0):
        """
        create NAF_document class instance and update
        -self.documents
        -self.lang_title2naf_obj

        :param iterable paths: iterable of paths to NAF files
        """
        doc = etree.parse(path)
        root = doc.getroot()
        lang = root.get('{http://www.w3.org/XML/1998/namespace}lang')

        # title
        file_desc_el = root.find('nafHeader/fileDesc')
        title = file_desc_el.get('title')

        naf_obj = NAF_document(title, lang, doc)
        self.lang_title2naf_obj[(lang, title)] = naf_obj

        if verbose >= 3:
            print()
            print(f'processing {title}')

        w_els = doc.xpath('text/wf')
        t_els = doc.xpath('terms/term')

        assert len(w_els) == len(t_els), f'{title} mismatch in number of w_els and t_els'

        for w_el, t_el in zip(w_els, t_els):
            sent_number = w_el.get('sent')
            sent_id = int(sent_number)
            token_obj = Token(sent_id, w_el, t_el)

            if sent_id not in naf_obj.sent_id2sent_obj:
                sent_obj = Sent(sent_id, lang)
                naf_obj.sent_id2sent_obj[sent_id] = sent_obj
            else:
                sent_obj = naf_obj.sent_id2sent_obj[sent_id]

            # update dicts
            sent_obj.tokens.append(token_obj)

            w_id = token_obj.token_id
            t_id = naf_obj.wid2tid[w_id]
            index = len(sent_obj.tokens)

            naf_obj.tid2sentid_index[t_id] = (sent_id, index)

        if load_distributions:
            naf_obj.set_terms_attribute(pos_mapping)
            naf_obj.set_predicate_attribute(doc)

        self.documents.append(naf_obj)

        return naf_obj

    def merge_distributions(self, attribute):
        """

        :param attribute:
        :return:
        """
        assert attribute in self.supported, f'supported: {self.supported} -> enter: {attribute}'

        merged_info = {
            'distribution' : defaultdict(int),
            'occurrences' : defaultdict(list),
        }
        for naf_obj in self.documents:

            doc_info = getattr(naf_obj, attribute)

            for key, value in doc_info['distribution'].items():
                merged_info['distribution'][key] += value

            for key, value in doc_info['occurrences'].items():
                merged_info['occurrences'][key].extend(value)

        setattr(self, attribute, merged_info)

    def distribution_as_df(self, attribute, rel_freq=True):
        """
        return distribution as df with optionally the relative frequency

        :param str attribute: terms

        :return: pandas Dataframe
        """
        supported = {'terms'}
        assert attribute in self.supported, f'supported: {self.supported} -> enter: {attribute}'

        list_of_lists = []
        headers = [attribute, 'Freq']
        if rel_freq:
            headers.append('%')

        distribution = getattr(self, attribute)['distribution']
        total = sum(distribution.values())
        for key, value in distribution.items():

            one_row = [key, value]

            if rel_freq:
                perc = perc_it(value, total)
                one_row.append(perc)

            list_of_lists.append(one_row)

        df = pandas.DataFrame(list_of_lists, columns=headers)

        return df


    def print_occurrences(self, attribute, lang, item):
        """

        :param str attribute: supported: terms
        :param str lang: en | it | nl
        :param item : e.g, 'wedding---N'
        """
        supported = {'terms'}
        assert attribute in self.supported, f'supported: {self.supported} -> enter: {attribute}'

        all_occurrences = getattr(self, attribute)['occurrences']
        occurrences = all_occurrences[(lang, item)]

        for title, sent_id, index in occurrences:
            naf_obj = self.lang_title2naf_obj[(lang, title)]
            sent_obj = naf_obj.sent_id2sent_obj[sent_id]
            print(f'INDEX: {index} for {lang} {item}')
            print(sent_obj)


class NAF_document:
    """

    """
    def __init__(self,
                 title,
                 language,
                 doc):
        self.title = title
        self.language = language
        self.sent_id2sent_obj = {}

        self.wid2tid = self.load_wid2tid(doc)
        self.tid2sentid_index = {}

    def load_wid2tid(self, doc):
        wid2tid = {}
        for target_el in doc.xpath('terms/term/span/target'):
            w_id = target_el.get('id')
            grandparent = target_el.getparent().getparent()
            t_id = grandparent.get('id')
            wid2tid[w_id] = t_id

        return wid2tid


    def set_terms_attribute(self, pos_mapping={}):
        lemma_pos2occurrences = defaultdict(list)

        for sent_id, sent_obj in self.sent_id2sent_obj.items():
            lang = sent_obj.lang

            for index, token_obj in enumerate(sent_obj.tokens):
                lemma = token_obj.lemma
                pos = token_obj.pos

                add = False
                pos_to_use = pos

                if pos_mapping:
                    if pos in pos_mapping:
                        pos_to_use = pos_mapping[pos]
                        add = True
                else:
                    add = True

                if add:
                    item = '---'.join([lemma, pos_to_use])
                    lemma_pos2occurrences[(lang, item)].append((self.title, sent_id, [index]))

        distribution = Counter([key
                                for key, occurrences in lemma_pos2occurrences.items()
                                for _ in range(len(occurrences))])

        self.terms = {'occurrences' : lemma_pos2occurrences,
                      'distribution' : distribution}


    def set_predicate_attribute(self,
                                doc,
                                verbose=0):
        """
        """
        all_occurrences = defaultdict(list)

        for el in doc.xpath('srl/predicate'):

            predicate = el.get('uri')

            # get t_ids
            t_ids = get_span_tids(el)

            sent_ids = []
            indices = []
            for t_id in t_ids:
                sent_id, t_index = self.tid2sentid_index[t_id]
                sent_ids.append(sent_id)
                indices.append(t_index)

            assert len(set(sent_ids)) == 1
            sent_id = sent_ids[0]

            occurrence = [self.title, sent_id, indices]

            all_occurrences[(self.language, predicate)].append(occurrence)

        distribution = Counter([key
                                for key, occurrences in all_occurrences.items()
                                for _ in range(len(occurrences))])

        self.predicates = {'occurrences': all_occurrences,
                           'distribution': distribution}







class Sent:
    """

    """
    def __init__(self, id_, lang):
        self.id_ = id_
        self.lang = lang
        self.tokens = []

    def __str__(self):
        info = [f'id: {self.id_}']
        sentence = ' '.join([token_obj.token
                             for token_obj in self.tokens])
        info.append(sentence)

        return '\n'.join(info)


class Token:
    """

    """
    def __init__(self, sent_id, wf_el, t_el):
        self.sent_id = sent_id
        self.token = self.get_token(wf_el)
        self.token_id = self.get_token_id(wf_el)
        self.lemma = self.get_lemma(t_el)
        self.pos = self.get_pos(t_el)


    def __str__(self):
        info = []
        attrs = ['sent_id', 'token_id', 'token',
                 'lemma', 'pos']

        for attr in attrs:
            value = getattr(self, attr)
            info.append(f'{attr}: {value}')

        return '\n'.join(info)

    def get_token(self, wf_el):
        return wf_el.text

    def get_token_id(self, wf_el):
        return wf_el.get('id')

    def get_lemma(self, t_el):
        return t_el.get('lemma')

    def get_pos(self, t_el):
        return t_el.get('pos')