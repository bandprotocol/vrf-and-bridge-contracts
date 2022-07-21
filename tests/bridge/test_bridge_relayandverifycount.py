import brownie
from brownie import accounts


def test_bridge_relayandverifycount_bridge_success(bridge, valid_count_proof):
    tx = bridge.relayAndVerifyCount(valid_count_proof, {"from": accounts[0]})
    assert tx.status == 1


def test_bridge_relayandverifycount_bridge_fail(bridge, invalid_proof):
    with brownie.reverts():
        tx = bridge.relayAndVerifyCount(invalid_proof, {"from": accounts[0]})
        tx.status == 0
