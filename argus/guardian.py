import requests
import json
from html_clean import sentence_split_guardian

def kw_to_query(keywords):
    query = ''
    for word in keywords:
            query += word + " AND "
    query = query[:-5]
    return query

def get_content_guardian(a):
    api_url = 'http://content.guardianapis.com/search'
    payload = {
        'q':                    kw_to_query(a.q.searchwords),
        'from-date':            '2014-09-01',
#        'to-date':              '2015-09-01',
        'api-key':              'qdz547b6gvss2ndwc9npwqcx',
        'page-size':            50,
        'format':               'json',
        'orderBy':             'newest',
        'show-fields':          'all'
    }
    response = requests.get(api_url, params=payload)
    data = response.json()
    jobj=json.loads(json.dumps(data, indent = 4))
#    print json.dumps(data, indent=4)
    return search_sentences(a, jobj)


def search_sentences(a, jobj):
    try:
#        print len(jobj['response']['results'])
        if len(jobj['response']['results']) == 0:
            return False, False
    except KeyError:
        print 'Unknown error occured while answering:',a.q.text
        return False, False
    for i in range(0, len(jobj['response']['results'])):
        try:
            bodyhtml = jobj['response']['results'][i]['fields']['body']
        except KeyError:
            continue

        sentences = sentence_split_guardian(bodyhtml)
#        print '\n-----\n'.join(sentences)

        for sentence in sentences:
            j = 0
            for word in a.q.keywords:
                if word.lower() not in sentence.lower():
                    j += 1
                    break
            if j == 0:
                a.headlines.append(jobj['response']['results'][i]['fields']['headline'])
                a.urls.append(jobj['response']['results'][i]['webUrl'])
                a.bodies.append(bodyhtml)
                a.sentences.append(sentence)
                a.sources.append('guardian')
    if len(a.urls) != 0:
        return True, True
    return False, True