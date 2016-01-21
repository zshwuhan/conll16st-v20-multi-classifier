#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Load provided CoNLL16st/CoNLL15st files untouched.
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2016@tnode.com>"
__license__ = "GPLv3+"

import codecs
import json


def load_parses(dataset_dir, doc_ids=None, parses_ffmts=None):
    """Load parses and tags untouched from CoNLL16st corpus.

        parses["wsj_1000"]['sentences'][0]['words'][0] = [
            'Kemper',
            {'CharacterOffsetEnd': 15, 'Linkers': ['arg1_14890'], 'PartOfSpeech': 'NNP', 'CharacterOffsetBegin': 9}
        ]
    """
    if parses_ffmts is None:
        parses_ffmts = [
            "{}/parses.json",             # CoNLL16st filenames
            "{}/pdtb-parses.json",        # CoNLL15st filenames
            "{}/pdtb_trial_parses.json",  # CoNLL15st trial filenames
        ]

    # load all parses
    parses = {}
    for parses_ffmt in parses_ffmts:
        try:
            f = codecs.open(parses_ffmt.format(dataset_dir), 'r', encoding='utf8')
            parses = json.load(f)
            f.close()
            break
        except IOError:
            pass

    # filter by document id
    if doc_ids is not None:
        parses = { doc_id: parses[doc_id]  for doc_id in doc_ids }
    return parses


def load_raws(dataset_dir, doc_ids, raw_ffmts=None):
    """Load raw text untouched by document id from CoNLL16st corpus.

        raws["wsj_1000"] = ".START \n\nKemper Financial Services Inc., charging..."
    """
    if raw_ffmts is None:
        raw_ffmts = [
            "{}/raw/{}",  # CoNLL16st/CoNLL15st filenames
        ]

    # load all raw texts
    raws = {}
    for doc_id in doc_ids:
        raws[doc_id] = None
        for raw_ffmt in raw_ffmts:
            try:
                f = codecs.open(raw_ffmt.format(dataset_dir, doc_id), 'r', encoding='utf8')
                raws[doc_id] = f.read()
                f.close()
                break  # skip other filenames
            except IOError:
                pass
    return raws


def load_relations_gold(dataset_dir, doc_ids=None, with_senses=True, filter_types=None, filter_senses=None, relations_ffmts=None):
    """Load shallow discourse relations untouched by relation id from CoNLL16st corpus.

        relations[14887] = {
            'Arg1': {'CharacterSpanList': [[2493, 2517]], 'RawText': 'and told ...', 'TokenList': [[2493, 2496, 465, 15, 8], [2497, 2501, 466, 15, 9], ...]},
            'Arg2': {'CharacterSpanList': [[2526, 2552]], 'RawText': "they're ...", 'TokenList': [[2526, 2530, 472, 15, 15], [2530, 2533, 473, 15, 16], ...]},
            'Connective': {'CharacterSpanList': [[2518, 2525]], 'RawText': 'because', 'TokenList': [[2518, 2525, 471, 15, 14]]},
            'Punctuation': {'CharacterSpanList': [], 'PunctuationType': '', 'RawText': '', 'TokenList': []},
            'DocID': 'wsj_1000',
            'ID': 14887,
            'Type': 'Explicit',
            'Sense': ['Contingency.Cause.Reason'],
        }
    """
    if relations_ffmts is None:
        relations_ffmts = []
        if not with_senses:
            relations_ffmts += [
                "{}/relations-no-senses.json",  # CoNLL16st filenames
            ]
        relations_ffmts += [
            "{}/relations.json",        # CoNLL16st filenames
            "{}/pdtb-data.json",        # CoNLL15st filenames
            "{}/pdtb_trial_data.json",  # CoNLL15st trial filenames
        ]

    # load all relations
    relations = {}
    for relations_ffmt in relations_ffmts:
        try:
            f = codecs.open(relations_ffmt.format(dataset_dir), 'r', encoding='utf8')
            for line in f:
                relation = json.loads(line)

                # filter by document id
                if doc_ids and relation['DocID'] not in doc_ids:
                    continue

                # filter by relation type
                if filter_types and relation['Type'] not in filter_types:
                    continue

                # filter by relation sense
                if filter_senses and relation['Sense'] not in filter_senses:
                    continue

                # fix inconsistent structure
                if 'TokenList' not in relation['Arg1']:
                    relation['Arg1']['TokenList'] = []
                if 'TokenList' not in relation['Arg2']:
                    relation['Arg2']['TokenList'] = []
                if 'TokenList' not in relation['Connective']:
                    relation['Connective']['TokenList'] = []
                if 'Punctuation' not in relation:
                    relation['Punctuation'] = {'CharacterSpanList': [], 'PunctuationType': "", 'RawText': "", 'TokenList': []}
                if 'PunctuationType' not in relation['Punctuation']:
                    relation['Punctuation']['PunctuationType'] = ""
                if 'TokenList' not in relation['Punctuation']:
                    relation['Punctuation']['TokenList'] = []

                # remove sense information
                if not with_senses:
                    relation['Sense'] = []
                    relation['Type'] = ""

                # save relation
                relations[relation['ID']] = relation
            f.close()
            break
        except IOError:
            pass
    return relations


