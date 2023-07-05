

test('JSZipUtils.diffZipArchives', async () => {

    const JSZipUtils = require('./JSZipUtils.js')

    const testDataFilesDir = './test-data/zip-diff/'
    /** @type {JSZip} */
    const expected = await JSZipUtils.loadZip(testDataFilesDir+'test1-expected.zip')
    /** @type {JSZip} */
    const actual = await JSZipUtils.loadZip(testDataFilesDir+'test1-actual.zip')

    const diff = JSZipUtils.diffZipArchives(expected, actual)
    console.log(`diff = ${diff}`)
    
    expect(diff).toBeNull()
    
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
