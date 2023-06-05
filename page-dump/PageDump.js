/**
 * @license
 * SPDX-FileCopyrightText: © 2023 Joe Panico <joe@panmachine.biz>
 * SPDX-License-Identifier: MIT
 */

class AssertionError extends Error {
  constructor(value) {
      super(`"${value}"`);
      this.name = 'AssertionError';
  }
}

/**
 * This Enum represents the type identifiers for the individual output elements 
 */
const VertexType = Object.freeze(
  {
    /** 1-1 w/ Roam `Page` type Node */
	ROAM_PAGE: Symbol("roam-page"),
    /** 1-1 w/ Roam `Block` type Node */
	ROAM_BLOCK: Symbol("roam-block"),
    /** a file that was uploaded to, and now managed by, Roam */
	ROAM_FILE: Symbol("roam-file")
  }
)

// this is an Enum
const FollowLinksDirective = Object.freeze(
  {
	DONT_FOLLOW: Symbol("DONT_FOLLOW"),
	SHALLOW: Symbol("SHALLOW"),
	DEEP: Symbol("DEEP")
  }
)

const dumpConfig = {
  "targetPageTitle": "Page 3",
  "followChildren": FollowLinksDirective.DEEP,
  "followRefs": FollowLinksDirective.DEEP,
  "includeProperties": ["uid", "string", "title", "children", "order", "refs", "id" ],
  /** these are properties synthesized by this script
   * (not having direct Roam representation)
   */
  "addProperties": ["vertex-type", "media-type"]
}

const pageContentFlattened = 
  pullPageNodes(dumpConfig.targetPageTitle, dumpConfig.followChildren, dumpConfig.followRefs)
console.log(`pageContentFlattened = ${JSON.stringify(pageContentFlattened)}`)

const pageShell = 
  pullPageNodes(dumpConfig.targetPageTitle,FollowLinksDirective.DONT_FOLLOW, FollowLinksDirective.DONT_FOLLOW)
console.log(`pageShell = ${JSON.stringify(pageShell)}`)

const pageNodes = [].concat(pageShell, pageContentFlattened)
const pageNodesReshaped = pageNodes.map(e => pick(e, dumpConfig.includeProperties))
const vertices = normalizeNodes(pageNodesReshaped, dumpConfig.addProperties)
const outputFileName = dumpConfig.targetPageTitle + `.json`

saveAsJSONFile(vertices, outputFileName)

function normalizeNodes(nodes, toAddProperties) {
    console.log(`
      normalizeNodes: 
      nodes = ${JSON.stringify(nodes)}, 
      toAddProperties = ${JSON.stringify(toAddProperties)}
  `)

  const id2UidMap = Object.fromEntries(nodes.map(x => [x.id, [x.uid,x.order]]));
  console.log(`normalizeNodes: id2UidMap = ${JSON.stringify(id2UidMap)}`)
  
  // all of the nodes that do not have a title property will be successively
  // mapped to the "undefined" property
  let title2UidMap = Object.fromEntries(nodes.map(x => [x.title, x.uid]));
  // remove the bogus "undefined" property that corresponds to nodes with no titles
  delete title2UidMap["undefined"];
  
  console.log(`normalizeNodes: title2UidMap = ${JSON.stringify(title2UidMap)}`)

  const normalizedNodes= nodes.map(node => normalizeNode(node, id2UidMap, title2UidMap))
  return addProperties(normalizedNodes, toAddProperties)
}

function addProperties(nodes, toAddProperties) {
  console.log(`
    addProperties: 
    nodes = ${JSON.stringify(nodes)}, 
    toAddProperties = ${JSON.stringify(toAddProperties)}
  `)
  if (! (Array.isArray(toAddProperties) && toAddProperties.length))
    return nodes

  var vertices = nodes
  if(toAddProperties.includes("vertex-type"))
    vertices = vertices.map(v => addVertexType(v))
  if(toAddProperties.includes("media-type"))
    vertices = vertices.map(v => addMediaType(v))
  
  return vertices
}

