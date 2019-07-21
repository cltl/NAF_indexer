

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