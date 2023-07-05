
/**
 * @license
 * SPDX-FileCopyrightText: © 2023 Joe Panico <joe@panmachine.biz>
 * SPDX-License-Identifier: MIT
 */
/**
 * @overview
 * convenience functions for using JSZip in Node.js
 */

/**
 * @typedef {JSZip} JSZip -- defined here: https://stuk.github.io/jszip/documentation/api_jszip.html
 * @typedef {ZipObject} ZipObject -- defined here: https://stuk.github.io/jszip/documentation/api_zipobject.html
 */

module.exports = {
    loadZip: loadZip,
    diffZipArchives: diffZipArchives,
    diffZipObjects: diffZipObjects
}

/** 
 * @param {JSZip} expected
 * @param {JSZip} actual
 * 
 * @returns {string | null} 
 *              if there is a diff, a string that attempts to explain the diff -- only the first diff is considered
 *              if no diff, null
 */
function diffZipArchives(expected, actual) {
    console.log(`diffZipArchives: expected = ${Object.keys(expected.files)}, actual = ${Object.keys(actual.files)}`)
    /** @type {boolean} */
    const expectedIsNull = (expected == null)
    /** @type {boolean} */
    const actualIsNull = (actual == null)

    if( expectedIsNull && actualIsNull)
        return null

    if( expectedIsNull || actualIsNull)
        return `one is null: expected = ${expected}, actual = ${actual}`

    /** @type {string[]} */
    const expectedFilePaths = Object.keys(expected.files)
     /** @type {string[]} */
     const actualFilePaths = Object.keys(actual.files)
    if( !actualFilePaths.equals(expectedFilePaths) )
        return `file paths don't match: ` +
            `expectedFilePaths = ${JSON.stringify(expectedFilePaths)}, ` +
            `actualFilePaths = ${JSON.stringify(actualFilePaths)}`

    console.log(`diffZipArchives: expectedFilePaths = ${expectedFilePaths}`)
    for( filePath of expectedFilePaths) {
        console.log(`diffZipArchives: filePath = ${filePath}`)
        const objectDiffResult = diffZipObjects(expected.files[filePath], actual.files[filePath])
        if(objectDiffResult != null)
            return `for key = ${filePath}, found diff = {objectDiffResult}`
    }

    return null
}

/** 
 * @param {ZipObject} expected
 * @param {ZipObject} actual
 * 
 * @returns {string | null} 
 *              if there is a diff, a string that attempts to explain the diff
 *              if no diff, null
 */
function diffZipObjects(expected, actual) {
    console.log(`diffZipObjects: expected = ${expected}, actual = ${actual}`)

    /** @type {boolean} */
    const expectedIsNull = (expected == null)
    const actualIsNull = (actual == null)

    if( expectedIsNull && actualIsNull)
        return null

    if( expectedIsNull || actualIsNull)
        return `one is null: expected = ${expected}, actual = ${actual}`

    if( expected.dir != actual.dir )
        return `dir attributes don't match: expected = ${expected.dir}, actual = ${actual.dir}`

    if( expected.dir )
        return diffZipDirs(expected, actual)

    // if it's not a dir, it has to be a file
    return diffZipFiles(expected, actual)
}

/** 
 * @param {ZipObject} expected
 * @param {ZipObject} actual
 * 
 * @returns {string | null} 
 *              if there is a diff, a string that attempts to explain the diff
 *              if no diff, null
 */
function diffZipDirs(expected, actual) {
    console.log(`diffZipDirs: expected = ${expected.name}, actual = ${actual.name}`)

    if(expected.name != actual.name)
        return `names don't match: expected = ${expected.name}, actual = ${actual.name}`

    return null
}

/** 
 * @param {ZipObject} expected
 * @param {ZipObject} actual
 * 
 * @returns {string | null} 
 *              if there is a diff, a string that attempts to explain the diff
 *              if no diff, null
 */
function diffZipFiles(expected, actual) {
    console.log(`diffZipDirs: expected = ${expected.name}, actual = ${actual.name}`)

    if(expected.name != actual.name)
        return `names don't match: expected = ${expected.name}, actual = ${actual.name}`

    // https://nodejs.org/api/buffer.html#static-method-buffercomparebuf1-buf2
    if(Buffer.compare(expected['_data'].compressedContent, actual['_data'].compressedContent) != 0)
        return `compressedContent don't match`

    return null
}

/**
 * @param {string} filePath
 * @returns {Promise<JSZip>}
 */
async function loadZip(filePath) {
    console.log(`loadZip: filePath = ${filePath}`)

    const fs = require('fs')
    /** @type {Buffer} -- if no options are passed to readFileSync, defaults to return a raw Buffer  */
    const fileContents = fs.readFileSync(filePath)

    const JSZip = require('jszip')
    /** @type {JSZip} */
    const zip = await JSZip.loadAsync(fileContents)

    return zip
}

// START: stolen from https://stackoverflow.com/questions/7837456/how-to-compare-arrays-in-javascript
// Warn if overriding existing method
if(Array.prototype.equals)
    console.warn("Overriding existing Array.prototype.equals. Possible causes: New API defines the method, there's a framework conflict or you've got double inclusions in your code.");
// attach the .equals method to Array's prototype to call it on any array
Array.prototype.equals = function (array) {
    // if the other array is a falsy value, return
    if (!array)
        return false;
    // if the argument is the same array, we can be sure the contents are same as well
    if(array === this)
        return true;
    // compare lengths - can save a lot of time 
    if (this.length != array.length)
        return false;

    for (var i = 0, l=this.length; i < l; i++) {
        // Check if we have nested arrays
        if (this[i] instanceof Array && array[i] instanceof Array) {
            // recurse into the nested arrays
            if (!this[i].equals(array[i]))
                return false;       
        }           
        else if (this[i] != array[i]) { 
            // Warning - two different object instances will never be equal: {x:20} != {x:20}
            return false;   
        }           
    }       
    return true;
}
// Hide method from for-in loops
Object.defineProperty(Array.prototype, "equals", {enumerable: false});
// END: stolen from https://stackoverflow.com/questions/7837456/how-to-compare-arrays-in-javascript

