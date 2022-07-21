import brownie
from brownie import accounts, Bridge


# chain_id is band-laozi-testnet1
ENCODED_CHAIN_ID = "0x321362616e642d6c616f7a692d746573746e657431"


def test_bridge_validatorpowers_total_validator_power(simple_validator_set):
    totalPower = sum([l[1] for l in simple_validator_set])
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    assert totalPower == bridge.totalValidatorPower()


def test_bridge_validatorpowers_validator_power(simple_validator_set):
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    for [address, power] in simple_validator_set:
        assert bridge.getValidatorPower(address) == power


def test_bridge_validatorpowers_get_power_from_non_existed_validator(simple_validator_set):
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    assert "a5a75393e7fd85f98efa6150c0929a6ba536df53" not in simple_validator_set
    assert bridge.getValidatorPower("a5a75393e7fd85f98efa6150c0929a6ba536df53") == 0


def test_bridge_update_validator_powers_success(simple_validator_set):
    new_validator_power = ["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 150]
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    assert bridge.totalValidatorPower() == 400
    tx = bridge.updateValidatorPowers([new_validator_power], 450)
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 450
    for [address, power] in simple_validator_set:
        if address == new_validator_power[0]:
            assert bridge.getValidatorPower(address) == new_validator_power[1]
        else:
            assert bridge.getValidatorPower(address) == power


def test_bridge_update_validator_powers_multi_total_power_checking_fail(simple_validator_set):
    new_validator_powers_1 = [
        ["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 150],
        ["0x88e1cd00710495EEB93D4f522d16bC8B87Cb00FE", 0],
        ["0x85109F11A7E1385ee826FbF5dA97bB97dba0D76f", 200],
    ]
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    assert bridge.totalValidatorPower() == 400

    with brownie.reverts("TOTAL_POWER_CHECKING_FAIL"):
        bridge.updateValidatorPowers(new_validator_powers_1, 500)


def test_bridge_update_validator_powers_multi_success(simple_validator_set):
    new_validator_powers_1 = [
        ["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 150],
        ["0x88e1cd00710495EEB93D4f522d16bC8B87Cb00FE", 0],
        ["0x85109F11A7E1385ee826FbF5dA97bB97dba0D76f", 200],
    ]
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    assert bridge.totalValidatorPower() == 400
    tx = bridge.updateValidatorPowers(new_validator_powers_1, 550)
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 550

    # checking of the first update
    for [addr1, power1] in simple_validator_set:
        is_removed = False
        new_power = None
        for [addr2, power2] in new_validator_powers_1:
            if addr1 == addr2:
                new_power = power2
                is_removed = new_power == 0
                break
        if new_power is not None:
            if is_removed:
                assert bridge.getValidatorPower(addr1) == 0
            else:
                assert bridge.getValidatorPower(addr1) == new_power
        else:
            assert bridge.getValidatorPower(addr1) == power1

    new_simple_validator_set = []
    for [addr1, power1] in simple_validator_set + new_validator_powers_1:
        is_removed = False
        for [addr2, power2] in new_validator_powers_1:
            if addr1 == addr2 and power2 == 0:
                is_removed = True
                break
        if not is_removed:
            new_simple_validator_set.append([addr1, power1])

    new_validator_powers_2 = [
        ["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 0],
        ["0x85109F11A7E1385ee826FbF5dA97bB97dba0D76f", 0],
    ]
    tx = bridge.updateValidatorPowers(new_validator_powers_2, 200)
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 200

    # checking of the second update
    for [addr1, power1] in new_simple_validator_set:
        is_removed = False
        new_power = None
        for [addr2, power2] in new_validator_powers_2:
            if addr1 == addr2:
                new_power = power2
                is_removed = new_power == 0
                break
        if new_power is not None:
            if is_removed:
                assert bridge.getValidatorPower(addr1) == 0
            else:
                assert bridge.getValidatorPower(addr1) == new_power
        else:
            assert bridge.getValidatorPower(addr1) == power1


def test_bridge_get_number_of_validators_success(simple_validator_set):
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    assert bridge.totalValidatorPower() == 400

    assert bridge.getNumberOfValidators() == len(simple_validator_set)


def test_bridge_get_validators_by_specifying_offset_and_size(simple_validator_set):
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    assert bridge.totalValidatorPower() == 400

    new_validators_1 = [
        ("0x7977B909D55a53F9c73140f7F611EaF0638238Ed", 100),
        ("0x13E35b33b929BD96A004ea88d1fec552B205a23B", 100),
        ("0x04A8C06Ac6D06f25c657Fe61106a485d2583BE71", 100),
        ("0x8908c7eD19595bF94b0622EfB4e098648f16a26c", 100),
    ]
    all_validators = set([(v, p) for v, p in simple_validator_set] + new_validators_1)

    tx = bridge.updateValidatorPowers(new_validators_1, 800)
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 800
    assert bridge.getNumberOfValidators() == 8
    assert set(list(bridge.getAllValidatorPowers())) == all_validators

    new_validators_2 = [
        # update this validator
        ("0x8908c7eD19595bF94b0622EfB4e098648f16a26c", 600),
        # add two more validators
        ("0x07022938e17988D2DF8FAC3bc3bb44422a8afafE", 100),
        ("0xEF60592a3fA43efF0A9eC95B47057a29423Ee800", 100),
    ]
    all_validators = (all_validators - set([("0x8908c7eD19595bF94b0622EfB4e098648f16a26c", 100)])).union(
        new_validators_2
    )

    tx = bridge.updateValidatorPowers(new_validators_2, 1500)
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 1500
    assert bridge.getNumberOfValidators() == 10
    assert set(list(bridge.getAllValidatorPowers())) == all_validators

    for offset, size in [(0, 1), (1, 1), (2, 5), (9, 1), (0, len(all_validators))]:
        validators = set(list(bridge.getValidators(offset, size)))
        assert len(validators) == size
        assert validators.issubset(all_validators)


def test_bridge_get_validator_even_the_non_existent_validators(simple_validator_set):
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    assert bridge.totalValidatorPower() == 400
    assert bridge.getNumberOfValidators() == 4

    query_range_for_testing = 10
    tuple_reference_validators = [(v, p) for v, p in simple_validator_set]
    for i in range(query_range_for_testing):
        for j in range(i, query_range_for_testing):
            assert list(bridge.getValidators(i, j)) == tuple_reference_validators[i : i + j]


def test_bridge_update_and_get_all_validators_success(simple_validator_set):
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    assert bridge.totalValidatorPower() == 400

    # set power for two validators and remove one validator
    tx = bridge.updateValidatorPowers(
        [
            ["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 150],
            ["0x88e1cd00710495EEB93D4f522d16bC8B87Cb00FE", 0],
            ["0x85109F11A7E1385ee826FbF5dA97bB97dba0D76f", 200],
        ],
        550,
    )
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 550
    assert bridge.getNumberOfValidators() == 4
    assert set(list(bridge.getAllValidatorPowers())) == set(
        [
            ("0xaAA22E077492CbaD414098EBD98AA8dc1C7AE8D9", 100),
            ("0xB956589b6fC5523eeD0d9eEcfF06262Ce84ff260", 100),
            ("0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 150),
            ("0x85109F11A7E1385ee826FbF5dA97bB97dba0D76f", 200),
        ]
    )

    # remove two more validators
    tx = bridge.updateValidatorPowers(
        [
            ["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 0],
            ["0x85109F11A7E1385ee826FbF5dA97bB97dba0D76f", 0],
        ],
        200,
    )
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 200
    assert bridge.getNumberOfValidators() == 2
    assert set(list(bridge.getAllValidatorPowers())) == set(
        [
            ("0xaAA22E077492CbaD414098EBD98AA8dc1C7AE8D9", 100),
            ("0xB956589b6fC5523eeD0d9eEcfF06262Ce84ff260", 100),
        ]
    )

    # should be able to set 0 for already removed validators (so, we do it two times)
    for _ in range(2):
        tx = bridge.updateValidatorPowers(
            [
                ["0xaAA22E077492CbaD414098EBD98AA8dc1C7AE8D9", 0],
                ["0xB956589b6fC5523eeD0d9eEcfF06262Ce84ff260", 0],
            ],
            0,
        )
        assert tx.status == 1
        assert bridge.totalValidatorPower() == 0
        assert bridge.getNumberOfValidators() == 0
        assert set(list(bridge.getAllValidatorPowers())) == set([])

    # set four validators
    tx = bridge.updateValidatorPowers(
        [
            ["0xaAA22E077492CbaD414098EBD98AA8dc1C7AE8D9", 1],
            ["0xB956589b6fC5523eeD0d9eEcfF06262Ce84ff260", 1],
            ["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 1],
            ["0x85109F11A7E1385ee826FbF5dA97bB97dba0D76f", 1],
        ],
        4,
    )
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 4
    assert bridge.getNumberOfValidators() == 4
    assert set(list(bridge.getAllValidatorPowers())) == set(
        [
            ("0xaAA22E077492CbaD414098EBD98AA8dc1C7AE8D9", 1),
            ("0xB956589b6fC5523eeD0d9eEcfF06262Ce84ff260", 1),
            ("0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 1),
            ("0x85109F11A7E1385ee826FbF5dA97bB97dba0D76f", 1),
        ]
    )


def test_bridge_update_validator_powers_not_owner(simple_validator_set):
    bridge = accounts[0].deploy(Bridge, simple_validator_set, ENCODED_CHAIN_ID)
    start_total_validator_power = 400
    with brownie.reverts("Ownable: caller is not the owner"):
        tx = bridge.updateValidatorPowers(
            [["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 150]], start_total_validator_power, {"from": accounts[1]}
        )
        assert tx.status == 0
    assert bridge.totalValidatorPower() == start_total_validator_power
    for [address, power] in simple_validator_set:
        assert bridge.getValidatorPower(address) == power
