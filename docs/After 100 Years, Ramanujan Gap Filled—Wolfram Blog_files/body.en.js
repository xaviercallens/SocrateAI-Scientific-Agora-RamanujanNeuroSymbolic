/* Global ui functionality for the <body> element.

   developer:   marionm
   requires:    jQuery
                /common/framework/js/head.en.js
   ========================================================================== */

/* ==========================================================================
   legacy variables; phasing out, stop using these
   ========================================================================== */

var _headerOffset = 50; // obsolete; clearance needed to properly offset linked elements from the thin header
var _headerThick = 50; // obsolete; maximum height of header, should always match css
var _headerThin = 50; // obsolete; minimum height of header, should always match css
var _headerHeight = 50; // height of header, should always match css

/* ==========================================================================
   functions
   ========================================================================== */

// obsolete; use _getAdjustedOffset instead
function _getTopOffset(el, header) {
    _getAdjustedOffset(el, header);
}

// obsolete; use _scrollToOffset instead
function _getScrollTop(href) {
    _scrollToOffset(href);
}

/* Return an element's true top offset that has been adjusted to include its margin-top, border-top, and (optionally) the global header height.

   params:      el (string, default=false) the element to assess, can be any standard jQuery selector
                header (boolean, default=true) if true and the global header is present, subtract _headerOffset from the offset value
   returns:     integer or float
   ========================================================================== */

function _getAdjustedOffset(el, header) {
    var el = el || false;
    var header = header || true;
    var offset = 0;
    if (el && $(el).length > 0) {
        offset = Math.ceil($(el).offset().top);
        var diff = Math.ceil(parseFloat($(el).css('margin-top')) + parseFloat($(el).css('border-top-width')));
        if (diff > 0) offset -= diff;
        if (header && $('#_header').length > 0) offset -= _headerHeight;
    }
    return offset;
}

/* A scrollTop function enhanced to compensate for the global header's height when jumping to specific elements or areas of the page.

   params:      href (string, no default), the anchor's href attribute
   returns:     n/a
   ========================================================================== */

function _scrollToOffset(href) {
    // use the current location if no href is specified
    var url = href || window.location.href;

    // search for hash
    var hash = url.indexOf('#');
    var len = url.slice(hash).length;
    if (hash == -1 || len < 2) return false;

    // search for element identifiers
    var id = url.slice(hash);
    var name = 'a[name=' + id.replace('#', '') + ']';
    if ($(id).length == 0 && $(name).length == 0) return false;

    // determine which element selector to use
    if ($(id).length > 0) {
        var select = id; // use element id
    } else if ($(id).length == 0 && $(name).length > 0) {
        var select = name; // use element name
    } else {
        return false;
    }

    // get element's top position
    var top = _getAdjustedOffset(select) || 0;

    // scroll to adjusted top position
    if (top > 0) {
        $('html, body').stop(true, true).animate({
            scrollTop: top + 'px'
        }, 1);
        //history.pushState(null, null, '#' + hash);
    }

    return false;
}

/* document ready function
   ========================================================================== */

