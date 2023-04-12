import pytest
import brownie
from brownie import accounts, Bridge
from random import randint
from collections import namedtuple

INPUT_SEED_1 = [("mumu1")]
INPUT_SEED_2 = [("mumu2")]
INPUT_SEED_3 = [("mumu3")]

Config = namedtuple("Config", ["oracle_script_id", "task_fee"])

# (os_id, task_fee)
FEE_1E14 = 10**14
FEE_1E15 = FEE_1E14 * 10
FEE_1E16 = FEE_1E15 * 10
PROVIDER_CONFIG_1 = Config(43, FEE_1E14)
PROVIDER_CONFIG_2 = Config(999, FEE_1E15)
MOCK_TIMESTAMP = 1655972425
MOCK_BLOCK_HASH = "0xdefbfd2812ce28404dc436710582118cfa12cd4c0fa3694323209f012ca36243"
MOCK_CHAIN_ID = 112
EXPECTED_RESULT_1 = "0x8e4276bb27f4546c479a88ee08af0956c500bbdc4ff09c206df5169006416d8f"
EXPECTED_RESULT_2 = "0x35e58b311de6db31ef9ba73ef94d9fd7559f7242ae8eeda977c6f050bccc432c"


@pytest.mark.parametrize("", [()])
def test_basic_parameters(vrf_provider_2, bridge_1):
    oracle_script_id = vrf_provider_2.oracleScriptID()
    task_nonce = vrf_provider_2.taskNonce()
    task_fee = vrf_provider_2.minimumFee()

    assert vrf_provider_2.bridge() == bridge_1.address
    assert oracle_script_id == PROVIDER_CONFIG_1.oracle_script_id
    assert task_fee == PROVIDER_CONFIG_1.task_fee
    assert task_nonce == 0


@pytest.mark.parametrize("", [()])
def test_set_bridge(vrf_provider_2, bridge_1):
    assert vrf_provider_2.bridge() == bridge_1.address

    # deploy new bridge and set
    new_bridge = accounts[0].deploy(Bridge)
    new_bridge.initialize([], "0x")

    tx = vrf_provider_2.setBridge(new_bridge.address, {"from": accounts[0]})
    assert dict(tx.events["SetBridge"][0])["newBridge"] == new_bridge.address
    assert vrf_provider_2.bridge() == new_bridge.address

    # set back
    vrf_provider_2.setBridge(bridge_1.address, {"from": accounts[0]})
    assert vrf_provider_2.bridge() == bridge_1.address


@pytest.mark.parametrize("", [()])
def test_set_bridge_script_id_not_owner(vrf_provider_2, bridge_1):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider_2.setBridge(bridge_1, {"from": accounts[1]})


@pytest.mark.parametrize("_oracle_script_id", [PROVIDER_CONFIG_2.oracle_script_id])
def test_set_oracle_script_id(vrf_provider_2, _oracle_script_id):
    assert vrf_provider_2.oracleScriptID() == PROVIDER_CONFIG_1.oracle_script_id
    tx = vrf_provider_2.setOracleScriptID(_oracle_script_id, {"from": accounts[0]})
    assert dict(tx.events["SetOracleScriptID"][0])["newOID"] == _oracle_script_id
    assert vrf_provider_2.oracleScriptID() == PROVIDER_CONFIG_2.oracle_script_id


@pytest.mark.parametrize("_oracleScriptID", [PROVIDER_CONFIG_2.oracle_script_id])
def test_set_oracle_script_id_not_owner(vrf_provider_2, _oracleScriptID):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider_2.setOracleScriptID(_oracleScriptID, {"from": accounts[1]})


@pytest.mark.parametrize("", [()])
def test_getting_random_task_should_be_an_empty_task(vrf_provider_2, default_task_v2):
    for _ in range(5):
        random_nonce = randint(20, 100)
        assert vrf_provider_2.tasks(random_nonce) == default_task_v2


@pytest.mark.parametrize("client_seed", INPUT_SEED_1)
def test_request_random_data_fee_is_lower_than_the_minimum_fee(vrf_provider_2, client_seed, default_task_v2):
    tx = vrf_provider_2.setMinimumFee(PROVIDER_CONFIG_2.task_fee, {"from": accounts[0]})
    assert dict(tx.events["SetMinimumFee"][0])["newMinimumFee"] == PROVIDER_CONFIG_2.task_fee
    assert vrf_provider_2.minimumFee() == PROVIDER_CONFIG_2.task_fee

    nonce = 0

    task = vrf_provider_2.tasks(nonce)
    assert task == default_task_v2

    with brownie.reverts("VRFProviderBase: Task fee is lower than the minimum fee"):
        vrf_provider_2.requestRandomData(client_seed, {"from": accounts[1], "value": FEE_1E14})


