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

    // Backbone.History, but using pushState instead of hashes
    Artemis.History = function() {
        this.handlers = [];
        _.bindAll(this, 'loadUrl');
        this.path = this.getPath();
    };

    _.extend(Artemis.History.prototype, {
        getPath: function(loc) {
            return (loc || window.location).pathname;
        },

        start: function() {
            var self = this;
            $(window).bind('popstate', function() {
                var path = self.getPath();
                if (path != this.path) {
                    var callback = self.routeUrl(path);
                    if (callback) {
                        callback(path);
                    }
                }
            });
            $('a').live('click', function(e) {
                // Only absolute links work
                path = $(this).attr('href');
                if (path && path[0] == '/') {
                    var callback = self.routeUrl(path);
                    if (callback) {
                        self.saveLocation(path);
                        callback(path);
                        e.preventDefault();
                        return false;
                    }
                    else {
                        self.navigateToPath(path);
                    }
                }
            });
        },

        route: Backbone.History.prototype.route,

        // Attempt to load the current URL fragment. If a route succeeds with a
        // match, returns `true`. If no defined routes matches the fragment,
        // returns `false`.
        routeUrl: function(path) {
            for (var i = 0; i < this.handlers.length; i++) {
                if (this.handlers[i].route.test(path)) {
                    return this.handlers[i].callback;
                }
            }
        },
        
        saveLocation: function(path) {
            this.path = path;
            history.pushState(null, document.title, path);
        },

        navigateToPath: function(path) {
            if (path === undefined) {
                path = this.getPath();
            }
            window.location = path;
        }
    });

    Artemis.LogLine = Backbone.Model.extend({
        
    }, {
        fromElement: function(e) {
            return new Artemis.LogLine({
                'id': parseInt(e.id.split('-')[2], 10)
            });
        }
    });

    Artemis.LogLineCollection = Backbone.Collection.extend({
        model: Artemis.LogLine,
        initialize: function(models, options) {
            _.bindAll(this);
        },

        updateFromElement: function(source) {
            if (!source) {
                source = $('#transcript');
            }
            
            this.add(_.map(source.children('div'), _.bind(function(e) {
                var logLine = new Artemis.LogLine.fromElement(e);
                return logLine;
            }, this)));
        }
    });

    var tspatt = '-?\\d{2}:\\d{2}:\\d{2}:\\d{2}';

    Artemis.Controller = Backbone.Controller.extend({
        initialize: function(options) {
            this.route('/page/', 'page', this.page);
            this.route('/page/('+tspatt+')/', 'page', this.page);
        },

        page: function(start, end) {
            if (!$('#content').hasClass('transcript')) {
                Backbone.history.navigateToPath();
                return;
            }
            if (!this.logLineCollection) {
                this.logLineCollection = new Artemis.LogLineCollection();
                this.logLineCollection.updateFromElement();
            }
            else {
                $.getJSON(Backbone.history.getPath(), _.bind(function(data) { 
                    $('title').text(data.title);
                    // If there is a crest, load the entire page
                    if ($(data.crest).children().length) {
                        $('#content').children().html(data.content);
                        $('#crest').replaceWith(data.crest);
                    }
                    else {
                        content = $(data.content);
                        var transcript = content.filter('#transcript');
                        this.logLineCollection.updateFromElement(transcript);
                        if (parseInt(transcript.children('div').attr('id').split('-')[2], 10) < this.logLineCollection.first().id) {
                            $('#transcript').prepend(transcript.children());
                        }
                        else {
                            $('#transcript').append(transcript.children());
                        }
                        if ($('#load-previous')) {
                            $('#load-previous').replaceWith(content.find('#load-previous'));
                        }
                        if ($('#load-more')) {
                            $('#load-more').replaceWith(content.find('#load-more'));
                        }
                    }

                }, this));
            }
        },
        

        _routeToRegExp: function(route) {
            return new RegExp('^' + route + '$');
        }
    });

    $(function() {
        Backbone.history = new Artemis.History();
        Artemis.controller = new Artemis.Controller();
        Backbone.history.start();
    });

    window.Artemis = Artemis;
})();




