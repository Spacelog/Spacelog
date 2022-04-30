function getTranscriptNameFromURL () {
    // Transcript is last path segment, and may contain [-_\w]
    var transcript = location.pathname.replace(
        /^.*\/.*\/([-_\w]+)\/$/, "$1"
    );
    
    // If we actually have a transcript, add it to the URL
    if ( transcript && transcript != location.pathname ) {
        return transcript;
    }
    return '';
}

Artemis.LogLine = Backbone.Model.extend({
    initialize: function(options) {
        this.id = parseInt(options.el.attr('id').slice(9), 10);
        options.model = this;
        this.view = new Artemis.LogLineView(options);
    },

    getURL: function() {
        return this.view.el.find('.time a').attr('href');
    },

    getTimestamp: function() {
        return this.getURL().split('/')[1];
    },

    getPageURL: function() {
        return '/page/'+this.getTimestamp()+'/#log-line-'+this.id;
    },

    getTranscriptPage: function() {
        return this.view.el.attr('data-transcript-page');
    },

    getText: function() {
        return this.view.el.find('dd').text().replace(/^\s+/, '').replace(/\s+$/, '');
    },

    getTweetableQuote: function() {
        var tweetableQuote = this.getText();
        if(tweetableQuote.length > 103) {
          tweetableQuote = tweetableQuote.substring(0, 100) + '...';
        }
        return '"' + tweetableQuote + '"';
    }
});

Artemis.HighlightedLogLineCollection = Backbone.Collection.extend({
    model: Artemis.LogLine,
    
    comparator: function(line) {
        return line.id;
    },

    add: function(model, options) {
        Backbone.Collection.prototype.add.call(this, model, options);
        this.highlight();
    },
    
    remove: function(model, options) {
        model.view.unHighlight();
        Backbone.Collection.prototype.remove.call(this, model, options);
        this.highlight();
    },

    // This could be more efficient by working it out in _add and _remove
    highlight: function() {
        this.each(_.bind(function(line) {
            line.view.highlight();
        }, this));
    },

    getURL: function() {
        var first = this.first().getURL().split('/')[1];
        var last = this.last().getURL().split('/')[1];
        var l = document.location;
        
        var out = [l.protocol, '//', l.host, '/', first, '/'];
        if (first != last) {
            out.push(last);
            out.push('/');
        }
        
        // If we actually have a transcript, add it to the URL
        var transcript = getTranscriptNameFromURL();
        if ( transcript ) {
            out.push(transcript + '/');
        }
        
        out.push('#log-line-' + this.first().id);
        return out.join('');
    }
});

