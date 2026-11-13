/* Force securityLevel loose so Material's mermaid.initialize() keeps HTML labels and themeCSS.
   Mermaid 11 inserts an edgeLabel group for every edge, then only sets its transform when the
   label text is non-empty. Unlabeled edges (for example `MCP <--> Tools`) stay at the SVG
   origin, and themeCSS paints that empty foreignObject as a visible box. Material renders
   via mermaid.render() and puts the returned SVG in a closed shadow root, so strip the
   empty groups from that string. */
(function () {
  if (typeof mermaid === "undefined") return;

  var EMPTY_EDGE_LABEL =
    /<g class="edgeLabel"(?:\s[^>]*)?>\s*<g class="label"[^>]*>\s*<foreignObject[^>]*>\s*<div[^>]*>\s*<span class="edgeLabel[^"]*">(?:\s|&nbsp;)*<\/span>\s*<\/div>\s*<\/foreignObject>\s*<\/g>\s*<\/g>/g;

  function stripEmptyEdgeLabels(svg) {
    return svg.replace(EMPTY_EDGE_LABEL, "");
  }

  if (typeof mermaid.initialize === "function") {
    var initialize = mermaid.initialize.bind(mermaid);
    mermaid.initialize = function (config) {
      return initialize(Object.assign({}, config, { securityLevel: "loose" }));
    };
  }

  if (typeof mermaid.render === "function") {
    var render = mermaid.render.bind(mermaid);
    mermaid.render = function () {
      return Promise.resolve(render.apply(mermaid, arguments)).then(function (result) {
        if (result && typeof result.svg === "string") {
          result.svg = stripEmptyEdgeLabels(result.svg);
        }
        return result;
      });
    };
  }
})();
