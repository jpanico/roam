

test('dumped "Page 3.json" matches "Page 3-expected.json"', () => {

    const pageDump = require('./PageDump.js')

    const config = {
        "followChildren": pageDump.FollowLinksDirective.DEEP,
        "followRefs": pageDump.FollowLinksDirective.DEEP,
        "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id"],
        "addProperties": ["vertex-type", "media-type"]
    }
    
    dumpPath = pageDump.dumpPage("Page 3", config)
    expectedPath = "./test-data/Page 3-expected.json"
    console.log(`dumpPath = ${dumpPath}, expectedPath = ${expectedPath}`)

    const fs = require("fs");
    const dumpedJSON = fs.readFileSync(dumpPath, { encoding: 'utf8', flag: 'r' })
    const expectedJSON = fs.readFileSync(expectedPath, { encoding: 'utf8', flag: 'r' })

    expect(dumpedJSON).toMatch(expectedJSON)
})

test('JSZip', () => {
(async () => {

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
    const zip = new JSZip();
    const zipEnvelope = zip.folder('Page 3')
    const zipFilesDir = zipEnvelope.folder('files')

    zipEnvelope.file("hello.txt", "Hello World\n");
    Object.entries(fileName2Buff).forEach( ([fname, buff]) => zipFilesDir.file(fname, buff))
    
    /** @type {Blob} */
    let zipBlob = await zip.generateAsync({type:"blob"})
    /** @type {ArrayBuffer} */
    let arrayBuff = await zipBlob.arrayBuffer()

    fs.writeFileSync('./out/Page 3.zip', Buffer.from(arrayBuff))

})()
})

/**
 * Blob api seems to be built into either Node.js or core JS
 */
test('Node.js Blob api', () => {
    const obj = { hello: "world" };
    const blob = new Blob([JSON.stringify(obj, null, 2)], {
      type: "application/json",
    });
    console.log(blob)
    console.log(`blob.stringify= ${JSON.stringify(blob)}`)
})

test('JS classes, properties, constructors', () => {
    class WebFile {
        constructor(name, color, price){
            this.name = name;
            this.color = color; 
            this.price = price;
        }
    }
    const webFile = new WebFile('test', 'red', 100)
    console.log(`webFile= ${JSON.stringify(webFile)}`)
    console.log(`webFile.properties= ${JSON.stringify(Object.getOwnPropertyNames(webFile))}`)
})

test('merge nested KV arrays', () => {

    const pageDump = require('./PageDump.js')
    const nested = [
        [["text", "Block 1.2"], ["uid", "mvVww9zGd"]],
        [["refs", ["refs.1"]]],
        [["children", ["Wu-bKjjdJ"]]],
        [["vertex-type", "roam/block"]],
        [["refs", ["refs.2"]]]
    ]
    console.log(`nested= ${JSON.stringify(nested)}`)
    const flat = nested.flat()
    console.log(`flat= ${JSON.stringify(flat)}`)
    const merged = pageDump.objectFromEntriesWithMerge(flat)
    console.log(`merged= ${JSON.stringify(merged)}`)

    expect(merged).toMatchObject({ "text": "Block 1.2", "uid": "mvVww9zGd", "refs": ["refs.1", "refs.2"], "children": ["Wu-bKjjdJ"], "vertex-type": "roam/block" })

})

test('flat', () => {

    const normalized = [[[["text","Block 1.2"]],null],[[["children",["Wu-bKjjdJ"]]],null],[[["uid","mvVww9zGd"]],null],[[["vertex-type","roam/block"]],null],[[["media-type","text/plain"]],null]]
    const allKVs = normalized.map(elem => elem[0])
    console.log(`normalizeNode: allKVs= ${JSON.stringify(allKVs)}`)
    const flat = normalized.map(elem => elem[0]).flat()
    console.log(`normalizeNode: flat= ${JSON.stringify(flat)}`)
})

test('Firebase regex', () => {
    const regex = /https:\/\/firebasestorage\.[\w.]+\.com\/[-a-zA-Z0-9@:%_\+.~#?&//=]*(&token=[0-9a-f]+-[0-9a-f]+-[0-9a-f]+-[0-9a-f]+-[0-9a-f]+)/g

    const url0 = `https://furbasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2FSCFH%2F-9owRBegJ8.jpeg.enc?alt=media&token=9b673aae-8089-4a91-84df-9dac152a7f94`
    const matches = [...url0.matchAll(regex)]
    console.log(`url0 = ${JSON.stringify(matches)}`)

    const url1 = `https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2FSCFH%2F-9owRBegJ8.jpeg.enc?alt=media&token=9b673aae-8089-4a91-84df-9dac152a7f94`
    console.log(`url1 = ${[...url1.matchAll(regex)]}`)

    const url2 = `![an image](https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2FSCFH%2F-9owRBegJ8.jpeg.enc?alt=media&token=9b673aae-8089-4a91-84df-9dac152a7f94)`
    console.log(`url2 = ${[...url2.matchAll(regex)]}`)

    const url3 = `blah blah blah: ![an image](https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2FSCFH%2F-9owRBegJ8.jpeg.enc?alt=media&token=9b673aae-8089-4a91-84df-9dac152a7f94)\n
    blah blah blah ![an image](https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2FSCFH%2F-9owRBegJ8.jpeg.enc?alt=media&token=11fff-22eee-33ddd-4444cccc)`
    console.log(`url3 = ${[...url3.matchAll(regex)]}`)

    const url4 = `blah blah blah: ![an image](https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2FSCFH%2F-9owRBegJ8.jpeg.enc?alt=media&token=9b673aae-8089-4a91-84df-9dac152a7f94)\n
    blah blah blah ![an image](https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2FSCFH%2F-9owRBegJ8.jpeg.enc?alt=media&token=11fff-22eee-33ddd-4444cccc) blah blah blah: `
    console.log(`url4 = ${[...url3.matchAll(regex)]}`)
})


