import brownie
from brownie import Contract, accounts, Bridge


ENCODED_CHAIN_ID = "0x320c616e795f636861696e5f6964"


def test_bridge_deployment(simple_validator_set, Proxy, ProxyAdmin):
    actors = {
        "deployer": accounts[0],
        "multisig": accounts[1],
        "updater_1": accounts[2],
        "updater_2": accounts[3],
    }

    proxy_admin = actors["deployer"].deploy(ProxyAdmin)
    proxy_admin.transferOwnership(actors["multisig"].address, {"from": actors["deployer"]})

    bridge_impl = actors["deployer"].deploy(Bridge)

    proxy = actors["deployer"].deploy(Proxy, bridge_impl.address, proxy_admin.address, b'')

    bridge_proxy = Contract.from_abi("Bridge", proxy.address, Bridge.abi)
    bridge_proxy.initialize(simple_validator_set, ENCODED_CHAIN_ID, {"from": actors["deployer"]})

    updater_role = bridge_proxy.VALIDATORS_UPDATER_ROLE()
    admin_role = bridge_proxy.DEFAULT_ADMIN_ROLE()

    bridge_proxy.grantRole(updater_role, actors["updater_1"].address, {"from": actors["deployer"]})
    bridge_proxy.grantRole(updater_role, actors["updater_2"].address, {"from": actors["deployer"]})
    bridge_proxy.grantRole(admin_role, actors["multisig"].address, {"from": actors["deployer"]})
    bridge_proxy.renounceRole(admin_role, actors["deployer"].address, {"from": actors["deployer"]})

    assert proxy_admin.getProxyImplementation(bridge_proxy.address) == bridge_impl.address
    assert proxy_admin.getProxyAdmin(bridge_proxy.address) == proxy_admin.address
    assert proxy_admin.owner() == actors["multisig"].address

    for actor_name, actor in actors.items():
        if actor_name == "multisig":
            assert bridge_proxy.hasRole(admin_role, actor.address)
        else:
            assert not bridge_proxy.hasRole(admin_role, actor.address)

        if "updater" in actor_name:
            assert bridge_proxy.hasRole(updater_role, actor.address)
        else:
            assert not bridge_proxy.hasRole(updater_role, actor.address)

    assert bridge_proxy.getAllValidatorPowers() == simple_validator_set
    assert bridge_proxy.encodedChainID() == ENCODED_CHAIN_ID
