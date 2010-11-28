(function() {
    var Artemis = {
        // Parses a mission timestamp from a URL and converts it to a number of 
        // seconds
        parseMissionTime: function(mission_time) {
            t = _.map(mission_time.split(':'), function(i) {
                return parseInt(i, 10);
            });
            return t[3] + t[2]*60 + t[1]*3600 + t[0]*86400;
        }
    };

    $(function() {
    });

    window.Artemis = Artemis;
})();

