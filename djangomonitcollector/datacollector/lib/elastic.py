from elasticsearch import Elasticsearch

es = Elasticsearch()


def publish_to_elasticsearch(index, doc_type, body):
    return
    # Disable for now until We understand the data structure behind elasticsearch.
    es.index(
        index=index,
        doc_type=doc_type,
        body=body
    )
