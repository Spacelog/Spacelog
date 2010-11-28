
Artemis.TranscriptView = Backbone.View.extend({
    el: $('#transcript').parent(),
    events: {
        'click #load-previous a': 'loadPrevious',
        'click #load-more a':     'loadMore'
    },

    initialize: function() {
        _.bindAll(this);
    },

    lastLoadMorePath: null,

    loadPrevious: function() {
        var a = $('#load-previous a');
        if (a) {
            $.getJSON(a.attr('href'), _.bind(function(data) {
                this.loadMoreCallback(data, true);
            }, this));
            Artemis.replaceWithSpinner(a);
            this.lastLoadMorePath = a.attr('href');
        }
        return false;
    },

    loadMore: function() {
        var a = $('#load-more a');
        if (a) {
            $.getJSON(a.attr('href'), _.bind(function(data) {
                this.loadMoreCallback(data, false)
            }, this));
            Artemis.replaceWithSpinner(a);
            this.lastLoadMorePath = a.attr('href');
        }
        return false;
    },

    loadMoreCallback: function(data, previous) {
        var content = $(data.content);
        var crest = $(data.crest);

        if (previous) {
            // Load previous button may disappear
            if (content.find('#load-previous').length) {
                $('#load-previous').replaceWith(content.find('#load-previous'));
            }
            else {
                $('#load-previous').remove();
            }
            if (crest.children().length) {
                $('#crest').replaceWith(data.crest);
            }
            $('#transcript').prepend(content.filter('#transcript'));
        }
        else {
            // If there is a crest, we've hit the next phase
            if (crest.children().length) {
                window.location = this.lastLoadMorePath;
                return;
            }
            $('#load-more').replaceWith(content.find('#load-more'));
            $('#transcript').append(content.filter('#transcript'));
        }
    }
});


Artemis.PhasesView = Backbone.View.extend({
    el: $('#phases'),
    events: {
        'click .map':   'toggleMap'
    },
    cookieName: 'mapIsOpen',
    openHeight: 150,
    closedHeight: 40.4,
    

    initialize: function() {
        this.el.find('ul').append('<li><a href="#" class="map">Show map</a></li>');
        if (this.getIsOpen()) {
            this.el.css({height: this.openHeight});
            this.el.addClass("open");
        }
    },

    toggleMap: function() {
        var height;
        var isOpen = this.getIsOpen();
        if (isOpen) {
            height = this.closedHeight;
        }
        else {
            height = this.openHeight;
        }
        this.el.toggleClass('open', !isOpen);
        this.el.stop().animate({height: height});
        this.setIsOpen(!isOpen);
        return false;
    },

    getIsOpen: function() {
        if ($.cookie(this.cookieName) == 'true') {
            return true;
        }
        else {
            return false;
        }
    },

    setIsOpen: function(v) {
        $.cookie(this.cookieName, v, {path: '/'});
    }
});


$(function() {
    Artemis.phasesView = new Artemis.PhasesView();
    Artemis.transcriptView = new Artemis.TranscriptView();
});


