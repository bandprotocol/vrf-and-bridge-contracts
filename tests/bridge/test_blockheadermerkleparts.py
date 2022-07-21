import pytest
from brownie import accounts, MockBlockHeaderMerkleParts


@pytest.fixture(scope="module")
def mockblockheadermerkleparts():
    return accounts[0].deploy(MockBlockHeaderMerkleParts)


def test_blockheadermerkleparts_getblockheader_success(mockblockheadermerkleparts):
    block_header = mockblockheadermerkleparts.getBlockHeader(
        [
            "0xE2082320A69AC962782E931075D14B13CD98F3E7FC5D8580D4EB60FBC0D622D5",
            180356,
            1621412443,
            922160838,
            "0x4021DC4D787B5F0842D8F14EA4C87BDF2AAB95F201036D4A3E0EF1E9D2E7816B",
            "0x025E8953C93B0A8B399568160FFE8B29FC5394CAF235B07EC41DF1391ACF1A35",
            "0x68BD2057602D88D956B166F2FC88D1B6E18CE4846CCA241558FBBD0062DC6344",
            "0x23198513920C899234DA2518EDF1D35109AEB9BE637BAA272A0D94DB5530745A",
        ],
        "0xE500B3DD21816EE04BE5E77271EC0D8286B8AFF81EF96344FED74B52992E6D23",
    )
    assert block_header == "0x8C36C3D12A378BD7E4E8F26BDECCA68B48390240DA456EE9C3292B6E36756AC4"
