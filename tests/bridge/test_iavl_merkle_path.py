import pytest
from brownie import accounts, MockIAVLMerklePath


@pytest.fixture(scope="module")
def mockiavlmerklepath():
    return accounts[0].deploy(MockIAVLMerklePath)


def test_iavlmerklepath_getparenthash_success(mockiavlmerklepath):
    parent_hash = mockiavlmerklepath.getParentHash(
        [
            False,
            1,
            2,
            436,
            "0x6763EDF42C0D7A3765E8CD9B970AE0E20DC6D3CF5DF0DC63CAD2C85FAFC6A803",
        ],
        "0x22AA109AFDA802E032EB0D4755090E67237F421DDCD5F2491128CB7768EA17A9",
    )
    assert parent_hash == "0x9CE895E70AEB8767D86B7D80C03B0DE7C6F03422E0A6050B474C737D272ABE2B"
    parent_hash = mockiavlmerklepath.getParentHash(
        [
            True,
            2,
            4,
            439,
            "0x92F33601466769D62670A58771C8F8F2695E7142B3852197DD3CA6825B8A3B26",
        ],
        "0x9CE895E70AEB8767D86B7D80C03B0DE7C6F03422E0A6050B474C737D272ABE2B",
    )
    assert parent_hash == "0xA36F3D44C03782769E03B659BFA473CA668C846E5C04300A08C1B0B33EB7FFA2"
    parent_hash = mockiavlmerklepath.getParentHash(
        [
            False,
            3,
            8,
            584,
            "0x52C4B25043FF760DB4AE3F341E830908004D1E7C3BBDF724BC71DC24AA685134",
        ],
        "0xA36F3D44C03782769E03B659BFA473CA668C846E5C04300A08C1B0B33EB7FFA2",
    )
    assert parent_hash == "0x7ED53BF9F8E8B899CF5C3949D634F6FE2555DD5F9FC1E00754107B70E15328F3"
    parent_hash = mockiavlmerklepath.getParentHash(
        [
            False,
            4,
            16,
            109145,
            "0xC0924EFCFAF77E4FF65E9F24ED0C43C7BBBBB070CC111C4A58DA2B66B1189E74",
        ],
        "0x7ED53BF9F8E8B899CF5C3949D634F6FE2555DD5F9FC1E00754107B70E15328F3",
    )
    assert parent_hash == "0xC2AE72F6381535536804DDEA42368C815840B46AE23362033F489B6AF4E13C68"
