(function($) {
    $('#main-posts').on('click','.loadMoreButton', function(event){
        var loadMoreButtonUrl = $(this).attr('href');
        var loadMoreButtonWrapper = $(this).parent();
        //var loadMoreButtonWrapper = $(this).parent(); //.inner

        $.ajax({
            url: loadMoreButtonUrl,
            dataType: 'html',
            complete: function(jqxhr, status) {
                if(jqxhr.status == 200) {
                    loadMoreButtonWrapper.replaceWith(jqxhr.responseText);
                } else {
                    loadMoreButtonWrapper.text('An Error Occurred');
                }
            }
        });

        event.preventDefault();
    });
})( jQuery );