/**
 * @license
 * SPDX-FileCopyrightText: © 2023 Joe Panico <joe@panmachine.biz>
 * SPDX-License-Identifier: MIT
 */

/**
 * @typedef {string} uid
 * @typedef {integer} id
 * @typedef {integer} order
 * @typedef {string} title
 * 
 * @typedef {['uid', uid]} UidTuple
 * @typedef {[uid, order]} OrderedUid
 * @typedef {[*, order]} OrderedValue
 * 
 * @typedef IdObject
 * @type {Object}
 * @property {id} id
 * 
 * @typedef LinkObject
 * @type {Object}
 * @property {UidTuple} source
 * @property {UidTuple} value
 * 
 * @typedef {IdObject[]} children
 * @typedef {IdObject[]} refs
 * 
 * @typedef {Object.<string, OrderedUid>} Id2UidMap - key is id (as string)
 * @typedef {Object.<title, uid>} Title2UidMap - 
 * 
 * @typedef RoamNode - the raw shape of Block/Page elements returned from Roam queries
 * @type {Object}
 * @property {uid} uid
 * @property {id} id
 * @property {integer} time
 * @property {IdObject} user
 * @property {string} [string] - present only for Blocks
 * @property {title} [title] - present only for Pages
 * @property {order} [order] - present only for Blocks that are children
 * @property {children} [children] 
 * @property {refs} [refs] 
 * @property {IdObject} [page] - present only for Blocks
 * @property {boolean} [open] - present only for Blocks
 * @property {integer} [sidebar] - present only for Pages
 * @property {IdObject[]} [parents] - present only for Blocks
 * @property {LinkObject[][]} [attrs] - :entity/attrs
 * @property {IdObject[]} [lookup] - no idea what this is used for
 * @property {IdObject[]} [seen_by] - no idea what this is used for
 */

/**
 * @typedef JSEnvironment
 * @type {Object}
 * @property {boolean} isBrowser
 * @property {boolean} isNode
 * @property {boolean} isWebWorker
 * @property {boolean} isJsDom
 * @property {boolean} isDeno
 * @property {boolean} isRoam
 * @property {boolean} isTest 
 */

/**
 * @typedef DumpConfig 
 * @type {Object} 
 * @property {FollowLinksDirective} followChildren
 * @property {FollowLinksDirective} followRefs
 * @property {string[]} includeProperties
 * @property {string[]} addProperties - properties synthesized by PageDump (not having direct Roam representation)
 */

/**
 * A poor man's version of Node.js AssertionError:
 * (https://nodejs.org/api/assert.html#class-assertassertionerror). 
 * roam/js scripts do not have access to Node.
 */
class AssertionError extends Error {
    constructor(value) {
        super(`"${value}"`);
        this.name = 'AssertionError';
    }
}

class NotImplementedError extends Error {
    constructor(value) {
        super(`"${value}"`);
        this.name = 'NotImplementedError';
    }
}

/**
 * This Enum provides type identifiers for the individual elements (vertices) in the output
 * array that represents a Roam graph. Every vertex in the output graph has exactly one VertexType.
 */
const VertexType = Object.freeze(
    {
        /** 1-1 w/ Roam `Page` type Node */
        ROAM_PAGE: Symbol("roam/page"),
        /** 1-1 w/ Roam `Block` type Node */
        ROAM_BLOCK: Symbol("roam/block"),
        /** a file that was uploaded to, and now managed by, Roam */
        ROAM_FILE: Symbol("roam/file")
    }
)

/**
 * This Enum is used to configure how the Roam hierarchical query (Datomic) 
 * will join (follow) the Nodes in the children/ and refs/ branches.
 */
const FollowLinksDirective = Object.freeze(
    {
        DONT_FOLLOW: Symbol("DONT_FOLLOW"),
        SHALLOW: Symbol("SHALLOW"),
        DEEP: Symbol("DEEP")
    }
)

