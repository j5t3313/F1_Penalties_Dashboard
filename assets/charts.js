(function () {
    var HIERARCHY_CLICK_EVENTS = ["plotly_treemapclick", "plotly_sunburstclick", "plotly_icicleclick"];

    function disableDrilldown(graph) {
        if (typeof graph.on !== "function" || graph._drilldownDisabledFor === graph.on) {
            return;
        }
        graph._drilldownDisabledFor = graph.on;
        HIERARCHY_CLICK_EVENTS.forEach(function (eventName) {
            graph.on(eventName, function () {
                return false;
            });
        });
    }

    new MutationObserver(function () {
        document.querySelectorAll(".js-plotly-plot").forEach(disableDrilldown);
    }).observe(document.documentElement, {childList: true, subtree: true});
})();
