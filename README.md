<div align="center">
  <h1>
    VRF And Bridge Contracts
  </h1>
<p>
<strong>Bring more use-cases to blockchains beyond DeFi</strong>

![Solidity](https://img.shields.io/badge/language-solidity-orange.svg?longCache=true&style=popout-square)
![Ethereum](https://img.shields.io/badge/platform-Ethereum-blue.svg?longCache=true&style=popout-square)
![Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green.svg?longCache=true&style=popout-square)
</p>
</div>

[Band Protocol](https://bandprotocol.com) is a decentralized oracle protocol.
This repository contains the implementation of Band's [Bridge](./contracts/bridge/) and [VRF](./contracts/vrf/) contracts with [Solidity](https://en.wikipedia.org/wiki/Solidity). 

## Overview

The Bridge is a smart contract that introduces Band Protocol's flexible oracle design, which allows consumers to use any data, including real-world events, sports, weather, random numbers, and more.
In addition, anyone can create a custom-made OracleScript on Bandchain like a smart contract using WebAssembly to produce the oracle result that suits their specific need. also allows the connection between Bandchain and other chains to be more decentralized because anyone can relay the oracle result produced on Bandchain to other chains safely and permissionless.

The VRF provider can be viewed as one of the Bridge's direct users. It is a contract that connects to verifiable random data consumers and Bridge to help collect requests from the consumers and resolve all those requests. To resolve a request, the VRF provider needs to retrieve a Merkle proof from Bandchain and then pass it to the Bridge to make use that the data is usable.

## More details
- 👉 [Bridge](./contracts/bridge/)
- 👉 [VRF](./contracts/vrf/)

## Installation

```shell=
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

## Testing

```shell=
brownie build

brownie test tests/bridge
brownie test tests/vrf
```
