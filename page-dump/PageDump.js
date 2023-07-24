/**
 * @license
 * SPDX-FileCopyrightText: © 2023 Joe Panico <joe@panmachine.biz>
 * SPDX-License-Identifier: MIT
 */
/**
 * @overview
 * This is a roam/js script. Run within a roam/js... page in RoamResearch (0.9.11+), by pasting this entire script into
 * a child block of a '{{[[roam/js]]}}' block.
 *
 * Roam/js scripting supports only vanilla, untyped, JavaScript-- it does not support TypeScript.
 * [JSDoc](https://jsdoc.app/tags-type.html) provides a method for adding type annotations to JS code, via special tags
 * (e.g. @typedef) placed in JSDoc style comments. IDEs like VS Code (1.78+) support JSDoc type annotations
 * out-of-the-box, so that the source editors will provide almost all of the type-directed assistance that would be
 * available in Typescript at development time. At runtime, all of these type annotations are invisible to the Roam JS
 * engine.
 *
 * JavaScript has evolved several different module systems. The most widely used are:
 * [CommonJS](https://nodejs.org/api/modules.html), and ECMAScript (ES6) modules. CommonJS grew out of Node.js, is the
 * default module system for Node, and uses module.exports() and require() function calls. ES6 modules are standardized
 * by ECMA and use export and import statements.
 *
 * Roam/js scripting does not support any module features, from any module system. The fact that Roam runs on Node.js is
 * an opaque implementation detail, and no Node.js api are accessible to roam/js scripts. Roam/js scripts are intended
 * to run as single file, self-contained, code units. But in order to effect unit testing at development time, some
 * module features are needed, so that the unit test code can access JS language elements (e.g. functions, type
 * definitions, etc.) in this script. As a result, this script needs conditional module support -- module features that
 * can be invoked only at development time, and completely turned off at runtime. Since CommonJS features are invoked
 * via function calls, rather than JS language level export/import statements, it is much better suited for dynamic,
 * conditional, module binding. So this script, and the associated test code, use CommonJS modules if the execution
 * environment is detected to be 'test'.
 */

// Whole-script strict mode syntax
"use strict";

/**
 * @typedef {string} uid
 * @typedef {integer} id
 * @typedef {integer} order
 * @typedef {integer} heading
 * @typedef {string} title
 * @typedef {string} url
 * 
 * https://en.wikipedia.org/wiki/Media_type
 * https://www.iana.org/assignments/media-types/media-types.xhtml
 * @typedef {string} media_type
 * 
 * @typedef {['uid', uid]} UidPair
 * @typedef {[uid, order]} OrderedUid
 * @typedef {[*, order]} OrderedValue
 * @typedef {[string, *]} KeyValuePair
 * 
 * @typedef IdObject
 * @type {Object}
 * @property {id} id
 * 
 * @typedef LinkObject
 * @type {Object}
 * @property {UidPair} source
 * @property {UidPair} value
 * 
 * @typedef {IdObject[]} raw_children
 * @typedef {IdObject[]} raw_refs
 * @typedef {uid[]} normal_children
 * @typedef {uid[]} normal_refs
 * 
 * @typedef {Object.<string, OrderedUid>} Id2UidMap - key is id (as string)
 * @typedef {Object.<title, uid>} Title2UidMap - 
 * @typedef {Object.<uid, RoamFileReference>} Uid2FileRefMap - 
 * @typedef {Object.<uid, RoamFile>} Uid2RoamFileMap - 
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
 * @property {heading} [heading] - present only for Blocks that are children
 * @property {raw_children} [children] 
 * @property {raw_refs} [refs] 
 * @property {IdObject} [page] - present only for Blocks
 * @property {boolean} [open] - present only for Blocks
 * @property {integer} [sidebar] - present only for Pages
 * @property {IdObject[]} [parents] - present only for Blocks
 * @property {LinkObject[][]} [attrs] - :entity/attrs
 * @property {IdObject[]} [lookup] - no idea what this is used for
 * @property {IdObject[]} [seen_by] - no idea what this is used for
 * 
 * @typedef EnrichedNode - a RoamNode with synthetic properties added
 * @type {RoamNode}
 * @property {VertexType} [vertex_type] - it's actually 'vertex-type', but JSDoc bug prevents
 * @property {media_type} [media_type] - it's actually 'media-type', but JSDoc bug prevents
 * 
 * @typedef Vertex - the normalized shape of Roam elements
 * @type {Object}
 * @property {uid} uid
 * @property {VertexType} vertex_type - it's actually 'vertex-type', but JSDoc bug prevents
 * @property {media_type} [media_type] - it's actually 'media-type', but JSDoc bug prevents
 * @property {string} [text]
 * @property {heading} [heading]
 * @property {normal_children} [children] 
 * @property {normal_refs} [refs]
 * @property {url} [source]
 * @property {string} [file_name]
 * 
 * @typedef RoamFileReference
 * @type {Object}
 * @property {uid} uid
 * @property {url} url
 * 
 * @typedef RoamFile
 * @type {RoamFileReference}
 * @property {WebFile} file
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
 * A poor man's version of Node.js AssertionError: (https://nodejs.org/api/assert.html#class-assertassertionerror).
 * roam/js scripts do not have access to Node.
 */
