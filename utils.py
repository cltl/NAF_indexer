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

