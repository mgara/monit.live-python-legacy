from elasticsearch import Elasticsearch

es = Elasticsearch()


def publish_to_elasticsearch(index, doc_type, body):
    es.index(
        index=index,
        doc_type=doc_type,
        body=body
    )
