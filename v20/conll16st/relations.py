#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Process shallow discourse relations from CoNLL16st corpus (from `relations.json` or `relations-no-senses.json`).
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2016@tnode.com>"
__license__ = "GPLv3+"

from files import load_parses, load_raws, load_relations_gold
from words import get_word_metas


def get_relations(relations_gold):
    """Extract only discourse relation spans of token ids by relation id from CoNLL16st corpus.

        relations[14887] = {
            'Arg1': [465, 466, 467, 468, 469, 470],
            'Arg1Len': 24,
            'Arg2': [472, 473, 474, 475, 476],
            'Arg2Len': 26,
            'Connective': [471],
            'ConnectiveLen': 7,
            'Punctuation': [],
            'PunctuationLen': 0,
            'PunctuationType': "",
            'DocID': "wsj_1000",
            'ID': 14887,
            'TokenMin': 465,
            'TokenMax': 476,
            'TokenCount': 12,
        }
    """

    relations = {}
    for rel_id, gold in relations_gold.iteritems():
        doc_id = gold['DocID']
        punct_type = gold['Punctuation']['PunctuationType']

        # short token lists from detailed/gold format to only token id
        arg1_list = [ t[2]  for t in gold['Arg1']['TokenList'] ]
        arg2_list = [ t[2]  for t in gold['Arg2']['TokenList'] ]
        conn_list = [ t[2]  for t in gold['Connective']['TokenList'] ]
        punct_list = [ t[2]  for t in gold['Punctuation']['TokenList'] ]
        all_list = sum([arg1_list, arg2_list, conn_list, punct_list], [])

        # character lengths of spans
        arg1_len = sum([ (e - b)  for b, e in gold['Arg1']['CharacterSpanList'] ])
        arg2_len = sum([ (e - b)  for b, e in gold['Arg2']['CharacterSpanList'] ])
        conn_len = sum([ (e - b)  for b, e in gold['Connective']['CharacterSpanList'] ])
        punct_len = sum([ (e - b)  for b, e in gold['Punctuation']['CharacterSpanList'] ])

        # save relation span
        rel = {
            'Arg1': arg1_list,
            'Arg1Len': arg1_len,
            'Arg2': arg2_list,
            'Arg2Len': arg2_len,
            'Connective': conn_list,
            'ConnectiveLen': conn_len,
            'Punctuation': punct_list,
            'PunctuationLen': punct_len,
            'PunctuationType': punct_type,
            'DocID': doc_id,
            'ID': rel_id,
            'TokenMin': min(all_list),
            'TokenMax': max(all_list),
            'TokenCount': len(all_list),
        }
        relations[rel_id] = rel
    return relations


def get_relation_metas(relations_gold):
    """Extract discourse relation types, senses and other by relation id from CoNLL16st corpus.

        relation_metas[14887] = {
            'Type': 'Explicit',
            'Sense': ['Contingency.Cause.Reason'],
            'DocID': "wsj_1000",
            'ID': 14887,
        }
    """

    relation_metas = {}
    for rel_id, gold in relations_gold.iteritems():
        doc_id = gold['DocID']

        # save relation sense
        rel_sense = {
            'Type': gold['Type'],
            'Sense': gold['Sense'],
            'DocID': doc_id,
            'ID': rel_id,
        }
        relation_metas[rel_id] = rel_sense
    return relation_metas


def add_relation_tags(word_metas, relation_metas):
    """Add discourse relation tags to metadata of words/tokens.

        word_metas['wsj_1000'][0] = {
            ...
            'RelationTags': ['Explicit:Contingency.Cause.Reason:14890:Arg1'],
        }
    """

    for doc_id in word_metas:
        for meta in word_metas[doc_id]:
            meta['RelationTags'] = []
            for rel_id, rel_span in zip(meta['RelationIDs'], meta['RelationSpans']):
                if rel_id not in relation_metas:
                    continue  # skip missing relations

                rel_type = relation_metas[rel_id]['Type']
                rel_sense = relation_metas[rel_id]['Sense'][0]  # only first sense

                # save to metadata
                rel_tag = ":".join([rel_type, rel_sense, str(rel_id), rel_span])
                meta['RelationTags'].append(rel_tag)


### Tests

def test_relations():
    dataset_dir = "./conll16st-en-trial"
    t_rel0 = {
        'Arg1': [465, 466, 467, 468, 469, 470],
        'Arg1Len': 24,
        'Arg2': [472, 473, 474, 475, 476],
        'Arg2Len': 26,
        'Connective': [471],
        'ConnectiveLen': 7,
        'Punctuation': [],
        'PunctuationLen': 0,
        'PunctuationType': "",
        'DocID': "wsj_1000",
        'ID': 14887,
        'TokenMin': 465,
        'TokenMax': 476,
        'TokenCount': 12,
    }

    relations_gold = load_relations_gold(dataset_dir)
    relations = get_relations(relations_gold)
    rel0 = relations[t_rel0['ID']]
    assert rel0 == t_rel0

def test_relation_metas():
    dataset_dir = "./conll16st-en-trial"
    t_rel0 = {
        'Type': 'Explicit',
        'Sense': ['Contingency.Cause.Reason'],
        'DocID': "wsj_1000",
        'ID': 14887,
    }

    relations_gold = load_relations_gold(dataset_dir)
    relation_metas = get_relation_metas(relations_gold)
    rel0 = relation_metas[t_rel0['ID']]
    assert rel0 == t_rel0

def test_relation_tags():
    dataset_dir = "./conll16st-en-trial"
    doc_id = "wsj_1000"
    t_meta0_id = 0
    t_meta0_tags = ['Explicit:Expansion.Conjunction:14890:Arg1']
    t_meta1_id = 894
    t_meta1_tags = ['Explicit:Comparison.Concession:14904:Arg2', 'Explicit:Contingency.Condition:14905:Arg2']
    t_meta2_id = 895
    t_meta2_tags = []

    parses = load_parses(dataset_dir)
    raws = load_raws(dataset_dir, [doc_id])
    word_metas = get_word_metas(parses, raws)
    relations_gold = load_relations_gold(dataset_dir)
    relation_metas = get_relation_metas(relations_gold)
    add_relation_tags(word_metas, relation_metas)
    assert word_metas[doc_id][t_meta0_id]['RelationTags'] == t_meta0_tags
    assert word_metas[doc_id][t_meta1_id]['RelationTags'] == t_meta1_tags
    assert word_metas[doc_id][t_meta2_id]['RelationTags'] == t_meta2_tags

if __name__ == '__main__':
    import pytest
    pytest.main(['-s', __file__])