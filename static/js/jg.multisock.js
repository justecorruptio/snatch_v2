;(function(JG, $){
    $.extend(JG, {
        multiSock: function(url, options){
            var ms = Object();

            options = options || {};

            ms.sock = new SockJS(url);
            ms.sock.onopen = options.onopen;
            ms.sock.onclose = options.onclose;

            ms.router = {};

            ms.sock.onmessage = function(e){
                console.debug(e);
                var data = $.parseJSON(e.data);
                if (!ms.router[data.route]){
                    return;
                }
                return ms.router[data.route](data);
            };

            ms.bind = function(route, func){
                ms.router[route] = func;
            };

            ms.unbind = function(route){
                delete ms.router[route];
            };

            ms.send = function(route, message){
                ms.sock.send(JSON.stringify({
                    route: route,
                    message: message
                }));
            };

            return ms;
        }
    });
})(window.JG = window.JG || {}, jQuery);
