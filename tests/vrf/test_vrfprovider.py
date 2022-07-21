import pytest
import brownie
from brownie import accounts, Bridge
from conftest import MockTask, MockConfig
from random import randint

INPUT_SEED_1 = [("mumu1")]
INPUT_SEED_2 = [("mumu2")]
INPUT_SEED_3 = [("mumu3")]

# (os_id,min_count,ask_count,task_fee)
FEE_1E14 = 10**14
FEE_1E15 = FEE_1E14 * 10
FEE_1E16 = FEE_1E15 * 10
PROVIDER_CONFIG_1 = MockConfig(36, 10, 16, FEE_1E14)
PROVIDER_CONFIG_2 = MockConfig(999, 1, 16, FEE_1E15)
MOCK_TIMESTAMP = 1655972425
MOCK_BLOCK_HASH = "0xdefbfd2812ce28404dc436710582118cfa12cd4c0fa3694323209f012ca36243"
MOCK_CHAIN_ID = 112
EXPECTED_RESULT_1 = "0x1217ad4e524a01e849d3baf1c694085790327f9a35668737abac69da77a1fa22becd05447f316750bc9f878c4e6bafe2a79e083c0a10a6c72da005127fad0b1a"
EXPECTED_PROOF_1 = "0x6e482bbd3b8e7294a98bd76dc7e512aa80592f5a8c3b74b3d2150058cc46c480a98d97bc61476062aae727c5df4145d488e2f353a9f774dd0e04c562c0839ad67d0c7ff0a70ee2598cb3b0c5315cca00"
EXPECTED_RESULT_2 = "0xbc798ebf37c99018c24ab4009072a4d7ee31159afe2684f685bcd8a2e56782229d094e995b569e1fd94753b644db5b05b7b91597e41c35566b58233d82c4704c"
EXPECTED_PROOF_2 = "0xc2c300bb8e36a044f1b87dbdc5cc671b52db3d9a144c824f0471cfcadac2b8b1e04f40a43342705bf9a3734cc9bebaeadc88acd6243755e22aeff54812946c8efcdf006453361db6a3002786e12a950a"


@pytest.mark.parametrize("", [()])
def test_basic_parameters(vrf_provider_1, bridge_1):
    oracle_script_id = vrf_provider_1.oracleScriptID()
    min_count = vrf_provider_1.minCount()
    ask_count = vrf_provider_1.askCount()
    task_nonce = vrf_provider_1.taskNonce()
    task_fee = vrf_provider_1.minimumFee()

    assert vrf_provider_1.bridge() == bridge_1.address
    assert oracle_script_id == PROVIDER_CONFIG_1.oracle_script_id
    assert min_count == PROVIDER_CONFIG_1.min_count
    assert ask_count == PROVIDER_CONFIG_1.ask_count
    assert task_fee == PROVIDER_CONFIG_1.task_fee
    assert task_nonce == 0


@pytest.mark.parametrize("", [()])
def test_set_bridge(vrf_provider_1, bridge_1):
    assert vrf_provider_1.bridge() == bridge_1.address

    # deploy new bridge and set
    new_bridge = accounts[0].deploy(Bridge, [], "0x")
    tx = vrf_provider_1.setBridge(new_bridge.address, {"from": accounts[0]})
    assert tx.status == 1
    assert dict(tx.events["SetBridge"][0])["newBridge"] == new_bridge.address
    assert vrf_provider_1.bridge() == new_bridge.address

    # set back
    vrf_provider_1.setBridge(bridge_1.address, {"from": accounts[0]})
    assert vrf_provider_1.bridge() == bridge_1.address


@pytest.mark.parametrize("", [()])
def test_set_bridge_script_id_not_owner(vrf_provider_1, bridge_1):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider_1.setBridge(bridge_1, {"from": accounts[1]})


