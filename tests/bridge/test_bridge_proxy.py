import brownie
from brownie import Contract, accounts, Bridge, MockNewVersionBridge


def test_proxy_initialize_success(simple_validator_set, Proxy, ProxyAdmin):
    bridge = accounts[0].deploy(Bridge)
    proxy_admin = accounts[1].deploy(ProxyAdmin)
    proxy = accounts[2].deploy(Proxy, bridge.address, proxy_admin.address, b'')

    admin_role = bridge.DEFAULT_ADMIN_ROLE()

    assert proxy_admin.address == proxy_admin.getProxyAdmin(proxy.address)
    assert bridge.address == proxy_admin.getProxyImplementation(proxy.address)
    assert accounts[1].address == proxy_admin.owner()

    assert not bridge.hasRole(admin_role, accounts[0])
    assert not bridge.hasRole(admin_role, accounts[1])
    assert not bridge.hasRole(admin_role, accounts[2])

    proxy_bridge = Contract.from_abi("Bridge", proxy.address, Bridge.abi)

    assert not proxy_bridge.hasRole(admin_role, accounts[0])
    assert not proxy_bridge.hasRole(admin_role, accounts[1])
    assert not proxy_bridge.hasRole(admin_role, accounts[2])

    proxy_bridge.initialize(simple_validator_set, "0xaabb", {"from": accounts[2]})

    assert not proxy_bridge.hasRole(admin_role, accounts[0])
    assert not proxy_bridge.hasRole(admin_role, accounts[1])
    assert proxy_bridge.hasRole(admin_role, accounts[2])

    assert proxy_bridge.getAllValidatorPowers() == simple_validator_set
    assert proxy_bridge.encodedChainID() == "0xaabb"

    with brownie.reverts("Initializable: contract is already initialized"):
        proxy_bridge.initialize(simple_validator_set, "0xccdd", {"from": accounts[0]})


def test_proxy_bridge_relayandverify(validator_set, valid_proof, Proxy, ProxyAdmin):
    bridge = accounts[0].deploy(Bridge)
    proxy_admin = accounts[0].deploy(ProxyAdmin)
    proxy = accounts[0].deploy(Proxy, bridge.address, proxy_admin.address, b'')

    assert bridge.address == proxy_admin.getProxyImplementation(proxy.address)

    proxy_bridge = Contract.from_abi("Bridge", proxy.address, Bridge.abi)
    proxy_bridge.initialize(validator_set, "0x320d6c616f7a692d6d61696e6e6574", {"from": accounts[0]})

    tx = proxy_bridge.relayAndVerify(valid_proof, {"from": accounts[0]})
    assert tx.status == 1


def test_proxy_bridge_update_validator_powers_success(simple_validator_set, Proxy, ProxyAdmin):
    bridge = accounts[0].deploy(Bridge)
    proxy_admin = accounts[0].deploy(ProxyAdmin)
    proxy = accounts[0].deploy(Proxy, bridge.address, proxy_admin.address, b'')

    assert bridge.address == proxy_admin.getProxyImplementation(proxy.address)

    proxy_bridge = Contract.from_abi("Bridge", proxy.address, Bridge.abi)
    proxy_bridge.initialize(simple_validator_set, "0xaabb", {"from": accounts[0]})

    admin_role = proxy_bridge.DEFAULT_ADMIN_ROLE()
    updater_role = proxy_bridge.VALIDATORS_UPDATER_ROLE()

    assert proxy_bridge.totalValidatorPower() == 400
    assert bridge.totalValidatorPower() == 0

    assert proxy_bridge.hasRole(admin_role, accounts[0])
    assert not proxy_bridge.hasRole(updater_role, accounts[0])

    # grant the updater role to account[0] before update the power
    proxy_bridge.grantRole(proxy_bridge.VALIDATORS_UPDATER_ROLE(), accounts[0].address, {"from": accounts[0]})
    assert proxy_bridge.hasRole(updater_role, accounts[0])

    new_validator_power = ["0x661f2c8D9CF784B7aAa9e19D94836B1a14cddd2A", 150]
    proxy_bridge.updateValidatorPowers([new_validator_power], 450, {"from": accounts[0]})

    assert proxy_bridge.totalValidatorPower() == 450
    assert bridge.totalValidatorPower() == 0

    for [address, power] in simple_validator_set:
        if address == new_validator_power[0]:
            assert proxy_bridge.getValidatorPower(address) == new_validator_power[1]
        else:
            assert proxy_bridge.getValidatorPower(address) == power


def test_proxy_bridge_update_implementation(simple_validator_set, Proxy, ProxyAdmin):
    bridge = accounts[0].deploy(Bridge)
    new_bridge_impl = accounts[0].deploy(MockNewVersionBridge)
    proxy_admin = accounts[0].deploy(ProxyAdmin)
    proxy = accounts[0].deploy(Proxy, bridge.address, proxy_admin.address, b'')

    assert bridge.address == proxy_admin.getProxyImplementation(proxy.address)

    proxy_bridge = Contract.from_abi("Bridge", proxy.address, Bridge.abi)
    proxy_bridge.initialize(simple_validator_set, "0xaabb", {"from": accounts[0]})

    assert proxy_bridge.totalValidatorPower() == 400

    proxy_admin.upgrade(proxy.address, new_bridge_impl.address, {"from": accounts[0]});

    proxy_bridge_new = Contract.from_abi("MockNewVersionBridge", proxy.address, MockNewVersionBridge.abi)
    proxy_bridge_new.resetValidatorsAndChainID({"from": accounts[0]})

    assert proxy_bridge_new.address == proxy_bridge.address

    assert proxy_bridge_new.totalValidatorPower() == 0
    assert proxy_bridge_new.getAllValidatorPowers() == []
