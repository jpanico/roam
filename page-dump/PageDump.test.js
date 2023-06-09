
const pageDump = require('./PageDump.js')

const config = {
    "followChildren": pageDump.FollowLinksDirective.DEEP,
    "followRefs": pageDump.FollowLinksDirective.DEEP,
    "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id"],
    /** these are properties synthesized by this script
     * (not having direct Roam representation)
     */
    "addProperties": ["vertex-type", "media-type"]
}

pageDump.dumpPage("Page 3", config)