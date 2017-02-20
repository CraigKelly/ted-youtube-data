function one(url) {
    var page = require('webpage').create();
    page.open(url, function(status) {
        console.log("Status: " + status + "  " + url);
        if (status === "success") {
            page.render('example.png');
        }

        phantom.exit();
    });
}

one('http://www.youtube.com/watch?v=wfW3aZCFfLA');

//click #action-panel-overflow-button
//wait for and click #action-panel-overflow-menu button.yt-ui-menu-item with data-trigger-for="action-panel-stats"
//wait for and grab:
// #watch-actions-stats td.stats-bragbar --> get children: .metric-label text AND .bragbar-metric text
