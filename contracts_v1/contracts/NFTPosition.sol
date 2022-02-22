// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./base64.sol";

contract NFTPosition is ERC721URIStorage, Ownable {
    address public governorAddress;

    constructor() ERC721("Freezer", "Freezer") {}

    // Modifier
    modifier onlyGovernor() {
        require(msg.sender == governorAddress, "Only Factory can call");
        _;
    }

    function setOnlyGovernor(address _governorAddress) external onlyOwner {
        governorAddress = _governorAddress;
    }

    function mint(
        address _to,
        uint256 _tokenId,
        uint256 _amountLocked,
        uint256 _lockingDate,
        uint256 _maturityDate
    ) external onlyGovernor {
        _mint(_to, _tokenId);
        (uint256 y1, uint256 m1, uint256 d1) = timestampToDate(_lockingDate);
        (uint256 y2, uint256 m2, uint256 d2) = timestampToDate(_maturityDate);

        string memory imageURI = svgToImageURI(
            uint2str(_amountLocked),
            uint2str(y1),
            uint2str(m1),
            uint2str(d1),
            uint2str(y2),
            uint2str(m2),
            uint2str(d2)
        );
        _setTokenURI(_tokenId, formatTokenURI(imageURI));
    }

    function burn(uint256 _tokenId) external onlyGovernor {
        _burn(_tokenId);
    }

    // Internal functions for generating NFT

    function svgToImageURI(
        string memory _amountLocked,
        string memory _y1,
        string memory _m1,
        string memory _d1,
        string memory _y2,
        string memory _m2,
        string memory _d2
    ) internal pure returns (string memory) {
        string memory baseURL = "data:image/svg+xml;base64,";
        string memory svgBase64Encoded = Base64.encode(bytes(generateSVG()));

        return string(abi.encodePacked(baseURL, svgBase64Encoded));
    }

    function generateSVG() private pure returns (string memory svg) {
        return string(
            abi.encodePacked(
                '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 400 500"><defs>',
                "<style>      .cls-1{fill:#1d1d3f;}.cls-2,.cls-3,.cls-4{fill:none;stroke-miterlimit:10;stroke-width:3px;}.cls-2{stroke:url(#linear-gradient);}.cls-3{stroke:url(#linear-gradient-2);}.cls-4{stroke:url(#linear-gradient-3);}.cls-5{font-size:94.4px;}.cls-5,.cls-7{fill:#fff;font-family:Montserrat-SemiBold, Montserrat;font-weight:600;}.cls-6{fill:#00e6b5;}.cls-7{font-size:40px;}.cls-8{letter-spacing:-0.01em;}.cls-9{letter-spacing:0.01em;}.cls-10{letter-spacing:-0.01em;}.cls-11{letter-spacing:-0.05em;}.cls-12{letter-spacing:-0.01em;}.cls-13{letter-spacing:0.01em;}.cls-14{fill:#557dff;}.cls-15{fill:url(#linear-gradient-4);}.cls-16{fill:url(#linear-gradient-5);}    </style>",
                '<linearGradient id="linear-gradient" x1="25.17" y1="427.03" x2="376.83" y2="427.03" gradientTransform="translate(-226.03 628.03) rotate(-90)" gradientUnits="userSpaceOnUse">      <stop offset="0" stop-color="#00e6b5"/>      <stop offset="1" stop-color="#557dff"/>    </linearGradient>',
                '<linearGradient id="linear-gradient-2" x1="25.17" y1="194.98" x2="376.83" y2="194.98" gradientTransform="translate(6.02 395.98) rotate(-90)" xlink:href="#linear-gradient"/>',
                ' <linearGradient id="linear-gradient-3" x1="69" y1="400.44" x2="331" y2="400.44" gradientTransform="matrix(1, 0, 0, 1, 0, 0)" xlink:href="#linear-gradient"/>',
                '<linearGradient id="linear-gradient-5" x1="106.26" y1="434.52" x2="331.01" y2="434.52" gradientTransform="matrix(1, 0, 0, 1, 0, 0)" xlink:href="#linear-gradient"/>'
            ) // encode each line in encodePacked and base 64 is just done once
        );
    }

    function formatTokenURI(string memory imageURI)
        internal
        pure
        returns (string memory)
    {
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

    function _daysToDate(uint256 _days)
        internal
        pure
        returns (
            uint256 year,
            uint256 month,
            uint256 day
        )
    {
        int256 __days = int256(_days);

        int256 L = __days + 68569 + 2440588;
        int256 N = (4 * L) / 146097;
        L = L - (146097 * N + 3) / 4;
        int256 _year = (4000 * (L + 1)) / 1461001;
        L = L - (1461 * _year) / 4 + 31;
        int256 _month = (80 * L) / 2447;
        int256 _day = L - (2447 * _month) / 80;
        L = _month / 11;
        _month = _month + 2 - 12 * L;
        _year = 100 * (N - 49) + _year + L;

        year = uint256(_year);
        month = uint256(_month);
        day = uint256(_day);
    }

    function timestampToDate(uint256 timestamp)
        public
        pure
        returns (
            uint256,
            uint256,
            uint256
        )
    {
        (uint256 year, uint256 month, uint256 day) = _daysToDate(
            timestamp / 86400
        );
        return (year, month, day);
    }

    function uint2str(uint256 _i) internal pure returns (string memory) {
        if (_i == 0) {
            return "0";
        }
        uint256 j = _i;
        uint256 len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint256 k = len;
        while (_i != 0) {
            k = k - 1;
            uint8 temp = (48 + uint8(_i - (_i / 10) * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }
}
