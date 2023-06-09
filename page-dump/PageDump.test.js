
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

