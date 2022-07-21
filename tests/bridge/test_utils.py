import pytest
from brownie import accounts, MockUtils
import time


@pytest.fixture(scope="module")
def mockutils():
    return accounts[0].deploy(MockUtils)


def test_utils_merkleleafhash_success(mockutils):
    hash = mockutils.merkleLeafHash("0x08d1082cc8d85a0833da8815ff1574675c415760e0aff7fb4e32de6de27faf86")
    assert hash == "0x35b401b2a74452d2252df60574e0a6c029885965ae48f006ebddc18e53427e26"


def test_utils_merkleinnerhash_success(mockutils):
    hash = mockutils.merkleInnerHash(
        "0x08d1082cc8d85a0833da8815ff1574675c415760e0aff7fb4e32de6de27faf86",
        "0x789411d15a12768a9c3eb99d3453d6ebb4481c2a03ab59cc262a97e25757afe6",
    )
    assert hash == "0xca48b611419f0848bf0fce9750caca6fd4fb8ef96ba8d7d3ccd4f05bf2af1661"


def test_utils_encodevarintunsigned_success(mockutils):
    encode = mockutils.encodeVarintUnsigned("116")
    assert encode == "0x74"
    encode = mockutils.encodeVarintUnsigned("14947")
    assert encode == "0xe374"
    encode = mockutils.encodeVarintUnsigned("244939043")
    assert encode == "0xa3f2e574"


def test_utils_encodevarintsigned_success(mockutils):
    encode = mockutils.encodeVarintSigned("58")
    assert encode == "0x74"
    encode = mockutils.encodeVarintSigned("7473")
    assert encode == "0xe274"
    encode = mockutils.encodeVarintSigned("122469521")
    assert encode == "0xa2f2e574"


def test_utils_encodetime_success(mockutils):
    encode = mockutils.encodeTime("1605781207", "476745924")
    assert encode == "0x08d78dd9fd0510c4a1aae301"
