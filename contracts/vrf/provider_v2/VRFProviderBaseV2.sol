// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Address} from "@openzeppelin/contracts/utils/Address.sol";
import {IBridge} from "../../../interfaces/bridge/IBridge.sol";
import {IVRFProvider} from "../../../interfaces/vrf/IVRFProvider.sol";
import {IVRFConsumer} from "../../../interfaces/vrf/IVRFConsumer.sol";
import {VRFDecoderV2} from "./VRFDecoderV2.sol";

/// @title VRFProvider contract
/// @notice Contract for working with BandChain's verifiable random function feature
abstract contract VRFProviderBaseV2 is IVRFProvider, Ownable, ReentrancyGuard {
    using VRFDecoderV2 for bytes;
    using Address for address;

    IBridge public bridge;
    uint64 public oracleScriptID;
    uint64 public taskNonce;
    uint256 public minimumFee;

    // Mapping that enforces the client to provide a unique seed for each request
    mapping(address => mapping(string => bool)) public hasClientSeed;
    // Mapping from nonce => task
    mapping(uint64 => Task) public tasks;

    event RandomDataRequested(
        uint64 time,
        uint64 nonce,
        address indexed caller,
        bytes32 blockHash,
        bytes32 seed,
        uint256 chainID,
        uint256 taskFee,
        string clientSeed
    );
    event RandomDataRelayed(
        uint64 time,
        uint64 bandRequestID,
        address indexed to,
        bytes32 resultHash,
        bytes32 seed,
        string clientSeed
    );
    event SetBridge(address indexed newBridge);
    event SetOracleScriptID(uint64 newOID);
    event SetMinimumFee(uint256 newMinimumFee);

    struct Task {
        bool isResolved;
        uint64 time;
        address caller;
        uint256 taskFee;
        bytes32 seed;
        bytes32 result;
        string clientSeed;
    }

    constructor(uint64 _oracleScriptID, IBridge _bridge, uint256 _minimumFee) {
        bridge = _bridge;
        oracleScriptID = _oracleScriptID;
        minimumFee = _minimumFee;

        emit SetBridge(address(_bridge));
        emit SetOracleScriptID(_oracleScriptID);
        emit SetMinimumFee(_minimumFee);
    }

    function getBlockTime() public view virtual returns (uint64) {
        return uint64(block.timestamp);
    }

    function getBlockLatestHash() public view virtual returns (bytes32) {
        return blockhash(block.number - 1);
    }

    function getChainID() public view virtual returns(uint256 id) {
        assembly {
            id := chainid()
        }
    }

    function getSeed(
        uint64 _time,
        address _caller,
        bytes32 _blockHash,
        uint256 _chainID,
        uint256 _nonce,
        string memory _clientSeed
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(_time, _caller, _blockHash, _chainID, _nonce, _clientSeed));
    }

    function setBridge(IBridge _bridge) external onlyOwner {
        bridge = _bridge;
        emit SetBridge(address(_bridge));
    }

    function setOracleScriptID(uint64 _oracleScriptID) external onlyOwner {
        oracleScriptID = _oracleScriptID;
        emit SetOracleScriptID(_oracleScriptID);
    }

    function setMinimumFee(uint256 _minimumFee) external onlyOwner {
        minimumFee = _minimumFee;
        emit SetMinimumFee(_minimumFee);
    }

    function requestRandomData(string calldata _clientSeed)
        external
        payable
        override
        nonReentrant
    {
        require(
            !hasClientSeed[msg.sender][_clientSeed],
            "VRFProviderBase: Seed already existed for this sender"
        );

        uint64 time = getBlockTime();
        uint64 currentTaskNonce = taskNonce;
        bytes32 blockHash = getBlockLatestHash();
        uint256 chainID = getChainID();
        bytes32 seed = getSeed(time, msg.sender, blockHash, chainID, currentTaskNonce, _clientSeed);

        require(msg.value >= minimumFee, "VRFProviderBase: Task fee is lower than the minimum fee");

        // Initiate a new task
        tasks[currentTaskNonce].time = time;
        tasks[currentTaskNonce].caller = msg.sender;
        tasks[currentTaskNonce].seed = seed;
        tasks[currentTaskNonce].taskFee = msg.value;
        tasks[currentTaskNonce].clientSeed = _clientSeed;

        emit RandomDataRequested(
            time,
            currentTaskNonce,
            msg.sender,
            blockHash,
            seed,
            chainID,
            msg.value,
            _clientSeed
        );

        hasClientSeed[msg.sender][_clientSeed] = true;
        taskNonce = currentTaskNonce + 1;
    }

    function relayProof(bytes calldata _proof, uint64 _taskNonce) external nonReentrant {
        // create a local var to save cost
        Task memory _task = tasks[_taskNonce];

        // Check the validity of the task
        require(_task.caller != address(0), "VRFProviderBase: Task not found");
        require(!_task.isResolved, "VRFProviderBase: Task already resolved");

        // Verify proof using Bridge and extract the result
        IBridge.Result memory res = bridge.verifyOracleResult(_proof);

        // check oracle script id, min count, ask count
        require(
            res.oracleScriptID == oracleScriptID,
            "VRFProviderBase: Oracle Script ID not match"
        );

        // Check that the request on Band was successfully resolved
        require(
            res.resolveStatus == IBridge.ResolveStatus.RESOLVE_STATUS_SUCCESS,
            "VRFProviderBase: Request not successfully resolved"
        );

        // Check if sender is a worker
        VRFDecoderV2.Params memory params = res.params.decodeParams();
        require(msg.sender == params.taskWorker, "VRFProviderBase: The sender must be the task worker");
        require(_task.seed == params.seed, "VRFProviderBase: Seed is mismatched");
        require(_task.time == params.time, "VRFProviderBase: Time is mismatched");

        // Extract the task's result
        bytes32 result = res.result.decodeResult();

        // Save update the storage task
        tasks[_taskNonce].isResolved = true;
        tasks[_taskNonce].result = result;

        emit RandomDataRelayed(
            _task.time,
            res.requestID,
            _task.caller,
            result,
            params.seed,
            _task.clientSeed
        );

        // End function by call consume function on VRF consumer with data from BandChain
        if (_task.caller.isContract()) {
            IVRFConsumer(_task.caller).consume(
                _task.clientSeed,
                _task.time,
                result
            );
        }

        // Pay fee to the worker
        msg.sender.call{value: _task.taskFee}("");
    }
}
