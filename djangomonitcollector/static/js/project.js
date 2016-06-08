/* Project specific Javascript goes here. */


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