@pytest.mark.parametrize("_oracle_script_id", [PROVIDER_CONFIG_2.oracle_script_id])
def test_set_oracle_script_id(vrf_provider_1, _oracle_script_id):
    assert vrf_provider_1.oracleScriptID() == PROVIDER_CONFIG_1.oracle_script_id
    tx = vrf_provider_1.setOracleScriptID(_oracle_script_id, {"from": accounts[0]})

    assert tx.status == 1
    assert dict(tx.events["SetOracleScriptID"][0])["newOID"] == _oracle_script_id
    assert vrf_provider_1.oracleScriptID() == PROVIDER_CONFIG_2.oracle_script_id


@pytest.mark.parametrize("_oracleScriptID", [PROVIDER_CONFIG_2.oracle_script_id])
def test_set_oracle_script_id_not_owner(vrf_provider_1, _oracleScriptID):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider_1.setOracleScriptID(_oracleScriptID, {"from": accounts[1]})


@pytest.mark.parametrize("_min_count", [PROVIDER_CONFIG_2.min_count])
def test_set_min_count(vrf_provider_1, _min_count):
    assert vrf_provider_1.minCount() == PROVIDER_CONFIG_1.min_count
    tx = vrf_provider_1.setMinCount(_min_count, {"from": accounts[0]})

    assert tx.status == 1
    assert dict(tx.events["SetMinCount"][0])["newMinCount"] == _min_count
    assert vrf_provider_1.minCount() == PROVIDER_CONFIG_2.min_count


@pytest.mark.parametrize("_minCount", [PROVIDER_CONFIG_1.min_count])
def test_set_min_count_not_owner(vrf_provider_1, _minCount):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider_1.setMinCount(_minCount, {"from": accounts[1]})


@pytest.mark.parametrize("_ask_count", [PROVIDER_CONFIG_2.ask_count])
def test_set_ask_count(vrf_provider_1, _ask_count):
    assert vrf_provider_1.askCount() == PROVIDER_CONFIG_1.ask_count
    tx = vrf_provider_1.setAskCount(_ask_count, {"from": accounts[0]})

    assert tx.status == 1
    assert dict(tx.events["SetAskCount"][0])["newAskCount"] == _ask_count
    assert vrf_provider_1.askCount() == PROVIDER_CONFIG_2.ask_count


@pytest.mark.parametrize("_askCount", [PROVIDER_CONFIG_2.ask_count])
def test_set_ask_count_not_owner(vrf_provider_1, _askCount):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider_1.setAskCount(_askCount, {"from": accounts[1]})


@pytest.mark.parametrize("_task_fee", [PROVIDER_CONFIG_2.task_fee])
def test_set_ask_count(vrf_provider_1, _task_fee):
    assert vrf_provider_1.minimumFee() == PROVIDER_CONFIG_1.task_fee
    tx = vrf_provider_1.setMinimumFee(_task_fee, {"from": accounts[0]})

    assert tx.status == 1
    assert dict(tx.events["SetMinimumFee"][0])["newMinimumFee"] == _task_fee
    assert vrf_provider_1.minimumFee() == PROVIDER_CONFIG_2.task_fee


@pytest.mark.parametrize("_task_fee", [PROVIDER_CONFIG_2.task_fee])
def test_set_ask_count_not_owner(vrf_provider_1, _task_fee):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider_1.setMinimumFee(_task_fee, {"from": accounts[1]})


@pytest.mark.parametrize("", [()])
def test_getting_random_task_should_be_an_empty_task(vrf_provider_1):
    for _ in range(5):
        random_nonce = randint(20, 100)
        assert vrf_provider_1.tasks(random_nonce) == MockTask().to_tuple()


@pytest.mark.parametrize("client_seed", INPUT_SEED_1)
def test_request_random_data_fee_is_lower_than_the_minimum_fee(vrf_provider_1, client_seed):
    nonce = 0
    caller = accounts[1]

    task = vrf_provider_1.tasks(nonce)
    assert task == MockTask().to_tuple()

    with brownie.reverts("VRFProviderBase: Task fee is lower than the minimum fee"):
        vrf_provider_1.requestRandomData(client_seed, {"from": accounts[1], "value": FEE_1E14})