Artemis.LogLineView = Backbone.View.extend({
    events: {
        'click dd #expand-previous':  'expandPrevious',
        'click dd #expand-next':      'expandNext',
        'click dd #contract-previous': 'contractPrevious',
        'click dd #contract-next':    'contractNext'
    },

    rangeAdvisoryTemplate: '<p id="range-advisory">\
                            Spoken on <%= time %><span>. </span><i>Link to this<span> transcript range is</span>:</i> <input type="text" name="" value="<%= permalink %>">\
                            <iframe allowtransparency="true" frameborder="0" scrolling="no" tabindex="0" class="twitter-share-button twitter-count-horizontal" src="<%= twitter_iframe_url %>" title="Twitter For Websites: Tweet Button"></iframe>\
                            </p>',

    highlight: function() {
        this.el.addClass('highlighted');
        this.el.css({'cursor': 'auto'});

        // Reset range UI
        this.el.find('.range-ui').remove();
        
        if (this.model.collection.first().id == this.model.id) {
            this.el.addClass('first');
            if (this.previousElement()) {
                this.addRangeUI('expand-previous');
            }
            else if (Artemis.transcriptView.loadPreviousButton) {
                Artemis.transcriptView.loadPreviousButton.loadMore();
            }

            this.addRangeUI('selection-close');
            if (this.model.collection.size() > 1) {
                this.addRangeUI('contract-previous');
            }

            Artemis.phasesView.setOriginalTranscriptPage(this.model.getTranscriptPage());
        }
        else {
            this.el.removeClass('first');
        }
        this.removeRangeAdvisory();
        if (this.model.collection.last().id == this.model.id) {
            this.el.addClass('last');
            if (this.nextElement()) {
                this.addRangeUI('expand-next');
            }
            else if (Artemis.transcriptView.loadMoreButton) {
                Artemis.transcriptView.loadMoreButton.loadMore();
            }
            if (this.model.collection.size() > 1) {
                this.addRangeUI('contract-next');
            }
            this.createRangeAdvisory();
        }
        else {
            this.el.removeClass('last');
        }
    },

    unHighlight: function() {
        this.el.removeClass('highlighted first last');
        this.el.css({'cursor': 'pointer'});
        this.el.find('.range-ui').remove();
        this.removeRangeAdvisory();
    },

    addRangeUI: function(id) {
        var href = '#';
        if (id == 'selection-close') {
            href = this.model.getPageURL();
        }
        this.el.children('dd').append('<a href="'+href+'" class="range-ui" id="'+id+'"></a>');
    },

    expandPrevious: function() {
        var prev = this.previousElement();
        if (prev) {
            var line = new Artemis.LogLine({el: prev});
            this.model.collection.add(line);
        }
        return false;
    },
    expandNext: function() {
        var next = this.nextElement();
        if (next) {
            var line = new Artemis.LogLine({el: next});
            this.model.collection.add(line);
        }
        return false;
    },
    contractPrevious: function() {
        this.model.collection.remove(this.model.collection.first());
        return false;
    },
    contractNext: function() {
        this.model.collection.remove(this.model.collection.last());
        return false;
    },
    createRangeAdvisory: function() {
        if (!this.el.children('#range-advisory').length) {
            var twitterURL = "https://platform.twitter.com/widgets/tweet_button.html?count=horizontal&amp;lang=en&amp;" +
                             "text=" + encodeURIComponent( this.model.collection.first().getTweetableQuote() ) + "&amp;" +
                             "url=" + encodeURIComponent( this.model.collection.getURL() ) + "&amp;" +
                             "via=spacelog&amp;related=devfort";

            var rangeAdvisory = $(_.template(this.rangeAdvisoryTemplate, {
                time: this.model.collection.first().view.el.find('time').data('range-advisory'),
                permalink: this.model.collection.getURL(),
                twitter_iframe_url: twitterURL
            }));
            // Select text in text field on focus
            rangeAdvisory.find('input').click(function() {
                $(this).focus().select();
            });
            this.el.append(rangeAdvisory);
        }
    },
    removeRangeAdvisory: function() {
        this.el.find('#range-advisory').remove();
    },
    previousElement: function() {
        var el = this.el.prevAll('div').get(0);
        if (el) {
            return $(el);
        }
    },
    nextElement: function() {
        var el = this.el.nextAll('div').get(0);
        if (el) {
            return $(el);
        }
    }

});

