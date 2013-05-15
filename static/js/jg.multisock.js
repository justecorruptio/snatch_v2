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
                if (!ms.router[e.data.route]){
                    return;
                }
                return ms.router[e.data.route](e.data);
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
