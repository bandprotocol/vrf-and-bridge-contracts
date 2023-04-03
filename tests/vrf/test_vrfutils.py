from brownie import accounts


MOCK_TIMESTAMP = 1655972425
MOCK_BLOCK_HASH = "0xdefbfd2812ce28404dc436710582118cfa12cd4c0fa3694323209f012ca36243"
MOCK_CHAIN_ID = 112


def test_vrf_lens_query(vrf_lens, vrf_provider_1, default_task_v1):
    assert vrf_lens.provider() == vrf_provider_1.address
    assert vrf_lens.getProviderConfig() == (
        vrf_provider_1.oracleScriptID(),
        vrf_provider_1.minCount(),
        vrf_provider_1.askCount(),
    )
    assert vrf_lens.getTasksBulk([0, 1, 2]) == (
        default_task_v1,
        default_task_v1,
        default_task_v1,
    )

    nonces = [0, 1, 2]
    client_seeds = ["mock_client_seed_1", "mock_client_seed_2", "mock_client_seed_3"]
    seeds = [
        vrf_provider_1.getSeed(MOCK_TIMESTAMP, accounts[1], MOCK_BLOCK_HASH, MOCK_CHAIN_ID, n, cs)
        for n, cs in zip(nonces, client_seeds)
    ]

    zip_envs = list(zip(nonces, client_seeds, seeds))
    expected_tasks = [default_task_v1 for _ in range(6)]

    for i in range(len(zip_envs)):
        n, cs, s = zip_envs[i]
        expected_tasks[i] = (False, MOCK_TIMESTAMP, accounts[1], 10**15, s, cs, "0x", "0x")

        vrf_provider_1.requestRandomData(cs, {"from": accounts[1], "value": 10**15})

        assert vrf_lens.getTasksBulk([0, 1, 2, 3, 4, 5]) == tuple(expected_tasks)