/** @type {DumpConfig} */
const config = {
    "followChildren": FollowLinksDirective.DEEP,
    "followRefs": FollowLinksDirective.DEEP,
    "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id"],
     "addProperties": ["vertex-type", "media-type"]
}

/** @type {JSEnvironment} */
const env = checkEnvironment()
if (env.isRoam) {
    const pageTitle = "Page 3"
    const dumpPath = dumpPage(pageTitle, config, env)
    console.log(`dumpPath = ${dumpPath}`)
} else if (env.isTest) {
    module.exports = {
        FollowLinksDirective: FollowLinksDirective,
        dumpPage: dumpPage
    };
}

/**
 * @param {string} pageTitle
 * @param {DumpConfig} config
 * @param {JSEnvironment} env
 * @returns {string|undefined} - if the environment isNode, then will return the path at which the file was saved
 */
function dumpPage(pageTitle, config, env) {
    if (env == undefined)
        env = checkEnvironment()

    /** @type {RoamNode[]} */
    const pageNodes = pullAllPageNodes(pageTitle, config, env)
    /** @type {RoamNode[]} */
    const pageNodesReshaped = pageNodes.map(e => pick(e, config.includeProperties))
    const vertices = normalizeNodes(pageNodesReshaped, config.addProperties)
    const outputFileName = pageTitle + `.json`

    return saveAsJSONFile(vertices, outputFileName, env)
}

/**
 * @param {RoamNode[]} nodes
 * @param {string[]} toAddProperties
 * @returns {Object[]}
 */
function normalizeNodes(nodes, toAddProperties) {
    console.log(`
        normalizeNodes: 
        nodes = ${JSON.stringify(nodes)}, 
        toAddProperties = ${JSON.stringify(toAddProperties)}
    `)

    /** @type {Id2UidMap} */
    const id2UidMap = Object.fromEntries(nodes.map(x => [x.id, [x.uid, x.order]]));
    console.log(`normalizeNodes: id2UidMap = ${JSON.stringify(id2UidMap)}`)

    // all of the nodes that do not have a title property will be successively
    // mapped to the "undefined" property
     /** @type {Title2UidMap} */
     let title2UidMap = new Map(nodes.map(x => [x.title, x.uid]));
    // remove the bogus "undefined" property that corresponds to nodes with no titles
    delete title2UidMap["undefined"];

    console.log(`normalizeNodes: title2UidMap = ${JSON.stringify(title2UidMap)}`)

    const normalizedNodes = nodes.map(node => normalizeNode(node, id2UidMap, title2UidMap))
    return addProperties(normalizedNodes, toAddProperties)
}

/**
 * Adds the specified JS properties to each of the Objects in nodes
 *
 * @param {Object[]} nodes
 * @param {string[]} toAddProperties
 * @returns {Object[]}
 */
function addProperties(nodes, toAddProperties) {
    console.log(`
        addProperties: 
        nodes = ${JSON.stringify(nodes)}, 
        toAddProperties = ${JSON.stringify(toAddProperties)}
    `)

    if (!(Array.isArray(toAddProperties) && toAddProperties.length))
        return nodes

    var vertices = nodes
    toAddProperties.forEach((propKey) => {
        vertices = vertices.map(getAddPropertyFunction(propKey))
    })

    return vertices
}

/**
 * Returns one of the add... functions
 *
 * @param {string} propertyName
 * @returns { (node:Object) => Object<node> }
 */
function getAddPropertyFunction(propertyName) {
    switch (propertyName) {
        case "vertex-type":
            return addVertexType
        case "media-type":
            return addMediaType
        default:
            throw Error(`getAddPropertyFunction: unrecognized propertyName: ${propertyName}`)
    }
}

/**
 * Add a "media-type" property to the JS Object 'node'. The media-type is derived from the content
 * in the Node: https://www.iana.org/assignments/media-types/media-types.xhtml
 *
 * @param {Object} node
 * @returns { Object<node> }
 */