@pytest.mark.parametrize("client_seed", INPUT_SEED_1)
def test_request_random_data_success_1(vrf_provider_1, client_seed):
    nonce = 0
    caller = accounts[1]

    task = vrf_provider_1.tasks(nonce)
    assert task == MockTask().to_tuple()
    assert vrf_provider_1.balance() == 0
    assert vrf_provider_1.taskNonce() == nonce

    tx = vrf_provider_1.requestRandomData(client_seed, {"from": accounts[1], "value": FEE_1E15})
    assert tx.status == 1

    seed = vrf_provider_1.getSeed(MOCK_TIMESTAMP, caller, MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed)

    events = dict(tx.events["RandomDataRequested"][0])
    assert events["nonce"] == nonce
    assert events["caller"] == caller
    assert events["clientSeed"] == client_seed
    assert events["time"] == MOCK_TIMESTAMP
    assert events["blockHash"] == MOCK_BLOCK_HASH
    assert events["chainID"] == MOCK_CHAIN_ID
    assert events["taskFee"] == FEE_1E15
    assert events["seed"] == seed

    task = vrf_provider_1.tasks(nonce)
    assert task == MockTask(False, MOCK_TIMESTAMP, caller, FEE_1E15, seed, client_seed).to_tuple()
    assert vrf_provider_1.balance() == FEE_1E15
    assert vrf_provider_1.taskNonce() == nonce + 1


@pytest.mark.parametrize("client_seed", INPUT_SEED_2)
def test_request_random_data_with_redundant_fee_success_2(vrf_provider_1, client_seed):
    nonce = 1
    caller = accounts[1]

    task = vrf_provider_1.tasks(nonce)
    assert task == MockTask().to_tuple()
    assert vrf_provider_1.balance() == FEE_1E15
    assert vrf_provider_1.taskNonce() == nonce

    tx = vrf_provider_1.requestRandomData(client_seed, {"from": accounts[1], "value": FEE_1E16})
    assert tx.status == 1

    seed = vrf_provider_1.getSeed(MOCK_TIMESTAMP, caller, MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed)

    events = dict(tx.events["RandomDataRequested"][0])
    assert events["nonce"] == nonce
    assert events["caller"] == caller
    assert events["clientSeed"] == client_seed
    assert events["time"] == MOCK_TIMESTAMP
    assert events["blockHash"] == MOCK_BLOCK_HASH
    assert events["chainID"] == MOCK_CHAIN_ID
    assert events["taskFee"] == FEE_1E16
    assert events["seed"] == seed

    task = vrf_provider_1.tasks(nonce)
    assert task == MockTask(False, MOCK_TIMESTAMP, caller, FEE_1E16, seed, client_seed).to_tuple()
    assert vrf_provider_1.balance() == FEE_1E15 + FEE_1E16
    assert vrf_provider_1.taskNonce() == nonce + 1


@pytest.mark.parametrize("used_client_seeds", [INPUT_SEED_1, INPUT_SEED_2])
def test_request_random_data_fail_seed_already_exist_for_sender(vrf_provider_1, used_client_seeds):
    for client_seed in used_client_seeds:
        with brownie.reverts("VRFProviderBase: Seed already existed for this sender"):
            vrf_provider_1.requestRandomData(client_seed, {"from": accounts[1], "value": FEE_1E15})


