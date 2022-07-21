import pytest
import brownie
from brownie import accounts, MockObiUser


@pytest.fixture(scope="module")
def mockobiuser():
    return accounts[0].deploy(MockObiUser)


def test_obi_decode_success(mockobiuser):
    decoded = mockobiuser.decode("0x00000003425443000000000000003264")
    assert decoded[0] == "BTC"
    assert decoded[1] == "50"
    assert decoded[2] == "100"

    decoded = mockobiuser.decode("0x0000000462616e64000000000000019064")
    assert decoded[0] == "band"
    assert decoded[1] == "400"
    assert decoded[2] == "100"


def test_obi_decode_invalid_bytes(mockobiuser):
    with brownie.reverts("Obi: Out of range"):
        mockobiuser.decode("0x000000034254433200000000000064")