$(document).ready(function() {

/* ==========================================================================
   gui header
   ========================================================================== */

    if ($('#_header').length > 0) {

        // remove href from tab urls (they're only for users without js or when the dropdowns are disabled)
        $('html:not(._header-no-dropdowns) #_nav-center div:not(#_nav-alpha) ._label, html:not(._header-no-dropdowns) #_nav-right div:not(#_nav-cloud) ._label').prop('href', '');

        // look for hash in url and matching element on the page; if found, trigger scroll animation
        $(window).on('hashchange load pageshow', function() {
            _scrollToOffset();
        });

        // look for anchors with a hash in the href attribute; if found, replace default scroll with animated scroll on click
        $('a[href*="#"]:not([href="#"])').on('click', function(e) {
            if ($(this).prop('href') === window.location.href) {
                // prevent default anchor behavior
                e.preventDefault();
                // scroll to anchor
                _scrollToOffset($(this).prop('href'));
            }
        });

        /* main nav dropdowns
           ================================================================== */

        // show main dropdowns on click
        $('html:not(._header-no-dropdowns) #_nav-center div:not(#_nav-alpha) ._label').on('click', function(e) {
            // ignore default functionality of anchor tag
            e.preventDefault();

            // hide any other open dropdowns
            hideUserDropdown();
            hideSearchDropdown();
            hideMobileDropdown();

            // determine what to do with main dropdowns
            if ($('#_nav-center ._open').length <= 0 || ($('#_nav-center ._open').length > 0 && !$(this).hasClass('_open'))) {
                // hide dropdowns
                $('#_nav-center ._open').removeClass('_open');

                // open this dropdown
                $(this).addClass('_open');

                // show dimmer
                $('#_dimmer').removeClass('hide').addClass('show');

                // refocus
                $(this).next('._dropdown').trigger('focus');

                // temporarily allow scrolling if total nav height is taller than the viewport
                var scrolltop = $(window).scrollTop() || 0,
                    windowheight = $(window).height(),
                    headertop = $('#_header').offset().top || 0,
                    headerheight = $('#_header').height() || 0,
                    dropdownheight = $('html:not(._header-no-dropdowns) #_header ._label._open + ._dropdown').height() || 0,
                    bufferzone = 100;

                if (windowheight < headertop + headerheight + dropdownheight + bufferzone) {
                    $('#_header').addClass('_temporarily-scrollable').css('top', scrolltop);
                } else {
                    $('#_header').removeClass('_temporarily-scrollable').css('top', '');
                }
            } else {
                // hide dropdowns
                hideMainDropdowns(this);
            }
        });

        // hide main dropdowns
        var hideMainDropdowns = function(t) {
            var t = t || '#_header';

            // hide dropdowns
            $('#_nav-center ._open').removeClass('_open');

            // hide dimmer
            $('#_dimmer').removeClass('show').addClass('hide');

            // refocus
            $(t).trigger('focus');
        };

        /* user nav dropdown
           ================================================================== */

        // show user dropdown on click
        $('html:not(._header-no-dropdowns) #_nav-user ._label').on('click', function(e) {
            // ignore default functionality of anchor tag
            e.preventDefault();

            // hide any other open dropdowns
            hideMainDropdowns();
            hideSearchDropdown();
            hideMobileDropdown();

            // open user dropdown
            $(this).toggleClass('_open').next('._dropdown').slideToggle(100);

            // refocus
            $(this).trigger('focus');
        });

        // hide user dropdown
        var hideUserDropdown = function() {
            $('#_nav-user ._label').removeClass('_open').next('._dropdown').slideUp(0);
        };

        /* search dropdown
           ================================================================== */

        // show search dropdown on click
        $('html:not(._header-no-dropdowns) #_nav-search ._label').on('click', function(e) {
            // ignore default functionality of anchor tag
            e.preventDefault();

            // close any other open dropdowns
            hideMainDropdowns();
            hideUserDropdown();
            hideMobileDropdown();

            // open search dropdown
            $(this).toggleClass('_open').next('._dropdown').slideToggle(100);

            // refocus
            $('#_search-input').trigger('focus');
        });

        // hide search dropdown
        var hideSearchDropdown = function() {
            // reset placeholder text
            $('#_search-form').get(0).reset();

            // close dropdown
            $('#_nav-search ._label').removeClass('_open').next('._dropdown').slideUp(0);
        };

        /* search input
           ========================== */

        // ensure localized placeholder text is being used
        $('#_search-form').get(0).reset();

        // avoid blank submissions
        $('#_search-form').on('submit', function(e) {
            if ($('#_search-input').val() == '') e.preventDefault();
        });

        // close button
        $('#_search-form .close').on('click', function(e) {
            // prevent form submission
            e.preventDefault();

            // hide search dropdown
            hideSearchDropdown();
        });

        /* mobile nav dropdown
           ================================================================== */

        // show mobile dropdown on click
        $('#_nav-mobile ._label').on('click', function(e) {
            // ignore default functionality of anchor tag
            e.preventDefault();

            // hide any other open dropdowns
            hideMainDropdowns();
            hideUserDropdown();
            hideSearchDropdown();

            // determine what to do with mobile dropdown
            if (!$(this).hasClass('_open')) {
                // show dimmer
                $('#_dimmer').removeClass('hide').addClass('show');

                // open mobile dropdown
                $(this).addClass('_open').next('._dropdown').slideToggle(100, assessHeaderPosition);
            } else {
                // hide mobile dropdown
                hideMobileDropdown();
            }
        });

        // hide mobile dropdown
        var hideMobileDropdown = function() {
            // hide dimmer
            $('#_dimmer').removeClass('show').addClass('hide');

            // close mobile dropdown
            $('#_nav-mobile ._label').removeClass('_open').next('._dropdown').slideUp(0, assessHeaderPosition);

            hideLevel1Content();
            hideLevel2Content();
        };

        // level 1 click behavior
        $('#_nav-mobile ._level-1-label').on('keyup', function(e) {
            var key = e.which || e.keyCode;
            if (key === 13) {
                // enter key triggers click
                $(this).trigger('click');
            }
        });
        $('#_nav-mobile ._level-1-label').on('click', function() {
            if (!$(this).parent().hasClass('_open')) {
                // reset icons
                $('#_nav-mobile ._level-1-label svg.rotated').removeClass('rotated');

                // close open drawers
                $('#_nav-mobile ._level-1 ._open').removeClass('_open');
                $('#_nav-mobile ._level-1-content').slideUp(0);

                // hide inactive labels
                $('#_nav-mobile ._level-1 > *, #_nav-mobile ._level-0 > *').addClass('hide');

                // switch icons
                $(this).find('svg').addClass('rotated');

                // open this drawer
                $(this).parent().addClass('_open').removeClass('hide');
                $(this).next('._level-1-content').slideDown(300, assessHeaderPosition);

                // temporarily allow scrolling if total nav height is taller than the viewport
                var scrolltop = $(window).scrollTop() || 0,
                    windowheight = $(window).height(),
                    headertop = $('#_header').offset().top || 0,
                    headerheight = $('#_header').height() || 0,
                    dropdownheight = $('html:not(._header-no-dropdowns) #_header ._label._open + ._dropdown').height() || 0,
                    bufferzone = 100;

                if (windowheight < headertop + headerheight + dropdownheight + bufferzone) {
                    $('#_header').addClass('_temporarily-scrollable').css('top', scrolltop);
                } else {
                    $('#_header').removeClass('_temporarily-scrollable').css('top', '');
                }
            } else {
                hideLevel1Content();
            }
        });

        // hide level 1 content
        var hideLevel1Content = function() {
            // reset icons
            $('#_nav-mobile ._level-1-label svg.rotated').removeClass('rotated');

            // restore hidden labels
            $('#_nav-mobile ._level-1 > *, #_nav-mobile ._level-0 > *').removeClass('hide');

            // close open drawers
            $('#_nav-mobile ._level-1 ._open').removeClass('_open');
            $('#_nav-mobile ._level-1-content').slideUp(0, assessHeaderPosition);
        };

        // level 2 click behavior
        $('#_nav-mobile ._level-2-label').on('keyup', function(e) {
            var key = e.which || e.keyCode;
            if (key === 13) {
                // enter key triggers click
                $(this).trigger('click');
            }
        });
        $('#_nav-mobile ._level-2-label').on('click', function() {
            if (!$(this).parent().hasClass('_open')) {
                // reset icons
                $('#_nav-mobile ._level-2-label svg use:first-of-type').removeClass('hide');
                $('#_nav-mobile ._level-2-label svg use:last-of-type').addClass('hide');

                // close open drawers
                $('#_nav-mobile ._level-2 ._open').removeClass('_open');
                $('#_nav-mobile ._level-2-content').slideUp(0);

                // switch icons
                $(this).find('svg use:first-of-type').addClass('hide');
                $(this).find('svg use:last-of-type').removeClass('hide');

                // open this drawer
                $(this).parent().addClass('_open');
                $(this).next('._level-2-content').slideDown(300, assessHeaderPosition);

                // temporarily allow scrolling if total nav height is taller than the viewport
                var scrolltop = $(window).scrollTop() || 0,
                    windowheight = $(window).height(),
                    headertop = $('#_header').offset().top || 0,
                    headerheight = $('#_header').height() || 0,
                    dropdownheight = $('html:not(._header-no-dropdowns) #_header ._label._open + ._dropdown').height() || 0,
                    bufferzone = 100;

                if (windowheight < headertop + headerheight + dropdownheight + bufferzone) {
                    $('#_header').addClass('_temporarily-scrollable');
                } else {
                    $('#_header').removeClass('_temporarily-scrollable');
                }
            } else {
                hideLevel2Content();
            }
        });

        // hide level 2 content
        var hideLevel2Content = function() {
            // reset icons
            $('#_nav-mobile ._level-2-label svg use:first-of-type').removeClass('hide');
            $('#_nav-mobile ._level-2-label svg use:last-of-type').addClass('hide');

            // close open drawers
            $('#_nav-mobile ._level-2 ._open').removeClass('_open');
            $('#_nav-mobile ._level-2-content').slideUp(0, assessHeaderPosition);
        };

        /* monitor scrolltop position
           ================================================================== */

        var lastposition = $(window).scrollTop() || 0;

        var assessHeaderPosition = function() {
            var scrolltop = $(window).scrollTop() || 0,
                windowheight = $(window).height(),
                headertop = $('#_header').offset().top || 0,
                headerheight = $('#_header').height() || 0,
                dropdownheight = $('html:not(._header-no-dropdowns) #_header ._label._open + ._dropdown').height() || 0,
                bufferzone = 100;

            //console.log(lastposition+', '+scrolltop+', '+windowheight+', '+headertop+', '+headerheight+', '+dropdownheight+', '+bufferzone);

            if ($('#_header').hasClass('_temporarily-scrollable') && (scrolltop < headertop || scrolltop > (headertop + headerheight + dropdownheight))) {
                // user scrolled beyond content boundaries, return to default state and close dropdowns
                hideMainDropdowns();
                hideMobileDropdown();

                // restore default scroll state
                $('#_header').removeClass('_temporarily-scrollable').css('top', '');
            } else if (!$('#_header').hasClass('_temporarily-scrollable') && dropdownheight > 0 && scrolltop < lastposition) {
                // user scrolled up, close dropdowns regardless
                hideMainDropdowns();
                hideMobileDropdown();
            }

            lastposition = scrolltop;
        };

        assessHeaderPosition();
        $(window).on('scroll', _throttle(assessHeaderPosition));

        /* shared dropdown functionality
           ================================================================== */

        // click anywhere below the header to hide dropdowns
        $('html:not(._header-no-dropdowns) #_header').nextAll().on('click', function() {
            hideMainDropdowns();
            hideUserDropdown();
            hideSearchDropdown();
            hideMobileDropdown();
        });

        // hide dropdowns if back-forward cache is detected
        $(window).on('pageshow', function(e) {
            if (e.originalEvent.persisted) {
                hideMainDropdowns();
                hideUserDropdown();
                hideSearchDropdown();
                hideMobileDropdown();
            }
        });

    }

/* ==========================================================================
   gui footer
   ========================================================================== */

    if ($('html:not(._no-footer) #_footer').length > 0) {
        // load alternate language picker options
        if ($('#_language-picker ._dropdown-menu').length > 0 && typeof _languagePickerOptions !== 'undefined' && _languagePickerOptions.length > 0) {
            $('#_language-picker ._dropdown-menu').html(_languagePickerOptions);
        }

        // show language dropdown on click
        $('#_language-picker > div:first-of-type').on('click', function(e) {
            // ignore click action on html element
            e.stopPropagation();

            // open language dropdown
            $(this).toggleClass('_open').next('._dropdown').slideToggle(100);

            // refocus
            $(this).trigger('focus');
        });

        // hide language dropdown
        var hideLanguageDropdown = function(e) {
            $('#_language-picker > div:first-of-type').removeClass('_open').next('._dropdown').slideUp(0);
        };

        // hide language dropdown when you click outside of the language
        $('html').on('click', hideLanguageDropdown);

        // insert footer offset div
        $('#_footer').before('<div id="_footer-offset"></div>');

        // use footer offset div to fill gaps between the global footer and the end of the page
        var offsetFooter = _throttle(function() {
            // remove existing offset
            $('#_footer-offset').hide().height(0);
            // get the difference between the viewport height and the document height
            var difference = parseInt($(window).height() - $('body').height() - parseFloat($('html').css('border-top-width')));
            if (difference > 0) {
                $('#_footer-offset').show().height(difference);
            }
        });

        // do first assessment on document ready and reassess as needed
        offsetFooter();
        $(window).on('load resize', offsetFooter);
    } else {
        // remove footer, if present
        $('#_footer').remove();
        if ($('#_language-picker._standalone-language-picker').length > 0 && $('#_language-picker._standalone-language-picker #_language-picker-select option:not(:disabled)').length > 0) {
            $('#_language-picker._standalone-language-picker').show().removeClass('hide');
            // make language picker switch to selected language on change
            $('#_language-picker-select').on('change', function() {
                window.location.href = $(this).val();
            });
        } else {
            // remove the language picker
            $('#_language-picker').remove();
        }
    }

/* ==========================================================================
   gui alert
   ========================================================================== */

    // once enabled, temporarily set your computer's clock forward to the start and end dates/times to confirm they are working correctly
    var alertActive = false; // set to true to enable
    var alertStart = new Date('August 8 2015 07:55:00'); // set start date and time
    var alertEnd = new Date('August 8 2015 16:00:00'); // set end date and time; test same as the start date
    var alertNow = new Date();
    var alertMessage = '<div id="_alert"><p>Note: Our purchasing system is down for maintenance right now. We\'re sorry for the inconvenience. We expect purchasing to be available again by 4pm CDT.</p><p>Close</p></div>';

    // only trigger when active and date is in range
    if (alertActive && alertStart < alertNow && alertNow < alertEnd) {
        // only trigger once per site
        if (document.cookie.indexOf('_alert') < 0) {
            // append message to page
            $('body').append(alertMessage);

            // remove alert on click
            $('#_alert').on('click', function() {
                $(this).remove();
            });

            // set cookie
            document.cookie = '_alert=1; expires='+alertEnd.toUTCString();
        }
    }

    // force alert to show itself when _show_alert parameter is found in the url
    if (window.location.href.indexOf('_show_alert') > -1) {
        // append message to page
        $('body').append(alertMessage);

        // remove alert on click
        $('#_alert').on('click', function() {
            $(this).remove();
        });
    }

/* ==========================================================================
   utility functionality
   ========================================================================== */

    /* widow management
       ====================================================================== */

    // prevent lone words on the last line of text when it wraps; automatically inserts a non-breaking space character between the last two words (or elements) found; ONLY FOR PLAIN TEXT, NOT FOR TEXT THAT INCLUDES HTML
    $('.no-widows, .heirs-no-widows > *').each(function() {
        var text = $(this).text().trim().split(' ');
        var last = text.pop();
        $(this).html(text.join(' ')+(text.length > 0 ? '&nbsp;'+last : last));
    });

    /* back/forward cache
       ====================================================================== */

    // disable back/forward cache by resetting forms
    $(window).on('load pageshow', function() {
        $('form.no-bfc').each(function() {
            $(this).get(0).reset();
        });
    });

    /* hide/show/remove
       ====================================================================== */

    $('.hide__ready, .heirs-hide__ready > *').removeClass('show').addClass('hide');
    $('.show__ready, .heirs-show__ready > *').removeClass('hide').addClass('show');
    $('.remove__ready, .heirs-remove__ready > *').remove();

    $(window).on('pageshow', function() {
        $('.hide__pageshow, .heirs-hide__pageshow > *').removeClass('show').addClass('hide');
        $('.show__pageshow, .heirs-show__pageshow > *').removeClass('hide').addClass('show');
        $('.remove__pageshow, .heirs-remove__pageshow > *').remove();
    });

    $(window).on('pagehide', function() {
        $('.hide__pagehide, .heirs-hide__pagehide > *').removeClass('show').addClass('hide');
        $('.show__pagehide, .heirs-show__pagehide > *').removeClass('hide').addClass('show');
        $('.remove__pagehide, .heirs-remove__pagehide > *').remove();
    });

    $(window).on('load', function() {
        $('.hide__load, .heirs-hide__load > *').removeClass('show').addClass('hide');
        $('.show__load, .heirs-show__load > *').removeClass('hide').addClass('show');
        $('.remove__load, .heirs-remove__load > *').remove();
    });

});