# Assignment: Data Structures & Systems Design

---

## Problem 1: LRU Cache Implementation

### My Approach

The main challenge here is making both `get` and `put` work in O(1). I needed two things at the same time — fast lookup by key, and a way to track which item was used least recently.

A dictionary (hash map) handles the lookup part — given a key, I can find its value instantly. But a dictionary doesn't remember the order things were accessed in.

For tracking recency, I used a doubly linked list. The idea is simple: whenever something is accessed, move it to the end of the list. The item at the front is always the least recently used one, so when I need to evict, I just remove from the front.

Why doubly linked and not singly linked? Because to remove a node from the middle of a linked list, I need to update the node before it (`prev.next = node.next`). In a singly linked list I'd have to walk from the head to find the previous node, which is O(n). With a doubly linked list, every node already has a `.prev` pointer, so removal is O(1).

I also use two dummy nodes (head and tail) to avoid having to handle edge cases like "what if the list is empty" or "what if I'm removing the first/last real node." The dummy nodes are always there, so the real nodes always have valid neighbors.

### Code

```python
import heapq


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
```

---

## Problem 2: Event Scheduler

### My Approach

**`can_attend_all`**: I sort the events by start time. Then I just check each consecutive pair — if any event starts before the previous one has ended, there's an overlap and one person can't attend all of them. Events that touch exactly (like one ends at 10 and the next starts at 10) are fine since the problem says adjacent events aren't overlaps.

**`min_rooms_required`**: This is basically the "meeting rooms" problem. I sort events by start time and maintain a min-heap of end times — each entry in the heap represents a room that's currently occupied.

The logic for each event:
1. First, check the heap. If the earliest ending meeting has already finished (its end time ≤ current start), free that room by popping it off.
2. Then assign the current event to a room by pushing its end time onto the heap.
3. Track the maximum size the heap reaches — that's the answer.

The reason this works is that the heap size at any point tells us how many meetings are happening simultaneously. The peak of that is exactly the minimum number of rooms we need.

### Code

```python
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
```

For the given example `[(9, 10), (10, 11), (11, 12)]` — after sorting, we process them in order. Event (9,10) takes a room. When we get to (10,11), the first room's end time (10) ≤ start (10), so we free it and reuse. Same thing for (11,12). So all three run sequentially in 1 room, and `can_attend_all` returns True.

---

## Final Discussion & Analysis

### Time & Space Complexity

**LRU Cache:**
- `get(key)`: O(1) average — dictionary lookup is O(1), and moving a node in the linked list is O(1) since we just update 4 pointers.
- `put(key, value)`: O(1) average — same reasoning. Eviction is also O(1) because we just remove `head.next`.
- Space: O(capacity) — we store at most `capacity` entries in the dict + linked list.

**Event Scheduler:**
- `can_attend_all`: O(n log n) time because of sorting. The loop after that is O(n). Space is O(n) for the sorted copy.
- `min_rooms_required`: O(n log n) time — sorting is O(n log n), and each event does at most one push and one pop on the heap, each costing O(log n). Space is O(n) in the worst case where all events overlap and the heap holds all of them.

### Trade-offs: Why a Hash Map + Doubly Linked List?

Neither data structure works well alone:

- **Hash map only**: Great for O(1) lookup, but it doesn't track any ordering. We'd have no way to know which key was used least recently without scanning everything.
- **Linked list only**: Maintains order perfectly, but finding a specific key means walking the list, which is O(n).
- **Array/list**: We could track order, but removing from the middle or moving elements around requires shifting, which is O(n).
- **Singly linked list + hash map**: Almost works, but removing a node requires knowing the previous node. The hash map points to the node itself, not the one before it. So we'd need to traverse to find the predecessor — O(n) again.

The doubly linked list fixes that last problem. Each node stores both `.prev` and `.next`, so once we have a reference to a node (from the hash map), we can remove it and reinsert it at the tail in O(1). The cost is just a bit of extra memory for the `.prev` pointer per node.

### Future Proofing: Assigning Room Numbers

To assign specific room names like "Room A", "Room B" to each event, I'd modify `min_rooms_required` to track which rooms are available:

- Keep a second min-heap of available room IDs (so we always reuse the lowest-numbered room first).
- When a room is freed (end time ≤ start), instead of just popping the end time, push its room ID onto the available-rooms heap.
- When assigning a room, pop from the available heap if one exists, otherwise create a new room ID.
- Store `(end_time, room_id)` tuples in the busy-rooms heap instead of just end times.
- Map room IDs to names: 0 → "Room A", 1 → "Room B", etc.

The time complexity stays O(n log n) and space stays O(n).

### Concurrency: Making the LRU Cache Thread-Safe

The tricky part is that even `get` modifies state — it moves the accessed node to the tail of the linked list. So two threads calling `get` at the same time could corrupt the list pointers.

The simplest fix is wrapping both `get` and `put` with a mutex lock (in Python, `threading.Lock()`). Every operation acquires the lock first, does its work, then releases it. This guarantees only one thread touches the cache internals at a time.

A reader-writer lock won't help here because reads are also writes (they update recency order).

For better performance under heavy load, we could shard the cache — split it into multiple smaller caches, each with its own lock, and route keys to shards using `hash(key) % num_shards`. That way threads accessing different shards don't block each other. The downside is that the total capacity is now split across shards, and eviction only happens within each shard, not globally.