function getAddPropertyFunction(propertyName) {
  switch(propertyName) {
    case "vertex-type":
      return addVertexType
    case "media-type":
      return addMediaType
    default:
      throw Error(`getAddPropertyFunction: unrecognized propertyName: ${propertyName}`)
  }
}

function addMediaType(node) {
  console.log(`addMediaType: node = ${JSON.stringify(node)}`)
  var mediaType
  if([VertexType.ROAM_PAGE.description, VertexType.ROAM_BLOCK.description].includes(node["vertex-type"]))
    mediaType = "text/plain"

  if(mediaType === undefined)
    throw Error(`unrecognized media type for node: ${JSON.stringify(node)}`)

  // clone the node argument
  const vertex = Object.assign({}, node)
  vertex[`media-type`] = mediaType
  return vertex  
}

function addVertexType(node) {
  console.log(`addVertexType: node = ${JSON.stringify(node)}`)
  const hasTitle = node.hasOwnProperty('title')
  const hasString = node.hasOwnProperty('string')
  assert( 
    ( hasTitle && !hasString ) ||
    ( !hasTitle && hasString ), 
    `one and only one condition must be true: hasTitle|hasString`
  )
  var vertexType
  if(hasTitle)
    vertexType = VertexType.ROAM_PAGE
  else if(hasString)
    vertexType = VertexType.ROAM_BLOCK
  else
    throw Error(`unrecognized Node type`)

  // clone the node argument
  const vertex = Object.assign({}, node)
  vertex[`vertex-type`] = vertexType.description
  return vertex  
}

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
  const keys = Object.keys(node).filter(key => !["order", "id"].includes(key) )
  console.log(`keys: ${JSON.stringify(keys)}`)

  return Object.fromEntries(keys.map(key => normalizeProperty(key, node[key], id2UidMap, title2UidMap)));
}

// return a [key,value] tuple (i.e. array)
function normalizeProperty(key, value, id2UidMap, title2UidMap) {
  console.log(`
    normalizeProperty: 
    key = ${JSON.stringify(key)}, 
    value = ${JSON.stringify(value)}, 
    id2UidMap = ${JSON.stringify(id2UidMap)},
    title2UidMap = ${JSON.stringify(title2UidMap)}
  `)
  switch(key) {
    case "string":
        return [key, normalizeString()]
    case "children":
        return [key, normalizeChildren()]
    case "refs":
        return [key, normalizeRefs()]
    default:
        return [key, value]
  }

  // nested functions are closures

  // replace page-refs based on page "title" with page-refs based on page "uid"
  // the "string" property value is a JS string
  function normalizeString() {
    // regex to match page reference
    const pageRefPattern = `\\[\\[([\\w\\s]+)\\]\\]`
    const matches = Array.from(value.matchAll(pageRefPattern))
    console.log(`normalizeString: matches = ${JSON.stringify(matches)}`)
    
    let normalized = value
    matches.forEach( (match) => {
        normalized = normalized.replaceAll(match[0], `[[${title2UidMap[match[1]]}]]`)
    })
    return normalized
  }

  // the "children" property value is a JS array of obj/dict, where each 
  // obj has a single property: "id", whose value is a 2 element array; uid,order
  function normalizeChildren() {
    // this creates an array of pairs/tuples/2elementarrays: [uid(String), order(int)]
    const unorderedUids = value.map( child => id2UidMap[child["id"]])
    console.log(`unorderedUids: ${JSON.stringify(unorderedUids)}`)
    const orderedUids = unorderedUids.sort(compareOrder)
    console.log(`orderedUids: ${JSON.stringify(orderedUids)}`)
    // only take the uid-- leave order behind
    return orderedUids.map(e => e[0])
  }

  // the "refs" property value is a JS array of obj/dict, where each 
  // obj has a single property: "id", whose value is a 2 element array; uid,order
  function normalizeRefs() {
    return value.map( e => id2UidMap[e["id"]][0])
  }

  // compare 2 JS arrays that have "order" value at index 1
  function compareOrder(lhs, rhs) {
    if( (lhs==null) || (rhs==null) )
      throw "null argument"
    
    lhsOrder = lhs[1]
    rhsOrder = rhs[1]
    
    if( (!Number.isInteger(lhsOrder)) || (!Number.isInteger(rhsOrder)) )
      throw "order not an integer"
    
    return lhsOrder - rhsOrder
  }
}

