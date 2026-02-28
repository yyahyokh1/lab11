#!/usr/bin/env python3
"""
Exhaustive decoder for the clock emoji CTF cipher in task.txt.

Clock emoji -> hour value mapping (1-12):
  🕐=1, 🕑=2, 🕒=3, 🕓=4, 🕔=5, 🕕=6,
  🕖=7, 🕗=8, 🕘=9, 🕙=10, 🕚=11, 🕛=12
"""

import itertools
import string

CLOCK_MAP = {
    '\U0001F550': 1,   # 🕐  1 o'clock
    '\U0001F551': 2,   # 🕑  2 o'clock
    '\U0001F552': 3,   # 🕒  3 o'clock
    '\U0001F553': 4,   # 🕓  4 o'clock
    '\U0001F554': 5,   # 🕔  5 o'clock
    '\U0001F555': 6,   # 🕕  6 o'clock
    '\U0001F556': 7,   # 🕖  7 o'clock
    '\U0001F557': 8,   # 🕗  8 o'clock
    '\U0001F558': 9,   # 🕘  9 o'clock
    '\U0001F559': 10,  # 🕙 10 o'clock
    '\U0001F55A': 11,  # 🕚 11 o'clock
    '\U0001F55B': 12,  # 🕛 12 o'clock
}

PRINTABLE = set(string.printable)


def is_printable(s):
    return all(c in PRINTABLE for c in s) and len(s) > 0


def parse_cipher(path='task.txt'):
    """Return list of group value-lists, preserving word boundary info."""
    with open(path, encoding='utf-8') as f:
        text = f.read().strip()

    groups = []
    word_break_after = None  # index into groups of last group before the space

    # Scan character by character
    current_group = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in CLOCK_MAP:
            current_group.append(CLOCK_MAP[ch])
        elif ch == '|':
            if current_group:
                groups.append(current_group)
                current_group = []
        elif ch == ' ':
            # If this space is NOT preceded by '|', it's a word break
            if current_group:
                groups.append(current_group)
                current_group = []
                # Check if previous char was NOT '|' (word break)
                if i > 0 and text[i-1] != '|' and word_break_after is None:
                    word_break_after = len(groups) - 1
        i += 1

    if current_group:
        groups.append(current_group)

    return groups, word_break_after


def decode_base(groups, base, offset):
    """Interpret each group as a base-N number where clock value v -> (v + offset)."""
    result = []
    for g in groups:
        n = 0
        for v in g:
            digit = v + offset
            n = n * base + digit
        result.append(n)
    return result


def try_decode(label, numbers, transform=None):
    """Try to convert a list of ints to a string; print if fully printable."""
    if transform:
        numbers = [transform(n) for n in numbers]
    try:
        s = ''.join(chr(n) for n in numbers)
        if is_printable(s):
            print(f"  [{label}] => {s!r}")
            return s
    except (ValueError, OverflowError):
        pass
    return None


def show_partial(label, numbers):
    """Show partial decode (replace non-printable with their values) for diagnostic."""
    parts = []
    for n in numbers:
        try:
            c = chr(n)
            parts.append(c if c in PRINTABLE else f'[{n}]')
        except (ValueError, OverflowError):
            parts.append(f'[{n}]')
    s = ''.join(parts)
    print(f"  [{label}] partial => {s!r}")


def rot_n(s, n):
    result = []
    for c in s:
        if 'A' <= c <= 'Z':
            result.append(chr((ord(c) - ord('A') + n) % 26 + ord('A')))
        elif 'a' <= c <= 'z':
            result.append(chr((ord(c) - ord('a') + n) % 26 + ord('a')))
        else:
            result.append(c)
    return ''.join(result)