function addMediaType(node) {
    console.log(`addMediaType: node = ${JSON.stringify(node)}`)

    var mediaType
    if ([VertexType.ROAM_PAGE.description, VertexType.ROAM_BLOCK.description].includes(node["vertex-type"]))
        mediaType = "text/plain"

    if (mediaType === undefined)
        throw Error(`unrecognized media type for node: ${JSON.stringify(node)}`)

    // clone the node argument
    const vertex = Object.assign({}, node)
    vertex[`media-type`] = mediaType
    return vertex
}

/**
 * Add a "vertex-type" property to the JS Object 'node'. The vertex-type values come from 
 * from the VertexType enum.
 *
 * @param {Object} node
 * @returns { Object<node> }
 */
function addVertexType(node) {
    console.log(`addVertexType: node = ${JSON.stringify(node)}`)

    const hasTitle = node.hasOwnProperty('title')
    const hasString = node.hasOwnProperty('string')
    assert(
        (hasTitle && !hasString) ||
        (!hasTitle && hasString),
        `one and only one condition must be true: hasTitle|hasString`
    )
    var vertexType
    if (hasTitle)
        vertexType = VertexType.ROAM_PAGE
    else if (hasString)
        vertexType = VertexType.ROAM_BLOCK
    else
        throw Error(`unrecognized Node type`)

    // clone the node argument
    const vertex = Object.assign({}, node)
    vertex[`vertex-type`] = vertexType.description
    return vertex
}

/**
 *
 * @param {RoamNode} node
 * @param {Id2UidMap} id2UidMap
 * @param {Title2UidMap} title2UidMap
 * @returns { Object<node> }
 */
function normalizeNode(node, id2UidMap, title2UidMap) {
    console.log(`
        normalizeNode: 
        node = ${JSON.stringify(node)}, 
        id2UidMap = ${JSON.stringify(id2UidMap)},
        title2UidMap = ${JSON.stringify(title2UidMap)}
    `)
    // we don't have to carry:
    // 1. "order" property, because we are going to order the uids in the children property
    // 2. "id" property, because the normalized form uses uid as PK
    const keys = Object.keys(node).filter(key => !["order", "id"].includes(key))
    console.log(`keys: ${JSON.stringify(keys)}`)

    return Object.fromEntries(keys.map(key => normalizeProperty(key, node[key], id2UidMap, title2UidMap)))
}

/**
 * @param {string} key
 * @param {*} value
 * @param {Id2UidMap} id2UidMap
 * @param {Title2UidMap} title2UidMap
 * @returns { [string, *] } a new key-value pair that replaces the input key-value pair
 */
