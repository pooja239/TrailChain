/*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
* http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

'use strict';

const Dictionary = 'abcdefghijklmnopqrstuvwxyz';
const DictionaryNum = '0123456789';
const Web3 = require("web3");

/**
 * Class for managing simple account states.
 */
class SimpleState {

    /**
     * Initializes the instance.
     */
    constructor(workerIndex, marketplace, ratio, trackerAddress, payment, trails = 0) {
        this.accountPrefix = this._get26Num(workerIndex);
        this.Marketplace = marketplace;
        this.ratio = ratio;
        this.trackerScAddress = trackerAddress;
        this.paymentAmount = payment;
        this.trailGenerated = trails;
    }

    /**
     * Generate string by picking characters from the dictionary variable.
     * @param {number} number Character to select.
     * @returns {string} string Generated string based on the input number.
     * @private
     */
    _get26Num(number){
        let result = '';
        while(number > 0) {
            result += Dictionary.charAt(number % Dictionary.length);
            number = parseInt(number / Dictionary.length);
        }
        return result;
    }

    _get10Num(number){
        let result = '';
        while(number > 0) {
            result += DictionaryNum.charAt(number % DictionaryNum.length);
            number = parseInt(number / DictionaryNum.length);
        }

        return result;
    }
    
    /**
     * Construct an account key from its index.
     * @param {number} index The account index.
     * @return {string} The account key.
     * @private
     */
    _getAccountKey(index) {
        let _key = this.accountPrefix + this._get26Num(index);
        return Web3.utils.soliditySha3(_key)
        //return this.accountPrefix + this._get26Num(index);
    }

    _getDIDKey(index) {
        let _key = "SID" + this._get10Num(index);
        return Web3.utils.soliditySha3(_key)
    }

    /**
     * Returns a random account key.
     * @return {string} Account key.
     * @private
     */
    _getRandomIndex(min, max) {
        // choose a random TX/account index based on the existing range, and restore the account name from the fragments
        const index = Math.ceil(Math.random() * (max - min) + min)
        //const index = Math.ceil(Math.random() * this.trailGenerated);
        //console.log("Key: " + index)
        return index;
        //return this._getAccountKey(index);
    }


    getmarketplaceArguments() {
        let _MID = Web3.utils.soliditySha3(this.Marketplace)
        return {
            marketplace: _MID
        };
    }

    gettrackerArguments() {
        return {
            trackerAddress: this.trackerScAddress
        };
    }

    getAddNewDataTrailArguments() {
        this.trailGenerated++;
        ////console.log("Key: " + this.trailGenerated)
        //console.log("owner: " + this._getAccountKey(this.trailGenerated))
        //console.log("MID: " + Web3.utils.soliditySha3(this.Marketplace))
        //console.log("DID: " + this._getDIDKey(this.trailGenerated))
        return {
            owner: this._getAccountKey(this.trailGenerated),
            MID: Web3.utils.soliditySha3(this.Marketplace),
            DID: this._getDIDKey(this.trailGenerated),
        };
    }


    getPaymentSharemultiArguments() {
        this.trailGenerated++;
        //console.log("Key: "+this.trailGenerated)
        let _owner = this._getAccountKey(this.trailGenerated)
        let _MID = Web3.utils.soliditySha3(this.Marketplace)
        let _DID = this._getDIDKey(this.trailGenerated)
        let _TID = Web3.utils.soliditySha3(_DID, _MID, _owner)
        //console.log("TID: " + _TID)
        //console.log("seller: " + _owner)
        //console.log("buyer: " + this._getAccountKey(this.trailGenerated+1))
        //console.log("ratio: " + this.ratio)
        //console.log("MID: " + _MID)
        //console.log("DID: " + _DID)
        //console.log("payment: " + this.paymentAmount)
        return {
            TID: _TID,
            seller: _owner,
            buyer: this._getAccountKey(this.trailGenerated+1),
            r: this.ratio,
            MID: _MID,
            DID: _DID,
            payment: this.paymentAmount
        };
    }

    getPaymentSharesingleArguments() {
        this.trailGenerated++;
        //console.log("Key: "+this.trailGenerated)
        let _owner = this._getAccountKey(1)
        let _MID = Web3.utils.soliditySha3(this.Marketplace)
        let _DID = this._getDIDKey(1)
        let _TID = Web3.utils.soliditySha3(_DID, _MID, _owner)
        //console.log("TID: " + _TID)
        //console.log("seller: " + this._getAccountKey(this.trailGenerated))
        //console.log("buyer: " + this._getAccountKey(this.trailGenerated+1))
        //console.log("ratio: " + this.ratio)
        //console.log("MID: " + _MID)
        //console.log("DID: " + _DID)
        //console.log("payment: " + this.paymentAmount)
        return {
            TID: _TID,
            seller: this._getAccountKey(this.trailGenerated),
            buyer: this._getAccountKey(this.trailGenerated+1),
            r: this.ratio,
            MID: _MID,
            DID: _DID,
            payment: this.paymentAmount
        };
    }

    getvalidateMultiTrailArguments() {
        //let _index = Math.ceil(Math.random() * this.trailGenerated);
        let _index = this._getRandomIndex(1, this.trailGenerated+1)
        let _owner = this._getAccountKey(_index)
        let _MID = Web3.utils.soliditySha3(this.Marketplace)
        let _DID = this._getDIDKey(_index)
        let _TID = Web3.utils.soliditySha3(_DID, _MID, _owner)
        //console.log("TID: " + _TID)
        //console.log("seller: " + this._getAccountKey(_index+1))
        //console.log("buyer: " + this._getAccountKey(2000))
        //console.log("MID: " + _MID)
        return {
            TID: _TID,
            seller: this._getAccountKey(_index+1),
            buyer: this._getAccountKey(2000),
            MID: _MID
        };
    }

    getvalidateSingleTrailArguments() {
        let _owner = this._getAccountKey(1)
        let _MID = Web3.utils.soliditySha3(this.Marketplace)
        let _DID = this._getDIDKey(1)
        let _TID = Web3.utils.soliditySha3(_DID, _MID, _owner)
        let _index = this._getRandomIndex(1, this.trailGenerated+1)
        //console.log("TID: " + _TID)
        //console.log("seller: " + this._getAccountKey(_index))
        //console.log("buyer: " + this._getAccountKey(2000))
        //console.log("MID: " + _MID)
        return {
            TID: _TID,
            seller: this._getAccountKey(_index),
            buyer: this._getAccountKey(2000),
            MID: _MID
        };
    }

}

module.exports = SimpleState;
