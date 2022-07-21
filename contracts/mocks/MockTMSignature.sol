// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {TMSignature} from "../bridge/library/TMSignature.sol";

contract MockTMSignature {
    function checkTimeAndRecoverSigner(
        TMSignature.Data memory _data,
        bytes memory _commonEncodedPart,
        bytes memory _encodedChainID
    )
        public
        pure
        returns (address)
    {
        return TMSignature.checkTimeAndRecoverSigner(_data, _commonEncodedPart, _encodedChainID);
    }
}
