import pytest
import brownie
from brownie import accounts, MockCommonEncodedVotePart


ENCODED_CHAIN_ID = "0x321362616e642d6c616f7a692d746573746e657431"
BLOCK_HASH = "0x8c36c3d12a378bd7e4e8f26bdecca68b48390240da456ee9c3292b6e36756ac4"


@pytest.fixture(scope="module")
def mockcommonvote():
    return accounts[0].deploy(MockCommonEncodedVotePart)


def test_commonvote_encode_success(mockcommonvote):
    common_vote_data = [
        "0x08021184C002000000000022480A20",
        "0x12240801122044551F853D916A7C630C0C210C921BAC7D05CE0C249DFC6088C0274F05841827",
    ]
    encoded_common_vote = mockcommonvote.checkPartsAndEncodedCommonParts(common_vote_data, BLOCK_HASH)
    assert encoded_common_vote == common_vote_data[0] + BLOCK_HASH[2:] + common_vote_data[1][2:]


def test_commonvote_encode_fail_invalid_prefix_size(mockcommonvote):
    prefix_base = "0x08021184C002000000000022480A20"
    suffix = "0x12240801122044551F853D916A7C630C0C210C921BAC7D05CE0C249DFC6088C0274F05841827"
    minimum_len = 15
    for i in range(-minimum_len, minimum_len):
        prefix = prefix_base[: 2 * (minimum_len + i)] + ("00" * i)
        size = len(prefix[2:]) // 2
        common_vote_data = [prefix, suffix]
        if size == minimum_len or size == minimum_len + 9:
            encoded_common_vote = mockcommonvote.checkPartsAndEncodedCommonParts(common_vote_data, BLOCK_HASH)
            assert encoded_common_vote == prefix + BLOCK_HASH[2:] + suffix[2:]
        else:
            with brownie.reverts("CommonEncodedVotePart: Invalid prefix's size"):
                mockcommonvote.checkPartsAndEncodedCommonParts(common_vote_data, BLOCK_HASH)


def test_commonvote_encode_fail_invalid_suffix_size(mockcommonvote):
    prefix = "0x08021184C002000000000022480A20"
    suffix_base = "0x12240801122044551F853D916A7C630C0C210C921BAC7D05CE0C249DFC6088C0274F05841827"
    fixed_len = 38
    for i in range(-fixed_len, fixed_len):
        suffix = suffix_base[: 2 * (fixed_len + i)] + ("00" * i)
        size = len(suffix[2:]) // 2
        common_vote_data = [prefix, suffix]
        if size == fixed_len:
            encoded_common_vote = mockcommonvote.checkPartsAndEncodedCommonParts(common_vote_data, BLOCK_HASH)
            assert encoded_common_vote == prefix + BLOCK_HASH[2:] + suffix[2:]
        else:
            with brownie.reverts("CommonEncodedVotePart: Invalid suffix's size"):
                mockcommonvote.checkPartsAndEncodedCommonParts(common_vote_data, BLOCK_HASH)
