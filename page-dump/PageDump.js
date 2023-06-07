/**
 * @license
 * SPDX-FileCopyrightText: © 2023 Joe Panico <joe@panmachine.biz>
 * SPDX-License-Identifier: MIT
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

const config = {
    "targetPageTitle": "Page 3",
    "followChildren": FollowLinksDirective.DEEP,
    "followRefs": FollowLinksDirective.DEEP,
    "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id"],
    /** these are properties synthesized by this script
     * (not having direct Roam representation)
     */
    "addProperties": ["vertex-type", "media-type"]
}

const env = checkEnvironment()
const pageNodes = pullAllPageNodes(config, env)
const pageNodesReshaped = pageNodes.map(e => pick(e, config.includeProperties))
const vertices = normalizeNodes(pageNodesReshaped, config.addProperties)
const outputFileName = config.targetPageTitle + `.json`

saveAsJSONFile(vertices, outputFileName, env)

/**
 * @param {Object[]} nodes
 * @param {string[]} toAddProperties
 * @returns {Object[]}
 */
function normalizeNodes(nodes, toAddProperties) {
    console.log(`
        normalizeNodes: 
        nodes = ${JSON.stringify(nodes)}, 
        toAddProperties = ${JSON.stringify(toAddProperties)}
    `)

    const id2UidMap = Object.fromEntries(nodes.map(x => [x.id, [x.uid, x.order]]));
    console.log(`normalizeNodes: id2UidMap = ${JSON.stringify(id2UidMap)}`)

    // all of the nodes that do not have a title property will be successively
    // mapped to the "undefined" property
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
 * @param {Object} node
 * @param {Map<String, Object>} id2UidMap
 * @param {Object.<string,string} title2UidMap
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
 * @param {Object} value
 * @param {Object.<string,string[]} id2UidMap
 * @param {Object.<string,string} title2UidMap
 * @returns { [string, Object] } a new key-value pair that replaces the input key-value pair
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
     * @param {string} value -- captured from enclosing function (closure)
     * @returns {string} a new value to replace input value
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

    // the "children" property value is a JS array of obj/dict, where each 
    // obj has a single property: "id", whose value is a 2 element array; uid,order
    function normalizeChildren() {
        // this creates an array of pairs/tuples/2elementarrays: [uid(String), order(int)]
        const unorderedUids = value.map(child => id2UidMap[child["id"]])
        console.log(`unorderedUids: ${JSON.stringify(unorderedUids)}`)
        const orderedUids = unorderedUids.sort(compareOrder)
        console.log(`orderedUids: ${JSON.stringify(orderedUids)}`)
        // only take the uid-- leave order behind
        return orderedUids.map(e => e[0])
    }

    // the "refs" property value is a JS array of obj/dict, where each 
    // obj has a single property: "id", whose value is a 2 element array; uid,order
    function normalizeRefs() {
        return value.map(e => id2UidMap[e["id"]][0])
    }

    /*
     * compare 2 JS tuples that have "order" integer value at index 1 
     *
     * @typedef {*} OrderTupleIndex0
     * @typedef {integer} OrderTupleIndex1
     * @typedef {[OrderTupleIndex0, OrderTupleIndex1]} OrderTuple
     * @param {OrderTuple} lhs
     * @param {OrderTuple} rhs
     * @returns {integer} -- standard Java contract:
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

/*
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
 * @param {Object} config
 * @param {string} config.targetPageTitle
 * @param {FollowLinksDirective} config.followChildren
 * @param {FollowLinksDirective} config.followRefs
 * @param {string[]} config.includeProperties
 * @param {string[]} config.addProperties
 * @param {JSEnvironment} env
 * @returns {Object[]}
 */
function pullAllPageNodes(config, env) {
    console.log(`pullAllPageNodes:\n   config= ${JSON.stringify(config)},\n   env= ${JSON.stringify(env)}`)
    const pageContentFlattened = pullPageNodes(config.targetPageTitle, config.followChildren, config.followRefs, env)
    console.log(`pageContentFlattened= ${JSON.stringify(pageContentFlattened)}`)

    const pageShell =
        pullPageNodes(config.targetPageTitle, FollowLinksDirective.DONT_FOLLOW,
            FollowLinksDirective.DONT_FOLLOW, env)
    console.log(`pageShell = ${JSON.stringify(pageShell)}`)

    return [].concat(pageShell, pageContentFlattened)
}

/**
 * @param {string} pageTitle
 * @param {FollowLinksDirective} followChildren
 * @param {FollowLinksDirective} followRefs
 * @param {JSEnvironment} env
 * @returns {Object[]}
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
 * @param {string} pageTitle
 * @param {FollowLinksDirective} followChildren
 * @param {FollowLinksDirective} followRefs
 * @returns {Object[]}
 */
function pullPageNodesFromFile(pageTitle, followChildren, followRefs) {
    console.log(`pullPageNodesFromFile: 
        pageTitle = ${pageTitle}, followChildren = ${followChildren.description},
        followRefs = ${followRefs.description} `)

    const targetEntity =
        (followChildren == FollowLinksDirective.DONT_FOLLOW &&
            followRefs == FollowLinksDirective.DONT_FOLLOW) ?
            "shell" : "content"
    const targetFilePath = `./test-data/${pageTitle}-${targetEntity}.json`
    console.log(`pullPageNodesFromFile: targetFilePath = ${targetFilePath}`)

    return require(targetFilePath)
}

/**
 * @param {string} pageTitle
 * @param {FollowLinksDirective} followChildren
 * @param {FollowLinksDirective} followRefs
 * @returns {Object[]}
 */
function pullPageNodesFromRoam(pageTitle, followChildren, followRefs) {
    console.log(`pullPageNodesFromRoam: 
        pageTitle = ${pageTitle}, followChildren = ${followChildren.description},
        followRefs = ${followRefs.description} `)

    const query = buildQuery(followChildren, followRefs)
    const rules = buildRules(followChildren, followRefs)
    console.log(`pullPageNodesFromRoam: query = ${query}, rules = ${rules}`)

    // the nature of this query is to return an array of arrays, where each nested array
    // contains a single node
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
 * @returns {undefined} -- no return; void
 */
function saveAsJSONFile(obj, fileName, env) {
    console.log(`saveAsJSONFile: nodeCount = ${obj.length}, fileName = ${fileName}, env = ${JSON.stringify(env)}`)

    // 3rd arg triggers pretty formatting: number of spaces per level of indent
    const json = JSON.stringify(obj, null, 4)
    console.log(`saveAsJSONFile: json = ${json}`)

    if (env.isRoam)
        writeJSONFromBrowser(fileName, json)
    else if (env.isNode)
        writeJSONFromNodeJS(fileName, json)
    else
        throw `unsupported env: ${JSON.stringify(env)} `
}

function writeJSONFromBrowser(fileName, json) {
    console.log(`writeJSONFromBrowser: fileName = ${fileName}, json = ${json}`)

    const options = { type: "application/json" }
    const blob = new Blob([json], options)
    window.saveAs(blob, fileName)
}

function writeJSONFromNodeJS(fileName, json) {
    console.log(`writeJSONFromNodeJS: fileName = ${fileName}, json = ${json}`)

    const fs = require('fs');
    fs.writeFileSync('./' + fileName, json);
}

/**
 * throws an AssertionError if value==false
 *
 * @param {boolean} value
 * @param {string} errorMessage
 * @returns {undefined} -- no return; void
 * @throws {AssertionError}
 */
function assert(value, errorMessage) {
    if (!value)
        throw new AssertionError(errorMessage)
}

/**
 * @typedef {Object} JSEnvironment
 * @property {boolean} isBrowser
 * @property {boolean} isNode
 * @property {boolean} isWebWorker
 * @property {boolean} isJsDom
 * @property {boolean} isDeno
 * @property {boolean} isRoam
 * 
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

    return {
        isBrowser: isBrowser, isNode: isNode, isWebWorker: isWebWorker, isJsDom: isJsDom, isDeno: isDeno,
        isRoam: isRoam
    }
}