class AssertionError extends Error {
    constructor(value) {
        super(`"${value}"`)
        this.name = 'AssertionError'
    }
}

class NotImplementedError extends Error {
    constructor(value) {
        super(`"${value}"`)
        this.name = 'NotImplementedError'
    }
}

/**
 * The File "Web api" (https://developer.mozilla.org/en-US/docs/Web/API/File) is the most convenient struct for handling
 * Roam managed files in this script. But that api is only present in web environments (Roam), and is not supported in
 * Node.js. However, the ArrayBuffer api is supported in both Web envs and Node.js. Hence, this class.
 * 
 * @property {string} fileName
 * @property {BigInt} lastModified
 * @property {string} mediaType 
 * @property {ArrayBuffer} contents
 */
class WebFile {
    constructor(fileName, lastModified, mediaType, contents){
        this.fileName = fileName;
        this.lastModified = lastModified; 
        this.mediaType = mediaType;
        this.contents = contents;
    }

    /**
     * factory method
     *
     * @param {File} file
     * @returns { WebFile }
     */
    static async fromFile(file) {
        console.log(`fromFile: file = ${file}`)
        // type "File" in Web API "is a specific kind of Blob, and can be used in any context that a Blob can."
        /** @type {ArrayBuffer} */
        const arrayBuffer = await file.arrayBuffer()
        return new WebFile(file.name, file.lastModified, file.type, arrayBuffer)
    }
    
    /**
     * @returns {string}
     */
    toShortString() {
        return this.fileName
    }
}

/**
 * This Enum provides type identifiers for the individual elements (vertices) in the output array that represents a Roam
 * graph. Every vertex in the output graph has exactly one VertexType.
 */
const VertexType = Object.freeze(
    {
        /** 1-1 w/ Roam `Page` type Node */
        ROAM_PAGE: Symbol("roam/page"),
        /** 1-1 w/ Roam `Block` type Node if there is no `heading` property */
        ROAM_BLOCK_CONTENT: Symbol("roam/block-content"),
        /** 1-1 w/ Roam `Block` type Node if there is a `heading` property */
        ROAM_BLOCK_HEADING: Symbol("roam/block-heading"),
        /** a file that was uploaded to, and now managed by, Roam */
        ROAM_FILE: Symbol("roam/file")
    }
)

/**
 * This Enum is used to configure how the Roam hierarchical query (Datomic) will join (follow) the Nodes in the
 * children/ and refs/ branches.
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
    "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id", "heading"],
    "addProperties": ["vertex-type", "media-type"]
}

// uncomment to disable all console logging
// console.log = function() {}


/** @type {JSEnvironment} */
const env = checkEnvironment()
if (env.isRoam) {
(async () => {
    const pageTitle = "Page 3"
    const dumpPath = await dumpPage(pageTitle, config, env)
    console.log(`dumpPath = ${dumpPath}`)
})()
} else if (env.isTest) {
    module.exports = {
        FollowLinksDirective: FollowLinksDirective,
        dumpPage: dumpPage,
        objectFromEntriesWithMerge: objectFromEntriesWithMerge
    }
} else
    throw `unsupported env: ${JSON.stringify(env)} `


/**
 * @param {string} pageTitle
 * @param {DumpConfig} config
 * @param {JSEnvironment} env
 * @returns {Promise<string|undefined>} - if the environment isNode, then will return the path at which the file was saved
 */
