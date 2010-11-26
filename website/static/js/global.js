(function() {
    var Artemis = {};

    // Backbone.History, but using pushState instead of hashes
    Artemis.History = function() {
        this.handlers = [];
        _.bindAll(this, 'loadUrl');
    };

    var slashRegex = /^\/+/;

    _.extend(Artemis.History.prototype, {
        _stripSlash: function(s) {
            return s.replace(slashRegex, '');
        },

        getPath: function(loc) {
            return this._stripSlash((loc || window.location).pathname);
        },

        start: function() {
            var self = this;
            $(window).bind('popstate', function() {
                self.loadUrl(self.getPath());
            });
            $('a').live('click', function(e) {
                // Only absolute links work
                href = $(this).attr('href');
                if (href && href[0] == '/') {
                    href = self._stripSlash(href);
                    self.loadUrl(href);
                    e.preventDefault();
                    return false;
                }
            });
            self.loadUrl(path);
        },

        route: Backbone.History.prototype.route,

        loadUrl: function(path) {
            if (this.routeUrl(path)) {
                if (path != this.getPath()) {
                    this.saveLocation(path);
                }
            }
            else if (path != this.getPath()) {
                window.location = '/'+path;
            }
        },

        // Attempt to load the current URL fragment. If a route succeeds with a
        // match, returns `true`. If no defined routes matches the fragment,
        // returns `false`.
        routeUrl: function(path) {
            var matched = _.any(this.handlers, function(handler) {
                if (handler.route.test(path)) {
                    handler.callback(path);
                    return true;
                }
            });
            return matched;
        },
        
        saveLocation: function(path) {
            history.pushState(null, document.title, '/'+path);
        }
    });

    Artemis.LogLine = Backbone.Model.extend({
        
    });

    Artemis.LogLineCollection = Backbone.Collection.extend({

    });

    Artemis.Controller = Backbone.Controller.extend({
        routes: {
            //'': 'homepage',
            //'phases/': 'phases'
        },

        homepage: function() {
        },

        phases: function() {
        
        }
    });

    $(function() {
        Backbone.history = new Artemis.History();
        new Artemis.Controller();
        Backbone.history.start();
    });

    window.Artemis = Artemis;
})();
