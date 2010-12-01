(function() {
    var Artemis = {
        animationTime: 250,

        // Parses a mission timestamp from a URL and converts it to a number of 
        // seconds
        parseMissionTime: function(mission_time) {
            t = _.map(mission_time.split(':'), function(i) {
                return parseInt(i, 10);
            });
            return t[3] + t[2]*60 + t[1]*3600 + t[0]*86400;
        },

        replaceWithSpinner: function(e, white) {
            var suffix = '';
            if (white) {
                suffix = '-white';
            }
            $(e).replaceWith('<img src="/assets/img/ajax-loader'+suffix+'.gif" alt="">');
        }
    };

    Artemis.HomepageQuoteView = Backbone.View.extend({
        el: $('#homepage-quote'),
        events: {
            'click i .refresh': 'refresh'
        },

        initialize: function() {
            _.bindAll(this, 'refreshCallback');
        },

        refresh: function() {
            Artemis.replaceWithSpinner(this.el.find('blockquote').children(), true);
            $.getJSON('/homepage-quote/', this.refreshCallback);
            return false;
        },

        refreshCallback: function(data) {
            this.el.children().replaceWith($(data.quote).children());
        }
    });

    $(function() {
        // Placeholder support for legacy browsers
        $('input[placeholder], textarea[placeholder]').placeholder();

        Artemis.homepageQuoteView = new Artemis.HomepageQuoteView();
            

    });

    window.Artemis = Artemis;
})();

