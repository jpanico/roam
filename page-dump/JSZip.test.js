


/**
 * test3-actual.zip was created by (macOS) unzipping test3-expected.zip, modifying 
 * 'Page 3.json' in the resulting folder, and then compressing the modified folder
 */
test('JSZipUtils.diffZipArchives: diff3', async () => {

    const JSZipUtils = require('./JSZipUtils.js')

    const testDataFilesDir = './test-data/zip-diff/'
    
    /** @type {JSZip} */
    const expected3 = await JSZipUtils.loadZip(testDataFilesDir+'test3-expected.zip')
    /** @type {JSZip} */
    const actual3 = await JSZipUtils.loadZip(testDataFilesDir+'test3-actual.zip')

    const diff3= JSZipUtils.diffZipArchives(expected3, actual3)
    console.log(`diff3 = ${diff3}`)
    
    expect(diff3).toMatch("for key = Page 3/Page 3.json, found diff = {objectDiffResult}")
    
})

/**
 * test2-expected.zip was created by JSZip. test2-actual.zip was created by (macOS) unzipping test2-expected.zip, and
 * then compressing (macOS) the resulting folder.
 */
test('JSZipUtils.diffZipArchives: diff2', async () => {

    const JSZipUtils = require('./JSZipUtils.js')

    const testDataFilesDir = './test-data/zip-diff/'
    
    /** @type {JSZip} */
    const expected2 = await JSZipUtils.loadZip(testDataFilesDir+'test1-expected.zip')
    /** @type {JSZip} */
    const actual2 = await JSZipUtils.loadZip(testDataFilesDir+'test1-actual.zip')

    const diff2= JSZipUtils.diffZipArchives(expected2, actual2)
    console.log(`diff2 = ${diff2}`)
    
    expect(diff2).toBeNull()
    
})

/**
 * test1-actual.zip is a direct file copy of test1-expected.zip, with only the filename changed
 */
test('JSZipUtils.diffZipArchives: diff1', async () => {

    const JSZipUtils = require('./JSZipUtils.js')

    const testDataFilesDir = './test-data/zip-diff/'
    /** @type {JSZip} */
    const expected1 = await JSZipUtils.loadZip(testDataFilesDir+'test1-expected.zip')
    /** @type {JSZip} */
    const actual1 = await JSZipUtils.loadZip(testDataFilesDir+'test1-actual.zip')

    const diff1 = JSZipUtils.diffZipArchives(expected1, actual1)
    console.log(`diff1 = ${diff1}`)
    
    expect(diff1).toBeNull()    
})

test('JSZipUtils.loadZip', async () => {

    const JSZipUtils = require('./JSZipUtils.js')

    const testDataFilesDir = './test-data/zip-diff/'
    /** @type {JSZip} */
    const zip = await JSZipUtils.loadZip(testDataFilesDir+'test1-expected.zip')
    /** @type {string[]} */
    const filePaths = Object.keys(zip.files)
    console.log(`filePaths = ${JSON.stringify(filePaths)}`)

    expect(
        filePaths
    ).toEqual(
        ["Page 3/", "Page 3/files/", "Page 3/Page 3.json", "Page 3/files/flower.jpeg", "Page 3/files/readme.md"]
    )

    const jsonZipFile = zip.files["Page 3/Page 3.json"]
    console.log(`jsonZipFile = ${JSON.stringify(jsonZipFile)}`)
    const compressedContent = jsonZipFile['_data'].compressedContent
    console.log(`compressedContent = ${JSON.stringify(compressedContent)}`)
    const comparison = Buffer.compare(compressedContent, compressedContent)
    console.log(`comparison = ${comparison}`)
    
})

test('JSZip', async () => {

    const fs = require("fs");
    /** @type {string} */
    const testDataFilesPath = './test-data/files/'
    /** @type {[string,Buffer]} */
    const fileName2Buff =
        Object.fromEntries(
            fs.readdirSync(testDataFilesPath).map(fname => [fname, fs.readFileSync(testDataFilesPath + fname)])
        )
    // console.log(`fileName2Buff = ${JSON.stringify(fileName2Buff)}`)

    const JSZip = require("jszip");
    console.log(`JSZip = ${JSZip}`)
    
    /** @type {JSZip} */
    const zip = new JSZip();
    const zipEnvelope = zip.folder('Page 3')
    const zipFilesDir = zipEnvelope.folder('files')

    zipEnvelope.file("hello.txt", "Hello World\n");
    console.log(`adding files`)
    Object.entries(fileName2Buff).forEach( ([fname, buff]) => zipFilesDir.file(fname, buff))
    
    console.log(`generateAsyncing...`)
    /** @type {Blob} */
    let zipBlob = await zip.generateAsync({type:"blob"})
    /** @type {ArrayBuffer} */
    let arrayBuff = await zipBlob.arrayBuffer()

    fs.writeFileSync('./out/Page 3.zip', Buffer.from(arrayBuff))

})