async function dumpPage(pageTitle, config, env) {
    if (env == undefined)
        env = checkEnvironment()

    /** @type {RoamNode[]} */
    const nodes = pullAllNodesFromPage(pageTitle, config, env)
    /** @type {RoamNode[]} */
    const thinnedNodes = nodes.map(e => pick(e, config.includeProperties))
    /** @type {Vertex[]} */
    let vertices = normalizeNodes(thinnedNodes, config.addProperties)
    /** @type {Uid2FileRefMap} */
    const roamFileRefs = createFileRefMap(vertices)
    /** @type {Uid2RoamFileMap} */
    const roamFiles = await fetchRoamFiles(roamFileRefs, env)
    console.log(`dumpPage: roamFiles = `)
    console.log(Object.values(roamFiles))
    vertices = addPropertiesToFileVertices(vertices, roamFiles)
    console.log(`dumpPage: vertices = ${JSON.stringify(vertices)}`)

    // I don't even know how to type this
    const JSZip = await getJSZipModule(env)
    console.log(`dumpPage: JSZip = ${JSZip}`) 
    /** @type {Blob} */
    let zipBlob = await createZipArchive(vertices, roamFiles, pageTitle, JSZip)

    const zipFileName = `${pageTitle}.zip`
    let writePath = await writeFile(zipFileName, zipBlob, env)
    console.log(`dumpPage: writePath= ${writePath}`)

    return writePath
}

/**
 * @param {RoamNode[]} nodes
 * @param {string[]} toAddProperties
 * @returns {Vertex[]}
 */
function normalizeNodes(nodes, toAddProperties) {
    console.log(`
        normalizeNodes: 
        nodes = ${JSON.stringify(nodes)}, 
        toAddProperties = ${JSON.stringify(toAddProperties)}
    `)

    /** @type {Id2UidMap} */
    const id2UidMap = Object.fromEntries(nodes.map(x => [x.id, [x.uid, x.order]]))
    console.log(`normalizeNodes: id2UidMap = ${JSON.stringify(id2UidMap)}`)

    // all of the nodes that do not have a 'title' property will be successively mapped to the 'undefined' property
    /** @type {Title2UidMap} */
    let title2UidMap = Object.fromEntries(nodes.map(x => [x.title, x.uid]))
    // remove the bogus "undefined" property that corresponds to nodes with no titles
    delete title2UidMap["undefined"]

    console.log(`normalizeNodes: title2UidMap = ${JSON.stringify(title2UidMap)}`)

    /** @type {EnrichedNode[]} */
    const enrichedNodes = addProperties(nodes, toAddProperties)
    /** @type {Vertex[][]} */
    const vertices = enrichedNodes.map(node => normalizeNode(node, id2UidMap, title2UidMap))
    console.log(`normalizeNodes: vertices = ${JSON.stringify(vertices)}`)

    return vertices.flat()
}
/**
 * Adds the specified JS properties to each of the Objects in nodes
 *
 * @param {RoamNode[]} nodes
 * @param {string[]} toAddProperties
 * @returns {EnrichedNode[]}
 */
function addProperties(nodes, toAddProperties) {
    console.log(`
        addProperties: 
        nodes = ${JSON.stringify(nodes)}, 
        toAddProperties = ${JSON.stringify(toAddProperties)}
    `)

    if (!(Array.isArray(toAddProperties) && toAddProperties.length))
        return nodes

    /** @type {EnrichedNode[]} */
    let enrichedNodes = nodes
    toAddProperties.forEach((propKey) => {
        enrichedNodes = enrichedNodes.map(getAddPropertyFunction(propKey))
    })

    return enrichedNodes
}

/**
 * To all of the elements in vertices where vertex_type == ROAM_FILE, add file-name and media-type properties
 *
 * @param {Vertex[]} vertices
 * @param {Uid2RoamFileMap} roamFiles
 * @returns {Vertex[]}
 */
function addPropertiesToFileVertices(vertices, roamFiles) {
    console.log(`
        addPropertiesToFileVertices: 
        vertices = ${JSON.stringify(vertices)}, 
        roamFiles = ${JSON.stringify(Object.values(roamFiles).map(e => RoamFileToShortString(e)))},
    `)

    return vertices.map( v => addFileProperties(v, roamFiles[v.uid]))
 }

 /**
 * add file-name and media-type properties from roamFile to vertex if vertex['media-type']== ROAM_FILE by creating a
 * copy of vertex. otherwise, just return vertex
 *
 * @param {Vertex} vertex
 * @param {RoamFile} roamFile
 * @returns {Vertex}
 */
function addFileProperties(vertex, roamFile) {
    console.log(`addFileProperties: 
        vertex = ${JSON.stringify(vertex)}, 
        roamFile = ${JSON.stringify(RoamFileToShortString(roamFile))}
    `)

    if (vertex == null)
        throw "null argument"
    if (!vertex.hasOwnProperty('vertex-type'))
        throw TypeError()
    if(vertex['vertex-type'] != VertexType.ROAM_FILE.description)
        return vertex
    if (roamFile == null)
        throw "null argument"

    // clone vertex
    const newVertex = Object.assign({}, vertex);
    newVertex['media-type'] = roamFile.file.mediaType
    newVertex['file-name'] = roamFile.file.fileName

    return newVertex
 }

