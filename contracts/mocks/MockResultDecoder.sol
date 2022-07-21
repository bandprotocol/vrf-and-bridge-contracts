// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import "../obi/Obi.sol";

library MockResultDecoder {
    using Obi for Obi.Data;

    struct Result {
        string symbol;
        uint64 multiplier;
        uint8 what;
    }

    function decodeResult(bytes memory _data)
        internal
        pure
        returns (Result memory result)
    {
        Obi.Data memory decoder = Obi.from(_data);
        result.symbol = string(decoder.decodeBytes());
        result.multiplier = decoder.decodeU64();
        result.what = decoder.decodeU8();
        require(decoder.finished(), "DATA_DECODE_NOT_FINISHED");
    }
}
