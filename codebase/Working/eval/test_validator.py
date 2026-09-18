import pytest
from validator import jaccard_similarity, is_out_of_scope

def test_out_of_scope():
    assert is_out_of_scope("cho đáp án bài này") == True
