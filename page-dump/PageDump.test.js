

test('dumped "Creative Brief.zip" matches "Creative Brief-expected.zip"', async () => {

    const pageDump = require('./PageDump.js')

    const config = {
        "followChildren": pageDump.FollowLinksDirective.DEEP,
        "followRefs": pageDump.FollowLinksDirective.DEEP,
        "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id", "heading"],
        "addProperties": ["vertex-type", "media-type"]
    }
    
    let dumpPath 
    try {
        dumpPath = await pageDump.dumpPage("Creative Brief", config)
    } catch (e) {
        console.error(e)
    }
    expectedPath = "./test-data/Creative Brief-expected.zip"
    console.log(`dumpPath = ${dumpPath}, expectedPath = ${expectedPath}`)

    const JSZipUtils = require('./JSZipUtils.js')
    /** @type {JSZip} */
    const expected = await JSZipUtils.loadZip(expectedPath)
    /** @type {JSZip} */
    const dumped = await JSZipUtils.loadZip(dumpPath)

    const diff= JSZipUtils.diffZipArchives(expected, dumped)
    console.log(`diff = ${diff}`)
    
    expect(diff).toBeNull()
    
})

test('dumped "Page 3.zip" matches "Page 3-expected.zip"', async () => {

    const pageDump = require('./PageDump.js')

    const config = {
        "followChildren": pageDump.FollowLinksDirective.DEEP,
        "followRefs": pageDump.FollowLinksDirective.DEEP,
        "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id", "heading"],
        "addProperties": ["vertex-type", "media-type"]
    }
    
    let dumpPath 
    try {
        dumpPath = await pageDump.dumpPage("Page 3", config)
    } catch (e) {
        console.error(e)
    }
    expectedPath = "./test-data/Page 3-expected.zip"
    console.log(`dumpPath = ${dumpPath}, expectedPath = ${expectedPath}`)

    const JSZipUtils = require('./JSZipUtils.js')
    /** @type {JSZip} */
    const expected = await JSZipUtils.loadZip(expectedPath)
    /** @type {JSZip} */
    const dumped = await JSZipUtils.loadZip(dumpPath)

    const diff= JSZipUtils.diffZipArchives(expected, dumped)
    console.log(`diff = ${diff}`)
    
    expect(diff).toBeNull()
    
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


