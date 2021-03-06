// Copyright (c) 2012 gocept gmbh & co. kg
// See also LICENSE.txt

(function($) {

// idempotent bind, see http://stackoverflow.com/a/12322655/1885340
$(document).bind('fragment-ready', function(event) {
    $('button.toggle_infos', event.__target).unbind(
    'click.zeit.edit.details').bind(
        'click.zeit.edit.details', function(event) {
        var button = $(event.target);
        $('.folded_information', button.parent()).slideToggle('slow');
        button.toggleClass('folded');
        return false;
    });
});

}(jQuery));