@pytest.mark.parametrize("client_seed", INPUT_SEED_1)
def test_request_random_data_success_1(vrf_provider_2, client_seed, default_task_v2):
    nonce = 0
    caller = accounts[1]

    task = vrf_provider_2.tasks(nonce)
    assert task == default_task_v2
    assert vrf_provider_2.balance() == 0
    assert vrf_provider_2.taskNonce() == nonce

    tx = vrf_provider_2.requestRandomData(client_seed, {"from": accounts[1], "value": FEE_1E15})

    seed = vrf_provider_2.getSeed(MOCK_TIMESTAMP, caller, MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed)

    events = dict(tx.events["RandomDataRequested"][0])
    assert events["nonce"] == nonce
    assert events["caller"] == caller
    assert events["clientSeed"] == client_seed
    assert events["time"] == MOCK_TIMESTAMP
    assert events["blockHash"] == MOCK_BLOCK_HASH
    assert events["chainID"] == MOCK_CHAIN_ID
    assert events["taskFee"] == FEE_1E15
    assert events["seed"] == seed

    task = vrf_provider_2.tasks(nonce)
    assert task == (False, MOCK_TIMESTAMP, caller, FEE_1E15, seed, "0x", client_seed)
    assert vrf_provider_2.balance() == FEE_1E15
    assert vrf_provider_2.taskNonce() == nonce + 1


@pytest.mark.parametrize("client_seed", INPUT_SEED_2)
def test_request_random_data_with_redundant_fee_success_2(vrf_provider_2, client_seed, default_task_v2):
    nonce = 1
    caller = accounts[1]

    task = vrf_provider_2.tasks(nonce)
    assert task == default_task_v2
    assert vrf_provider_2.balance() == FEE_1E15
    assert vrf_provider_2.taskNonce() == nonce

    tx = vrf_provider_2.requestRandomData(client_seed, {"from": accounts[1], "value": FEE_1E16})
    seed = vrf_provider_2.getSeed(MOCK_TIMESTAMP, caller, MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed)
    events = dict(tx.events["RandomDataRequested"][0])

    assert events["nonce"] == nonce
    assert events["caller"] == caller
    assert events["clientSeed"] == client_seed
    assert events["time"] == MOCK_TIMESTAMP
    assert events["blockHash"] == MOCK_BLOCK_HASH
    assert events["chainID"] == MOCK_CHAIN_ID
    assert events["taskFee"] == FEE_1E16
    assert events["seed"] == seed

    task = vrf_provider_2.tasks(nonce)
    assert task == (False, MOCK_TIMESTAMP, caller, FEE_1E16, seed, "0x", client_seed)
    assert vrf_provider_2.balance() == FEE_1E15 + FEE_1E16
    assert vrf_provider_2.taskNonce() == nonce + 1


@pytest.mark.parametrize("used_client_seeds", [INPUT_SEED_1, INPUT_SEED_2])
def test_request_random_data_fail_seed_already_exist_for_sender(vrf_provider_2, used_client_seeds):
    for client_seed in used_client_seeds:
        with brownie.reverts("VRFProviderBase: Seed already existed for this sender"):
            vrf_provider_2.requestRandomData(client_seed, {"from": accounts[1], "value": FEE_1E15})


def test_relay_proof_success(vrf_provider_2, testnet_vrf_v2_proof_1):
    assert (vrf_provider_2.oracleScriptID(), vrf_provider_2.minimumFee()) == PROVIDER_CONFIG_2

    # set back the parameters
    for call, param in zip((vrf_provider_2.setOracleScriptID, vrf_provider_2.setMinimumFee), PROVIDER_CONFIG_1):
        call(param, {"from": accounts[0]})

    assert (vrf_provider_2.oracleScriptID(), vrf_provider_2.minimumFee()) == PROVIDER_CONFIG_1

    nonce = 0

    # before relay balance
    account1_prev_balance = accounts[1].balance()

    vrf_provider_2.relayProof(testnet_vrf_v2_proof_1, nonce, {"from": accounts[1]})

    task = vrf_provider_2.tasks(nonce)

    assert task == (
        True,
        MOCK_TIMESTAMP,
        accounts[1].address,
        FEE_1E15,
        vrf_provider_2.getSeed(MOCK_TIMESTAMP, accounts[1], MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, INPUT_SEED_1[0]),
        EXPECTED_RESULT_1,
        INPUT_SEED_1[0],
    )

    # the balance after relaying
    # the relayer must receive the fee
    assert accounts[1].balance() == account1_prev_balance + FEE_1E15


def test_vrf_request_relay_consume_fail_task_already_resolved(vrf_provider_2, testnet_vrf_proof):
    with brownie.reverts("VRFProviderBase: Task already resolved"):
        nonce = 0
        vrf_provider_2.relayProof(testnet_vrf_proof, nonce, {"from": accounts[2]})


