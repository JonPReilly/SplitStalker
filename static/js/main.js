(function(chosenAjax, $, undefined){
    $(document).ready(function(){
        var $ajaxSelect = $('.chznAjax'),
            $multiSelect = $('.chznSelect');

        // Extend django admin function `dismissAddAnotherPopup` to
        // call $.fn.trigger('liszt:updated') on the chosen <select> element
        var _dismissAddAnotherPopup = window.dismissAddAnotherPopup;
        window.dismissAddAnotherPopup = function(win, newId, newRepr) {
            var $elem = $('#' + windowname_to_id(win.name));
            if (typeof _dismissAddAnotherPopup === 'function') {
                _dismissAddAnotherPopup(win, newId, newRepr);
            }
            if ($elem.hasClass('chznSelect') || $elem.hasClass('.chznAjax')) {
                $elem.trigger('liszt:updated');
            }
        };       

        // Set django admin form-row to behave proper
        $('.form-row').css('overflow', 'visible');
        
        // Invoke ajaxChosen on fields with .autocomplete
        $ajaxSelect.each(function(i, val){
            var $select = $(val),
                app = $select.attr('data-app'),
                model = $select.attr('data-model'),
                fields = $select.attr('data-fields');

            $select.ajaxChosen({
                url: '/chosen/lookup/',
                data: {'app': app, 'model': model, 'fields': fields},
                dataType: 'json',
                minLength: 1,
            });
        });

        // Invoke chosen on multi fields
        $multiSelect.each(function(i, val){
            var $select = $(val);
            $select.chosen()
        });
    });
}(window.chosenAjax = window.chosenAjax || {}, django.jQuery))

