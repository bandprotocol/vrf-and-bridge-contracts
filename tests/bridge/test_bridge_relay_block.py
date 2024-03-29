import brownie


def test_bridge_relayBlock_insufficient_validator(bridge_with_minimal_validators):
    with brownie.reverts("INSUFFICIENT_VALIDATOR_SIGNATURES"):
        bridge_with_minimal_validators.relayBlock(
            [
                "0x59188F8A2B866DE5E1703DFD148A7C6D9A4A68209B707C5C92985219D1461832",
                "0x6233CC684B6F6562575C7031E30E8763F54DFF765637FD2AA1FD3CBC33CB4636",
                "0x2A723363A0213CF0BDAE15ABFF9D350803D8D9C7DF1F4016E4A1A3E40644B01D",
                "0xE00B143C946C1B1EB4854970C4B959C71CC9D966A26C73DC022365266E841678",
                "0x4062B683A35480084E214536EB7786AC91D70B2F058E88E87FEDDBAB53786E78",
                "0x0ABD414B7B9290D0075CD683B8DBED0C6B7E5D1162338FB8828B00E32E3C5F02",
            ],
            [
                "0x327BB8E7C548CDA20A3F9330131E658F4BCB5BE238F5EE94D79FD5019E3F7559",  # versionAndChainIdHash
                13134348,  # height
                1673424387,  # timeSecond
                945622137,  # timeNanoSecond
                "0xBD9E2B4E29E24E7089AE44521C03F43DACE0E94D32437130EE5AAA094D501D53",  # lastBlockIDAndOther
                "0xA68E9D00675E0B49185C965860A888185B57249923C8B2397033C05C23E2A878",  # nextValidatorHashAndConsensusHash
                "0x6C77405C1B4C8229D8197895A009D42DB0D2F1D834029C47C71EB78574D8B524",  # lastResultsHash
                "0x8BFFF44CBE70909971A6E58601ABFA2904E22BEA73FACCC9EE17EA556D20F128",  # evidenceAndProposerHash
            ],
            [
                "0x0802110C6AC8000000000022480A20",
                "0x12240801122054F5D98B1E5770CA5138BEF8487A52FB919B657833921782AE862087001A3ADA",
            ],
            [
                [
                    "0x0a3322eacdcc9ed3cce50f5d5ed4563c9861b7b7addc1424584056eca5c066fa",
                    "0x191cb3ef7640cd82726189e3f1f18617475d5baeeffb3ffcb4afa2bc7a981b08",
                    28,
                    "0x0886DCF99D0610AFF88CE201",
                ]
            ],
        )


def test_bridge_relayBlock_invalid_signature_order(bridge_with_minimal_validators):
    with brownie.reverts("INVALID_SIGNATURE_SIGNER_ORDER"):
        bridge_with_minimal_validators.relayBlock(
            [
                "0x59188F8A2B866DE5E1703DFD148A7C6D9A4A68209B707C5C92985219D1461832",
                "0x6233CC684B6F6562575C7031E30E8763F54DFF765637FD2AA1FD3CBC33CB4636",
                "0x2A723363A0213CF0BDAE15ABFF9D350803D8D9C7DF1F4016E4A1A3E40644B01D",
                "0xE00B143C946C1B1EB4854970C4B959C71CC9D966A26C73DC022365266E841678",
                "0x4062B683A35480084E214536EB7786AC91D70B2F058E88E87FEDDBAB53786E78",
                "0x0ABD414B7B9290D0075CD683B8DBED0C6B7E5D1162338FB8828B00E32E3C5F02",
            ],
            [
                "0x327BB8E7C548CDA20A3F9330131E658F4BCB5BE238F5EE94D79FD5019E3F7559",  # versionAndChainIdHash
                13134348,  # height
                1673424387,  # timeSecond
                945622137,  # timeNanoSecond
                "0xBD9E2B4E29E24E7089AE44521C03F43DACE0E94D32437130EE5AAA094D501D53",  # lastBlockIDAndOther
                "0xA68E9D00675E0B49185C965860A888185B57249923C8B2397033C05C23E2A878",
                # nextValidatorHashAndConsensusHash
                "0x6C77405C1B4C8229D8197895A009D42DB0D2F1D834029C47C71EB78574D8B524",  # lastResultsHash
                "0x8BFFF44CBE70909971A6E58601ABFA2904E22BEA73FACCC9EE17EA556D20F128",  # evidenceAndProposerHash
            ],
            [
                "0x0802110C6AC8000000000022480A20",
                "0x12240801122054F5D98B1E5770CA5138BEF8487A52FB919B657833921782AE862087001A3ADA",
            ],
            [
                [
                    "0x0a3322eacdcc9ed3cce50f5d5ed4563c9861b7b7addc1424584056eca5c066fa",
                    "0x191cb3ef7640cd82726189e3f1f18617475d5baeeffb3ffcb4afa2bc7a981b08",
                    28,
                    "0x0886DCF99D0610AFF88CE201",
                ],
                [
                    "0x94899AB6AE568AA58F56F8770BCD19A37B90D30EE76F5701299E947F55152C16",
                    "0x1F7125F5CA10488B5AF95F37424A08D31E2F7C54D7B37BB2AC6BB07CB923BC5D",
                    27,
                    "0x0886DCF99D061097A1C68102",
                ],
                [
                    "0x48B8C52A57CCD5D18F446D4A578888E40DB79918EAD341E05E6F6C95ABE42292",
                    "0x30443C08A23B546B878233D98FCF14099C60D560B06DA61B485B95413D8C41A8",
                    27,
                    "0x0886DCF99D0610D4A3C7EC01",
                ],
                [
                    "0x5CE60A59BEBE03A92E09CB9CEB20C2D9F7C4D31982CE4142E37E0CB26A13E439",
                    "0x2D53591979650FD4BF9B7224081802BC5C84622DEC32F47BB55738B2BE7766F6",
                    27,
                    "0x0886DCF99D06108E96A88102",
                ],
            ],
        )


