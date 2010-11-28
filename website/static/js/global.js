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
            return this._cleanPath((loc || window.location).pathname);
        },

        _cleanPath: function(path) {
            return path.replace(/#.+?$/, '').replace(/\?.+?$/, '');
        },

        start: function() {
            var self = this;
            $(window).bind('popstate', function() {
                var path = self.getPath();
                var callback = self.routeUrl(path);
                if (callback) {
                    callback(path);
                }
            });
            $('a').live('click', function(e) {
                // Only absolute links work
                path = self._cleanPath($(this).attr('href'));
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
            console.debug(e);
            return new Artemis.LogLine({
                'id': parseInt(e.id.split('-')[2], 10)
            });
        }
    });

    Artemis.LogLineCollection = Backbone.Collection.extend({
        model: Artemis.LogLine,
        initialize: function(models, options) {
            _.bindAll(this);
            this.previousId = null;
            this.nextId = null;
        },

        updateFromContent: function(sourceContent) {
            var destContent, destTranscript;
            if (!sourceContent) {
                sourceContent = $('#content').children().children();
                var sourceTranscript = sourceContent.filter('#transcript');
            }
            else {
                var sourceTranscript = sourceContent.filter('#transcript');
                destContent = $('#content');
                destTranscript = destContent.find('#transcript');
            }
            
            if (sourceContent.find('#load-previous')) {
                if (destContent) {
                    destContent.find('#load-previous').replaceWith(
                        sourceContent.find('#load-previous')
                    );
                }
            }
            if (sourceContent.find('#load-more')) {
                if (destContent) {
                    destContent.find('#load-more').replaceWith(
                        sourceContent.find('#load-more')
                    );
                }
            }
            
            this.add(_.map(sourceTranscript.children('div'), _.bind(function(e) {
                var logLine = new Artemis.LogLine.fromElement(e);
                if (destTranscript) {
                    if (logLine.id < this.first().id) {
                        $('#transcript').prepend(e);
                    }
                    else {
                        $('#transcript').append(e);
                    }
                }
                return logLine;
            }, this)));
        }
    });

    var tspatt = '-?\\d{2}:\\d{2}:\\d{2}:\\d{2}';

    Artemis.Controller = Backbone.Controller.extend({
        initialize: function(options) {
            this.route('/page/', 'page', this.page);
            this.route('/page/('+tspatt+')/', 'page', this.page);
            this.route('/('+tspatt+')/', 'logLine', this.logLine);
            this.route('/('+tspatt+')/('+tspatt+')/', 'logLine', this.logLine);
            
            // After a route is triggered, save it as the previous route
            this.previous = null;
            this.bind('all', function(eventName) {
                var bits = eventName.split(':');
                if (bits[0] == 'route') {
                    this.previous = bits[1];
                }
            });
        },
        
        page: function(start) {
            this.checkContentClasses(['transcript']);
            this.transition('page', start);
        },
        
        logLine: function(start, end) {
            this.checkContentClasses(['transcript']);
            this.transition('logLine', start, end);
        },

        transition: function(next) {
            var prev = Artemis.transitions[this.previous]
            if (prev && prev[next]) {
                prev[next].apply(this, Array.prototype.slice.call(arguments, 1));
            }
        },
        
        checkContentClasses: function(classes) {
            if (!_.all(classes, function(c) { return $('#content').hasClass(c) })) {
                Backbone.history.navigateToPath();
                return;
            }
        },

        _routeToRegExp: function(route) {
            return new RegExp('^' + route + '$');
        }
    });

    Artemis.transitions = {
        null: {
            'page': function() {
                this.logLineCollection = new Artemis.LogLineCollection();
                this.logLineCollection.updateFromContent();
            }
        },

        'page': {
            'page': function() {
                $.getJSON(Backbone.history.getPath()+'?json', _.bind(function(data) { 
                    $('title').text(data.title);
                    // If there is a crest, load the entire page
                    // TODO: do this if this page is not next/prev
                    if ($(data.crest).children().length) {
                        $('#content').children().html(data.content);
                        $('#crest').replaceWith(data.crest);
                        $(document).scrollTop(0);
                    }
                    else {
                        content = $(data.content);
                        this.logLineCollection.updateFromContent(content);
                    }

                }, this));
            },
            'logLine': function() {
                var content = $('#content');
                content.addClass('with-highlight');
            }
        },


        'logLine': {
            'page': function() {
                var content = $('#content');
                content.removeClass('with-highlight');
            }
        }
    };

    $(function() {
        Backbone.history = new Artemis.History();
        Artemis.controller = new Artemis.Controller();
        Backbone.history.start();
    });

    window.Artemis = Artemis;
})();




