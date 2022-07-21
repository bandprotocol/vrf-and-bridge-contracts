// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {IBridge} from "../../interfaces/bridge/IBridge.sol";
import {ResultCodec} from "../bridge/library/ResultCodec.sol";

contract MockResultCodec {
    function encode(IBridge.Result memory _res)
        public
        pure
        returns (bytes memory)
    {
        return ResultCodec.encode(_res);
    }
}
