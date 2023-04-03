import brownie
from brownie import accounts, Bridge


# chain_id is band-laozi-testnet1
ENCODED_CHAIN_ID = "0x321362616e642d6c616f7a692d746573746e657431"


def test_bridge_validatorpowers_total_validator_power(simple_validator_set):
    totalPower = sum([l[1] for l in simple_validator_set])
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)
    assert totalPower == bridge.totalValidatorPower()


def test_bridge_validatorpowers_validator_power(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)
    for [address, power] in simple_validator_set:
        assert bridge.getValidatorPower(address) == power


def test_bridge_validatorpowers_get_power_from_non_existed_validator(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)
    assert "a5a75393e7fd85f98efa6150c0929a6ba536df53" not in simple_validator_set
    assert bridge.getValidatorPower("a5a75393e7fd85f98efa6150c0929a6ba536df53") == 0


def test_bridge_admin_update_validator_powers_fail_not_validator_updater(simple_validator_set):
    new_validator_power = ["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150]
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)
    assert bridge.totalValidatorPower() == 400

    revert_msg = 'AccessControl: account {} is missing role {}'.format(
        accounts[0].address.lower(),
        bridge.VALIDATORS_UPDATER_ROLE()
    )

    with brownie.reverts(revert_msg):
        bridge.updateValidatorPowers([new_validator_power], 450, {"from": accounts[0]})


def test_bridge_grant_updater_role_fail_not_admin(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)

    revert_msg = 'AccessControl: account {} is missing role {}'.format(
        accounts[1].address.lower(),
        bridge.DEFAULT_ADMIN_ROLE()
    )

    with brownie.reverts(revert_msg):
        bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[0].address, {"from": accounts[1]})


def test_bridge_update_validator_powers_success(simple_validator_set):
    new_validator_power = ["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150]
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)

    assert bridge.totalValidatorPower() == 400

    # grant the updater role to account[0] before update the power
    bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[0].address, {"from": accounts[0]})
    bridge.updateValidatorPowers([new_validator_power], 450)

    assert bridge.totalValidatorPower() == 450
    for [address, power] in simple_validator_set:
        if address == new_validator_power[0]:
            assert bridge.getValidatorPower(address) == new_validator_power[1]
        else:
            assert bridge.getValidatorPower(address) == power


def test_bridge_update_validator_powers_multi_total_power_checking_fail(simple_validator_set):
    new_validator_powers_1 = [
        ["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150],
        ["0xDbebCF3D304fA3461e6FaD9CBeA2e77Fa3a06fCE", 0],
        ["0xFf8f4195F7aBf32d0716Cb1e000A7eA96eF57328", 200],
    ]
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)

    assert bridge.totalValidatorPower() == 400

    bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[0].address, {"from": accounts[0]})

    with brownie.reverts("TOTAL_POWER_CHECKING_FAIL"):
        bridge.updateValidatorPowers(new_validator_powers_1, 500, {"from": accounts[0]})


def test_bridge_update_validator_powers_multi_success(simple_validator_set):
    new_validator_powers_1 = [
        ["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150],
        ["0xDbebCF3D304fA3461e6FaD9CBeA2e77Fa3a06fCE", 0],
        ["0xFf8f4195F7aBf32d0716Cb1e000A7eA96eF57328", 200],
    ]

    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)

    bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[1].address, {"from": accounts[0]})

    assert bridge.totalValidatorPower() == 400
    bridge.updateValidatorPowers(new_validator_powers_1, 450, {"from": accounts[1]})
    assert bridge.totalValidatorPower() == 450

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
        ["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 0],
        ["0xFf8f4195F7aBf32d0716Cb1e000A7eA96eF57328", 0],
    ]
    bridge.updateValidatorPowers(new_validator_powers_2, 100, {"from": accounts[1]})
    assert bridge.totalValidatorPower() == 100

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
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)

    assert bridge.totalValidatorPower() == 400

    assert bridge.getNumberOfValidators() == len(simple_validator_set)


