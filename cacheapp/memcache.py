import random
import sys
from collections import OrderedDict


class Memcache:
    """
    The replacement policy of mem-cache is restricted by "LRU" or "Random"
    Capacity is restricted in MB
    Cache is used to store key and image
    """

    def __init__(self):
        self.num_items = 0  # number of items in cache
        self.total_size = 0  # bytes

        self.total_request = 0  # int
        self.hit = 0  # int
        self.miss = 0  # int

        self.cache = OrderedDict()

        self.policy = "Random"
        self.capacity = 128

    def get(self, key):
        self.total_request += 1
        if key not in self.cache:
            self.miss += 1
            return False
        else:
            self.hit += 1
            # to make sure the rencently visited key goes to the end
            if self.policy == "LRU":
                self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        # If the image size is larger than capacity itself,return False
        imgSize = sys.getsizeof(value)
        if imgSize > self.capacity * 1024 * 1024:
            return False

        # If the key is already exist in cache,first invalidate it.
        if key in self.cache:
            self.invalidateKey(key)
        else:
            self.num_items += 1

        # Free cache space before add a new item
        self.free_space(imgSize)

        self.cache[key] = value
        self.total_size += imgSize

        return True

    # Free the cache space when necessary
    def free_space(self, item_size):
        while item_size + self.total_size > self.capacity * 1024 * 1024:
            # "LRU" policy:first drop the least recently used key
            if self.policy == "LRU":
                drop_item = self.cache.popitem(last=False)[1]
            # Random policy
            else:
                drop_item = self.cache.pop(random.choice(list(self.cache.keys())))
            self.total_size -= sys.getsizeof(drop_item)
            self.num_items -= 1

    # Clear everything in the cache
    def clear(self):
        self.total_size = 0
        self.num_items = 0
        self.cache.clear()

    # Delete item in cache with given key.
    # Reduce the number of items in cache and cache space
    def invalidateKey(self, key):
        if key not in self.cache:
            return False
        else:
            self.num_items -= 1
            remove_item = self.cache.pop(key)
            self.total_size -= sys.getsizeof(remove_item)
            return True

    def existKey(self, key):
        if key in self.cache:
            return True
        else:
            return False

    def getMissRate(self):
        if self.total_request != 0:
            return self.miss / self.total_request
        else:
            return 0

    def getHitRate(self):
        if self.total_request != 0:
            return self.hit / self.total_request
        else:
            return 0

    def getNumItems(self):
        return self.num_items

    # Return cache space in MB
    def getSpace(self):
        return self.total_size / (1024**2)

    # Return cache capacity in MB
    def getCapacity(self):
        return self.capacity

    def getLeftCapacity(self):
        return self.capacity - (self.total_size / (1024**2))

    # Use database to store statistics
    # number of items in cache, total size of items in cache, number of requests served, miss rate and hit rate
    def updateStatistics(self):
        return

    # Read new policy and capacity from database
    def refreshConfiguration(self, capacity, policy):
        self.capacity = capacity
        self.policy = policy
        return