def test_relay_proof_success(vrf_provider_1, testnet_vrf_proof):
    assert (
        vrf_provider_1.oracleScriptID(),
        vrf_provider_1.minCount(),
        vrf_provider_1.askCount(),
        vrf_provider_1.minimumFee()
    ) == PROVIDER_CONFIG_2.to_tuple()

    # set back the parameters
    for call, param in zip((
            vrf_provider_1.setOracleScriptID,
            vrf_provider_1.setMinCount,
            vrf_provider_1.setAskCount,
            vrf_provider_1.setMinimumFee
    ), PROVIDER_CONFIG_1.to_tuple()):
        tx = call(param, {"from": accounts[0]})
        assert tx.status == 1

    assert (
        vrf_provider_1.oracleScriptID(),
        vrf_provider_1.minCount(),
        vrf_provider_1.askCount(),
        vrf_provider_1.minimumFee()
    ) == PROVIDER_CONFIG_1.to_tuple()

    nonce = 0

    # before relay balance
    account2_prev_balance = accounts[2].balance()

    tx = vrf_provider_1.relayProof(testnet_vrf_proof, nonce, {"from": accounts[2]})
    assert tx.status == 1

    task = vrf_provider_1.tasks(nonce)

    assert task == MockTask(
        True,
        MOCK_TIMESTAMP,
        accounts[1].address,
        FEE_1E15,
        vrf_provider_1.getSeed(MOCK_TIMESTAMP, accounts[1], MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, INPUT_SEED_1[0]),
        INPUT_SEED_1[0],
        EXPECTED_PROOF_1,
        EXPECTED_RESULT_1,
    ).to_tuple()

    # the balance after relaying
    # the relayer must receive the fee
    assert accounts[2].balance() == account2_prev_balance + FEE_1E15


def test_vrf_request_relay_consume_fail_task_already_resolved(vrf_provider_1, testnet_vrf_proof):
    with brownie.reverts("VRFProviderBase: Task already resolved"):
        nonce = 0
        vrf_provider_1.relayProof(testnet_vrf_proof, nonce, {"from": accounts[2]})


@pytest.mark.parametrize("client_seed", INPUT_SEED_2)
def test_request_random_data_2(vrf_provider_1, client_seed):
    nonce = 2
    caller = accounts[2]

    assert vrf_provider_1.minCount() == PROVIDER_CONFIG_1.min_count
    assert vrf_provider_1.askCount() == PROVIDER_CONFIG_1.ask_count
    vrf_provider_1.setMinCount(PROVIDER_CONFIG_2.min_count, {"from": accounts[0]})
    vrf_provider_1.setAskCount(PROVIDER_CONFIG_2.ask_count, {"from": accounts[0]})

    task = vrf_provider_1.tasks(nonce)
    assert task == MockTask().to_tuple()

    tx = vrf_provider_1.requestRandomData(client_seed, {"from": accounts[2], "value": FEE_1E15})
    assert tx.status == 1

    seed = vrf_provider_1.getSeed(MOCK_TIMESTAMP, caller, MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed)

    events = dict(tx.events["RandomDataRequested"][0])
    assert events["nonce"] == nonce
    assert events["caller"] == caller
    assert events["clientSeed"] == client_seed
    assert events["time"] == MOCK_TIMESTAMP
    assert events["blockHash"] == MOCK_BLOCK_HASH
    assert events["taskFee"] == FEE_1E15
    assert events["seed"] == seed

    task = vrf_provider_1.tasks(nonce)
    assert task == MockTask(False, MOCK_TIMESTAMP, caller, FEE_1E15, seed, client_seed).to_tuple()
    assert vrf_provider_1.balance() == FEE_1E15 + FEE_1E16
    assert vrf_provider_1.taskNonce() == nonce + 1


def test_relay_proof_min_count_not_match(vrf_provider_1, testnet_vrf_proof_2_16_min_count_not_match):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    nonce = 2
    with brownie.reverts("VRFProviderBase: Min Count not match"):
        vrf_provider_1.relayProof(testnet_vrf_proof_2_16_min_count_not_match, nonce, {"from": accounts[2]})


def test_relay_proof_ask_count_not_match(vrf_provider_1, testnet_vrf_proof_1_15_ask_count_not_match):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    nonce = 2
    with brownie.reverts("VRFProviderBase: Ask Count not match"):
        vrf_provider_1.relayProof(testnet_vrf_proof_1_15_ask_count_not_match, nonce, {"from": accounts[2]})


