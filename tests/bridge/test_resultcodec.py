import pytest
from brownie import accounts, MockResultCodec


@pytest.fixture(scope="module")
def mockresultcodec():
    return accounts[0].deploy(MockResultCodec)


def test_resultcodec_encode_success(mockresultcodec):
    encoded_result = mockresultcodec.encode(
        ["beeb", 1, "0x0000000342544300000000000003e8", 1, 1, 2, 1, 1591622616, 1591622618, 1, "0x00000000009443ee"],
    )
    assert (
        encoded_result
        == "0x0a046265656210011a0f0000000342544300000000000003e8200128013002380140d8f7f8f60548daf7f8f60550015a0800000000009443ee"
    )
    encoded_result = mockresultcodec.encode(
        ["", 1, "0x0000000342544300000000000003e8", 1, 1, 1, 1, 1591622426, 1591622429, 1, "0x0000000000944387"],
    )
    assert (
        encoded_result
        == "0x10011a0f0000000342544300000000000003e82001280130013801409af6f8f605489df6f8f60550015a080000000000944387"
    )
    encoded_result = mockresultcodec.encode(
        ["client_id", 1, "0x0000000342544300000000000003e8", 1, 1, 1, 1, 1591622426, 1591622429, 2, b""],
    )
    assert (
        encoded_result
        == "0x0a09636c69656e745f696410011a0f0000000342544300000000000003e82001280130013801409af6f8f605489df6f8f6055002"
    )
