/* scrollstart and scrollstop cribbed directly from jQuery Mobile
 *
 * Copyright 2010, jQuery Project
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 */
var scrollEvent = "touchmove scroll";
$.event.special.scrollstart = {
    enabled: true,
    
    setup: function() {
        var thisObject = this,
            $this = $( thisObject ),
            scrolling,
            timer;
        
        function trigger( event, state ) {
            scrolling = state;
            var originalType = event.type;
            event.type = scrolling ? "scrollstart" : "scrollstop";
            $.event.handle.call( thisObject, event );
            event.type = originalType;
        }
        
        // iPhone triggers scroll after a small delay; use touchmove instead
        $this.bind( scrollEvent, function( event ) {
            if ( !$.event.special.scrollstart.enabled ) {
                return;
            }
            
            if ( !scrolling ) {
                trigger( event, true );
            }
            
            clearTimeout( timer );
            timer = setTimeout(function() {
                trigger( event, false );
            }, 50 );
        });
    }
};
$.event.special.scrollstop = {
    setup: function() {
        $( this ).bind( "scrollStart", $.noop );
    }
};
// End jQuery cribbed code

(function() {
    Artemis.animationTime = 250;

    // Parses a mission timestamp from a URL and converts it to a number of
    // seconds
    Artemis.parseMissionTime = function(mission_time) {
        t = _.map(mission_time.split(':'), function(i) {
            return parseInt(i, 10);
        });
        return t[3] + t[2]*60 + t[1]*3600 + t[0]*86400;
    };

    Artemis.replaceWithSpinner = function(e, white) {
        var src = white ? Artemis.assets.spinnerWhite : Artemis.assets.spinner;
        $(e).replaceWith('<img src="' + src + '" alt="">');
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
            $.ajax({
                url: '/homepage-quote/', 
                success: this.refreshCallback,
                cache: false,
                dataType: 'json'
            });
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
        
        // HACK: Replace position: fixed with update-on-scroll for footer
        var userAgent    = navigator.userAgent.toLowerCase();
        var phasesFooter = $( '#phases' );
        if ( -1 < userAgent.indexOf( 'webkit' ) && phasesFooter.length ) {
            var mobileUAs = [
                // iOS devices
                'ipad', 'ipod', 'iphone',
                // Android
                'android',
            ];
            
            // Cycle through each mobile UA we care about and see
            // if this is one of them
            var isMobile = false;
            for (var i = mobileUAs.length - 1; i >= 0; i--){
                var mobileUA = mobileUAs[i];
                
                if ( -1 < userAgent.indexOf( mobileUA ) ) {
                    isMobile = true;
                    break;
                }
            };
            
            // If we have a mobile UA, change the footer to update
            if ( isMobile ) {
                var phasesShower = null;
                
                // Hide the footer when scrolling
                $( document ).bind( 'scrollstart', function () {
                    phasesFooter.hide();
                    clearTimeout( phasesShower );
                } );
                
                // Re-show the footer when scrolling stops
                $( document ).bind( 'scrollstop', function () {
                    phasesFooter.css({
                        'top': $( window ).scrollTop() + window.innerHeight - phasesFooter.height(),
                    });
                    phasesShower = setTimeout( function () {
                        phasesFooter.fadeIn();
                    }, 500 );
                } );
                
                // alert( $( window ).height() + ":" + window.innerHeight + ":" + document.body.offsetHeight );
                // Forcibly reset the footer position on load
                phasesFooter.hide();
                setTimeout( function () {
                    phasesFooter.css({
                        'position': 'absolute',
                        'top': $( window ).scrollTop() + window.innerHeight - phasesFooter.height(),
                    });
                    phasesFooter.show();
                }, 500 );
            }
        }
    });
})();

