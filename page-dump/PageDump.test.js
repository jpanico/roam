
const fs = require("fs");
const pageDump = require('./PageDump.js')

const config = {
    "followChildren": pageDump.FollowLinksDirective.DEEP,
    "followRefs": pageDump.FollowLinksDirective.DEEP,
    "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id"],
    "addProperties": ["vertex-type", "media-type"]
}

test('dumped "Page 3.json" matches "Page 3-expected.json"', () => {

    dumpPath = pageDump.dumpPage("Page 3", config)
    expectedPath = "./test-data/Page 3-expected.json"
    console.log(`dumpPath = ${dumpPath}, expectedPath = ${expectedPath}`)

    const dumpedJSON = fs.readFileSync(dumpPath, { encoding: 'utf8', flag: 'r' })
    const expectedJSON = fs.readFileSync(expectedPath, { encoding: 'utf8', flag: 'r' })

    expect(dumpedJSON).toMatch(expectedJSON)
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


