"""Synthetic algorithmic task generator.

Each task is drawn from a *problem family*: a genuine algorithmic problem with a
real reference solution. Hidden tests are produced by running the reference
solution on randomly sampled inputs, so expected outputs are correct by
construction. Families span the 16 plan categories and three difficulty tiers,
giving real diversity instead of one templated problem.
"""
import json
import random
import argparse
from pathlib import Path
from typing import Callable, List, Tuple, Any

from code_model_lab.data.schemas import (
    AlgorithmicProblem, Example, HiddenTest, Complexity, CommonFailure,
)


class Family:
    """A parameterized algorithmic problem family."""

    def __init__(
        self,
        key: str,
        func_name: str,
        difficulty: str,
        tags: List[str],
        problem: str,
        constraints: str,
        ref_src: str,
        ref: Callable[..., Any],
        sampler: Callable[[random.Random], Tuple],
        time: str,
        space: str,
        explanation: str,
        wrong_solution: str = "",
        failure_reason: str = "",
    ):
        self.key = key
        self.func_name = func_name
        self.difficulty = difficulty
        self.tags = tags
        self.problem = problem
        self.constraints = constraints
        self.ref_src = ref_src.strip("\n")
        self.ref = ref
        self.sampler = sampler
        self.time = time
        self.space = space
        self.explanation = explanation
        self.wrong_solution = wrong_solution.strip("\n")
        self.failure_reason = failure_reason

    def starter(self) -> str:
        # First line of the reference is the signature.
        sig = self.ref_src.splitlines()[0]
        return f"{sig}\n    pass"

    def make_test(self, args: Tuple) -> HiddenTest:
        return HiddenTest(input=repr(args), expected_output=repr(self.ref(*args)))


# --------------------------------------------------------------------------
# Reference solutions
# --------------------------------------------------------------------------

