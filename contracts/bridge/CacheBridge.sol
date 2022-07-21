// // SPDX-License-Identifier: Apache-2.0

// pragma solidity ^0.6.0;
// pragma experimental ABIEncoderV2;

// import {Packets} from "./library/Packets.sol";
// import {Bridge} from "./Bridge.sol";
// import {ICacheBridge} from "../../interfaces/bridge/ICacheBridge.sol";
// import {IBridge} from "../../interfaces/bridge/IBridge.sol";

// /// @title BandChain CacheBridge
// /// @author Band Protocol Team
// contract CacheBridge is Bridge, ICacheBridge {
//     using Packets for IBridge.RequestPacket;

//     /// Mapping from hash of RequestPacket to the latest ResponsePacket.
//     mapping(bytes32 => ResponsePacket) public requestsCache;

//     /// Initializes an oracle bridge to BandChain by pass the argument to the parent contract (Bridge.sol).
//     /// @param validators The initial set of BandChain active validators.
//     constructor(ValidatorWithPower[] memory validators)
//         public
//         Bridge(validators)
//     {}

//     /// Returns the ResponsePacket for a given RequestPacket.
//     /// Reverts if can't find the related response in the mapping.
//     /// @param request A tuple that represents RequestPacket struct.
//     function getLatestResponse(RequestPacket memory request)
//         public
//         override
//         view
//         returns (ResponsePacket memory)
//     {
//         ResponsePacket memory res = requestsCache[request.getRequestKey()];
//         require(res.requestID != 0, "RESPONSE_NOT_FOUND");

//         return res;
//     }

//     /// Save the new ResponsePacket to the state by using hash of its associated RequestPacket,
//     /// provided that the saved ResponsePacket is newer than the one that was previously saved.
//     /// Reverts if the new ResponsePacket is not newer than the current one or not successfully resolved.
//     /// @param request A tuple that represents a RequestPacket struct that associated the new ResponsePacket.
//     /// @param response A tuple that represents a new ResponsePacket struct.
//     function _cacheResponse(
//         RequestPacket memory request,
//         ResponsePacket memory response
//     ) internal {
//         bytes32 requestKey = request.getRequestKey();

//         require(
//             response.resolveTime > requestsCache[requestKey].resolveTime,
//             "FAIL_LATEST_REQUEST_SHOULD_BE_NEWEST"
//         );

//         require(
//             response.resolveStatus == 1,
//             "FAIL_REQUEST_IS_NOT_SUCCESSFULLY_RESOLVED"
//         );

//         requestsCache[requestKey] = response;
//     }

//     /// Performs oracle state relay and oracle data verification in one go.
//     /// After that, the results will be recorded to the state by using the hash of RequestPacket as key.
//     /// @param data The encoded data for oracle state relay and data verification.
//     function relay(bytes calldata data) external override {
//         (RequestPacket memory request, ResponsePacket memory response) = this
//             .relayAndVerify(data);

//         _cacheResponse(request, response);
//     }

//     /// Performs oracle state relay and many times of oracle data verification in one go.
//     /// After that, the results which is an array of Packet will be recorded to the state by using the hash of RequestPacket as key.
//     /// @param data The encoded data for oracle state relay and an array of data verification.
//     function relayMulti(bytes calldata data) external override {
//         (
//             RequestPacket[] memory requests,
//             ResponsePacket[] memory responses
//         ) = this.relayAndMultiVerify(data);

//         for (uint256 i = 0; i < requests.length; i++) {
//             _cacheResponse(requests[i], responses[i]);
//         }
//     }
// }
