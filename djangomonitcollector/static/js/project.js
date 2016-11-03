/* Project specific Javascript goes here. */

    var minimize = function(btn, url, id) {
        header = $(btn).parent()
        key = url + "_" + id
        val = "_"
        title = header.children('h2')
        card = header.parent()
        card_body = card.children('div.card-body')
        card_body.toggle(300)
        if (card_body.hasClass("toggled")) {
            $(btn).html('<i class="zmdi zmdi-minus"></i>')
            card_body.removeClass("toggled")
            title.fadeTo("slow", 1)
            val = "maximized"
        } else {
            $(btn).html('<i class="zmdi zmdi-plus"></i>')
            card_body.addClass("toggled")
            title.fadeTo("slow", 0.4)
            val = "minimized"
        }
        save_user_settings(key, val)
    }



$(document).ready(function() {
    //  Set all html elements with data toggle "tooltip" to a tooltip object
    $('[data-toggle="tooltip"]').tooltip()

    //  Check if the browser supports local storage
    if (window.localStorage) {
        localStorageSupport = true
    }

    // Save the state ot the side-menu
    $('.navbar-minimalize').click(function() {
        side_menu_collapsed = $("body").hasClass('mini-navbar');
        console.log(side_menu_collapsed)
        if (side_menu_collapsed)
            localStorage.setItem("side-menu", 'off');
        else
            localStorage.setItem("side-menu", 'on');
    })

    if (localStorageSupport) {
        side_menu_status = localStorage.getItem("side-menu")
        if (side_menu_status == "off") {
            $("body").addClass('mini-navbar');
        }
    }





})

   function _notify(from, align, icon, type, animIn, animOut, message, title){
                icon = !!icon  ? icon  : 'fa fa-comments';

                $.growl({
                    icon: icon,
                    title: title,
                    message: message,
                    url: ''
                },{
                        element: 'body',
                        type: type,
                        allow_dismiss: true,
                        placement: {
                                from: from,
                                align: align
                        },
                        offset: {
                            x: 20,
                            y: 85
                        },
                        spacing: 10,
                        z_index: 1031,
                        delay: 2500,
                        timer: 1000,
                        url_target: '_blank',
                        mouse_over: false,
                        animate: {
                                enter: animIn,
                                exit: animOut
                        },
                        icon_type: 'class',
                        template: '<div data-growl="container" class="alert" role="alert">' +
                                        '<button type="button" class="close" data-growl="dismiss">' +
                                            '<span aria-hidden="true">&times;</span>' +
                                            '<span class="sr-only">Close</span>' +
                                        '</button>' +
                                        '<span data-growl="icon"></span>' +
                                        '<span data-growl="title"></span>' +
                                        '<span data-growl="message"></span>' +
                                        '<a href="#" data-growl="url"></a>' +
                                    '</div>'
                });
            };


function notify(type, title, message, icon){
    _notify("top", "right", icon, type, "animated fadeIn", "animated fadeOut", message, title);
}
function warning(title , message, icon){
   _notify("top", "right",icon, "warning", "animated fadeIn", "animated fadeOut", message, title);

}
function error(title , message, icon){
   _notify("top", "right", icon, "danger", "animated fadeIn", "animated fadeOut", message, title);

}
function success(title , message, icon){
    _notify("top", "right", icon, "success", "animated fadeIn", "animated fadeOut", message, title);
}
function info(title , message, icon){
    _notify("top", "right", icon, "info", "animated fadeIn", "animated fadeOut", message, title);
}
