class Solution:
    def convert(self, s: str, numRows: int) -> str:
        if numRows == 1:
            return s
        
        rs = [[] for i in range(numRows)]
        i = 0
        c = 0
        col_switches = numRows - 1
        while i < len(s):
            if c % col_switches == 0:
                for r in rs:
                    if i >= len(s):
                        break

                    r.append(s[i])
                    i += 1
            else:
                r_i = numRows - 1 - (c % col_switches)
                rs[r_i].append(s[i])
                i += 1
            c += 1

        result = []
        for r in rs:
            result.extend(r)
        return "".join(result)

