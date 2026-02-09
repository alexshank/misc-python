# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # quickly return for small lists
        if not head or not head.next:
            return head

        # need to keep reference to the first node
        dummy = ListNode(0, head)

        # need three pointers for swapping
        # starts: t0 -> t1 -> t2 (t1 is the "current" node)
        t0 = dummy
        t1 = head
        t2 = head.next

        # while there is a set of two nodes to swap
        while t1 and t2:
            # now: t0 -> t2 -> t1
            t0.next = t2
            t1.next = t2.next
            t2.next = t1

            # back to: t0 -> t1 -> t2 (but advanced "current" down the list TWO nodes)
            t0 = t1
            t1 = t1.next
            t2 = t1.next if t1 else None

        return dummy.next

