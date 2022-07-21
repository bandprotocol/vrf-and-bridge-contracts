import pytest
import brownie
from brownie import accounts, MockTMSignature, MockCommonEncodedVotePart


ENCODED_CHAIN_ID = "0x321362616e642d6c616f7a692d746573746e657431"
BLOCK_HASH = "0x8c36c3d12a378bd7e4e8f26bdecca68b48390240da456ee9c3292b6e36756ac4"
COMMON_ENCODED_VOTE_PART = [
    "0x08021184C002000000000022480A20",
    "0x12240801122044551F853D916A7C630C0C210C921BAC7D05CE0C249DFC6088C0274F05841827",
]


@pytest.fixture(scope="module")
def mocktmsignature():
    return accounts[0].deploy(MockTMSignature)


@pytest.fixture(scope="module")
def mockcommonvote():
    return accounts[0].deploy(MockCommonEncodedVotePart)


def test_tmsignature_check_time_and_recoversigner_success(mocktmsignature, mockcommonvote):
    encoded_common_vote = mockcommonvote.checkPartsAndEncodedCommonParts(COMMON_ENCODED_VOTE_PART, BLOCK_HASH)
    assert encoded_common_vote == COMMON_ENCODED_VOTE_PART[0] + BLOCK_HASH[2:] + COMMON_ENCODED_VOTE_PART[1][2:]

    # signer 1
    signers = mocktmsignature.checkTimeAndRecoverSigner(
        [
            "0x6916405D52FF02EC26DD78E831E0A179C89B99CBBDB15C9DA802B75A7621D5EB",
            "0x69CF40BE7AC1AA176B13BA4D57EB2B8735A5832014F0DC168EA6F580C51BB222",
            28,
            "0x08DE9493850610F0FFAEEB02",
        ],
        encoded_common_vote,
        ENCODED_CHAIN_ID,
    )
    assert signers == "0x3b759C4d728e50D5cC04c75f596367829d5b5061"

    # signer 2
    signers = mocktmsignature.checkTimeAndRecoverSigner(
        [
            "0x6A8E3C35DEED991D257BCA9451360BFBE7978D388AF8D2F864A6919FE1083C7E",
            "0x14D145DD6BC1A770ACBDF37DAC08DD8076AB888FDA2739BE9B9767B23A387D1E",
            27,
            "0x08DE9493850610DAEB8D9C03",
        ],
        encoded_common_vote,
        ENCODED_CHAIN_ID,
    )
    assert signers == "0x49897b9D617AD700b84a935616E81f9f4b5305bc"

    # signer 3
    signers = mocktmsignature.checkTimeAndRecoverSigner(
        [
            "0xEB402F4B863A1DF91E7772D9574640EFFC5447ECEC6EDF6F1CFE2C33D7DC8DD4",
            "0x1FEC45523E885DD6E8AD75EA2D81D30657267DF646406240F206A98749EBD0A7",
            27,
            "0x08DE9493850610B68FD4E702",
        ],
        encoded_common_vote,
        ENCODED_CHAIN_ID,
    )
    assert signers == "0x7054bd1Fd7535A0DD552361e634196b1574594BB"


def test_tmsignature_check_time_and_recoversigner_fail_invalid_timestamp(mocktmsignature, mockcommonvote):
    encoded_common_vote = mockcommonvote.checkPartsAndEncodedCommonParts(COMMON_ENCODED_VOTE_PART, BLOCK_HASH)
    assert encoded_common_vote == COMMON_ENCODED_VOTE_PART[0] + BLOCK_HASH[2:] + COMMON_ENCODED_VOTE_PART[1][2:]

    max_len = 12
    base_encoded_time = "0x08DE9493850610F0FFAEEB02"
    rsv = [
        "0x6916405D52FF02EC26DD78E831E0A179C89B99CBBDB15C9DA802B75A7621D5EB",
        "0x69CF40BE7AC1AA176B13BA4D57EB2B8735A5832014F0DC168EA6F580C51BB222",
        28,
    ]
    for i in range(-max_len, max_len):
        encoded_time = base_encoded_time[: 2 * (max_len + i)] + ("00" * i)
        size = len(encoded_time[2:]) // 2
        if 6 <= size <= 12:
            mocktmsignature.checkTimeAndRecoverSigner(rsv + [encoded_time], encoded_common_vote, ENCODED_CHAIN_ID)
        else:
            with brownie.reverts("TMSignature: Invalid timestamp's size"):
                mocktmsignature.checkTimeAndRecoverSigner(rsv + [encoded_time], encoded_common_vote, ENCODED_CHAIN_ID)


def test_tmsignature_check_time_and_recoversigner_fail_invalid_validator(mocktmsignature, mockcommonvote):
    encoded_common_vote = mockcommonvote.checkPartsAndEncodedCommonParts(COMMON_ENCODED_VOTE_PART, BLOCK_HASH)
    assert encoded_common_vote == COMMON_ENCODED_VOTE_PART[0] + BLOCK_HASH[2:] + COMMON_ENCODED_VOTE_PART[1][2:]

    # signer 1
    signers = mocktmsignature.checkTimeAndRecoverSigner(
        [
            "0x6916405D52FF02EC26DD78E831E0A179C89B99CBBDB15C9DA802B75A7621D5EB",
            "0x69CF40BE7AC1AA176B13BA4D57EB2B8735A5832014F0DC168EA6F580C51BB222",
            28,
            "0x08DE9493850610F0FFAEEB02"[:-2],
        ],
        encoded_common_vote,
        ENCODED_CHAIN_ID,
    )
    assert signers != "0x3b759C4d728e50D5cC04c75f596367829d5b5061"
