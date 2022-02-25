// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./base64.sol";
import "./utils.sol";

library NFTDescriptor {
    struct paramsTokenURI {
        uint256 amountLocked;
        string y1;
        string m1;
        string d1;
        string y2;
        string m2;
        string d2;
    }

    function _constructTokenURI(
        uint256 _amountLocked,
        uint256 _lockingDate,
        uint256 _maturityDate
    ) internal pure returns (string memory) {
        paramsTokenURI memory params = _constructParamsTokenURI(
            _amountLocked,
            _lockingDate,
            _maturityDate
        );

        string memory imageURI = generateSVG(params);
        return
            string(
                abi.encodePacked(
                    "data:application/json;base64,",
                    Base64.encode(
                        bytes(
                            abi.encodePacked(
                                '{"name":"',
                                "DeepFreeze NFT",
                                '", "description":"This NFT represent a locked position in DeepFreeze protocol", "image":"',
                                imageURI,
                                '"}'
                            )
                        )
                    )
                )
            );
    }

    function _constructParamsTokenURI(
        uint256 _amountLocked,
        uint256 _lockingDate,
        uint256 _maturityDate // here maybe get the tokenID that will query ?
    ) internal pure returns (paramsTokenURI memory) {
        (uint256 y1, uint256 m1, uint256 d1) = Utils.timestampToDate(
            _lockingDate
        );
        (uint256 y2, uint256 m2, uint256 d2) = Utils.timestampToDate(
            _maturityDate
        );
        return
            paramsTokenURI({
                amountLocked: _amountLocked,
                y1: Utils.uint2str(y1),
                m1: Utils.uint2str(m1),
                d1: Utils.uint2str(d1),
                y2: Utils.uint2str(y2),
                m2: Utils.uint2str(m2),
                d2: Utils.uint2str(d2)
            });
    }

    function generateSVG(paramsTokenURI memory _params)
        internal
        pure
        returns (string memory svg)
    {
        return
            string(
                abi.encodePacked(
                    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 400 500">'
                )
            );
    }
}