/**
 * Returns one of the add... functions
 *
 * @param {string} propertyName
 * @returns { (node:RoamNode) => EnrichedNode }
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
 * Add a "media-type" property to the JS Object 'node'. The media-type value is derived from the content in the Node.
 *
 * @param {RoamNode} node
 * @returns {EnrichedNode}
 */
function addMediaType(node) {
    console.log(`addMediaType: node = ${JSON.stringify(node)}`)

    const textPlainVertexTypes = [
        VertexType.ROAM_PAGE.description, 
        VertexType.ROAM_BLOCK_CONTENT.description, 
        VertexType.ROAM_BLOCK_HEADING.description
    ]

    /** @type {string} */
    let mediaType
    if (textPlainVertexTypes.includes(node["vertex-type"]))
        mediaType = "text/plain"

    if (mediaType === undefined)
        throw Error(`unrecognized media-type for node: ${JSON.stringify(node)}`)

    // clone the node argument
    /** @type {EnrichedNode} */
    const enrichedNode = Object.assign({}, node)
    enrichedNode[`media-type`] = mediaType
    return enrichedNode
}

/**
 * Add a "vertex-type" property to the JS Object 'node'. The vertex-type values come from from the VertexType enum.
 *
 * @param {RoamNode} node
 * @returns {EnrichedNode}
 */
function addVertexType(node) {
    console.log(`addVertexType: node = ${JSON.stringify(node)}`)

    /** @type {boolean} */
    const hasTitle = node.hasOwnProperty('title')
    /** @type {boolean} */
    const hasString = node.hasOwnProperty('string')
    assert(
        (hasTitle && !hasString) ||
        (!hasTitle && hasString),
        `one and only one condition must be true: hasTitle|hasString`
    )
   /** @type {boolean} */
   const hasHeading = node.hasOwnProperty('heading')
   if(hasHeading)
        assert(!hasTitle && hasString)

   /** @type {VertexType} */
    let vertexType
    if (hasTitle)
        vertexType = VertexType.ROAM_PAGE
    else if (hasString && !hasHeading)
        vertexType = VertexType.ROAM_BLOCK_CONTENT
    else if (hasString && hasHeading)
        vertexType = VertexType.ROAM_BLOCK_HEADING
    else
        throw Error(`unrecognized Node type`)

    // clone the node argument
    /** @type {EnrichedNode} */
    const enrichedNode = Object.assign({}, node)
    enrichedNode[`vertex-type`] = vertexType.description
    return enrichedNode
}

/**
 *
 * @param {EnrichedNode} node
 * @param {Id2UidMap} id2UidMap
 * @param {Title2UidMap} title2UidMap
 * @returns {Vertex[]} - an array of Vertex that replaces the "node" param in the normalized graph. A single input Node
 * can normalize to multiple Vertices
 */
function normalizeNode(node, id2UidMap, title2UidMap) {
    console.log(`
        normalizeNode: 
        node = ${JSON.stringify(node)}, 
        id2UidMap = ${JSON.stringify(id2UidMap)},
        title2UidMap = ${JSON.stringify(title2UidMap)}
    `)
    // we don't have to carry:
    // 1. "order" property, because we are going to order the uids in the "children" property of the parent
    // 2. "id" property, because the normalized form uses uid as PK
    const keys = Object.keys(node).filter(key => !["order", "id"].includes(key))
    console.log(`normalizeNode: keys= ${JSON.stringify(keys)}`)

    /** @type {[ [KeyValuePair[], ?Vertex[]] ]} */
    const normalized = keys.map(key => normalizeProperty(key, node[key], id2UidMap, title2UidMap))
    console.log(`normalizeNode: normalized= ${JSON.stringify(normalized)}`)
    /** @type {KeyValuePair[]} */
    const allKVs = normalized.map(elem => elem[0]).flat()
    console.log(`normalizeNode: allKVs= ${JSON.stringify(allKVs)}`)
    /** @type {Vertex} */
    const vertexForNode = objectFromEntriesWithMerge(allKVs)
    /** @type {Vertex[]} */
    const derivedVertices = (normalized.map(elem => elem[1])).flat()
    console.log(`normalizeNode: derivedVertices= ${JSON.stringify(derivedVertices)}`)

    return [vertexForNode].concat(derivedVertices.filter(e => e != null))
}

/**
 * @param {string} key
 * @param {*} value
 * @param {Id2UidMap} id2UidMap
 * @param {Title2UidMap} title2UidMap
 * @returns {[KeyValuePair[], ?Vertex[]]} a new Array of key-value pairs to replace the single input key-value pair, and
 * an optional array of new Vertices that are derived from normalizing the property
 */
