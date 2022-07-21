// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {Obi} from "../obi/Obi.sol";
import {MockResultDecoder} from "./MockResultDecoder.sol";

contract MockObiUser {
    using MockResultDecoder for bytes;

    function decode(bytes memory data)
        public
        pure
        returns (MockResultDecoder.Result memory)
    {
        return data.decodeResult();
    }
}
