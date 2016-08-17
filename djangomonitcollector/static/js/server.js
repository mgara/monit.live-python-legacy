    var minimize=function(btn){
                    header = $(btn).parent()

                    title = header.children('h2')
                    card = header.parent()
                    card_body = card.children('div.card-body')
                    card_body.toggle(300)
                    if (card_body.hasClass("toggled")){
                        $(btn).html('<i class="zmdi zmdi-minus"></i>')
                        card_body.removeClass("toggled")
                        title.fadeTo( "slow" , 1)
                    }else{
                        $(btn).html('<i class="zmdi zmdi-plus"></i>')
                        card_body.addClass("toggled")
                        title.fadeTo( "slow" , 0.4)
                    }
                }