def test_bridge_relayBlock_success(bridge_with_minimal_validators):
    bridge_with_minimal_validators.relayBlock(
        [
            "0x59188F8A2B866DE5E1703DFD148A7C6D9A4A68209B707C5C92985219D1461832",
            "0x6233CC684B6F6562575C7031E30E8763F54DFF765637FD2AA1FD3CBC33CB4636",
            "0x2A723363A0213CF0BDAE15ABFF9D350803D8D9C7DF1F4016E4A1A3E40644B01D",
            "0xE00B143C946C1B1EB4854970C4B959C71CC9D966A26C73DC022365266E841678",
            "0x4062B683A35480084E214536EB7786AC91D70B2F058E88E87FEDDBAB53786E78",
            "0x0ABD414B7B9290D0075CD683B8DBED0C6B7E5D1162338FB8828B00E32E3C5F02",
        ],
        [
            "0x327BB8E7C548CDA20A3F9330131E658F4BCB5BE238F5EE94D79FD5019E3F7559",  # versionAndChainIdHash
            13134348,  # height
            1673424387,  # timeSecond
            945622137,  # timeNanoSecond
            "0xBD9E2B4E29E24E7089AE44521C03F43DACE0E94D32437130EE5AAA094D501D53",  # lastBlockIDAndOther
            "0xA68E9D00675E0B49185C965860A888185B57249923C8B2397033C05C23E2A878",  # nextValidatorHashAndConsensusHash
            "0x6C77405C1B4C8229D8197895A009D42DB0D2F1D834029C47C71EB78574D8B524",  # lastResultsHash
            "0x8BFFF44CBE70909971A6E58601ABFA2904E22BEA73FACCC9EE17EA556D20F128",  # evidenceAndProposerHash
        ],
        [
            "0x0802110C6AC8000000000022480A20",
            "0x12240801122054F5D98B1E5770CA5138BEF8487A52FB919B657833921782AE862087001A3ADA",
        ],
        [
            [
                "0x0a3322eacdcc9ed3cce50f5d5ed4563c9861b7b7addc1424584056eca5c066fa",
                "0x191cb3ef7640cd82726189e3f1f18617475d5baeeffb3ffcb4afa2bc7a981b08",
                28,
                "0x0886DCF99D0610AFF88CE201",
            ],
            [
                "0x94899AB6AE568AA58F56F8770BCD19A37B90D30EE76F5701299E947F55152C16",
                "0x1F7125F5CA10488B5AF95F37424A08D31E2F7C54D7B37BB2AC6BB07CB923BC5D",
                27,
                "0x0886DCF99D061097A1C68102",
            ],
            [
                "0x5CE60A59BEBE03A92E09CB9CEB20C2D9F7C4D31982CE4142E37E0CB26A13E439",
                "0x2D53591979650FD4BF9B7224081802BC5C84622DEC32F47BB55738B2BE7766F6",
                27,
                "0x0886DCF99D06108E96A88102",
            ],
            [
                "0x48B8C52A57CCD5D18F446D4A578888E40DB79918EAD341E05E6F6C95ABE42292",
                "0x30443C08A23B546B878233D98FCF14099C60D560B06DA61B485B95413D8C41A8",
                27,
                "0x0886DCF99D0610D4A3C7EC01",
            ],
        ],
    )
