import pytest
import brownie
from brownie import accounts

INPUT_SEED = [("mumu1")]
FEE_1E14 = 10**14
FEE_1E15 = FEE_1E14 * 10
FEE_1E16 = FEE_1E15 * 10
MOCK_TIMESTAMP = 1655972425
MOCK_BLOCK_HASH = "0xdefbfd2812ce28404dc436710582118cfa12cd4c0fa3694323209f012ca36243"
MOCK_CHAIN_ID = 112
EXPECTED_RESULT_HASH = "0x8e8ffefac10eeb82bce4eb01e4b052936e86ee1d62f30f0b936976e41eaf1483"


@pytest.mark.parametrize("client_seed", INPUT_SEED)
def test_vrf_request_by_consumer(vrf_provider_1, mock_vrf_consumer, client_seed, default_task_v1):
    nonce = 0
    caller = mock_vrf_consumer.address

    # before request
    task = vrf_provider_1.tasks(nonce)
    assert task == default_task_v1

    mock_vrf_consumer.requestRandomDataFromProvider(client_seed, {"from": accounts[1], "value": FEE_1E14})

    seed = vrf_provider_1.getSeed(MOCK_TIMESTAMP, caller, MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed)

    # after request
    task = vrf_provider_1.tasks(nonce)
    assert task == (False, MOCK_TIMESTAMP, caller, FEE_1E14, seed, client_seed, "0x", "0x")


def test_consume_fail_not_the_provider(mock_vrf_consumer):
    fake_result = "a" * 64
    with brownie.reverts("VRFConsumerBaseStaticProvider: The sender is not the provider"):
        mock_vrf_consumer.consume(INPUT_SEED[0], MOCK_TIMESTAMP, fake_result, {"from": accounts[1]})


def test_vrf_request_relay_consume_success(vrf_provider_1, mock_vrf_consumer, testnet_vrf_proof_for_consumer):
    assert mock_vrf_consumer.latestSeed() == ""
    assert mock_vrf_consumer.latestTime() == 0
    assert mock_vrf_consumer.latestResult() == "0x00"

    nonce = 0
    account2_prev_balance = accounts[2].balance()
    vrf_provider_1.relayProof(testnet_vrf_proof_for_consumer, nonce, {"from": accounts[2]})

    # relayer must receive the fee
    assert accounts[2].balance() == account2_prev_balance + FEE_1E14

    assert mock_vrf_consumer.latestSeed() == INPUT_SEED[0]
    assert mock_vrf_consumer.latestTime() == MOCK_TIMESTAMP
    assert mock_vrf_consumer.latestResult() == EXPECTED_RESULT_HASH


@pytest.mark.parametrize("client_seed", INPUT_SEED)
def test_vrf_request_by_consumer_reentrant(
    vrf_provider_1, mock_vrf_consumer_reentrant, client_seed, testnet_vrf_proof_for_consumer_reentrant, default_task_v1
):
    nonce = 1
    caller = mock_vrf_consumer_reentrant.address

    # before request
    task = vrf_provider_1.tasks(nonce)
    assert task == default_task_v1

    mock_vrf_consumer_reentrant.requestRandomDataFromProvider(client_seed, {"from": accounts[1], "value": FEE_1E14})

    seed = vrf_provider_1.getSeed(MOCK_TIMESTAMP, caller, MOCK_BLOCK_HASH, MOCK_CHAIN_ID, nonce, client_seed)

    # after request
    task = vrf_provider_1.tasks(nonce)
    assert task == (False, MOCK_TIMESTAMP, caller, FEE_1E14, seed, client_seed, "0x", "0x")

    # prepare for reentrancy
    mock_vrf_consumer_reentrant.saveProofAndNonce(
        testnet_vrf_proof_for_consumer_reentrant, nonce, {"from": accounts[0]}
    )

    assert not mock_vrf_consumer_reentrant.reentrantFlag()

    with brownie.reverts("ReentrancyGuard: reentrant call"):
        mock_vrf_consumer_reentrant.relayProofReentrant({"from": accounts[0]})

    tx = mock_vrf_consumer_reentrant.flipReentrantFlag({"from": accounts[0]})

    assert dict(tx.events["FlipReentrantFlag"][0])["currentReentrantFlag"] is True
    assert mock_vrf_consumer_reentrant.reentrantFlag() is True

    with brownie.reverts("ReentrancyGuard: reentrant call"):
        mock_vrf_consumer_reentrant.relayProofReentrant({"from": accounts[0]})
