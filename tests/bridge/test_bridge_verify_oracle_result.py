import brownie
from brownie import accounts
import time


def test_bridge_relayandverify_bridge_success(bridge, valid_proof):
    result = bridge.verifyOracleResult(valid_proof, {"from": accounts[0]})
    # check resolve status
    assert result[9] == 1


def test_bridge_relayandverify_bridge_fail(bridge, invalid_proof):
    with brownie.reverts():
        bridge.verifyOracleResult(invalid_proof, {"from": accounts[0]})
