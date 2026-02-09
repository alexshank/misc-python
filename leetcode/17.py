MAPPINGS = {
    "2": ["a", "b", "c"],
    "3": ["d", "e", "f"],
    "3": ["d", "e", "f"],
    "4": ["g", "h", "i"],
    "5": ["j", "k", "l"],
    "6": ["m", "n", "o"],
    "7": ["p", "q", "r", "s"],
    "8": ["t", "u", "v"],
    "9": ["w", "x", "y", "z"],
}
            

class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        def perms(digits):
            if len(digits) == 0:
                return []
            elif len(digits) == 1:
                return MAPPINGS[digits[0]]

            start_digit = digits[0]
            options = MAPPINGS[start_digit]
            other_perms = perms(digits[1:])

            result = []
            for option in options:
                for other_perm in other_perms:
                    result.append(option + other_perm)

            return result

        return perms(digits)