def _two_sum_ref(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []


def _max_subarray_ref(nums):
    best = cur = nums[0]
    for n in nums[1:]:
        cur = max(n, cur + n)
        best = max(best, cur)
    return best


def _longest_unique_ref(s):
    seen = {}
    start = best = 0
    for i, c in enumerate(s):
        if c in seen and seen[c] >= start:
            start = seen[c] + 1
        seen[c] = i
        best = max(best, i - start + 1)
    return best


def _binary_search_ref(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def _valid_parens_ref(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for c in s:
        if c in "([{":
            stack.append(c)
        elif not stack or stack.pop() != pairs[c]:
            return False
    return not stack


def _max_profit_ref(prices):
    lo = prices[0]
    best = 0
    for p in prices[1:]:
        best = max(best, p - lo)
        lo = min(lo, p)
    return best


def _climb_stairs_ref(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _coin_change_ref(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != INF else -1


def _count_primes_ref(n):
    if n < 2:
        return 0
    sieve = [True] * n
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n, i):
                sieve[j] = False
    return sum(sieve)


def _merge_intervals_ref(intervals):
    intervals = sorted(intervals)
    out = []
    for iv in intervals:
        if out and iv[0] <= out[-1][1]:
            out[-1][1] = max(out[-1][1], iv[1])
        else:
            out.append(list(iv))
    return out


def _kth_largest_ref(nums, k):
    return sorted(nums, reverse=True)[k - 1]


def _is_palindrome_ref(s):
    clean = [c.lower() for c in s if c.isalnum()]
    return clean == clean[::-1]


def _move_zeroes_ref(nums):
    out = [x for x in nums if x != 0]
    out += [0] * (len(nums) - len(out))
    return out


def _subset_count_ref(nums):
    return 2 ** len(nums)


# --------------------------------------------------------------------------
# Reference solutions — hard families
# --------------------------------------------------------------------------

def _decode_ways_ref(s):
    if not s or s[0] == "0":
        return 0
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = dp[1] = 1
    for i in range(2, n + 1):
        if s[i - 1] != "0":
            dp[i] += dp[i - 1]
        if 10 <= int(s[i - 2:i]) <= 26:
            dp[i] += dp[i - 2]
    return dp[n]


def _next_permutation_ref(nums):
    a = list(nums)
    n = len(a)
    i = n - 2
    while i >= 0 and a[i] >= a[i + 1]:
        i -= 1
    if i >= 0:
        j = n - 1
        while a[j] <= a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]
    a[i + 1:] = reversed(a[i + 1:])
    return a


def _trap_ref(height):
    if not height:
        return 0
    lo, hi = 0, len(height) - 1
    lmax = rmax = res = 0
    while lo < hi:
        if height[lo] < height[hi]:
            lmax = max(lmax, height[lo])
            res += lmax - height[lo]
            lo += 1
        else:
            rmax = max(rmax, height[hi])
            res += rmax - height[hi]
            hi -= 1
    return res


def _lis_ref(nums):
    import bisect
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def _edit_distance_ref(a, b):
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            cur = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = cur
    return dp[n]


def _max_profit_two_ref(prices):
    buy1 = buy2 = float("-inf")
    sell1 = sell2 = 0
    for p in prices:
        buy1 = max(buy1, -p)
        sell1 = max(sell1, buy1 + p)
        buy2 = max(buy2, sell1 - p)
        sell2 = max(sell2, buy2 + p)
    return sell2


def _largest_rectangle_ref(heights):
    stack = []
    best = 0
    for i, h in enumerate(heights + [0]):
        start = i
        while stack and stack[-1][1] > h:
            idx, height = stack.pop()
            best = max(best, height * (i - idx))
            start = idx
        stack.append((start, h))
    return best


# --------------------------------------------------------------------------
# Input samplers
# --------------------------------------------------------------------------

def _rand_list(rng, lo=-20, hi=20, n_lo=1, n_hi=12):
    return [rng.randint(lo, hi) for _ in range(rng.randint(n_lo, n_hi))]


def _rand_paren_string(rng):
    n = rng.randint(1, 6)
    return "".join(rng.choice("()[]{}") for _ in range(2 * n))


def _two_sum_sampler(rng):
    base = _rand_list(rng, n_lo=2, n_hi=6)
    a, b = base[0], base[1]
    rest = base[2:]
    nums = rest[:1] + [a, b] + rest[1:]
    return (nums, a + b)


def _binary_search_sampler(rng):
    arr = sorted(set(_rand_list(rng, n_lo=1, n_hi=12)))
    return (arr, rng.choice(arr + [999]))


def _kth_largest_sampler(rng):
    arr = _rand_list(rng, n_lo=1, n_hi=10)
    return (arr, rng.randint(1, len(arr)))


def _decode_sampler(rng):
    # Weight toward 1/2 and zeros to exercise the tricky boundary cases.
    digits = "112233045"
    return ("".join(rng.choice(digits) for _ in range(rng.randint(1, 9))),)


def _perm_sampler(rng):
    return (rng.sample(range(1, 10), rng.randint(2, 6)),)


def _trap_sampler(rng):
    return ([rng.randint(0, 6) for _ in range(rng.randint(2, 12))],)


def _two_str_sampler(rng):
    def word():
        return "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
    return (word(), word())


def _prices_sampler(rng):
    return ([rng.randint(0, 30) for _ in range(rng.randint(1, 12))],)


def _hist_sampler(rng):
    return ([rng.randint(0, 8) for _ in range(rng.randint(1, 10))],)


# --------------------------------------------------------------------------
# Problem families
# --------------------------------------------------------------------------

FAMILIES: List[Family] = [
    Family(
        "two_sum", "two_sum", "easy", ["hash maps", "arrays"],
        "Given an array of integers `nums` and an integer `target`, return the "
        "indices of the two numbers that add up to `target`. Assume exactly one "
        "solution exists and you may not use the same element twice.",
        "2 <= nums.length <= 1000\n-10^9 <= nums[i] <= 10^9",
        "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n    return []",
        _two_sum_ref, _two_sum_sampler,
        "O(N)", "O(N)",
        "Map each value to its index; for each element check whether its complement is already seen.",
        "def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]",
        "Allows using the same element twice (j may equal i).",
    ),
    Family(
        "max_subarray", "max_subarray", "medium", ["arrays", "dynamic programming"],
        "Given an integer array `nums`, find the contiguous subarray with the "
        "largest sum and return that sum.",
        "1 <= nums.length <= 1000\n-10^4 <= nums[i] <= 10^4",
        "def max_subarray(nums):\n    best = cur = nums[0]\n    for n in nums[1:]:\n        cur = max(n, cur + n)\n        best = max(best, cur)\n    return best",
        _max_subarray_ref, lambda rng: (_rand_list(rng, n_lo=1, n_hi=12),),
        "O(N)", "O(1)",
        "Kadane's algorithm: track the best sum ending at each index.",
        "def max_subarray(nums):\n    return sum(x for x in nums if x > 0)",
        "Fails when all numbers are negative (returns 0 instead of the largest element).",
    ),
    Family(
        "longest_unique", "longest_unique_substring", "medium", ["sliding window", "strings"],
        "Given a string `s`, return the length of the longest substring without "
        "repeating characters.",
        "0 <= s.length <= 1000",
        "def longest_unique_substring(s):\n    seen = {}\n    start = best = 0\n    for i, c in enumerate(s):\n        if c in seen and seen[c] >= start:\n            start = seen[c] + 1\n        seen[c] = i\n        best = max(best, i - start + 1)\n    return best",
        _longest_unique_ref,
        lambda rng: ("".join(rng.choice("abcde") for _ in range(rng.randint(0, 14))),),
        "O(N)", "O(min(N, alphabet))",
        "Sliding window keyed by last-seen index of each character.",
    ),
    Family(
        "binary_search", "binary_search", "easy", ["binary search", "arrays"],
        "Given a sorted ascending array `nums` and a `target`, return the index "
        "of `target` or -1 if it is absent.",
        "1 <= nums.length <= 10^4",
        "def binary_search(nums, target):\n    lo, hi = 0, len(nums) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if nums[mid] == target:\n            return mid\n        if nums[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
        _binary_search_ref, _binary_search_sampler,
        "O(log N)", "O(1)",
        "Standard binary search over the sorted array.",
    ),
    Family(
        "valid_parens", "valid_parentheses", "easy", ["stacks/queues", "strings"],
        "Given a string `s` of brackets '()[]{}', return True if every bracket is "
        "correctly opened and closed in order.",
        "0 <= s.length <= 100",
        "def valid_parentheses(s):\n    pairs = {')': '(', ']': '[', '}': '{'}\n    stack = []\n    for c in s:\n        if c in '([{':\n            stack.append(c)\n        elif not stack or stack.pop() != pairs[c]:\n            return False\n    return not stack",
        _valid_parens_ref, lambda rng: (_rand_paren_string(rng),),
        "O(N)", "O(N)",
        "Push openers on a stack; on a closer, the top must be its matching opener.",
    ),
    Family(
        "max_profit", "max_profit", "easy", ["greedy", "arrays"],
        "Given daily `prices`, return the maximum profit from buying on one day "
        "and selling on a later day. Return 0 if no profit is possible.",
        "1 <= prices.length <= 10^4\n0 <= prices[i] <= 10^4",
        "def max_profit(prices):\n    lo = prices[0]\n    best = 0\n    for p in prices[1:]:\n        best = max(best, p - lo)\n        lo = min(lo, p)\n    return best",
        _max_profit_ref, lambda rng: ([rng.randint(0, 50) for _ in range(rng.randint(1, 12))],),
        "O(N)", "O(1)",
        "Track the minimum price so far and the best profit against it.",
    ),
    Family(
        "climb_stairs", "climb_stairs", "easy", ["dynamic programming", "math/combinatorics"],
        "You climb a staircase of `n` steps taking 1 or 2 steps at a time. Return "
        "the number of distinct ways to reach the top.",
        "1 <= n <= 35",
        "def climb_stairs(n):\n    a, b = 1, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a",
        _climb_stairs_ref, lambda rng: (rng.randint(1, 30),),
        "O(N)", "O(1)",
        "Fibonacci recurrence: ways(n) = ways(n-1) + ways(n-2).",
    ),
    Family(
        "coin_change", "coin_change", "hard", ["dynamic programming"],
        "Given coin denominations `coins` and an `amount`, return the fewest "
        "coins needed to make `amount`, or -1 if it cannot be made.",
        "1 <= coins.length <= 12\n0 <= amount <= 5000",
        "def coin_change(coins, amount):\n    INF = amount + 1\n    dp = [0] + [INF] * amount\n    for a in range(1, amount + 1):\n        for c in coins:\n            if c <= a:\n                dp[a] = min(dp[a], dp[a - c] + 1)\n    return dp[amount] if dp[amount] != INF else -1",
        _coin_change_ref,
        lambda rng: (sorted(rng.sample(range(1, 12), rng.randint(1, 4))), rng.randint(0, 30)),
        "O(amount * len(coins))", "O(amount)",
        "Bottom-up DP over amounts; dp[a] is the fewest coins to make a.",
    ),
    Family(
        "count_primes", "count_primes", "medium", ["math/combinatorics"],
        "Return the number of prime numbers strictly less than `n`.",
        "0 <= n <= 5*10^4",
        "def count_primes(n):\n    if n < 2:\n        return 0\n    sieve = [True] * n\n    sieve[0] = sieve[1] = False\n    for i in range(2, int(n ** 0.5) + 1):\n        if sieve[i]:\n            for j in range(i * i, n, i):\n                sieve[j] = False\n    return sum(sieve)",
        _count_primes_ref, lambda rng: (rng.randint(0, 200),),
        "O(N log log N)", "O(N)",
        "Sieve of Eratosthenes up to n.",
    ),
    Family(
        "merge_intervals", "merge_intervals", "medium", ["intervals", "arrays"],
        "Given a list of `intervals` [start, end], merge all overlapping "
        "intervals and return the merged list sorted by start.",
        "1 <= intervals.length <= 10^4",
        "def merge_intervals(intervals):\n    intervals = sorted(intervals)\n    out = []\n    for iv in intervals:\n        if out and iv[0] <= out[-1][1]:\n            out[-1][1] = max(out[-1][1], iv[1])\n        else:\n            out.append(list(iv))\n    return out",
        _merge_intervals_ref,
        lambda rng: ([sorted((rng.randint(0, 20), rng.randint(0, 20)))
                      for _ in range(rng.randint(1, 6))],),
        "O(N log N)", "O(N)",
        "Sort by start, then extend or append based on overlap with the last interval.",
    ),
    Family(
        "kth_largest", "kth_largest", "medium", ["heaps", "arrays"],
        "Return the k-th largest element in the array `nums` (1-indexed).",
        "1 <= k <= nums.length <= 10^4",
        "def kth_largest(nums, k):\n    return sorted(nums, reverse=True)[k - 1]",
        _kth_largest_ref, _kth_largest_sampler,
        "O(N log N)", "O(N)",
        "Sort descending and index, or use a size-k min-heap.",
    ),
    Family(
        "is_palindrome", "is_palindrome", "easy", ["two pointers", "strings"],
        "Return True if `s` is a palindrome considering only alphanumeric "
        "characters and ignoring case.",
        "0 <= s.length <= 1000",
        "def is_palindrome(s):\n    clean = [c.lower() for c in s if c.isalnum()]\n    return clean == clean[::-1]",
        _is_palindrome_ref,
        lambda rng: ("".join(rng.choice("aA1, bB.") for _ in range(rng.randint(0, 12))),),
        "O(N)", "O(N)",
        "Filter to alphanumerics, lowercase, and compare with the reverse.",
    ),
    Family(
        "move_zeroes", "move_zeroes", "easy", ["two pointers", "arrays"],
        "Given `nums`, return a new list with all zeroes moved to the end while "
        "preserving the relative order of the non-zero elements.",
        "1 <= nums.length <= 10^4",
        "def move_zeroes(nums):\n    out = [x for x in nums if x != 0]\n    out += [0] * (len(nums) - len(out))\n    return out",
        _move_zeroes_ref,
        lambda rng: ([rng.choice([0, 0, rng.randint(-5, 5)]) for _ in range(rng.randint(1, 10))],),
        "O(N)", "O(N)",
        "Collect the non-zero elements, then pad with the removed zeroes.",
    ),
    Family(
        "subset_count", "count_subsets", "medium", ["backtracking", "math/combinatorics"],
        "Return the number of distinct subsets (including the empty set) of a "
        "list `nums` of distinct integers.",
        "0 <= nums.length <= 20",
        "def count_subsets(nums):\n    return 2 ** len(nums)",
        _subset_count_ref, lambda rng: (rng.sample(range(100), rng.randint(0, 12)),),
        "O(1)", "O(1)",
        "A set of n distinct elements has 2**n subsets.",
    ),
]


# Harder families: multi-step, edge-case heavy, or adversarially phrased to lure
# the model toward a more famous (but wrong) problem. These are meant to push
# first-attempt pass@1 below ceiling so the eval can discriminate model ability.
HARD_FAMILIES: List[Family] = [
    Family(
        "decode_ways", "decode_ways", "hard", ["dynamic programming", "strings"],
        "A digit string is decoded by mapping '1'->'A' ... '26'->'Z'. Given a "
        "string `s` of digits, return the number of distinct ways to decode it. "
        "A leading '0' or any standalone '0' that cannot pair into 10-26 yields 0 ways.",
        "1 <= s.length <= 100\ns consists of digits only",
        "def decode_ways(s):\n    if not s or s[0] == '0':\n        return 0\n    n = len(s)\n    dp = [0] * (n + 1)\n    dp[0] = dp[1] = 1\n    for i in range(2, n + 1):\n        if s[i - 1] != '0':\n            dp[i] += dp[i - 1]\n        if 10 <= int(s[i - 2:i]) <= 26:\n            dp[i] += dp[i - 2]\n    return dp[n]",
        _decode_ways_ref, _decode_sampler,
        "O(N)", "O(1)",
        "DP where dp[i] sums one-digit (if s[i-1]!='0') and two-digit (if 10..26) decodings. The '0' cases are the trap.",
        "def decode_ways(s):\n    n = len(s)\n    dp = [1] * (n + 1)\n    for i in range(2, n + 1):\n        dp[i] = dp[i - 1] + (dp[i - 2] if 10 <= int(s[i-2:i]) <= 26 else 0)\n    return dp[n]",
        "Ignores '0' handling, so strings containing '0' are mis-counted.",
    ),
    Family(
        "next_permutation", "next_permutation", "hard", ["arrays", "math/combinatorics"],
        "Given a list `nums`, return the next lexicographically greater "
        "permutation of its elements. If no greater permutation exists, return "
        "the smallest (sorted ascending) permutation.",
        "1 <= nums.length <= 100",
        "def next_permutation(nums):\n    a = list(nums)\n    n = len(a)\n    i = n - 2\n    while i >= 0 and a[i] >= a[i + 1]:\n        i -= 1\n    if i >= 0:\n        j = n - 1\n        while a[j] <= a[i]:\n            j -= 1\n        a[i], a[j] = a[j], a[i]\n    a[i + 1:] = reversed(a[i + 1:])\n    return a",
        _next_permutation_ref, _perm_sampler,
        "O(N)", "O(1)",
        "Find the rightmost ascending pair, swap with the next-larger suffix element, then reverse the suffix.",
    ),
    Family(
        "trapping_rain_water", "trap", "hard", ["two pointers", "arrays"],
        "Given non-negative integers `height` representing an elevation map where "
        "each bar has width 1, return how many units of water it can trap after raining.",
        "1 <= height.length <= 10^4\n0 <= height[i] <= 10^5",
        "def trap(height):\n    if not height:\n        return 0\n    lo, hi = 0, len(height) - 1\n    lmax = rmax = res = 0\n    while lo < hi:\n        if height[lo] < height[hi]:\n            lmax = max(lmax, height[lo])\n            res += lmax - height[lo]\n            lo += 1\n        else:\n            rmax = max(rmax, height[hi])\n            res += rmax - height[hi]\n            hi -= 1\n    return res",
        _trap_ref, _trap_sampler,
        "O(N)", "O(1)",
        "Two pointers moving inward; water at each bar is bounded by the smaller of the running left/right maxima.",
    ),
    Family(
        "lis", "length_of_lis", "hard", ["dynamic programming", "binary search"],
        "Given an integer array `nums`, return the length of the longest strictly "
        "increasing subsequence (not necessarily contiguous).",
        "1 <= nums.length <= 2500",
        "def length_of_lis(nums):\n    import bisect\n    tails = []\n    for x in nums:\n        i = bisect.bisect_left(tails, x)\n        if i == len(tails):\n            tails.append(x)\n        else:\n            tails[i] = x\n    return len(tails)",
        _lis_ref, lambda rng: (_rand_list(rng, lo=-10, hi=10, n_lo=1, n_hi=12),),
        "O(N log N)", "O(N)",
        "Patience sorting: keep the smallest possible tail for each subsequence length via binary search.",
    ),
    Family(
        "edit_distance", "edit_distance", "hard", ["dynamic programming", "strings"],
        "Given two strings `a` and `b`, return the minimum number of single-"
        "character insertions, deletions, or substitutions to turn `a` into `b`.",
        "0 <= a.length, b.length <= 500",
        "def edit_distance(a, b):\n    m, n = len(a), len(b)\n    dp = list(range(n + 1))\n    for i in range(1, m + 1):\n        prev = dp[0]\n        dp[0] = i\n        for j in range(1, n + 1):\n            cur = dp[j]\n            if a[i - 1] == b[j - 1]:\n                dp[j] = prev\n            else:\n                dp[j] = 1 + min(prev, dp[j], dp[j - 1])\n            prev = cur\n    return dp[n]",
        _edit_distance_ref, _two_str_sampler,
        "O(M*N)", "O(N)",
        "Levenshtein DP over the two strings with a rolling row.",
    ),
    Family(
        "max_profit_two", "max_profit_two", "hard", ["dynamic programming", "greedy"],
        "Given daily stock `prices`, return the maximum profit using AT MOST TWO "
        "non-overlapping buy/sell transactions (you must sell before buying again).",
        "1 <= prices.length <= 10^5\n0 <= prices[i] <= 10^5",
        "def max_profit_two(prices):\n    buy1 = buy2 = float('-inf')\n    sell1 = sell2 = 0\n    for p in prices:\n        buy1 = max(buy1, -p)\n        sell1 = max(sell1, buy1 + p)\n        buy2 = max(buy2, sell1 - p)\n        sell2 = max(sell2, buy2 + p)\n    return sell2",
        _max_profit_two_ref, _prices_sampler,
        "O(N)", "O(1)",
        "Track four running states: best profit after the 1st buy, 1st sell, 2nd buy, 2nd sell.",
        "def max_profit_two(prices):\n    lo = prices[0]\n    best = 0\n    for p in prices[1:]:\n        best = max(best, p - lo)\n        lo = min(lo, p)\n    return best",
        "Solves the single-transaction problem, ignoring the second allowed trade.",
    ),
    Family(
        "largest_rectangle", "largest_rectangle", "hard", ["stacks/queues", "arrays"],
        "Given `heights` of histogram bars each of width 1, return the area of the "
        "largest rectangle that fits entirely within the histogram.",
        "1 <= heights.length <= 10^5\n0 <= heights[i] <= 10^4",
        "def largest_rectangle(heights):\n    stack = []\n    best = 0\n    for i, h in enumerate(heights + [0]):\n        start = i\n        while stack and stack[-1][1] > h:\n            idx, height = stack.pop()\n            best = max(best, height * (i - idx))\n            start = idx\n        stack.append((start, h))\n    return best",
        _largest_rectangle_ref, _hist_sampler,
        "O(N)", "O(N)",
        "Monotonic increasing stack; when a shorter bar arrives, pop and settle rectangles using the recorded start index.",
    ),
]


def generate_task(task_id: int, family: Family, rng: random.Random) -> dict:
    # Build hidden tests from sampled inputs; reference computes expected output.
    hidden_tests, seen = [], set()
    attempts = 0
    while len(hidden_tests) < 6 and attempts < 60:
        attempts += 1
        args = family.sampler(rng)
        key = repr(args)
        if key in seen:
            continue
        try:
            ht = family.make_test(args)
        except Exception:
            continue
        seen.add(key)
        hidden_tests.append(ht)

    first = hidden_tests[0]
    examples = [Example(
        input=first.input,
        output=first.expected_output,
        explanation=f"{family.func_name}{first.input} == {first.expected_output}.",
    )]

    common_failures = None
    if family.wrong_solution:
        # Find a sampled input on which the wrong solution actually fails.
        failing_input = ""
        wrong_ns = {}
        try:
            exec(family.wrong_solution, wrong_ns)
            wrong_fn = wrong_ns[family.func_name]
            for ht in hidden_tests:
                args = eval(ht.input)
                if wrong_fn(*args) != family.ref(*args):
                    failing_input = ht.input
                    break
        except Exception:
            failing_input = ""
        if failing_input:
            common_failures = [CommonFailure(
                wrong_solution=family.wrong_solution,
                failure_reason=family.failure_reason,
                failing_test=failing_input,
            )]

    task = AlgorithmicProblem(
        id=f"algo_{task_id:06d}",
        task_type="algorithmic_problem",
        source="synthetic_generator",
        license="MIT",
        difficulty=family.difficulty,
        tags=family.tags,
        language="python",
        problem=family.problem,
        constraints=family.constraints,
        starter_code=family.starter(),
        examples=examples,
        hidden_tests=hidden_tests,
        reference_solution=family.ref_src,
        explanation=family.explanation,
        complexity=Complexity(time=family.time, space=family.space),
        common_failures=common_failures,
    )
    return task.model_dump()


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic algorithmic problems.")
    parser.add_argument("--count", type=int, default=1000, help="Number of tasks to generate.")
    parser.add_argument("--output", type=str, default="data/synthetic/algorithmic_tasks.jsonl")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--set", choices=["standard", "hard", "all"], default="standard",
                        help="Which family pool to draw from.")
    args = parser.parse_args()

    pool = {"standard": FAMILIES, "hard": HARD_FAMILIES, "all": FAMILIES + HARD_FAMILIES}[args.set]
    rng = random.Random(args.seed)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for i in range(1, args.count + 1):
            # Round-robin the first pass so every family is represented, then random.
            family = pool[(i - 1) % len(pool)] if i <= len(pool) else rng.choice(pool)
            task = generate_task(i, family, rng)
            f.write(json.dumps(task) + "\n")
            written += 1

    print(f"Generated {written} synthetic algorithmic tasks across "
          f"{len(pool)} '{args.set}' problem families saved to {out_path}.")


if __name__ == "__main__":
    main()
