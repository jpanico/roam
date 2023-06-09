const pd = require('./PageDump.js')

const config = {
    "followChildren": pd.FollowLinksDirective.DEEP,
    "followRefs": pd.FollowLinksDirective.DEEP,
    "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id"],
    /** these are properties synthesized by this script
     * (not having direct Roam representation)
     */
    "addProperties": ["vertex-type", "media-type"]
}

pd.dumpPage("Page 3", config)