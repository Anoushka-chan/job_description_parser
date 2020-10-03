from elasticsearch import Elasticsearch
from datetime import datetime
# es = Elasticsearch(HOST="http://localhost", PORT=9200)
es = Elasticsearch()

# es.indices.create(index="first_index", ignore=400)
# es.indices.exists(index='first_name')

# doc1 = {"city":"new delhi", "country":"india"}
# doc1 = {"city":"london", "country":"england"}
# doc1 = {"city":"los angeles", "country":"usa"}

# es.index(index="cities", doc_type="places", id=1, body=doc1)


doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': datetime.now(),
}
res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
print(res['result'])