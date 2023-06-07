
const env = checkEnvironment()
console.log(`env= ${JSON.stringify(env)}`)

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
        (typeof window.roamAlphaAPI !== "undefined" )

    return { isBrowser: isBrowser, isNode: isNode, isWebWorker: isWebWorker, isJsDom: isJsDom, isDeno: isDeno, isRoam: isRoam }
}
