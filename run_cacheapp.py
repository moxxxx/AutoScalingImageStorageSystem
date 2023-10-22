import threading

import cacheapp
import os

if __name__ == "__main__":
    def start_cacheapp0():
        cacheapp.create_cacheapp().run(
            host="localhost", port=4000, debug=False
        )

    threading.Thread(target=start_cacheapp0).start()

    def start_cacheapp1():
        cacheapp.create_cacheapp().run(
            host="localhost", port=4001, debug=False
        )

    threading.Thread(target=start_cacheapp1).start()

    def start_cacheapp2():
        cacheapp.create_cacheapp().run(
            host="localhost", port=4002, debug=False
        )

    threading.Thread(target=start_cacheapp2).start()

    def start_cacheapp3():
        cacheapp.create_cacheapp().run(
            host="localhost", port=4003, debug=False
        )

    threading.Thread(target=start_cacheapp3).start()

    def start_cacheapp4():
        cacheapp.create_cacheapp().run(
            host="localhost", port=4004, debug=False
        )

    threading.Thread(target=start_cacheapp4).start()

    def start_cacheapp5():
        cacheapp.create_cacheapp().run(
            host="localhost", port=4005, debug=False
        )

    threading.Thread(target=start_cacheapp5).start()

    def start_cacheapp6():
        cacheapp.create_cacheapp().run(
            host="localhost", port=4006, debug=False
        )

    threading.Thread(target=start_cacheapp6).start()

    def start_cacheapp7():
        cacheapp.create_cacheapp().run(
            host="localhost", port=4007, debug=False
        )

    threading.Thread(target=start_cacheapp7).start()
