import brownie
from brownie import accounts, Bridge


ENCODED_CHAIN_ID_1 = "0x111111111111111111111111111111111111111111"
ENCODED_CHAIN_ID_2 = "0x222222222222222222222222222222222222222222"


def test_bridge_encoded_chain_id(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    assert ENCODED_CHAIN_ID_1 == bridge.encodedChainID()


def test_bridge_set_encoded_chain_id_fail_not_admin(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    assert ENCODED_CHAIN_ID_1 == bridge.encodedChainID()

    revert_msg = "AccessControl: account {} is missing role {}".format(
        accounts[1].address.lower(), bridge.DEFAULT_ADMIN_ROLE()
    )

    with brownie.reverts(revert_msg):
        bridge.updateEncodedChainID(ENCODED_CHAIN_ID_2, {"from": accounts[1]})


def test_bridge_set_encoded_chain_id_success(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    assert ENCODED_CHAIN_ID_1 == bridge.encodedChainID()

    bridge.updateEncodedChainID(ENCODED_CHAIN_ID_2, {"from": accounts[0]})

    assert ENCODED_CHAIN_ID_2 == bridge.encodedChainID()


def test_bridge_update_validators_fail_not_updater(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    assert bridge.totalValidatorPower() == 400

    # account 0, 1, 2 fail to update validators
    for account_i in accounts[:3]:
        revert_msg = "AccessControl: account {} is missing role {}".format(
            account_i.address.lower(), bridge.VALIDATORS_UPDATER_ROLE()
        )

        with brownie.reverts(revert_msg):
            bridge.updateValidatorPowers(
                [["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150]], 450, {"from": account_i}
            )


def test_bridge_update_validators_success_after_grant_updater_role(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    assert bridge.totalValidatorPower() == 400

    bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[1].address, {"from": accounts[0]})
    bridge.updateValidatorPowers([["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150]], 450, {"from": accounts[1]})

    assert bridge.totalValidatorPower() == 450


def test_bridge_grant_role_fail_not_admin(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    revert_msg = "AccessControl: account {} is missing role {}".format(
        accounts[1].address.lower(), bridge.DEFAULT_ADMIN_ROLE()
    )

    with brownie.reverts(revert_msg):
        bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[2].address, {"from": accounts[1]})


def test_bridge_revoke_role_fail_not_admin(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    assert bridge.totalValidatorPower() == 400

    bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[2].address, {"from": accounts[0]})
    bridge.updateValidatorPowers([["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150]], 450, {"from": accounts[2]})

    assert bridge.totalValidatorPower() == 450

    revert_msg = "AccessControl: account {} is missing role {}".format(
        accounts[1].address.lower(), bridge.DEFAULT_ADMIN_ROLE()
    )

    with brownie.reverts(revert_msg):
        bridge.revokeRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[2].address, {"from": accounts[1]})


def test_bridge_revoke_success_by_admin(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    assert bridge.totalValidatorPower() == 400

    bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[2].address, {"from": accounts[0]})
    bridge.updateValidatorPowers([["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150]], 450, {"from": accounts[2]})

    assert bridge.totalValidatorPower() == 450

    bridge.revokeRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[2].address, {"from": accounts[0]})

    revert_msg = "AccessControl: account {} is missing role {}".format(
        accounts[2].address.lower(), bridge.VALIDATORS_UPDATER_ROLE()
    )
    with brownie.reverts(revert_msg):
        bridge.updateValidatorPowers([["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 200]], 500, {"from": accounts[2]})


def test_bridge_transfer_admin_role_fail_not_admin(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    admin_role = bridge.DEFAULT_ADMIN_ROLE()
    updater_role = bridge.VALIDATORS_UPDATER_ROLE()

    assert bridge.hasRole(admin_role, accounts[0])
    assert not bridge.hasRole(admin_role, accounts[1])
    assert not bridge.hasRole(admin_role, accounts[2])

    assert not bridge.hasRole(updater_role, accounts[0])
    assert not bridge.hasRole(updater_role, accounts[1])
    assert not bridge.hasRole(updater_role, accounts[2])

    bridge.grantRole(bridge.VALIDATORS_UPDATER_ROLE(), accounts[2].address, {"from": accounts[0]})
    assert bridge.hasRole(updater_role, accounts[2])

    for account_i in [accounts[1], accounts[2]]:
        revert_msg = "AccessControl: account {} is missing role {}".format(
            account_i.address.lower(), bridge.DEFAULT_ADMIN_ROLE()
        )

        with brownie.reverts(revert_msg):
            bridge.grantRole(bridge.DEFAULT_ADMIN_ROLE(), accounts[3].address, {"from": account_i})
            bridge.revokeRole(bridge.DEFAULT_ADMIN_ROLE(), account_i.address, {"from": account_i})


def test_bridge_transfer_admin_role_success(simple_validator_set):
    bridge = accounts[0].deploy(Bridge)
    bridge.initialize(simple_validator_set, ENCODED_CHAIN_ID_1)

    admin_role = bridge.DEFAULT_ADMIN_ROLE()
    assert ENCODED_CHAIN_ID_1 == bridge.encodedChainID()

    admin_matrix = [[True, False], [False, True]]

    chain_ids = [ENCODED_CHAIN_ID_1, ENCODED_CHAIN_ID_2]
    revert_msg = "AccessControl: account {} is missing role {}"

    for i in range(len(admin_matrix)):
        with brownie.reverts(revert_msg.format(accounts[i + 1].address.lower(), bridge.DEFAULT_ADMIN_ROLE())):
            bridge.updateEncodedChainID(chain_ids[(i + 1) % 2], {"from": accounts[i + 1]})

        for j in range(len(admin_matrix)):
            assert bridge.hasRole(admin_role, accounts[j]) == admin_matrix[i][j]

        bridge.grantRole(bridge.DEFAULT_ADMIN_ROLE(), accounts[i + 1].address, {"from": accounts[i]})
        bridge.revokeRole(bridge.DEFAULT_ADMIN_ROLE(), accounts[i].address, {"from": accounts[i]})

        bridge.updateEncodedChainID(chain_ids[(i + 1) % 2], {"from": accounts[i + 1]})