### Tests

def test_parses():
    dataset_dir = "./conll16st-en-trial"
    t_doc_id = "wsj_1000"
    t_s0_word0 = "Kemper"
    t_s0_word0_linkers = ["arg1_14890"]
    t_s0_word0_pos = "NNP"
    t_s0_parsetree = "( (S (NP (NNP Kemper) (NNP Financial) (NNPS Services)"
    t_s0_dependency0 = ["root", "ROOT-0", "cut-16"]
    t_s0_dependency1 = ["nn", "Inc.-4", "Kemper-1"]

    parses = load_parses(dataset_dir)
    s0 = parses[t_doc_id]['sentences'][0]
    assert s0['words'][0][0] == t_s0_word0
    assert s0['words'][0][1]['Linkers'] == t_s0_word0_linkers
    assert s0['words'][0][1]['PartOfSpeech'] == t_s0_word0_pos
    assert s0['parsetree'].startswith(t_s0_parsetree)
    assert t_s0_dependency0 in s0['dependencies']
    assert t_s0_dependency1 in s0['dependencies']

def test_raws():
    dataset_dir = "./conll16st-en-trial"
    doc_id = "wsj_1000"
    t_raw = ".START \n\nKemper Financial Services Inc., charging"

    raws = load_raws(dataset_dir, [doc_id])
    assert raws[doc_id].startswith(t_raw)

def test_relations():
    dataset_dir = "./conll16st-en-trial"
    t_rel0 = {
        "Arg1": {"CharacterSpanList": [[2493, 2517]], "RawText": "and told them to cool it", "TokenList": [[2493, 2496, 465, 15, 8], [2497, 2501, 466, 15, 9], [2502, 2506, 467, 15, 10], [2507, 2509, 468, 15, 11], [2510, 2514, 469, 15, 12], [2515, 2517, 470, 15, 13]]},
        "Arg2": {"CharacterSpanList": [[2526, 2552]], "RawText": "they're ruining the market", "TokenList": [[2526, 2530, 472, 15, 15], [2530, 2533, 473, 15, 16], [2534, 2541, 474, 15, 17], [2542, 2545, 475, 15, 18], [2546, 2552, 476, 15, 19]]},
        "Connective": {"CharacterSpanList": [[2518, 2525]], "RawText": "because", "TokenList": [[2518, 2525, 471, 15, 14]]},
        "Punctuation": {"CharacterSpanList": [], "PunctuationType": "", "RawText": "", "TokenList": []},
        "DocID": "wsj_1000",
        "ID": 14887,
        "Sense": ["Contingency.Cause.Reason"],
        "Type": "Explicit"
    }

    relations = load_relations_gold(dataset_dir)
    rel0 = relations[t_rel0['ID']]
    for span in ['Arg1', 'Arg2', 'Connective', 'Punctuation']:
        for k in ['CharacterSpanList', 'RawText', 'TokenList']:
            assert rel0[span][k] == t_rel0[span][k], (span, k)
    assert rel0['Punctuation']['PunctuationType'] == t_rel0['Punctuation']['PunctuationType']

if __name__ == '__main__':
    import pytest
    pytest.main(['-s', __file__])