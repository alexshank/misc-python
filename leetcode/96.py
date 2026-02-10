class Solution:
    def numTrees(self, n: int) -> int:
        # array will hold results of each sub problem
        # already hardcoded answers for 0, 1, and 2 cases
        # 0 nodes => 1 structure, because "empty" is a structure
        trees = [1, 1, 2] + ([1] * (n + 1 - 3))

        # dynamic programming: solve small problems first
        # already solved 0, 1, and 2 cases
        for n_local in range(3, n + 1):

            total = 0
            for root in range(0, n_local):
                count_left = root
                count_right = n_local - root - 1

                # possible left subtree structures * possible right subtree structures
                total += trees[count_left] * trees[count_right]

            trees[n_local] = total

        # space: O(n)
        # time: O(n^2)
        # for n = 4, answer should be 14
        return trees[n]

