import brownie
from brownie import accounts


def test_bridge_relayandverifycount_bridge_success(bridge, valid_count_proof):
    bridge.relayAndVerifyCount(valid_count_proof, {"from": accounts[0]})


def test_bridge_relayandverifycount_bridge_fail(bridge, invalid_proof):
    with brownie.reverts():
        bridge.relayAndVerifyCount(invalid_proof, {"from": accounts[0]})
