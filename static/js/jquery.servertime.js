;(function($, window){
    $.extend({
        servertime: function(url, poll) {

            var st = Object();

            st.poll = poll === false?
                60 * 60 * 1000: typeof poll === 'undefined'? 5000: poll;
            st.url = url;
            st.best_latency = 9999999;
            //correction offset, add to get server time
            st.offset = 0;
            st.latency = 0;

            var fetch_servertime = function(){
                $.getJSON(st.url, {a: $.now()}, function(data, textStatus, jqXHR){
                    var now = $.now();
                    var latency = (0 + now - data.a) / 2;
                    if (latency < st.best_latency){
                        st.offset = Math.round(data.b - now + latency);
                        st.best_latency = latency;
                    }
                    else {
                        st.best_latency *= 1.1;
                    }
                    st.latency = latency;
                    $('#latency').html(latency);
                });
            };

            setTimeout(fetch_servertime, 0);
            setTimeout(fetch_servertime, 1000);
            setTimeout(fetch_servertime, 2000);
            setTimeout(fetch_servertime, 3000);
            st.int_handle = setInterval(fetch_servertime, st.poll);

            st.now = function(){
                return $.now() + st.offset;
            }

            st.schedule = function(func, servertime){
                return setTimeout(func, servertime - st.offset - $.now());
            }

            return st;
        }
    });
})(jQuery, window);
