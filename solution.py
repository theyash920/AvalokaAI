import heapq


# ---------------------------------------------------------------------------
# Problem 1: LRU Cache
# ---------------------------------------------------------------------------
#
# Approach:
# A hash map alone gives O(1) lookup but no way to track usage order.
# A linked list alone gives ordering but O(n) lookup.
# Combining both gives O(1) for everything:
#   - dict: key -> node, for instant lookup
#   - doubly linked list: keeps nodes ordered from least to most recently used
#
# Doubly linked (not singly) because when we remove a node we need its
# previous node too, and a singly linked list can't give us that without
# walking from the head, which is O(n).
#
# Two dummy nodes (head and tail) are used so we never have to special-case
# an empty list or the first/last real node.

class Node:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> Node

        self.head = Node()  # least recently used side
        self.tail = Node()  # most recently used side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_end(self, node):
        prev_last = self.tail.prev
        prev_last.next = node
        node.prev = prev_last
        node.next = self.tail
        self.tail.prev = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_end(node)
        return node.value

    def put(self, key, value):
        if self.capacity == 0:
            return

        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_end(node)
            return

        if len(self.cache) == self.capacity:
            lru_node = self.head.next
            self._remove(lru_node)
            del self.cache[lru_node.key]

        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_end(new_node)


# ---------------------------------------------------------------------------
# Problem 2: Event Scheduler
# ---------------------------------------------------------------------------
#
# can_attend_all:
# Sort events by start time. If any event starts before the previous one
# ends, there's a clash. Events that touch exactly (end == start) are fine
# since one finishes right as the other begins.
#
# min_rooms_required:
# Same idea as the classic "meeting rooms II" problem. Sort by start time
# and use a min-heap of end times for rooms currently in use.
# For each event, first free up any room whose meeting has already ended
# (end time <= current start), then assign a room (push end time onto heap).
# The largest the heap ever gets is the minimum number of rooms needed.

def can_attend_all(events):
    if not events:
        return True

    events = sorted(events)
    for i in range(1, len(events)):
        if events[i][0] < events[i - 1][1]:
            return False
    return True


def min_rooms_required(events):
    if not events:
        return 0

    events = sorted(events)
    end_times = []  # min-heap
    max_rooms = 0

    for start, end in events:
        while end_times and end_times[0] <= start:
            heapq.heappop(end_times)

        if start == end:
            continue

        heapq.heappush(end_times, end)
        max_rooms = max(max_rooms, len(end_times))

    return max_rooms


# ---------------------------------------------------------------------------
# Quick checks
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # -- LRU Cache --
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)          # evicts key 2
    assert cache.get(2) == -1
    cache.put(4, 4)          # evicts key 1
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4

    # updating an existing key shouldn't change capacity
    cache2 = LRUCache(2)
    cache2.put(1, 10)
    cache2.put(1, 20)        # update, not a new entry
    assert cache2.get(1) == 20
    cache2.put(2, 30)
    assert cache2.get(1) == 20  # key 1 still there, not evicted
    assert cache2.get(2) == 30

    # capacity 0 should just silently ignore puts
    cache0 = LRUCache(0)
    cache0.put(1, 1)
    assert cache0.get(1) == -1

    print("LRU Cache tests passed")

    # -- Event Scheduler --
    # exact example from the assignment
    events1 = [(9, 10), (10, 11), (11, 12)]
    assert can_attend_all(events1) is True
    assert min_rooms_required(events1) == 1

    # overlapping events
    events2 = [(9, 11), (10, 12), (11, 13)]
    assert can_attend_all(events2) is False
    assert min_rooms_required(events2) == 2

    # empty list
    assert can_attend_all([]) is True
    assert min_rooms_required([]) == 0

    # single event
    assert can_attend_all([(5, 8)]) is True
    assert min_rooms_required([(5, 8)]) == 1

    # all events at the same time
    events3 = [(1, 5), (1, 5), (1, 5)]
    assert can_attend_all(events3) is False
    assert min_rooms_required(events3) == 3

    print("Event Scheduler tests passed")