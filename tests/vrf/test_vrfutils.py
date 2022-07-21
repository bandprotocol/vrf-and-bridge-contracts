import pytest
import brownie
from brownie import accounts, Bridge
from conftest import MockTask

MOCK_TIMESTAMP = 1655972425
MOCK_BLOCK_HASH = "0xdefbfd2812ce28404dc436710582118cfa12cd4c0fa3694323209f012ca36243"
MOCK_CHAIN_ID = 112


def test_vrf_lens_query(vrf_lens, vrf_provider_1):
    assert vrf_lens.provider() == vrf_provider_1.address
    assert vrf_lens.getProviderConfig() == (
        vrf_provider_1.oracleScriptID(), vrf_provider_1.minCount(), vrf_provider_1.askCount()
    )
    assert vrf_lens.getTasksBulk([0, 1, 2]) == (
        MockTask().to_tuple(),
        MockTask().to_tuple(),
        MockTask().to_tuple(),
    )

    nonces = [0, 1, 2]
    client_seeds = ["mock_client_seed_1", "mock_client_seed_2", "mock_client_seed_3"]
    seeds = [
        vrf_provider_1.getSeed(MOCK_TIMESTAMP, accounts[1], MOCK_BLOCK_HASH, MOCK_CHAIN_ID, n, cs)
        for n, cs in zip(nonces, client_seeds)
    ]

    zip_envs = list(zip(nonces, client_seeds, seeds))
    expected_tasks = [MockTask().to_tuple() for _ in range(6)]

    for i in range(len(zip_envs)):
        n, cs, s = zip_envs[i]
        expected_tasks[i] = MockTask(False, MOCK_TIMESTAMP, accounts[1], 10**15, s, cs).to_tuple()

        tx = vrf_provider_1.requestRandomData(cs, {"from": accounts[1], "value": 10**15})
        assert tx.status == 1

        assert vrf_lens.getTasksBulk([0, 1, 2, 3, 4, 5]) == tuple(expected_tasks)
