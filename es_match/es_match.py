#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 www.drcubic.com, Inc. All Rights Reserved
#
"""
File: es_match.py
Author: shileicao(shileicao@stu.xjtu.edu.cn)
Date: 17-2-26 上午10:51
"""

# import pprint
import pypinyin
from elasticsearch import Elasticsearch

es = Elasticsearch([{"host": "localhost", "port": 9200}])


def hanzi2pinyin(word):

    return [ch[0] for ch in pypinyin.pinyin(word, style=pypinyin.NORMAL)]


def encode_pinyin(word):
    pinyin_ = []
    pinyin = hanzi2pinyin(word)
    for ch in pinyin:
        pinyin_.append('@'.join(list(ch)))
    return '@@'.join(pinyin_)


def encode_pinyin2(word):
    pinyin_ = []
    pinyin = hanzi2pinyin(word)
    return ' '.join(pinyin)


def encode_pinyin3(word):
    pinyin_ = []
    pinyin = hanzi2pinyin(word)
    return ''.join(pinyin)


def create_index(id, doc):
    es.index(index="entity-index", doc_type='search', id=id, body=doc)


def refresh_index():
    es.indices.refresh(index="entity-index")


def search_index(query_string, return_number=1):
    query_pinyin = encode_pinyin(query_string)
    res1 = es.search(
        index='entity-index',
        doc_type='search',
        body={
            'size': return_number,
            'query': {
                "query_string": {
                    'fields': ['Name'],
                    "query": query_string
                }
            }
        })

    res2 = es.search(
        index='entity-index',
        doc_type='search',
        body={
            'size': return_number,
            'query': {
                "query_string": {
                    'fields': ['Pinyin'],
                    "query": query_pinyin
                }
            }
        })

    res3 = es.search(
        index='entity-index',
        doc_type='search',
        body={
            'size': return_number,
            'query': {
                "fuzzy": {
                    'Pinyin3': encode_pinyin3(query_string)
                }
            }
        })

    answers = res1['hits']['hits'] + res2['hits']['hits']
    answers0 = res3['hits']['hits']
    print answers[0]
    print res2['hits']['hits'][0]
    print 'dklsd:' + res2['hits']['hits'][0]['_source']['Name']
    answers = sorted(
        answers, cmp=(lambda x, y: 1 if x['_score'] < y['_score'] else -1))
    # pprint.pprint(answers)

    result_names = []
    entity_types = []
    re_num = return_number
    if len(answers0) > 0 and answers[0]['_source']['Name'] != query_string:
        result_names.append(answers0[0]['_source']['Name'])
        re_num -= 1
    #print re_num
    if re_num >= 1:
        for item in answers:
            if item['_source']['Name'] not in result_names:
                result_names.append(item['_source']['Name'])
                entity_types.append(item['_source']['Entity_type'])
                re_num -= 1
                #print re_num
                if re_num == 0:
                    break
    '''        
    else:
        result_names.append(answers[0]['_source']['Name'])
        entity_types.append(answers[0]['_source']['Entity_type'])
    '''
    return result_names, entity_types