def test_relay_proof_incorrect_worker(vrf_provider_1, testnet_vrf_proof_1_16_incorrect_worker):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    nonce = 2
    with brownie.reverts("VRFProviderBase: The sender must be the task worker"):
        vrf_provider_1.relayProof(testnet_vrf_proof_1_16_incorrect_worker, nonce, {"from": accounts[2]})


def test_relay_proof_incorrect_os_id(vrf_provider_1, testnet_vrf_proof_1_16_incorrect_os_id):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    nonce = 2
    with brownie.reverts("VRFProviderBase: Oracle Script ID not match"):
        vrf_provider_1.relayProof(testnet_vrf_proof_1_16_incorrect_os_id, nonce, {"from": accounts[2]})


def test_relay_proof_not_successfully_resolved(vrf_provider_1, testnet_vrf_proof_1_16_not_successfully_resolved):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    nonce = 2
    with brownie.reverts("VRFProviderBase: Request not successfully resolved"):
        vrf_provider_1.relayProof(testnet_vrf_proof_1_16_not_successfully_resolved, nonce, {"from": accounts[2]})


def test_relay_proof_seed_mismatch(vrf_provider_1, testnet_vrf_proof_1_16_seed_mismatch):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    nonce = 2
    with brownie.reverts("VRFProviderBase: Seed is mismatched"):
        vrf_provider_1.relayProof(testnet_vrf_proof_1_16_seed_mismatch, nonce, {"from": accounts[2]})


def test_relay_proof_time_mismatch(vrf_provider_1, testnet_vrf_proof_1_16_time_mismatch):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    nonce = 2
    with brownie.reverts("VRFProviderBase: Time is mismatched"):
        vrf_provider_1.relayProof(testnet_vrf_proof_1_16_time_mismatch, nonce, {"from": accounts[2]})


def test_relay_proof_task_not_found(vrf_provider_1, testnet_vrf_proof_1_16):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    # invalid nonce
    nonce = 3
    with brownie.reverts("VRFProviderBase: Task not found"):
        vrf_provider_1.relayProof(testnet_vrf_proof_1_16, nonce, {"from": accounts[2]})


def test_relay_proof_not_enough_power(vrf_provider_1, bridge_1, bridge_2, testnet_vrf_proof_1_16):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    # change bridge to bridge_2
    vrf_provider_1.setBridge(bridge_2.address, {"from": accounts[0]})

    nonce = 2
    with brownie.reverts("RELAY_BLOCK_FAILED"):
        vrf_provider_1.relayProof(testnet_vrf_proof_1_16, nonce, {"from": accounts[2]})

    # change back bridge_1
    vrf_provider_1.setBridge(bridge_1.address, {"from": accounts[0]})


@pytest.mark.parametrize("client_seed", INPUT_SEED_2)
def test_relay_proof_1_16_success(vrf_provider_1, testnet_vrf_proof_1_16, client_seed):
    assert (
        vrf_provider_1.minCount(), vrf_provider_1.askCount()
    ) == (
        PROVIDER_CONFIG_2.min_count, PROVIDER_CONFIG_2.ask_count
    )

    # before relay balance
    account2_prev_balance = accounts[2].balance()

    nonce = 2

    tx = vrf_provider_1.relayProof(testnet_vrf_proof_1_16, nonce, {"from": accounts[2]})
    assert tx.status == 1
    assert vrf_provider_1.tasks(nonce) == MockTask(
        True,
        MOCK_TIMESTAMP,
        accounts[2].address,
        FEE_1E15,
        vrf_provider_1.getSeed(MOCK_TIMESTAMP, accounts[2], MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed),
        INPUT_SEED_2[0],
        EXPECTED_PROOF_2,
        EXPECTED_RESULT_2,
    ).to_tuple()

    # the balance after relaying
    # the relayer must receive the fee
    assert accounts[2].balance() == account2_prev_balance + FEE_1E15