function normalizeProperty(key, value, id2UidMap, title2UidMap) {
    console.log(`
        normalizeProperty: 
        key = ${JSON.stringify(key)}, 
        value = ${JSON.stringify(value)}, 
        id2UidMap = ${JSON.stringify(id2UidMap)},
        title2UidMap = ${JSON.stringify(title2UidMap)}
    `)

    switch (key) {
        case "string":
            return [key, normalizeString()]
        case "children":
            return [key, normalizeChildren()]
        case "refs":
            return [key, normalizeRefs()]
        default:
            return [key, value]
    }

    /**
     * replace page-refs based on page "title", with page-refs based on page "uid"
     *
     * @param {string} value - captured from enclosing function (closure)
     * @returns {string} - a new value to replace input value
     */
    function normalizeString() {
        // regex to match page reference
        const pageRefPattern = `\\[\\[([\\w\\s]+)\\]\\]`
        const matches = Array.from(value.matchAll(pageRefPattern))
        console.log(`normalizeString: matches = ${JSON.stringify(matches)}`)

        let normalized = value
        matches.forEach((match) => {
            normalized = normalized.replaceAll(match[0], `[[${title2UidMap[match[1]]}]]`)
        })
        return normalized
    }

    /**
     * @param {children} value - captured from enclosing function
     * @param {Id2UidMap} id2UidMap - captured from enclosing function
     */
    function normalizeChildren() {
        // this creates an array of pairs/tuples/2elementarrays: [uid(String), order(int)]
        const unorderedUids = value.map(child => id2UidMap[child["id"]])
        console.log(`unorderedUids: ${JSON.stringify(unorderedUids)}`)
        const orderedUids = unorderedUids.sort(compareOrder)
        console.log(`orderedUids: ${JSON.stringify(orderedUids)}`)
        // only take the uid-- leave order behind
        return orderedUids.map(e => e[0])
    }

    /**
     * @param {refs} value - captured from enclosing function
     * @param {Id2UidMap} id2UidMap - captured from enclosing function
     */
    function normalizeRefs() {
        return value.map(e => id2UidMap[e["id"]][0])
    }

    /**
     * compare 2 JS tuples that have "order" integer value at index 1 
     *
     * @param {OrderedValue} lhs
     * @param {OrderedValue} rhs
     * @returns {integer} - standard Java contract:
     *        0 if lhs.order == rhs.order
     *        <0 if lhs.order < rhs.order
     *        >0 if lhs.order > rhs.order
     */
    function compareOrder(lhs, rhs) {
        if ((lhs == null) || (rhs == null))
            throw "null argument"

        lhsOrder = lhs[1]
        rhsOrder = rhs[1]

        if ((!Number.isInteger(lhsOrder)) || (!Number.isInteger(rhsOrder)))
            throw "order not an integer"

        return lhsOrder - rhsOrder
    }
}

/**
 * create a new Object that contains a subset of properties 
 * (only those listed in the props param) from obj
 *
 * @param {Object} obj
 * @param {string[]} props
 * @returns {Object}
 */
function pick(obj, props) {
    return Object.fromEntries(
        Object.entries(obj).filter(([key, val]) => props.includes(key) && val != null)
    )
}

/**
 * @param {title} pageTitle
 * @param {DumpConfig} config
 * @param {FollowLinksDirective} config.followChildren
 * @param {FollowLinksDirective} config.followRefs
 * @param {string[]} config.includeProperties
 * @param {string[]} config.addProperties
 * @param {JSEnvironment} env
 * @returns {RoamNode[]}
 */
function pullAllPageNodes(pageTitle, config, env) {
    console.log(`pullAllPageNodes: 
        pageTitle = ${pageTitle}, config = ${JSON.stringify(config)}, env= ${JSON.stringify(env)}`)

    /** @type {RoamNode[]} */
    const pageContentFlattened = pullPageNodes(pageTitle, config.followChildren, config.followRefs, env)
    console.log(`pageContentFlattened= ${JSON.stringify(pageContentFlattened)}`)

    /** @type {RoamNode[]} */
    const pageShell =
        pullPageNodes(pageTitle, FollowLinksDirective.DONT_FOLLOW, FollowLinksDirective.DONT_FOLLOW, env)
    console.log(`pageShell = ${JSON.stringify(pageShell)}`)

    return [].concat(pageShell, pageContentFlattened)
}

/**
 * @param {title} pageTitle
 * @param {FollowLinksDirective} followChildren
 * @param {FollowLinksDirective} followRefs
 * @param {JSEnvironment} env
 * @returns {RoamNode[]}
 */
function pullPageNodes(pageTitle, followChildren, followRefs, env) {
    console.log(`pullPageNodes: 
        pageTitle = ${pageTitle}, followChildren = ${followChildren.description}, 
        followRefs = ${followRefs.description}, env = ${env}`)

    if (!env.isRoam)
        return pullPageNodesFromFile(pageTitle, followChildren, followRefs)

    return pullPageNodesFromRoam(pageTitle, followChildren, followRefs)
}

/**
 * @param {title} pageTitle
 * @param {FollowLinksDirective} followChildren
 * @param {FollowLinksDirective} followRefs
 * @returns {RoamNode[]}
 */
