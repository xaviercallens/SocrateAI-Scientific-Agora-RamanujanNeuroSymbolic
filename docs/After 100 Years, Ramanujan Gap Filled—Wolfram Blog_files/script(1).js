$(document).ready(function(){
    //categories dropdowns
    $('body').click(function(){
        $('.categories-list-menu').addClass('hide');
        $('.categories').removeClass('active');
    });
    $('.categories').click(function(e) {
        e.stopPropagation();
        if (!$(this).hasClass('active')) {
            $('.categories-list-menu').addClass('hide');
            $('.categories').removeClass('active');
            $(this).toggleClass('active');
            $(this).next().toggleClass('hide');
        } else {
            $('.categories-list-menu').addClass('hide');
            $('.categories').removeClass('active');
        }
    });
    $('.categories-list-menu').click(function(e){
        e.stopPropagation();
    });


    //super snowflakes that strip_tags()/css can't handle
    $('.wp-content p').has('a:empty').remove();


    //comments
    if(document.URL.indexOf('#comments') != -1 || document.URL.indexOf('#comment-') != -1) {
        $('#comment-section').removeClass('hide');
        $('.expand-collapse').removeClass('expand');
        $('.expand-collapse').addClass('collapse');
        //$('#show-all-comments').addClass('hide');
    }
    if(document.URL.indexOf('?replytocom') != -1 || document.URL.indexOf('#respond') != -1) {
        $('#join-small').addClass('hide');
        $('#join-big').removeClass('hide');
        $('#comment-section').removeClass('hide');
        $('.expand-collapse').removeClass('expand');
        $('.expand-collapse').addClass('collapse');
    }

    $('#join-small').click( function() {
        $('#join-big').removeClass('hide');
        $('#comment').focus();
        $('#join-small').addClass('hide');
    });
    $('input#cancel').click( function() {
        //close
        $('#join-big').addClass('hide');
        $('#join-small').removeClass('hide');
        //erase inputs
        $(this).closest('form').find(".hover-label-input .label-target").val('');
        $(this).closest('form').find('label').removeClass('label-hover');
    });
    $('#comments-heading').click( function() {
        $('#comment-section').toggleClass('hide');
        $('.expand-collapse').toggleClass('expand');
        $('.expand-collapse').toggleClass('collapse');
    });


    //comments, fancy labels
    $('.hover-label-input .label-target').focus( function() {
        $(this).parent().find('label').addClass('label-hover');
    });
    $('.hover-label-input .label-target').blur( function() {
        $(this).parent().find('label').removeClass('label-hover');
        if ($(this).val()) {
            $(this).parent().find('label').addClass('label-hover');
        }
    });
    $('.hover-label-input .label-target').each(function() {
        if ($(this).val()) {
            $(this).parent().find('label').addClass('label-hover');
        }
    });


    //audio
    $('.wri-audio').on('click', function() {
        var clicked = document.getElementById($(this).find('audio').attr('id'));

        $('.wri-audio').each(function(e) {
            var audio = document.getElementById($(this).find('audio').attr('id'));
            if (audio !== clicked) {
                if (audio.paused == false && audio.currentTime > 0) {
                    audio.pause();
                    audio.parentNode.classList.remove('playing');
                }
            }
        });

        if (clicked.paused == false) {
            clicked.pause();
            clicked.parentNode.classList.remove('playing');
        } else if (clicked.paused == true) {
            clicked.play();
            clicked.parentNode.classList.add('playing');
        } else if (clicked.ended == true) {
            clicked.parentNode.classList.add('HELLO');
        } else {
            clicked.play();
            clicked.parentNode.classList.remove('playing');
        }

        clicked.addEventListener("ended",function() {
            clicked.parentNode.classList.remove('playing');
        });
    });


    //FF & safari casching fix for dropdowns and such
    function unloadingWebsite() {
        $('.categories-list-menu').addClass('hide');
        $('.categories').removeClass('active');
    }
    window.addEventListener("pagehide", function() {
        unloadingWebsite();
    });
    window.addEventListener("pageshow", function() {
        unloadingWebsite();
    });
});


//progress bar
window.onscroll = function() { scrollFunction() };

function scrollFunction() {
    if (document.getElementById('single-post') !== null) {
        var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        var height = document.getElementById("single-post").scrollHeight - document.documentElement.clientHeight;
        var scrolled = (winScroll / height) * 100;
        document.getElementById("scroll-progress").style.width = scrolled + "%";
    }
}