Artemis.LoadMoreButtonView = Backbone.View.extend({
    events: {
        'click a':  'loadMore',
    },

    initialize: function(options) {
        _.bindAll(this, 'loadMore', 'loadMoreCallback');
        this.isPrevious = options.isPrevious;
    },

    loadMore: function() {
        var a = this.el.children('a');
        if (a.size()) {
            this.elLast = this.el.clone();
            jQuery.ajax({
                url:        a.attr('href')+'?json',
                dataType:   'json',
                success:    this.loadMoreCallback,
                error:      function(jqXHR, textStatus, errorThrown) {
                    window.location = a.attr('href');
                }
            });
            _gaq.push(['_trackPageview', a.attr('href')]);
            Artemis.replaceWithSpinner(a);
        }
        return false;
    },

    loadMoreCallback: function(data) {
        var content = $(data.content);
        var crest = $(data.crest);
        var topLogLine = $('#transcript div')[0];
        var transcriptTop = $('#transcript')[0].offsetTop;
        var initialWindowTop  = $( window ).scrollTop();

        // We've hit the start of a new phase
        if (crest.children().size()) {
            // If we're going backwards, show the new crest
            if (this.isPrevious) {
                $('#crest').replaceWith(data.crest);
            }
            // Don't load anything if we're highlighted and reached the end of
            // a phase
            else if (Artemis.transcriptView.highlightedLines.size()) {
                this.el.children().replaceWith(this.elLast.clone().children());
                return;
            }
            // If going forwards, skip to next phase 
            else {
                window.location = this.elLast.children('a').attr('href');
                return;
            }
        }
        else if (this.isPrevious) {
            $('#crest').html('');
        }
        
        // To start with, get rid of the spinner
        this.el.children().replaceWith(this.elLast.clone().children());

        // See if the new content has a button
        var newEl = content.find('#'+this.el.attr('id'));
        if (newEl.size() && newEl.children().size()) {
            this.el.children().replaceWith(newEl.children());
        }
        else {
            this.el.children().remove();
        }

        // With lines highlighted, hide the button
        if (Artemis.transcriptView.highlightedLines.size()) {
            this.el.children().hide();
        }

        // Allow clicking of links in new content
        Artemis.transcriptView.bustPreventDefault(content.filter('#transcript'));
        
        // Insert new lines
        if (this.isPrevious) {
            $('#transcript').prepend(content.filter('#transcript').children());
            
        }
        else {
            $('#transcript').append(content.filter('#transcript').children());
        }

        // Rehighlight all rows to add any missing "+" buttons
        Artemis.transcriptView.highlightedLines.highlight();

        // Readjust height of overlay
        Artemis.transcriptView.setOverlayHeight();
        
        // Mark the page boundaries for the window onscroll handler
        Artemis.transcriptView.markTranscriptPageBoundaries();

        // Keep the topmost item in (almost the same place)
        $( window ).scrollTop(
            topLogLine.offsetTop - transcriptTop + initialWindowTop
        );
        // HACK: on detail pages, for some reason a redraw is needed before we
        // get the right offsetTop for topLogLine.
        setTimeout(function () {
            $( window ).scrollTop(
                topLogLine.offsetTop - transcriptTop + initialWindowTop
            );
        }, 0);
    },

    hide: function() {
        this.el.children().fadeOut(Artemis.animationTime);
    },

    show: function() {
        this.el.children().fadeIn(Artemis.animationTime);
    }
});


