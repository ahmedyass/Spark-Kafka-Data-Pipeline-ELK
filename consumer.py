import requests, json, os
from elasticsearch import Elasticsearch
from pykafka import KafkaClient
from pyspark import SparkContext

client = KafkaClient(hosts='127.0.0.1:9092')
sc = SparkContext()


res = requests.get('http://localhost:9200')
es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

x = []
i = 1
for i in client.topics['speech'].get_simple_consumer():
    print('data:{0}\n\n'.format(i.value.decode()))
    x.append('{0}'.format(i.value.decode()))
    lines = sc.parallelize(x)
    word_counts = lines.flatMap(lambda line: line.split(' ')) \
                        .map(lambda word: (word, 1)) \
                        .reduceByKey(lambda count1, count2: count1 + count2) \
                        .collect()

    word_counts.pprint()
    rec = {
            "word" : word_counts.value,
            "count" : word_counts.count,
        }
    es.index(index='wordcount', doc_type='wordcount', id=i, body=rec)
    i+=1