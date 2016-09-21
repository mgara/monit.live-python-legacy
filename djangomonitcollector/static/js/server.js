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
