from collections import defaultdict
from lxml import etree


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


def iterable_of_meanings(naf_obj,
                         xml_path,
                         selected_attributes,
                         attr_requirements={},
                         verbose=0):
    """
    Create iterable of values in a NAF files, e.g.,
    all senses, frames, or entities
    :param classes.NAF_document naf_obj: instance of class NAF_document
    :param xml_path: e.g., srl/predicate
    :param list attribute: list of attributes to concatenate, e.g., ["lemma"] or ["lemma", "pos"]
    :param dict attr_requirements: whether you want other attributes of the
    same element to have a specific value, e.g, {"type": {"location"}}
    :rtype: dict
    :return meaning -> occurrences, i.e., title, sent_id, indices
    """
    occurrences = defaultdict(list)
    for el in naf_obj.doc.xpath(xml_path):

        el_attributes = el.attrib

        to_add = True

        for req_attr, ok_values in attr_requirements.items():
            el_attr_value = el_attributes[req_attr]
            assert req_attr in el_attributes, f'required attribute not part of element attributes: {el_attributes}'
            if el_attr_value not in ok_values:
                if verbose >= 2:
                    print(f'skipping element because {req_attr} has value {el_attr_value}')
                to_add = False

        if not to_add:
            continue

        values = [el.get(attr)
                  for attr in selected_attributes]
        the_value = '--'.join(values)

        # get t_ids
        t_ids = get_span_tids(el)

        sent_ids = []
        indices = []
        for t_id in t_ids:
            sent_id, t_index = naf_obj.tid2sentid_index[t_id]
            sent_ids.append(sent_id)
            indices.append(t_index)

        assert len(set(sent_ids)) == 1
        sent_id = sent_ids[0]

        occurrence = [naf_obj.title, sent_id, indices]

        occurrences[the_value].append(occurrence)

    return occurrences











































if __name__ == '__main__':
    import naf_classes

    # TODO: mention meaning system, except for terms

    naf_coll_obj = naf_classes.NAF_collection()
    paths = ['example_files/Wedding of Albert II, Prince of Monaco, and Charlene Wittstock.naf']
    naf_coll_obj.add_naf_documents(paths, verbose=2)

    for naf_obj in naf_coll_obj.documents:
        iterable_of_meanings(naf_obj,
                             xml_path='srl/predicate',
                             selected_attributes=['uri'],
                             attr_requirements={},
                             verbose=0)

