import brownie
from brownie import accounts
import time


def test_bridge_relayandverify_bridge_success(bridge, valid_proof):
    tx = bridge.relayAndVerify(valid_proof, {"from": accounts[0]})
    assert tx.status == 1


def test_bridge_relayandverify_bridge_fail(bridge, invalid_proof):
    with brownie.reverts():
        tx = bridge.relayAndVerify(invalid_proof, {"from": accounts[0]})
        tx.status == 0


def test_bridge_relayandverify_bridgeinfo_success(bridgeinfo, valid_proof):
    tx = bridgeinfo.relayAndSave(valid_proof, {"from": accounts[0]})
    assert tx.status == 1


def test_bridge_relayandverify_bridgeinfo_success(bridgeinfo, invalid_proof):
    with brownie.reverts():
        tx = bridgeinfo.relayAndSave(invalid_proof, {"from": accounts[0]})
        tx.status == 0


def test_bridge_relay_request_clientid(bridgeinfo_relayed):
    assert bridgeinfo_relayed.ClientID() == "feeder"


def test_bridge_relayandverify_request_oraclescriptid(bridgeinfo_relayed):
    assert bridgeinfo_relayed.oracleScriptID() == 3


def test_bridge_relayandverify_request_params(bridgeinfo_relayed):
    assert (
        bridgeinfo_relayed.params()
        == "0x000000120000000341444100000003424e4200000004434f4d5000000003444742000000024854000000034b534d000000044c494e41000000044c494e4b000000054d494f5441000000034d4b52000000034f4d4700000003534e580000000354525800000003554e490000000356455400000003584c4d0000000358525000000003594649000000003b9aca00"
    )


def test_bridge_relayandverify_askcount(bridgeinfo_relayed):
    assert bridgeinfo_relayed.askCount() == 16


def test_bridge_relayandverify_mincount(bridgeinfo_relayed):
    assert bridgeinfo_relayed.minCount() == 10


def test_bridge_relayandverify_requestid(bridgeinfo_relayed):
    assert bridgeinfo_relayed.requestID() == 39521


def test_bridge_relayandverify_anscount(bridgeinfo_relayed):
    assert bridgeinfo_relayed.ansCount() == 13


def test_bridge_relayandverify_request_time(bridgeinfo_relayed):
    ts = time.time()
    assert bridgeinfo_relayed.requestTime() < ts
    assert bridgeinfo_relayed.requestTime() == 1632920991


def test_bridge_relayandverify_resolve_time(bridgeinfo_relayed):
    ts = time.time()
    assert bridgeinfo_relayed.resolveTime() < ts
    assert bridgeinfo_relayed.resolveTime() > bridgeinfo_relayed.requestTime()
    assert bridgeinfo_relayed.resolveTime() == 1632921003


def test_bridge_relayandverify_resolve_status(bridgeinfo_relayed):
    assert bridgeinfo_relayed.resolveStatus() == 1


def test_bridge_relayandverify_resolve_status(bridgeinfo_relayed):
    assert (
        bridgeinfo_relayed.result()
        == "0x00000012000000007e4510cc000000560a892eb00000004dddb5a1f0000000000299879600000001cf292ef00000004e73af08e00000000002017550000000057f0880200000000040a86de0000002130a987dc000000002671eb4000000000244e751a80000000005362ec8000000058577afd000000000052c40de0000000010961c91000000003a37426000001aa324d61000"
    )