function pullPageNodesFromFile(pageTitle, followChildren, followRefs) {
    console.log(`pullPageNodesFromFile: 
        pageTitle = ${pageTitle}, followChildren = ${followChildren.description},
        followRefs = ${followRefs.description} `)

    /** @type {string} */
    const targetEntity =
        (followChildren == FollowLinksDirective.DONT_FOLLOW &&
            followRefs == FollowLinksDirective.DONT_FOLLOW) ?
            "shell" : "content"
    /** @type {string} */
    const targetFilePath = `./test-data/${pageTitle}-${targetEntity}-input.json`
    console.log(`pullPageNodesFromFile: targetFilePath = ${targetFilePath}`)

    return require(targetFilePath)
}

/**
 * @param {title} pageTitle
 * @param {FollowLinksDirective} followChildren
 * @param {FollowLinksDirective} followRefs
 * @returns {RoamNode[]}
 */
function pullPageNodesFromRoam(pageTitle, followChildren, followRefs) {
    console.log(`pullPageNodesFromRoam: 
        pageTitle = ${pageTitle}, followChildren = ${followChildren.description},
        followRefs = ${followRefs.description} `)

    /** @type {string} */
    const query = buildQuery(followChildren, followRefs)
    /** @type {string} */
    const rules = buildRules(followChildren, followRefs)
    console.log(`pullPageNodesFromRoam: query = ${query}, rules = ${rules}`)

    // the nature of this query is to return an array of arrays, where each nested array
    // contains a single node
     /** @type {RoamNode[][]} */
     const nodesRaw = window.roamAlphaAPI.q(query, pageTitle, rules)
    // flatten array of arrays of nodes -> array of nodes
    return nodesRaw.flat()
}

/**
 * @param {FollowLinksDirective} followChildren
 * @param {FollowLinksDirective} followRefs
 * @returns {string}
 */
function buildRules(followChildren, followRefs) {
    console.log(`buildRules: followChildren = ${followChildren.description}, followRefs = ${followRefs.description}`)
    if (
        followChildren == FollowLinksDirective.DONT_FOLLOW &&
        followRefs == FollowLinksDirective.DONT_FOLLOW
    ) { return "[]" }

    const proximateRefsRule =
        (followRefs == FollowLinksDirective.DONT_FOLLOW) ?
            "" : "[?a :block/refs ?b]"
    const proximateChildrenRule =
        (followChildren == FollowLinksDirective.DONT_FOLLOW) ?
            "" : "[?a :block/children ?b]"
    const inductiveRefsRule =
        (followRefs == FollowLinksDirective.DEEP) ?
            "[?proximate_linker :block/refs ?b]" : ""
    const inductiveChildrenRule =
        (followChildren == FollowLinksDirective.DEEP) ?
            "[?proximate_linker :block/children ?b]" : ""
    const inductiveLinkerRule =
        (!inductiveRefsRule && !inductiveChildrenRule) ?
            "" :
            `[  (linker ?b ?a ) 
                ( or 
                    ${inductiveRefsRule}
                    ${inductiveChildrenRule} 
                )         
                (linker ?proximate_linker ?a) 
            ]`
    const rules =
        `[ 
                [ (linker ?b ?a )
                ( or 
                    ${proximateRefsRule} 
                    ${proximateChildrenRule} 
                )
                ]
                ${inductiveLinkerRule}   
            ]`
    return rules
}

/**
 * @param {FollowLinksDirective} followChildren
 * @param {FollowLinksDirective} followRefs
 * @returns {string}
 */
