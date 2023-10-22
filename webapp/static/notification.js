        function set_message_count(size_now, time_stamp) {
            const toastLive = document.getElementById('liveToast')
            const toast = new bootstrap.Toast(toastLive)
            $('#timeStamp').html(time_stamp);
            $('#resizeDetail').html('Cache Pool Size: ' + size_now);
            toast.show()
        }
        prev_value = 1

        $(function () {
            setInterval(function () {
                $.ajax('{{ url_for('notification') }}').done(
                    function (notification) {
                        if (notification.size_now != prev_value) {
                            set_message_count(notification.size_now, notification.timestamp);
                            prev_value = notification.size_now
                        }
                    }
                );
            }, 1000);
        });