function normalizeProperty(key, value, id2UidMap, title2UidMap) {
    console.log(`
        normalizeProperty: 
        key = ${JSON.stringify(key)}, 
        value = ${JSON.stringify(value)}, 
        id2UidMap = ${JSON.stringify(id2UidMap)},
        title2UidMap = ${JSON.stringify(title2UidMap)}
    `)

    let normalized
    switch (key) {
        case "title":
            normalized = [ [normalizeTitle()] , null ]
            break
        case "string":
            normalized = normalizeString()
            break
        case "children":
            normalized = [ [ [key, normalizeChildren()] ], null ]
            break
        case "refs":
            normalized = [ [ [key, normalizeRefs()] ], null ]
            break
        default:
            normalized = [ [ [key, value] ], null ]
            break
    }
    console.log(`normalizeProperty: normalized = ${JSON.stringify(normalized)}`)
    return normalized

    /**
     * replace the 'title' key with 'text'
     *
     * @param {string} key - captured from enclosing function (closure)
     * @param {string} value - captured from enclosing function (closure)
     * @returns {KeyValuePair} a new key-value pair that replaces the input key-value pair
     */
    function normalizeTitle() {
        return ['text', value]
    }

    /**
     * replace page-refs based on page 'title, with page-refs based on page 'uid' replace the 'string' key with 'text'
     *
     * @param {string} key - captured from enclosing function (closure)
     * @param {string} value - captured from enclosing function (closure)
     * @param {Title2UidMap} title2UidMap - captured from enclosing function (closure)
     * @returns {[KeyValuePair[], ?Vertex[]]} a new Array of key-value pairs to replace the single input key-value pair,
     *        and an optional array of new Vertices that are derived from normalizing the property
     */
    function normalizeString() {
        /** @type {string} */
        const normal1 = normalizePageRefs(value, title2UidMap)
        console.log(`normalizeString: normal1 = ${JSON.stringify(normal1)}`)
        /** @type {[string, ?Vertex[]]} */
        const normal2 = normalizeRoamFileUrls(normal1)
        console.log(`normalizeString: normal2 = ${JSON.stringify(normal2)}`)

        return normal2
    }

    /**
     * applied to the 'string' property of roam/block nodes. Replace Firebase URLs with a random uid 
     * (using Firebase token for now) and create a roam/file type node to standin for each of those URLs.
     *
     * @param {string} target 
     * @returns {[KeyValuePair[], ?Vertex[]]} a new "string" value to replace the input "string" value,
     *        and an optional array of new Vertices that are derived from normalizing the property
     */
    function normalizeRoamFileUrls(target) {
        // regex to match Firebase URLs for files stored by Roam
        /** @type {RegExp} */
        const fireRegex = /https:\/\/firebasestorage\.[\w.]+\.com\/[-a-zA-Z0-9@:%_\+.~#?&//=]*(&token=[0-9a-f]+-[0-9a-f]+-[0-9a-f]+-[0-9a-f]+-[0-9a-f]+)/g
        const matches = [...target.matchAll(fireRegex)]
        console.log(`normalizeRoamFileUrls: matches = ${JSON.stringify(matches)}`)
        if(!matches.length)
            return [ [ ['text', target] ], null ] 
        
        /** @type {string} */
        let normalized = target
        /** @type {normal_refs} */
        let refs = []
        /** @type {Vertex[]} */
        let fileVertices = []
        matches.forEach((match) => {
            /** @type {string} */
            const url = match[0]
            // remove the '&token=' literal prefix from the regex group-1 match
            /** @type {uid} */
            const uid = match[1].slice("&token=".length)
            /** @type {Vertex} */
            const fileVertex = createRoamFileVertex(uid, url)

            refs.push(uid)
            fileVertices.push(fileVertex)
            normalized = normalized.replaceAll(url, "<<"+uid+">>")
        })
        return [ [ ['text', normalized], ['refs', refs] ], fileVertices ]    
    }

    /**
     * @param {uid} uid 
     * @param {string} source 
     * @returns {Vertex}
     */
    function createRoamFileVertex(uid, source) {
        console.log(`createRoamFileVertex: uid = ${uid}, source = ${source}`)

        return {
            "uid": uid, "source": source, "vertex-type": VertexType.ROAM_FILE.description
        }
    }
 
    /**
     * applied to the 'string' property of roam/block nodes. Replace page-refs based on page 'title, with page-refs
     * based on page 'uid'; replace the 'string' key with 'text'
     *
     * @param {string} target 
     * @param {Title2UidMap} title2UidMap
     * @returns {string} the normalized value
     */
    function normalizePageRefs(target, title2UidMap) {
        // regex to match page reference
        const pageRefRegex = /\[\[([\w\s]+)\]\]/g
        const matches = [...value.matchAll(pageRefRegex)]
        console.log(`normalizePageRefs: matches = ${JSON.stringify(matches)}`)

        let normalized = value
        matches.forEach((match) => {
            normalized = normalized.replaceAll(match[0], `[[${title2UidMap[match[1]]}]]`)
        })
        return normalized
    }
    
    /**
     * @param {raw_children} value - captured from enclosing function
     * @param {Id2UidMap} id2UidMap - captured from enclosing function
     * @returns {normal_children}
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
     * @param {raw_refs} value - captured from enclosing function
     * @param {Id2UidMap} id2UidMap - captured from enclosing function
     * @returns {normal_refs}
     */
    function normalizeRefs() {
        return value.map(e => id2UidMap[e["id"]][0])
    }

    /**
     * compare 2 JS 2-tuples that have "order" integer value at index 1 
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

        const lhsOrder = lhs[1]
        const rhsOrder = rhs[1]

        if ((!Number.isInteger(lhsOrder)) || (!Number.isInteger(rhsOrder)))
            throw "order not an integer"

        return lhsOrder - rhsOrder
    }
}

/**
 * @param {Uid2FileRefMap} fileRefMap
 * @param {JSEnvironment} env
 * @returns {Uid2RoamFileMap}
 */
async function fetchRoamFiles(fileRefMap, env) {
    console.log(`fetchRoamFiles: fileRefMap = ${JSON.stringify(fileRefMap)}, env = ${JSON.stringify(env)}`)

    if (env.isRoam) {
        return await getFilesFromRoam(fileRefMap)
    } else if (env.isTest) {
        return getFilesFromFilesystem(fileRefMap)
    } else
        throw `unsupported env: ${JSON.stringify(env)} `
}

/**
 * @param {Uid2FileRefMap} fileRefMap
 * @returns {Uid2RoamFileMap}
 */
async function getFilesFromRoam(fileRefMap) {
    console.log(`getFilesFromRoam: fileRefMap = ${JSON.stringify(fileRefMap)}`)

    /** @type {RoamFileReference[]}  */
    const fileRefs = Object.values(fileRefMap)
    console.log(`getFilesFromRoam: fileRefs = ${JSON.stringify(fileRefs)}`)
    /** @type {Promise<File>[]}  */
    const filePromises = fileRefs.map( (fileRef) => getFileFromRoam(fileRef))
    console.log(filePromises)

    /** @type {File[]}  */
    const rawFiles = await Promise.all(filePromises)
    console.log(`getFilesFromRoam: rawFiles = ${JSON.stringify(rawFiles)}`)
    console.log(rawFiles)

    /** @type {WebFile[]}  */
    const webFiles = await Promise.all(rawFiles.map( rawFile => WebFile.fromFile(rawFile)))
    console.log(`getFilesFromRoam: webFiles = ${JSON.stringify(webFiles)}`)
    console.log(webFiles)
    
    /** @type {RoamFile[]}  */
    let roamFiles = []

    fileRefs.forEach( (fileRef, index) => {
        /** @type {WebFile}  */
        const webFile = webFiles[index]
        console.log(`getFilesFromRoam: rawFile = ${JSON.stringify(webFile)}`)
        /** @type {RoamFile}  */
        const roamFile =                
                Object.fromEntries(
                    [
                        ['uid', fileRef.uid],
                        ['url', fileRef.url],
                        ['file', webFile]
                    ]
                )
        console.log(`getFilesFromRoam: roamFile = ${JSON.stringify(roamFile)}`)
        roamFiles.push(roamFile)
    })

    /** @type {Uid2RoamFileMap} */
    const uid2RoamFileMap = Object.fromEntries(roamFiles.map(roamFile => [roamFile.uid, roamFile]))

    console.log(`getFilesFromRoam: uid2RoamFileMap = ${JSON.stringify(uid2RoamFileMap)}}`)
    return uid2RoamFileMap
}

/**
 * @param {RoamFileReference} fileRef
 * @returns {Promise<File>}
 */
async function getFileFromRoam(fileRef) {
    console.log(`getFileFromRoam: fileRef = ${JSON.stringify(fileRef)}`)
    const filePromise = roamAlphaAPI.file.get({url: fileRef.url})
    console.log(`getFileFromRoam: filePromise = ${filePromise.toString()}`)
    return filePromise
}
/**
 * @param {Uid2FileRefMap} fileRefMap
 * @returns {Uid2RoamFileMap}
 */
function getFilesFromFilesystem(fileRefMap) {
    console.log(`getFilesFromFilesystem: fileRefMap = ${JSON.stringify(fileRefMap)}`)

    return Object.fromEntries(
        Object.entries(fileRefMap).map( ([uid, fileRef]) =>
            [
                uid,
                Object.fromEntries(
                    [
                        ['uid', fileRef.uid],
                        ['url', fileRef.url],
                        ['file', getFileFromFilesystem(fileRef)]
                    ]
                )
            ]
        )
    )
}

/**
 * @param {RoamFileReference} fileRef
 * @returns {RoamFile}
 */
function getFileFromFilesystem(fileRef) {
    console.log(`getFileFromFilesystem: fileRef = ${JSON.stringify(fileRef)}`)

    /** @type {string} */
    const testDataFilesPath = './test-data/files/'
    const fs = require('fs')
    /** @type {string[]} */
    const allTestFileNames = fs.readdirSync(testDataFilesPath)
    console.log(`getFileFromFilesystem: allTestFileNames= ${allTestFileNames}`)
    /** @type {string} */
    const refFileName = allTestFileNames.find(fname => fname.startsWith(fileRef.uid))
    console.log(`getFileFromFilesystem: refFileName = ${JSON.stringify(refFileName)} `)
    if(!refFileName)
        throw   `can't find file for ` +
                `fileRef.uid: ${JSON.stringify(fileRef.uid)}, ` +
                `in testDataFilesPath: ${JSON.stringify(testDataFilesPath)}`

    /** @type {string} */
    const refFilePath = testDataFilesPath + refFileName
    /** @type {Buffer} -- if no options are passed to readFileSync, defaults to return a raw Buffer  */
    const fileContents = fs.readFileSync(refFilePath)
    // console.log(`getFileFromFilesystem: fileContents = ${fileContents} `)


    // Roam files are stored in test directory with filename: uid + '_' + original-file-name
    /** @type {string} */
    const originalFileName = refFileName.split('_')[1]
    /** @type {string} */
    const fileNameExt = originalFileName.split('.').at(-1)
    const mime = require('mime')
    /** @type {string} */
    const mimeType = mime.getType(fileNameExt)
    console.log(`getFileFromFilesystem: fileNameExt= ${fileNameExt}, mimeType= ${mimeType}`)
    return new WebFile(originalFileName, 0, mimeType, BufferToArrayBuffer(fileContents))
}

/**
 * @param {Vertex[]} vertices
 * @returns {Uid2FileRefMap}
 */
function createFileRefMap(vertices) {
    console.log(`createFileRefMap: vertices = ${JSON.stringify(vertices)}`)

    /** @type {Vertex[]} */
    const roamFileVertices = vertices.filter(vertex => vertex['vertex-type'] === VertexType.ROAM_FILE.description)
    console.log(`createFileRefMap: roamFileVertices = ${JSON.stringify(roamFileVertices)}`)

    /** @type {Uid2FileRefMap} */
    const fileRefMap =
        Object.fromEntries(
            roamFileVertices.map(v =>
                [v.uid, Object.fromEntries([['uid', v.uid], ['url', v.source]]) ]
            )
        )
    console.log(`createFileRefMap: fileRefMap = ${JSON.stringify(fileRefMap)}`)

    return fileRefMap
}

/**
 * create a new Object that contains a subset of properties (only those listed in the props param) from obj
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
 * @param {JSEnvironment} env
 * @returns {RoamNode[]}
 */
function pullAllNodesFromPage(pageTitle, config, env) {
    console.log(`pullAllNodesFromPage: 
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

    // the nature of this query is to return an array of arrays, where each nested array contains a single node
    /** @type {RoamNode[][]} */
    const nodesRaw = window.roamAlphaAPI.q(query, pageTitle, rules)
    // flatten array of arrays of Nodes -> array of Nodes
    return nodesRaw.flat()
}

/**
 * build 'rules' string that is used in Roam/Datomic query
 * 
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
 * build 'query' string that is used in Roam/Datomic query
 * 
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
 * @param {Vertex[]} vertices
 * @param {Uid2RoamFileMap} roamFiles
 * @param {string} pageTitle
 * @param {any} zipModule
 * @returns {Promise<Blob>} 
 */
async function createZipArchive(vertices, roamFiles, pageTitle, zipModule) {
    console.log(`
        saveAsZipFile: 
        vertices = ${JSON.stringify(vertices)}, 
        roamFiles = ${JSON.stringify(Object.values(roamFiles).map(e => RoamFileToShortString(e)))},
        pageTitle = ${pageTitle},
        zipModule = ${JSON.stringify(zipModule)}
    `)   

    /** @type {JSZip} */
    const zip = new zipModule();
    const zipEnvelope = zip.folder(pageTitle)
    const zipFilesDir = zipEnvelope.folder('files')
    
    /** @type {string} */
    const graphJSON = JSON.stringify(vertices, null, 4)
    zipEnvelope.file(pageTitle + '.json', graphJSON)
    Object.entries(roamFiles).forEach(([uid, roamFile]) => {
        zipFilesDir.file(roamFile.file.fileName, roamFile.file.contents)
    })
        
    /** @type {Blob} */
    let zipBlob = await zip.generateAsync({type:"blob"})
    return zipBlob
}

/**
 * @param {JSEnvironment} env
 * @returns {Promise<any>}
 */
async function getJSZipModule(env) {

    if(env.isRoam) {
        return await window.RoamLazy.JSZip()
    } else if (env.isTest) {
        return require("jszip");
    } else
        throw `unsupported env: ${JSON.stringify(env)}`

}

/**
 * @param {string} fileName
 * @param {Blob} blob
 * @param {JSEnvironment} env
 * @returns {string|undefined} - if the environment isNode, then will return the path at which the file was saved
 */
function writeFile(fileName, blob, env) {
    console.log(`writeFile: fileName = ${fileName}, blob = ${JSON.stringify(blob)}, env = ${JSON.stringify(env)}`)

    /** @type {string} */
    let writePath
    if (env.isRoam)
        writeFileFromBrowser(fileName, blob)
    else if (env.isNode)
        writePath = writeFileFromNodeJS(fileName, blob)
    else
        throw `unsupported env: ${JSON.stringify(env)} `

    return writePath
}

/**
 * @param {string} fileName
 * @param {Blob} blob
 * @returns {undefined} - no return; void
 */
function writeFileFromBrowser(fileName, blob) {
    console.log(`writeFileFromBrowser: fileName = ${fileName}, blob = ${blob}`)
    window.saveAs(blob, fileName)
}

/**
 * @param {string} fileName
 * @param {Blob} blob
 * @returns {string} - the path at which the file was written
 */
async function writeFileFromNodeJS(fileName, blob) {
    console.log(`writeFileFromNodeJS: fileName = ${fileName}, blob = ${blob}`)

    const writeDir = './out/'
    const writePath = writeDir + fileName
    /** @type {ArrayBuffer} */
    let arrayBuff = await blob.arrayBuffer()
    
    const fs = require('fs')
    if (!fs.existsSync(writeDir))
        fs.mkdirSync(writeDir)
    fs.writeFileSync(writePath,  Buffer.from(arrayBuff))

    return writePath
}

/**
 * like Object.fromEntries(), except if entries argument contains multiple KeyValuePairs having same key, will
 * attempt to merge the associated values into a single Array
 * 
 * @param {KeyValuePair[]} entries
 * @returns {Object}
 */
function objectFromEntriesWithMerge(entries) {
    console.log(`objectFromEntriesWithMerge: entries = ${JSON.stringify(entries)}`)

    if( (entries==null) || (entries==undefined) )
        return null
    if(! Array.isArray(entries))
        throw TypeError()
    if(entries.length==0)
        return {}

     /** @type {Object} */
     const result = entries.reduce((accumulator, [key, value]) => {
        /** @type {boolean} */
        const hasKey = accumulator.hasOwnProperty(key)
        if(!hasKey) 
            accumulator[key]=value
        else if(!Array.isArray(accumulator[key])) {
            if(!Array.isArray(value))
                accumulator[key]=[accumulator[key],value]
            else
               accumulator[key]=[accumulator[key]].concat(value)
        }
        else if(!Array.isArray(value)) 
            accumulator[key]= accumulator[key].push(value)
        else 
            accumulator[key]= accumulator[key].concat(value)

        return accumulator
    }, {})
    console.log(`objectFromEntriesWithMerge: result = ${JSON.stringify(result)}`)
    
    return result
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

/**
 * @param {RoamFile} roamFile
 * @returns {string}
 */
function RoamFileToShortString(roamFile) {
    if(roamFile == undefined)
        return undefined
    if(roamFile == null)
        return undefined

    return `RoamFile{uid=${roamFile.uid}, file=${roamFile.file.fileName}}`
}

/**
 * convert Node.js Buffer to Web API ArrayBuffer
 * 
 * @param {Buffer} buffer
 * @returns {ArrayBuffer}
 */
function BufferToArrayBuffer(buffer) {
    const arrayBuffer = new ArrayBuffer(buffer.length);
    const view = new Uint8Array(arrayBuffer);
    for (let i = 0; i < buffer.length; ++i) {
      view[i] = buffer[i];
    }
    return arrayBuffer;
}