@pytest.mark.parametrize("client_seed", INPUT_SEED_2)
def test_request_random_data_2(vrf_provider_2, client_seed, default_task_v2):
    nonce = 2
    caller = accounts[2]

    task = vrf_provider_2.tasks(nonce)
    assert task == default_task_v2

    tx = vrf_provider_2.requestRandomData(client_seed, {"from": accounts[2], "value": FEE_1E15})

    seed = vrf_provider_2.getSeed(MOCK_TIMESTAMP, caller, MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed)

    events = dict(tx.events["RandomDataRequested"][0])
    assert events["nonce"] == nonce
    assert events["caller"] == caller
    assert events["clientSeed"] == client_seed
    assert events["time"] == MOCK_TIMESTAMP
    assert events["blockHash"] == MOCK_BLOCK_HASH
    assert events["taskFee"] == FEE_1E15
    assert events["seed"] == seed

    task = vrf_provider_2.tasks(nonce)
    assert task == (False, MOCK_TIMESTAMP, caller, FEE_1E15, seed, "0x", client_seed)
    assert vrf_provider_2.balance() == FEE_1E15 + FEE_1E16
    assert vrf_provider_2.taskNonce() == nonce + 1


def test_relay_proof_incorrect_worker(vrf_provider_2, testnet_vrf_v2_proof_2_incorrect_worker):
    nonce = 2
    with brownie.reverts("VRFProviderBase: The sender must be the task worker"):
        vrf_provider_2.relayProof(testnet_vrf_v2_proof_2_incorrect_worker, nonce, {"from": accounts[2]})


def test_relay_proof_incorrect_os_id(vrf_provider_2, testnet_vrf_proof_1_16_incorrect_os_id):
    nonce = 2
    with brownie.reverts("VRFProviderBase: Oracle Script ID not match"):
        vrf_provider_2.relayProof(testnet_vrf_proof_1_16_incorrect_os_id, nonce, {"from": accounts[2]})


def test_relay_proof_not_successfully_resolved(vrf_provider_2, testnet_vrf_v2_proof_2_not_successfully_resolved):
    nonce = 2
    with brownie.reverts("VRFProviderBase: Request not successfully resolved"):
        vrf_provider_2.relayProof(testnet_vrf_v2_proof_2_not_successfully_resolved, nonce, {"from": accounts[2]})


def test_relay_proof_seed_mismatch(vrf_provider_2, testnet_vrf_v2_proof_2_seed_mismatch):
    nonce = 2
    with brownie.reverts("VRFProviderBase: Seed is mismatched"):
        vrf_provider_2.relayProof(testnet_vrf_v2_proof_2_seed_mismatch, nonce, {"from": accounts[2]})


def test_relay_proof_time_mismatch(vrf_provider_2, testnet_vrf_v2_proof_2_time_mismatch):
    nonce = 2
    with brownie.reverts("VRFProviderBase: Time is mismatched"):
        vrf_provider_2.relayProof(testnet_vrf_v2_proof_2_time_mismatch, nonce, {"from": accounts[2]})


def test_relay_proof_task_not_found(vrf_provider_2, testnet_vrf_v2_proof_2):
    # invalid nonce
    nonce = 3
    with brownie.reverts("VRFProviderBase: Task not found"):
        vrf_provider_2.relayProof(testnet_vrf_v2_proof_2, nonce, {"from": accounts[2]})


def test_relay_proof_not_enough_power(vrf_provider_2, bridge_1, bridge_2, testnet_vrf_v2_proof_2):
    # change bridge to bridge_2
    vrf_provider_2.setBridge(bridge_2.address, {"from": accounts[0]})

    nonce = 2
    with brownie.reverts("INSUFFICIENT_VALIDATOR_SIGNATURES"):
        vrf_provider_2.relayProof(testnet_vrf_v2_proof_2, nonce, {"from": accounts[2]})

    # change back bridge_1
    vrf_provider_2.setBridge(bridge_1.address, {"from": accounts[0]})


@pytest.mark.parametrize("client_seed", INPUT_SEED_2)
def test_relay_proof_v2_2(vrf_provider_2, testnet_vrf_v2_proof_2, client_seed):
    # before relay balance
    account2_prev_balance = accounts[2].balance()

    nonce = 2

    vrf_provider_2.relayProof(testnet_vrf_v2_proof_2, nonce, {"from": accounts[2]})

    assert vrf_provider_2.tasks(nonce) == (
        True,
        MOCK_TIMESTAMP,
        accounts[2].address,
        FEE_1E15,
        vrf_provider_2.getSeed(MOCK_TIMESTAMP, accounts[2], MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed),
        EXPECTED_RESULT_2,
        INPUT_SEED_2[0],
    )

    # the balance after relaying
    # the relayer must receive the fee
    assert accounts[2].balance() == account2_prev_balance + FEE_1E15
