"""
Sentence analysis and keyword extraction using Spacy.
"""
from nltk.corpus import stopwords
import csv
from spacy.en import English
from spacy.parts_of_speech import ADP, PUNCT, VERB, PART, ADV

nlp = English()
print 'SpaCy loaded'


def load_sw():
    sw = []
    for line in csv.reader(open('sources/stopwords_long.txt'), delimiter='\t'):
        for word in line:
            sw.append(word)
    return sw


stop_words = stopwords.words('english')
stop_words = stop_words + load_sw()


def in_stop_words(word):
    return word.lower() in stop_words


def is_unimportant(token):
    unimportant = 'the a and'
    return ((token.lower_ in unimportant) or
            (token.pos == PART) or
            (token.pos == PUNCT) or
            (token.orth_ in stop_words))


def more_nouns(ents, noun_chunks, keywords):
    for n_ch in noun_chunks:
        chunk = []
        for token in n_ch:
            if is_unimportant(token):
                continue
            i = 0
            for ent in ents:
                if token.lower_ in ent.string.lower():
                    i += 1
                    break
            if i == 0:
                chunk.append(token.text)
        if len(chunk) > 0:
            keywords.append(' '.join(chunk))


def all_years(spaced, question):
    """ add anything that looks like a year as a date """
    for t in spaced:
        s = t.lower_
        if not s.isdigit():
            continue
        if int(s) < 2013 or int(s) > 2020:  # XXX gross hack; well...
            continue
        if s in question.date_texts:
            continue
        question.set_date(s)
        break


def extract(question):
    spaced = nlp(unicode(question.text))
    keywords = []
    sent = []
    for sentence in spaced.sents:
        sent = sentence
        break
    #    if not in_stop_words(sent.root.text):
    non_keywords = ['TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']
    for ent in spaced.ents:
        if ent.label_ in non_keywords:
            continue
        if ent.label_ == 'DATE':
            # if ent[0].nbor(-1).pos == ADP:
            #     date = ent[0].nbor(-1).orth_ + ' ' + ent.orth_
            # ^^^ ???
            question.set_date(ent.orth_)
        else:
            kw = ''
            for word in ent:
                if word.lower_ not in 'the a':
                    kw += word.text_with_ws
            keywords.append(kw)

    more_nouns(spaced.ents, spaced.noun_chunks, keywords)
    question.searchwords = set(keywords)

    all_years(spaced, question)

    question.root_verb.append(sent.root)

    for branch in sent.root.rights:
        if branch.pos == VERB:
            question.root_verb.append(branch)

    # Ignore the MT question date info.  It's noisy, often missing, and
    # confusing wrt. real-world usage.
    # load_dates(question)


def verbs(sent):
    verbs = []
    if sent.root.pos == VERB:
        verbs.append(sent.root)
    for branch in sent.root.rights:
        if branch.pos == VERB:
            verbs.append(branch)
    for branch in sent.root.lefts:
        if branch.pos == VERB:
            verbs.append(branch)
    return verbs


def check_keywords(question):
    """ check whether question keywords cover the question text
    sufficiently; return False if we've likely missed something
    important """
    nikw = []
    spaced = nlp(unicode(question.text))
    for token in spaced:
        if (in_stop_words(token.lower_) or is_unimportant(token) or
           token.lower_ in [t.lower() for t in question.date_texts] or
           token.pos == ADV):
            continue
        i = 0
        for kw in question.all_keywords():
            if token.lower_ in kw.lower():
                i += 1
                break
        if i == 0:
            nikw.append(token.text)
    question.not_in_kw = nikw
    if len(nikw) > 0:
        return False
    return True


def load_dates(question):
    for line in csv.reader(open('tests/filtereddate.tsv'), delimiter='\t'):
        if line[0] == question.text:
            question.dates = []  # drop anything we've seen in the question
            question.set_date(line[1])
            break


def extract_from_string(question):
    spaced = nlp(unicode(question))
    keywords = []
    non_keywords = ['TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']
    for ent in spaced.ents:
        if ent.label_ in non_keywords:
            continue
        if ent.label_ != 'DATE':
            kw = ''
            for word in ent:
                if word.lower_ not in 'the a':
                    kw += word.text_with_ws
            keywords.append(kw)

    more_nouns(spaced.ents, spaced.noun_chunks, keywords)
    return keywords


def get_subj(root):
    for child in root.children:
        if child.dep_ == 'nsubj':
            return child


def get_obj(root):
    for child in root.children:
        if child.dep_ == 'dobj':
            return child
