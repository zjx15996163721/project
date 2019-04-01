# 冒泡排序
# a = [6, 4, 10, 5, 13, 8]
#
#
# def run(a):
#     for i in range(0, len(a)):
#         for j in range(i+1, len(a)):
#             if a[i] > a[j]:
#                 a[i], a[j] = a[j], a[i]
#     return a
#
#
# print(run(a))


# 罗马数字
# class Solution:
#     def romanToInt(self, s):
#         """
#         :type s: str
#         :rtype: int
#         """
#         rule_dict = {
#             'M': 1000,
#             'D': 500,
#             'C': 100,
#             'L': 50,
#             'X': 10,
#             'V': 5,
#             'I': 1
#         }
#         sum = 0
#         for i in range(len(s)-1):
#             if rule_dict[s[i]] >= rule_dict[s[i+1]]:
#                 sum += rule_dict[s[i]]
#             else:
#                 sum -= rule_dict[s[i]]
#         sum += rule_dict[s[-1]]
#         return sum
#
#
# S = Solution()
# print(S.romanToInt('LVIII'))

# 数字翻转
# class Solution:
#     def reverse(self, x):
#         """
#         :type x: int
#         :rtype: int
#         """
#         # return str()[::-1]
#         return (lambda x : int(str(x)[::-1]) if x >= 0 else -int(str(abs(x))[::-1]))(x)
#
#
# s = Solution()
# print(s.reverse(1235))

# def reverse(text):
#     ret = ""
#     for i in range(len(text) - 1, -1, -1):
#         ret = ret + text[i]
#     return ret
# print(reverse("#ab@cd!"))

# 两个数字的和
# class Solution:
#     def twoSum(self, nums, target):
#         """
#         :type nums: List[int]
#         :type target: int
#         :rtype: List[int]
#         """
#         var = dict((nums[i], i) for i in range(len(nums)))
#         print(var)
#         for i in range(len(nums)):
#             num = target - nums[i]
#             if num in var and i != var[num]:
#                 return [i, var[num]]
#
#
# s = Solution()
# print(s.twoSum([3, 2, 4], 6))


# def insert(L):
#     for i in range(1, len(L)):
#         for j in range(i-1, -1, -1):
#             if L[i] < L[j]:
#                 L[j], L[i] = L[i], L[j]
#
#     return L
#
#
# print(insert([3, 1, 5, 4, 8]))

# 取两个字符相同连续部分
# class Solution:
#     def longestCommonPrefix(self, strs):
#         """
#         :type strs: List[str]
#         :rtype: str
#         """
#         # if len(strs) <= 1:
#         #     return ''
#         # else:
#         #     rep_list = []
#         #     for i in range(len(strs[0])):
#         #         for j in range(i+1, len(strs[0])+1):
#         #             if strs[0][i:j] in strs[1]:
#         #                 rep_list.append(strs[0][i:j])
#         #     for k in range(len(rep_list)-1):
#         #         if len(rep_list[k]) > len(rep_list[k+1]):
#         #             rep_list[k], rep_list[k+1] = rep_list[k+1], rep_list[k]
#         #     a = rep_list[-1:]
#         #     print(rep_list)
#         #     for m in rep_list:
#         #         if
#         if not strs:
#             return ''
#
#         mins = min((strs))
#         print(mins)
#         maxs = max((strs))
#         print(maxs)
#         pre = ''
#         print(min(len(mins), len(maxs)))
#         for i in range(min(len(mins), len(maxs))):
#             if mins[i] == maxs[i]:
#                 pre = pre+mins[i]
#             else:
#                 break
#         return pre
#
#
# s = Solution()
# print(s.longestCommonPrefix(['afbsdgv', 'afbq', 'afjnh']))

class Solution:
    def jump(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        for i in range(len(nums)):
            print(i)



s = Solution()
print(s.jump([2, 3, 1, 1, 4]))


