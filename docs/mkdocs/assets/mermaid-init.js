/* Force securityLevel loose so Material's mermaid.initialize() keeps HTML labels and themeCSS. */
(function () {
  if (typeof mermaid === "undefined" || typeof mermaid.initialize !== "function") return;
  var initialize = mermaid.initialize.bind(mermaid);
  mermaid.initialize = function (config) {
    initialize(Object.assign({}, config, { securityLevel: "loose" }));
  };
})();
