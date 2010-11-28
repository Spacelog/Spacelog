
Artemis.PhasesView = Backbone.View.extend({
    el: $('#phases'),
    events: {
        'click .map':   'toggleMap'
    },
    cookieName: 'mapIsOpen',
    openHeight: 150,
    closedHeight: 38.4,
    

    initialize: function() {
        this.el.find('ul').append('<li><a href="#" class="map">Map</a></li>');
        if (this.getIsOpen()) {
            this.el.css({height: this.openHeight});
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
        this.el.stop().animate({height: height});
        console.debug(!isOpen);
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
});


