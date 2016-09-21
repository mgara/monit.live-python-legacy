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