Artemis.TranscriptView = Backbone.View.extend({
    el: $('#transcript').parent(),
    overlay: $('<div id="highlight-overlay"></div>'),
    events: {
        'click #transcript > div':  'selectionOpen',
        'click #transcript > div .time a': 'selectionOpen',
        'click #transcript > div dd #selection-close': 'selectionClose'
    },
    // The log lines which are currently highlighted
    highlightedLines: new Artemis.HighlightedLogLineCollection(),
    
    initialize: function() {
        _.bindAll(this, 'selectionClose', 'setOverlayHeight', 'scrollWindow', 'keyDown');

        if ($('#load-previous').size()) {
            this.loadPreviousButton = new Artemis.LoadMoreButtonView({
                el: $('#load-previous'),
                isPrevious: true,
            });
        }
        if ($('#load-more').size()) {
            this.loadMoreButton = new Artemis.LoadMoreButtonView({
                el: $('#load-more'),
            });
        }

        this.overlay.click(this.selectionClose);
        this.el.find('#transcript').css({'cursor': 'pointer'});

        this.markTranscriptPageBoundaries();
        $(window).scroll(this.scrollWindow);

        $('body').keydown(this.keyDown);

        this.bustPreventDefault(this.el.find('#transcript'));

    },

    markTranscriptPageBoundaries: function() {
      // Mark elements at the end of source transcript pages
      // This will give us fewer elements to look at in the window.onscroll handler
      var logLineElements = this.el.find('#transcript > div'),
          currentPage, i;

      for(i = logLineElements.length - 1; i >= 0; i--) {
          var ll = $(logLineElements[i]),
              page = ll.attr('data-transcript-page');

          if(page != currentPage) {
              ll.attr('data-end-transcript-page', true);
              currentPage = page;
          }
      }
    },

    gatherCurrentSelection: function() {
        // Gather any currently selected lines
        var content = $('#content');
        if (content.hasClass('with-highlight')) {
            content.removeClass('with-highlight');
            if (this.loadPreviousButton) this.loadPreviousButton.hide();
            if (this.loadMoreButton) this.loadMoreButton.hide();
           
            _.each($('#transcript > .highlighted'), _.bind(function(e) {
                this.highlightedLines.add(
                    new Artemis.LogLine({el: $(e)})
                );
            }, this));

            this.showOverlay(false);
        }
    },

    selectionOpen: function(e) {
        if (this.highlightedLines.size() == 0) {
            var target = $(e.currentTarget).closest('div');
            var line = new Artemis.LogLine({el: target});
            this.highlightedLines.add(line);
            
            if (this.loadPreviousButton) this.loadPreviousButton.hide();
            if (this.loadMoreButton) this.loadMoreButton.hide();

            this.showOverlay();
            line.view.el.find('#range-advisory').hide().show('blind', {}, Artemis.animationTime);
        }
        return false;
    },

    selectionClose: function(e) {
        this.el.find('.range-ui').fadeOut(Artemis.animationTime);
        this.el.find('#range-advisory').hide('blind', Artemis.animationTime, _.bind(function() {
            this.highlightedLines.each(function(line) {
                line.view.unHighlight();
            });
            this.highlightedLines = new Artemis.HighlightedLogLineCollection();

        }, this));
        this.hideOverlay();
        if (this.loadPreviousButton) this.loadPreviousButton.show();
        if (this.loadMoreButton) this.loadMoreButton.show();
        return false;
    },

    showOverlay: function(animate) {
        if (animate === undefined) {
            animate = true;
        }
        this.overlay.css({
            'background-color': 'black',
            'opacity': '0.5'
        });
        if (animate) {
            this.overlay.css({'opacity': '0'});
            this.overlay.animate({'opacity': '0.5'}, Artemis.animationTime);
        }

        // HACK: on detail pages, for some reason a redraw is needed before we
        // get the right height
        setTimeout(this.setOverlayHeight, 0);
        this.overlay.appendTo($('body'));
    },

    setOverlayHeight: function() {
        this.overlay.css({
            'height': ($(document).height() - 38) + 'px'
        });
    },

    hideOverlay: function() {
        this.overlay.animate({'opacity': 0}, Artemis.animationTime, _.bind(function() {
            this.overlay.detach();
        }, this));
    },

    scrollWindow: function(e) {
        if (this.highlightedLines.size() > 0) {
            return true;
        }

        var target = $(window).scrollTop();
        var visible = _.detect(
                this.el.find('#transcript > div[data-end-transcript-page]'),
                function(el) { return el.offsetTop >= target; }
            );

        if(!visible) {
            return;
        }

        var page = $(visible).attr('data-transcript-page');
        Artemis.phasesView.setOriginalTranscriptPage(page);
    },
    bustPreventDefault: function(transcriptElement) {
        // Bust through the div's click event to allow all links to work apart from 
        // the time link
        transcriptElement.find('dt.speaker a, dd a').click(function(e) {
            e.stopImmediatePropagation();
            return true;
        });
    },
    keyDown: function(e) {
        if(e.keyCode === 27) {
            this.selectionClose();
            return false;
        }
        else {
            return true;
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
        if(this.el.find('img.orbital').length === 0) {
            return;
        }

        // this.el.find('ul').append('<li><a href="#" class="map">Show map</a></li>');
        this.el.find('ul').find('li:last').before('<li><a href="#" class="map">Show map</a></li>');
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
    },

    setOriginalTranscriptPage: function(page) {
        if(typeof page === "undefined") { return; }
        
        // Transcript is last path segment, and may contain [-_\w]
        var transcript = getTranscriptNameFromURL();
        
        // If we actually have a transcript, add it to the URL
        if ( transcript ) {
            transcript += '/';
        }
        this.el.find('.original a')
          .attr('href', '/original/' + transcript + page + '/')
          .attr('title', 'View original transcript, page ' + page);
    }
});


$(function() {
    Artemis.phasesView = new Artemis.PhasesView();
    Artemis.transcriptView = new Artemis.TranscriptView();
    Artemis.transcriptView.gatherCurrentSelection();
    
    // If we don't have a hash, and the page has selected loglines, move to them
    if ( !location.hash && document.getElementById( 'show-selection' ) ) {
        location.hash = 'show-selection';
    }
});