/*
 * create a new Object that contains a subset of properties 
 * (only those listed in the props arg) from obj
 */
function pick(obj, props) {
  return Object.fromEntries(
    Object.entries(obj).filter(([key, val]) => props.includes(key) && val != null)
  )
}

function pullPageNodes(pageTitle, followChildren, followRefs) {
  console.log(`
    pullPageNodes: 
    pageTitle = ${pageTitle}, 
    followChildren = ${followChildren.description},
    followRefs = ${followRefs.description}
  `)
  
  const query = buildQuery(followChildren, followRefs)
  const rules = buildRules(followChildren, followRefs)
  console.log(`pullPageNodes: query = ${query}, rules = ${rules}`)
  
  // the nature of this query is to return an array of arrays, where each nested array
  // contains a single node
  const nodesRaw = window.roamAlphaAPI.q(query, pageTitle, rules)
  // flatten array of arrays of nodes -> array of nodes
  return nodesRaw.flat()
}

function buildRules(followChildren, followRefs) {
  console.log(`buildRules: followChildren = ${followChildren.description}, followRefs = ${followRefs.description}`)
  if (
    followChildren==FollowLinksDirective.DONT_FOLLOW &&
    followRefs==FollowLinksDirective.DONT_FOLLOW
  ) { return "[]" }
  
  const proximateRefsRule = 
    (followRefs==FollowLinksDirective.DONT_FOLLOW) ? 
      "": "[?a :block/refs ?b]"
  const proximateChildrenRule = 
    (followChildren==FollowLinksDirective.DONT_FOLLOW) ? 
      "": "[?a :block/children ?b]"
  const inductiveRefsRule = 
    (followRefs==FollowLinksDirective.DEEP) ? 
      "[?proximate_linker :block/refs ?b]" : ""
  const inductiveChildrenRule = 
    (followChildren==FollowLinksDirective.DEEP) ? 
      "[?proximate_linker :block/children ?b]" : ""
  const inductiveLinkerRule = 
    ( !inductiveRefsRule && !inductiveChildrenRule ) ?
      "":
      `[ (linker ?b ?a ) 
          ( or 
            ${inductiveRefsRule}
            ${inductiveChildrenRule} 
          )         
          (linker ?proximate_linker ?a) 
        ]`  
  return (
    `[ 
        [ (linker ?b ?a )
          ( or 
            ${proximateRefsRule} 
            ${proximateChildrenRule} 
          )
        ]
        ${inductiveLinkerRule}   
     ]`
  )
}

function buildQuery(followChildren, followRefs) {
  console.log(`buildQuery: followChildren = ${followChildren.description}, followRefs = ${followRefs.description}`)
  
  const targetEntity = 
    (followChildren==FollowLinksDirective.DONT_FOLLOW && 
     followRefs==FollowLinksDirective.DONT_FOLLOW) ? 
    "page" : "node"
  const linkerClause = 
    (followChildren==FollowLinksDirective.DONT_FOLLOW && 
     followRefs==FollowLinksDirective.DONT_FOLLOW) ? 
    "" : "(linker ?node ?page)"
  return (
  `[:find 
      (pull ?${targetEntity} [*] )
    :in $ ?target_page_title % 
    :where
      [?page :node/title ?target_page_title]
      ${linkerClause}
   ]`
  )
}

function saveAsJSONFile(obj, fileName) {
  console.log(`saveAsJSONFile: obj = ${obj}, fileName = ${fileName}`)

  // 3rd arg triggers pretty formatting: number of spaces per level of indent
  const json = JSON.stringify(obj, null, 4)
  console.log(`saveAsJSONFile: json = ${json}`)

  const options = { type: "application/json" }
  const blob = new Blob([json], options)
  window.saveAs(blob, fileName)
}

function assert(value, errorMessage) {
    if(!value)
        throw new AssertionError(errorMessage)
}