def test_bridge_get_validators_by_specifying_offset_and_size(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)
    assert bridge.totalValidatorPower() == 400

    bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[0].address, {"from": accounts[0]})

    new_validators_1 = [
        ("0x7977B909D55a53F9c73140f7F611EaF0638238Ed", 100),
        ("0x13E35b33b929BD96A004ea88d1fec552B205a23B", 100),
        ("0x04A8C06Ac6D06f25c657Fe61106a485d2583BE71", 100),
        ("0x8908c7eD19595bF94b0622EfB4e098648f16a26c", 100),
    ]
    all_validators = set([(v, p) for v, p in simple_validator_set] + new_validators_1)

    bridge.updateValidatorPowers(new_validators_1, 800, {"from": accounts[0]})

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

    bridge.updateValidatorPowers(new_validators_2, 1500)
    assert bridge.totalValidatorPower() == 1500
    assert bridge.getNumberOfValidators() == 10
    assert set(list(bridge.getAllValidatorPowers())) == all_validators

    for offset, size in [(0, 1), (1, 1), (2, 5), (9, 1), (0, len(all_validators))]:
        validators = set(list(bridge.getValidators(offset, size)))
        assert len(validators) == size
        assert validators.issubset(all_validators)


def test_bridge_get_validator_even_the_non_existent_validators(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)

    assert bridge.totalValidatorPower() == 400
    assert bridge.getNumberOfValidators() == 4

    query_range_for_testing = 10
    tuple_reference_validators = [(v, p) for v, p in simple_validator_set]
    for i in range(query_range_for_testing):
        for j in range(i, query_range_for_testing):
            assert list(bridge.getValidators(i, j)) == tuple_reference_validators[i : i + j]


def test_bridge_update_and_get_all_validators_success(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)

    assert bridge.totalValidatorPower() == 400

    bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[0].address, {"from": accounts[0]})

    # set power for two validators and remove one validator
    bridge.updateValidatorPowers(
        [
            ["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150],
            ["0xDbebCF3D304fA3461e6FaD9CBeA2e77Fa3a06fCE", 0],
            ["0xFf8f4195F7aBf32d0716Cb1e000A7eA96eF57328", 200],
        ],
        450,
        {"from": accounts[0]}
    )
    assert bridge.totalValidatorPower() == 450
    assert bridge.getNumberOfValidators() == 3
    assert set(list(bridge.getAllValidatorPowers())) == set(
        [
            ("0xE1C0Be3b8acE7dfC33D70bf57f4d23565b15B5d6", 100),
            ("0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150),
            ("0xFf8f4195F7aBf32d0716Cb1e000A7eA96eF57328", 200),
        ]
    )

    # remove two more validators
    bridge.updateValidatorPowers(
        [
            ["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 0],
            ["0xFf8f4195F7aBf32d0716Cb1e000A7eA96eF57328", 0],
        ],
        100,
    )
    assert bridge.totalValidatorPower() == 100
    assert bridge.getNumberOfValidators() == 1
    assert set(list(bridge.getAllValidatorPowers())) == set(
        [
            ("0xE1C0Be3b8acE7dfC33D70bf57f4d23565b15B5d6", 100),
        ]
    )

    # should be able to set 0 for already removed validators (so, we do it two times)
    for _ in range(2):
        bridge.updateValidatorPowers(
            [
                ["0xE1C0Be3b8acE7dfC33D70bf57f4d23565b15B5d6", 0],
            ],
            0,
        )
        assert bridge.totalValidatorPower() == 0
        assert bridge.getNumberOfValidators() == 0
        assert set(list(bridge.getAllValidatorPowers())) == set([])

    # set four validators
    bridge.updateValidatorPowers(
        [
            ["0xDbebCF3D304fA3461e6FaD9CBeA2e77Fa3a06fCE", 1],
            ["0xE1C0Be3b8acE7dfC33D70bf57f4d23565b15B5d6", 1],
            ["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 1],
            ["0xFf8f4195F7aBf32d0716Cb1e000A7eA96eF57328", 1],
        ],
        4,
    )
    assert bridge.totalValidatorPower() == 4
    assert bridge.getNumberOfValidators() == 4
    assert set(list(bridge.getAllValidatorPowers())) == set(
        [
            ("0xDbebCF3D304fA3461e6FaD9CBeA2e77Fa3a06fCE", 1),
            ("0xE1C0Be3b8acE7dfC33D70bf57f4d23565b15B5d6", 1),
            ("0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 1),
            ("0xFf8f4195F7aBf32d0716Cb1e000A7eA96eF57328", 1),
        ]
    )


def test_bridge_update_validator_powers_not_owner(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID)

    start_total_validator_power = 400
    revert_msg = 'AccessControl: account {} is missing role {}'.format(
        accounts[1].address.lower(),
        bridge.VALIDATORS_UPDATER_ROLE()
    )

    with brownie.reverts(revert_msg):
        bridge.updateValidatorPowers(
            [["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150]], start_total_validator_power, {"from": accounts[1]}
        )
    assert bridge.totalValidatorPower() == start_total_validator_power
    for [address, power] in simple_validator_set:
        assert bridge.getValidatorPower(address) == power
