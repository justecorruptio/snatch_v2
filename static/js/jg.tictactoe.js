;(function(JG, $){
    $.extend(JG, {
        tictactoe: function(div, multiSock){

            var game = Object();

            game.div = div;
            game.state = [];
            game.rendered = false;

            function create_button(num, val){
                var new_div = $('<div></div>');
                new_div.addClass('tictactoe_button');
                new_div.html(' ');
                new_div.data('val', 0);
                new_div.click(function(e){
                    multiSock.send('test_chan', num);
                });
                game.div.append(new_div);
                game.state.push(new_div);
            }

            game.render = function(){
                if(!game.rendered){
                    for (var i=0; i < 9; i++){
                        create_button(i, 0);
                    }
                }
                game.rendered = true;
            };

            multiSock.bind('test_chan', function(data){
                console.debug(data);
                var div = game.state[parseInt(data.message)];
                var val = (div.data('val') + 1) % 3;
                div.html(' OX'[val]);
                div.data('val', val);
            });

            return game;
        }
    });
})(window.JG = window.JG || {}, jQuery);