def main():
    groups, word_break = parse_cipher()
    print(f"Parsed {len(groups)} groups (word break after group {word_break}):")
    for i, g in enumerate(groups, 1):
        marker = " <-- WORD BREAK" if word_break == i - 1 else ""
        print(f"  Group {i:2d}: {g}{marker}")
    print()

    sums = [sum(g) for g in groups]
    word1_groups = groups[:word_break+1] if word_break else groups
    word2_groups = groups[word_break+1:] if word_break else []

    # ---- Method 1: base-12 positional, various offsets ----
    print("=== Method 1: base-12 positional (clock value mapped to digit) ===")
    for offset in range(-1, 2):
        label = f"base12 offset={offset}"
        nums = decode_base(groups, 12, offset)
        r = try_decode(label, nums)
        if not r:
            show_partial(label, nums)
        for shift in range(-32, 33):
            shifted = [n + shift for n in nums]
            try_decode(f"{label} +{shift}", shifted)

    # ---- Method 2: base-13 positional ----
    print("\n=== Method 2: base-13 positional ===")
    for offset in range(-1, 2):
        label = f"base13 offset={offset}"
        nums = decode_base(groups, 13, offset)
        try_decode(label, nums)
        for shift in range(-32, 33):
            try_decode(f"{label} +{shift}", [n + shift for n in nums])

    # ---- Method 3: sum of group digits -> ASCII ----
    print("\n=== Method 3: sum of clocks per group -> ASCII (with various offsets) ===")
    for offset in range(-1, 2):
        raw_sums = [sum(v + offset for v in g) for g in groups]
        label = f"sum (clock offset={offset})"
        try_decode(label, raw_sums)
        show_partial(label, raw_sums)
        for shift in range(0, 128):
            try_decode(f"{label} +{shift}", [n + shift for n in raw_sums])

    # ---- Method 4: digit-string concatenation as decimal -> ASCII ----
    print("\n=== Method 4: digit-string concatenation as decimal -> ASCII ===")
    for offset in range(-1, 2):
        nums = []
        for g in groups:
            s = ''.join(str(v + offset) for v in g)
            try:
                nums.append(int(s))
            except ValueError:
                nums.append(-1)
        label = f"concat-decimal offset={offset}"
        r = try_decode(label, nums)
        if not r:
            show_partial(label, nums)

    # ---- Method 5: each group -> hex string -> int ----
    print("\n=== Method 5: group digits as hex ===")
    for offset in range(-1, 2):
        nums = []
        valid = True
        for g in groups:
            digits = [v + offset for v in g]
            h = ''.join(f'{d:x}' for d in digits)
            try:
                nums.append(int(h, 16))
            except ValueError:
                valid = False
                break
        if valid:
            label = f"hex offset={offset}"
            r = try_decode(label, nums)
            if not r:
                show_partial(label, nums)

    # ---- Method 6: mixed - 2-clock groups base-10, 3-clock groups summed ----
    print("\n=== Method 6: mixed - 2-clock groups base-10, 3-clock groups summed ===")
    for c_offset in range(-1, 2):
        nums = []
        for g in groups:
            digs = [v + c_offset for v in g]
            if len(g) == 2:
                n = digs[0] * 10 + digs[1]
            else:
                n = sum(digs)
            nums.append(n)
        label = f"mixed b10/sum offset={c_offset}"
        r = try_decode(label, nums)
        if not r:
            show_partial(label, nums)

    # ---- Method 7: product of clocks -> ASCII ----
    print("\n=== Method 7: product of clocks per group -> ASCII ===")
    for offset in range(-1, 2):
        prods = []
        for g in groups:
            p = 1
            for v in g:
                p *= (v + offset)
            prods.append(p)
        label = f"product offset={offset}"
        r = try_decode(label, prods)
        if not r:
            show_partial(label, prods)

    # ---- Method 8: sum as A=1...Z=26 letter index ----
    print("\n=== Method 8: sum as A=1...Z=26 letter index ===")
    letters = []
    for n in sums:
        if 1 <= n <= 26:
            letters.append(chr(ord('A') + n - 1))
        elif 27 <= n <= 52:
            letters.append(chr(ord('a') + n - 27))
        else:
            letters.append(f'[{n}]')
    s = ''.join(letters)
    print(f"  [A1Z26 sum] => {s!r}")

    # ---- Method 9: flat digit stream re-split ----
    print("\n=== Method 9: flat digit stream re-split ===")
    for offset in range(-1, 2):
        flat = []
        for g in groups:
            for v in g:
                flat.append(v + offset)
        for chunk in [2, 3]:
            pieces = [flat[i:i+chunk] for i in range(0, len(flat) - chunk + 1, chunk)]
            for base in [10, 12, 16]:
                nums = []
                for p in pieces:
                    n = 0
                    for d in p:
                        n = n * base + d
                    nums.append(n)
                label = f"flat off={offset} chunk={chunk} base={base}"
                try_decode(label, nums)

    # ---- Method 10: base-12 decode then apply ROT-N ----
    print("\n=== Method 10: base-12 -> printable subset -> ROT-N ===")
    nums = decode_base(groups, 12, 1)  # clocks 1-12
    for shift in range(-32, 33):
        shifted = [n + shift for n in nums]
        s = ''.join(chr(n) if 32 <= n <= 126 else '?' for n in shifted)
        if '?' not in s:
            print(f"  [base12 +{shift} no-gap] => {s!r}")
            for rot in range(1, 26):
                print(f"    ROT{rot}: {rot_n(s, rot)!r}")

    # ---- Method 11: two separate words decoded independently ----
    print("\n=== Method 11: two words decoded separately ===")
    w_sums = [[sum(g) for g in word1_groups], [sum(g) for g in word2_groups]]
    for wi, ws in enumerate(w_sums):
        for shift in range(32, 127):
            s = ''.join(chr(n + shift) for n in ws if 32 <= n + shift <= 126)
            if len(s) == len(ws):
                break
        print(f"  Word {wi+1} sums: {ws}")
        for shift in range(0, 128):
            try_decode(f"word{wi+1} sum+{shift}", [n + shift for n in ws])

    # ---- Method 12: reversed group order ----
    print("\n=== Method 12: reversed group order ===")
    rev = list(reversed(groups))
    for base in [12]:
        for offset in [0, 1, -1]:
            nums = decode_base(rev, base, offset)
            for shift in range(-32, 33):
                try_decode(f"reversed base{base} off={offset} +{shift}",
                           [n + shift for n in nums])

    # ---- Method 13: XOR of clock values per group ----
    print("\n=== Method 13: XOR of clocks per group ===")
    xors = [0 for _ in groups]
    for i, g in enumerate(groups):
        x = 0
        for v in g:
            x ^= v
        xors[i] = x
    for shift in range(0, 128):
        try_decode(f"XOR +{shift}", [n + shift for n in xors])

    # ---- Method 14: group as octal ----
    print("\n=== Method 14: group as octal ===")
    for offset in [0, -1]:
        nums = []
        valid = True
        for g in groups:
            digs = [v + offset for v in g]
            if any(d >= 8 for d in digs):
                valid = False
                break
            n = int(''.join(str(d) for d in digs), 8)
            nums.append(n)
        if valid:
            for shift in range(-32, 33):
                try_decode(f"octal off={offset} +{shift}", [n + shift for n in nums])

    # ---- Method 15: pair consecutive group sums ----
    print("\n=== Method 15: pair consecutive group sums ===")
    for base in [26, 27, 32]:
        pairs = []
        for i in range(0, len(sums) - 1, 2):
            pairs.append(sums[i] * base + sums[i + 1])
        for shift in range(-32, 33):
            try_decode(f"paired sums base{base} +{shift}", [n + shift for n in pairs])

    # ---- Method 16: clock as minute value (v*5), sum per group ----
    print("\n=== Method 16: minute values (clock*5), sum per group -> ASCII ===")
    min_sums = [sum(v * 5 for v in g) for g in groups]
    label = "minute_sum"
    r = try_decode(label, min_sums)
    if not r:
        show_partial(label, min_sums)
    for shift in range(-64, 65):
        try_decode(f"minute_sum +{shift}", [n + shift for n in min_sums])

    # ---- Method 17: 1-prefix rule for 3-clock groups, base-12 for 2-clock ----
    print("\n=== Method 17: mixed - 3-clock 🕐-prefix use 100+sum(rest); others base-12 ===")
    nums17 = []
    for g in groups:
        if len(g) == 3 and g[0] == 1:
            nums17.append(100 + sum(g[1:]))
        else:
            nums17.append(sum(v * (12**(len(g)-1-i)) for i, v in enumerate(g)))
    r = try_decode("1prefix+base12", nums17)
    if not r:
        show_partial("1prefix+base12", nums17)
    for shift in range(-32, 33):
        try_decode(f"1prefix+base12 +{shift}", [n + shift for n in nums17])

    # ---- Method 18: sum approach, ROT search for flag patterns ----
    print("\n=== Method 18: sum+offset, search ROT-N for flag patterns ===")
    for offset in range(32, 127):
        chars = []
        ok = True
        for n in sums:
            v = n + offset
            if not (32 <= v <= 126):
                ok = False
                break
            chars.append(chr(v))
        if not ok:
            continue
        s = ''.join(chars)
        for rot_shift in range(0, 26):
            rotated = rot_n(s, rot_shift)
            has_flag_fmt = (
                'MBM' in rotated or 'mbm' in rotated or
                'CTF' in rotated or 'FLAG' in rotated or
                ('{' in rotated and '}' in rotated)
            )
            if has_flag_fmt:
                print(f"  [sum+{offset} ROT{rot_shift}] => {rotated!r}")

    # ---- Method 19: each clock = letter A-L, concatenate ----
    print("\n=== Method 19: each clock directly = letter (🕐=A,...🕛=L) ===")
    all_letters = ''.join(chr(ord('A') + v - 1) for g in groups for v in g)
    print(f"  [A-L concat] => {all_letters!r}")
    for shift in range(0, 26):
        s = rot_n(all_letters, shift)
        if 'MBM' in s or 'CTF' in s or 'FLAG' in s:
            print(f"  [A-L ROT{shift}] => {s!r}")

    # ---- Method 20: base-12 values as Latin-1 bytes ----
    print("\n=== Method 20: base-12 values mod 256 as bytes decoded as Latin-1 ===")
    nums_b12 = decode_base(groups, 12, 1)
    print(f"  base-12 values: {nums_b12}")
    try:
        as_bytes = bytes([n % 256 for n in nums_b12])
        decoded_latin1 = as_bytes.decode('latin-1')
        print(f"  as latin-1: {decoded_latin1!r}")
        decoded_utf8_safe = ''.join(c if c in PRINTABLE else f'[{ord(c)}]'
                                    for c in decoded_latin1)
        print(f"  printable: {decoded_utf8_safe!r}")
    except Exception as e:
        print(f"  error: {e}")

    # ---- Method 21: adjacent clock-value pairs across all groups ----
    print("\n=== Method 21: adjacent clock pairs (all values flattened), sum pairs ===")
    flat_vals = [v for g in groups for v in g]
    pair_sums = [flat_vals[i] + flat_vals[i+1]
                 for i in range(0, len(flat_vals)-1, 2)]
    for shift in range(0, 128):
        try_decode(f"pair_sums +{shift}", [n + shift for n in pair_sums])

    # ---- Method 22: 2-clock sum+offset; 3-clock 1-prefix; include space as '_' ----
    print("\n=== Method 22: 2-clock sum+offset, 3-clock 1-prefix; space -> char ===")
    for two_off in range(60, 110):
        chars = []
        ok = True
        for g in groups:
            if len(g) == 3 and g[0] == 1:
                n = 100 + sum(g[1:])
            else:
                n = sum(g) + two_off
            if not (32 <= n <= 126):
                ok = False
                break
            chars.append(chr(n))
        if ok:
            chars_with_sep = chars[:]
            if word_break is not None:
                chars_with_sep.insert(word_break + 1, '_')
            nums22 = [ord(c) for c in chars_with_sep]
            try_decode(f"2clk+{two_off},3clk-1prefix", nums22)

    # ---- Method 23: Vigenère - decrypt word2 using word1 as key ----
    print("\n=== Method 23: Vigenère cross-word decryption ===")
    w1_sums = [sum(g) for g in word1_groups]
    w2_sums = [sum(g) for g in word2_groups]
    if len(w1_sums) == len(w2_sums):
        # word2 - word1 mod 26 (both 0-indexed: A=0)
        decrypted = [(b - a) % 26 for a, b in zip(w1_sums, w2_sums)]
        msg = ''.join(chr(ord('A') + n) for n in decrypted)
        print(f"  [word2 - word1 mod26] => {msg!r}")
        decrypted2 = [(a - b) % 26 for a, b in zip(w1_sums, w2_sums)]
        msg2 = ''.join(chr(ord('A') + n) for n in decrypted2)
        print(f"  [word1 - word2 mod26] => {msg2!r}")
        decrypted3 = [(a + b) % 26 for a, b in zip(w1_sums, w2_sums)]
        msg3 = ''.join(chr(ord('A') + n) for n in decrypted3)
        print(f"  [word1 + word2 mod26] => {msg3!r}")
        decrypted4 = [(a ^ b) for a, b in zip(w1_sums, w2_sums)]
        for shift in range(64, 97):
            try_decode(f"word1 XOR word2 +{shift}",
                       [n + shift for n in decrypted4])

    # ---- FINAL: summarise the most promising flag candidates ----
    print("\n" + "="*60)
    print("FINAL FLAG CANDIDATES")
    print("="*60)

    msg_upper = ''.join(chr(n + 64) for n in sums)
    msg_lower = ''.join(chr(n + 96) for n in sums)
    w1_up = ''.join(chr(n + 64) for n in w1_sums)
    w2_up = ''.join(chr(n + 64) for n in w2_sums)
    w1_lo = ''.join(chr(n + 96) for n in w1_sums)
    w2_lo = ''.join(chr(n + 96) for n in w2_sums)

    print(f"\n[SUM DECODE - uppercase]: {msg_upper!r}")
    print(f"[SUM DECODE - lowercase]: {msg_lower!r}")
    print(f"[Word 1 (uppercase)]: {w1_up!r}")
    print(f"[Word 2 (uppercase)]: {w2_up!r}")
    print(f"\n[Candidate A] MBM{{{msg_lower}}}")
    print(f"[Candidate B] MBM{{{w1_lo}_{w2_lo}}}")
    print(f"[Candidate C] MBM{{{msg_upper}}}")
    print(f"[Candidate D] {{{msg_lower}}}")

    # Show base-12 partial for reference
    b12_vals = [sum(v * (12**(len(g)-1-i)) for i, v in enumerate(g)) for g in groups]
    b12_partial = ''.join(chr(n) if 32 <= n <= 126 else f'[{n}]' for n in b12_vals)
    print(f"\n[BASE-12 partial]: {b12_partial!r}")
    print(f"  -> Note: group 1 = '{{' (123), group 21 = '}}' (125), groups 22&26 = 'M' (77)")

    print("\nDone.")


if __name__ == '__main__':
    main()
