import pytest
import brownie

RESULT = [
    "from_scan",
    1,
    "0x0000000342544300000000000f4240",
    1,
    1,
    1,
    1,
    1622111198,
    1622111200,
    1,
    "0x000000092b6826f2",
]
VERSION = "1007"

INVALID_RESULT = [
    "wrong_id",
    1,
    "0x0000000342544300000000000f4240",
    1,
    1,
    1,
    1,
    1622111198,
    1622111200,
    1,
    "0x000000092b6826f2",
]

MERKLE_PATHS = [
    [
        True,
        1,
        2,
        1007,
        "0xEB739BB22F48B7F3053A90BA2BA4FE07FAB262CADF8664489565C50FF505B8BD",
    ],
    [
        True,
        2,
        4,
        1007,
        "0xBF32F8B214E4C36170D09B5125395C4EF1ABFA26583E676EF79AA3BA20A535A4",
    ],
    [
        True,
        3,
        6,
        1007,
        "0xF732D5B5007633C64B77F6CCECF01ECAB2537501D28ED623B6EC97DA4C1C6005",
    ],
    [
        True,
        4,
        10,
        1007,
        "0xF054C5E2412E1519951DBD7A60E2C5EDE41BABA494A6AF6FD0B0BAC4A4695C41",
    ],
    [
        True,
        5,
        20,
        3417,
        "0xFFA5A376D4DCA03596020A9A256DF9B73FE42ADEF285DD0ABE7E89A9819144EF",
    ],
]

INCOMPLETE_MERKLE_PATHS = [
    [
        True,
        1,
        2,
        1007,
        "0xEB739BB22F48B7F3053A90BA2BA4FE07FAB262CADF8664489565C50FF505B8BD",
    ],
    [
        True,
        2,
        4,
        1007,
        "0xBF32F8B214E4C36170D09B5125395C4EF1ABFA26583E676EF79AA3BA20A535A4",
    ],
    [
        True,
        3,
        6,
        1007,
        "0xF732D5B5007633C64B77F6CCECF01ECAB2537501D28ED623B6EC97DA4C1C6005",
    ],
]


@pytest.fixture(scope="module")
def set_oracle_state(mockbridge):
    mockbridge.setOracleState(
        "3417",  # _blockHeight
        "0x7920D562EC07A9979286FDCDA975F943D41D31974B01B8DC5B1B374878B194DA",  # _oracleIAVLStateHash)
    )
    return mockbridge


def test_bridge_verifyoracledata_success(set_oracle_state):
    res = set_oracle_state.verifyOracleData(
        "3417",  # _blockHeight
        RESULT,  # _result
        VERSION,  # _leafVersion
        MERKLE_PATHS,
    )
    for i in range(len(RESULT)):
        assert res[i] == RESULT[i]


def test_bridge_verifyoracledata_unrelayed_block(set_oracle_state):
    with brownie.reverts("NO_ORACLE_ROOT_STATE_DATA"):
        set_oracle_state.verifyOracleData(
            "9999",  # _blockHeight
            RESULT,  # _result
            VERSION,  # _leafVersion
            MERKLE_PATHS,
        )


def test_bridge_verifyoracledata_invalid_data(set_oracle_state):
    with brownie.reverts("INVALID_ORACLE_DATA_PROOF"):
        set_oracle_state.verifyOracleData(
            "3417",  # _blockHeight
            INVALID_RESULT,  # _result
            VERSION,  # _leafVersion
            MERKLE_PATHS,
        )


def test_bridge_verifyoracledata_invalid_merkle_proof_paths(set_oracle_state):
    with brownie.reverts("INVALID_ORACLE_DATA_PROOF"):
        set_oracle_state.verifyOracleData(
            "3417",  # _blockHeight
            RESULT,  # _result
            VERSION,  # _leafVersion
            INCOMPLETE_MERKLE_PATHS,
        )