function buildQuery(followChildren, followRefs) {
    console.log(`buildQuery: followChildren = ${followChildren.description}, followRefs = ${followRefs.description}`)

    const targetEntity =
        (followChildren == FollowLinksDirective.DONT_FOLLOW &&
            followRefs == FollowLinksDirective.DONT_FOLLOW) ?
            "page" : "node"
    const linkerClause =
        (followChildren == FollowLinksDirective.DONT_FOLLOW &&
            followRefs == FollowLinksDirective.DONT_FOLLOW) ?
            "" : "(linker ?node ?page)"
    const query =
        `[
            :find 
                (pull ?${targetEntity} [*] )
            :in 
                $ ?target_page_title % 
            :where
                [?page :node/title ?target_page_title]
                ${linkerClause}
        ]`
    return query
}

/**
 * @param {[*]} obj
 * @param {string} fileName
 * @param {JSEnvironment} env
 * @returns {string|undefined} - if the environment isNode, then will return the 
 *                                path at which the file was saved
 */
function saveAsJSONFile(obj, fileName, env) {
    console.log(`saveAsJSONFile: nodeCount = ${obj.length}, fileName = ${fileName}, env = ${JSON.stringify(env)}`)

    // 3rd arg triggers pretty formatting: number of spaces per level of indent
    const json = JSON.stringify(obj, null, 4)
    console.log(`saveAsJSONFile: json = ${json}`)

    var writePath
    if (env.isRoam)
        writeJSONFromBrowser(fileName, json)
    else if (env.isNode)
        writePath = writeJSONFromNodeJS(fileName, json)
    else
        throw `unsupported env: ${JSON.stringify(env)} `

    return writePath
}

/**
 * @param {string} fileName
 * @param {string} json
 * @returns {undefined} - no return; void
 */
function writeJSONFromBrowser(fileName, json) {
    console.log(`writeJSONFromBrowser: fileName = ${fileName}, json = ${json}`)

    const options = { type: "application/json" }
    const blob = new Blob([json], options)
    window.saveAs(blob, fileName)
}

/**
 * @param {string} fileName
 * @param {string} json
 * @returns {string} - the path at which the file was written
 */
function writeJSONFromNodeJS(fileName, json) {
    console.log(`writeJSONFromNodeJS: fileName = ${fileName}, json = ${json}`)

    const outputDir = './out/'
    const outputPath = outputDir + fileName
    const fs = require('fs');

    if (!fs.existsSync(outputDir))
        fs.mkdirSync(outputDir)
    fs.writeFileSync(outputPath, json)

    return outputPath
}

/**
 * throws an AssertionError if value==false
 *
 * @param {boolean} value
 * @param {string} errorMessage
 * @returns {undefined} - no return; void
 * @throws {AssertionError}
 */
function assert(value, errorMessage) {
    if (!value)
        throw new AssertionError(errorMessage)
}

/**
 * @return {JSEnvironment}
 */
function checkEnvironment() {
    const isBrowser =
        (typeof window !== "undefined") &&
        (typeof window.document !== "undefined")

    const isNode =
        (typeof process !== "undefined") &&
        (process.versions != null) &&
        (process.versions.node != null)

    const isWebWorker =
        (typeof self === "object") &&
        (self.constructor) &&
        (self.constructor.name === "DedicatedWorkerGlobalScope")

    /**
     * @see https://github.com/jsdom/jsdom/releases/tag/12.0.0
     * @see https://github.com/jsdom/jsdom/issues/1537
     */
    const isJsDom =
        (typeof window !== "undefined" && window.name === "nodejs") ||
        ((typeof navigator !== "undefined") &&
            (navigator.userAgent.includes("Node.js") ||
                navigator.userAgent.includes("jsdom")
            )
        )

    const isDeno =
        (typeof Deno !== "undefined") &&
        (typeof Deno.version !== "undefined") &&
        (typeof Deno.version.deno !== "undefined")

    const isRoam =
        (isBrowser) &&
        (typeof window.roamAlphaAPI !== "undefined")

    const isTest = !isRoam

    return {
        isBrowser: isBrowser, isNode: isNode, isWebWorker: isWebWorker, isJsDom: isJsDom, isDeno: isDeno,
        isRoam: isRoam, isTest: isTest
    }
}
