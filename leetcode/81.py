from typing import List


class Solution:
    def search(self, nums: List[int], target: int) -> bool:

        start = 0
        end = len(nums) - 1
        while start <= end:

            pivot = (end + start) // 2

            if nums[pivot] == target:
                return True

            # right side is sorted
            if nums[pivot] < nums[end]:
                # value is in right side
                if nums[pivot] < target and target <= nums[end]:
                    start = pivot + 1
                # value is in left side
                else:
                    end = pivot - 1
            # left side is sorted
            elif nums[pivot] > nums[end]:
                # value in the left side
                if nums[pivot] > target and target >= nums[start]:
                    end = pivot - 1
                # value in the right side
                else:
                    start = pivot + 1
            # can't tell, best we can do is reduce search space by 1 (O(n))
            elif nums[pivot] == nums[end]:
                end -= 1

        return False

            
tests = [
    ([1, 2, 3], 2),
    ([2,5,6,0,0,1,2], 0),
    ([2,5,6,0,0,1,2], 7),
    ([1,1,1,1,1,1,1,1,1,13,1,1,1,1,1,1,1,1,1,1,1,1], 13)
]
for test in tests:
    print()    
    print(test)
    print(Solution().search(*test))


                
            
