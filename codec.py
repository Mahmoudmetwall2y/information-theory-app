# codec.py
import collections
import heapq
import random
from typing import Dict, List, Tuple, Optional


class HuffmanNode:
    def __init__(
        self,
        symbol: Optional[str] = None,
        prob: float = 0.0,
        left: Optional["HuffmanNode"] = None,
        right: Optional["HuffmanNode"] = None,
    ):
        self.symbol = symbol
        self.prob = prob
        self.left = left
        self.right = right

    def __lt__(self, other: "HuffmanNode") -> bool:
        return self.prob < other.prob


def compute_symbol_probabilities(text: str) -> Dict[str, float]:
    if not text:
        return {}
    counts = collections.Counter(text)
    total = sum(counts.values())
    return {sym: counts[sym] / total for sym in counts}


def build_huffman_tree(probabilities: Dict[str, float]) -> Optional[HuffmanNode]:
    heap: List[HuffmanNode] = [HuffmanNode(sym, p) for sym, p in probabilities.items()]
    if not heap:
        return None
    heapq.heapify(heap)

    if len(heap) == 1:
        only = heap[0]
        return HuffmanNode(symbol=None, prob=only.prob, left=only, right=None)

    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        parent = HuffmanNode(symbol=None, prob=n1.prob + n2.prob, left=n1, right=n2)
        heapq.heappush(heap, parent)
    return heap[0]


def build_huffman_codes(root: Optional[HuffmanNode]) -> Dict[str, str]:
    codes: Dict[str, str] = {}
    if root is None:
        return codes

    def traverse(node: HuffmanNode, prefix: str) -> None:
        if node.symbol is not None:
            codes[node.symbol] = prefix if prefix else "0"
            return
        if node.left:
            traverse(node.left, prefix + "0")
        if node.right:
            traverse(node.right, prefix + "1")

    traverse(root, "")
    return codes


def huffman_encode(text: str, codes: Dict[str, str]) -> str:
    return "".join(codes[ch] for ch in text)


def huffman_decode(bits: str, root: Optional[HuffmanNode]) -> str:
    if root is None:
        return ""
    result_chars: List[str] = []
    node = root
    for b in bits:
        node = node.left if b == "0" else node.right
        if node is None:
            break
        if node.symbol is not None:
            result_chars.append(node.symbol)
            node = root
    return "".join(result_chars)


def huffman_decode_safe(bits: str, root: Optional[HuffmanNode]) -> Tuple[str, bool]:
    if root is None:
        return "", True

    result_chars: List[str] = []
    node = root

    for b in bits:
        node = node.left if b == "0" else node.right
        if node is None:
            return "".join(result_chars), False
        if node.symbol is not None:
            result_chars.append(node.symbol)
            node = root

    return "".join(result_chars), True


def _bitstr_to_int_list(bits: str) -> List[int]:
    return [1 if b == "1" else 0 for b in bits]


def _int_list_to_bitstr(bits: List[int]) -> str:
    return "".join("1" if b else "0" for b in bits)


def hamming_7_4_encode(bitstring: str) -> Tuple[str, int]:
    if not bitstring:
        return "", 0

    pad_bits = (4 - (len(bitstring) % 4)) % 4
    bitstring_padded = bitstring + "0" * pad_bits

    encoded_bits: List[int] = []

    for i in range(0, len(bitstring_padded), 4):
        d1 = int(bitstring_padded[i])
        d2 = int(bitstring_padded[i + 1])
        d3 = int(bitstring_padded[i + 2])
        d4 = int(bitstring_padded[i + 3])

        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p4 = d2 ^ d3 ^ d4

        codeword = [p1, p2, d1, p4, d2, d3, d4]
        encoded_bits.extend(codeword)

    return _int_list_to_bitstr(encoded_bits), pad_bits


def add_errors(bitstring: str, interval: int = 50, seed: int = 123) -> str:
    if not bitstring or interval <= 0:
        return bitstring

    random.seed(seed)
    bits = list(bitstring)

    start_index = random.randint(0, max(0, interval - 1)) if interval > 1 else 0
    for i in range(start_index, len(bits), interval):
        bits[i] = "0" if bits[i] == "1" else "1"

    return "".join(bits)


def hamming_7_4_decode(encoded_bits: str, pad_bits: int) -> str:
    if not encoded_bits:
        return ""

    if len(encoded_bits) % 7 != 0:
        raise ValueError("Hamming(7,4) encoded length must be multiple of 7.")

    bits = _bitstr_to_int_list(encoded_bits)
    data_bits: List[int] = []

    for i in range(0, len(bits), 7):
        b1, b2, b3, b4, b5, b6, b7 = bits[i:i + 7]

        s1 = b1 ^ b3 ^ b5 ^ b7
        s2 = b2 ^ b3 ^ b6 ^ b7
        s4 = b4 ^ b5 ^ b6 ^ b7

        error_pos = s1 + (s2 << 1) + (s4 << 2)

        if error_pos != 0:
            idx = i + error_pos - 1
            bits[idx] ^= 1
            b1, b2, b3, b4, b5, b6, b7 = bits[i:i + 7]

        data_bits.extend([b3, b5, b6, b7])

    if pad_bits > 0:
        data_bits = data_bits[:-pad_bits]

    return _int_list_to_bitstr(data_bits)


def hamming_7_4_decode_no_correction(encoded_bits: str, pad_bits: int) -> str:
    if not encoded_bits:
        return ""

    if len(encoded_bits) % 7 != 0:
        raise ValueError("Hamming(7,4) encoded length must be multiple of 7.")

    bits = _bitstr_to_int_list(encoded_bits)
    data_bits: List[int] = []

    for i in range(0, len(bits), 7):
        b1, b2, b3, b4, b5, b6, b7 = bits[i:i + 7]
        data_bits.extend([b3, b5, b6, b7])

    if pad_bits > 0:
        data_bits = data_bits[:-pad_bits]

    return _int_list_to_bitstr(data_bits)


def run_full_pipeline(text: str, error_interval: int = 50) -> dict:
    # Part 1
    probs = compute_symbol_probabilities(text)

    # Parts 2–3: Huffman
    root = build_huffman_tree(probs)
    codes = build_huffman_codes(root)
    encoded_bits = huffman_encode(text, codes) if text else ""
    decoded_text = huffman_decode(encoded_bits, root)

    # Parts 4–6: Hamming
    hamming_bits, pad_bits = hamming_7_4_encode(encoded_bits)
    corrupted_bits = add_errors(hamming_bits, interval=error_interval, seed=2024)

    # (Part 5 extra) decode corrupted bits WITHOUT correction
    corrupted_data_bits = hamming_7_4_decode_no_correction(corrupted_bits, pad_bits)
    corrupted_decoded_text, corrupted_decode_ok = huffman_decode_safe(corrupted_data_bits, root)

    # Part 6: decode WITH correction
    recovered_bits = hamming_7_4_decode(corrupted_bits, pad_bits)

    # NEW: النص بعد التصحيح (بعد الـ correction)
    recovered_decoded_text = huffman_decode(recovered_bits, root)
    recovered_text_ok = recovered_decoded_text == text

    return {
        "text_length": len(text),
        "probabilities": probs,
        "codes": codes,
        "encoded_bits": encoded_bits,
        "decoded_text": decoded_text,

        "hamming_bits": hamming_bits,
        "pad_bits": pad_bits,
        "corrupted_bits": corrupted_bits,

        "corrupted_data_bits": corrupted_data_bits,
        "corrupted_decoded_text": corrupted_decoded_text,
        "corrupted_decode_ok": corrupted_decode_ok,

        "recovered_bits": recovered_bits,

        # NEW outputs
        "recovered_decoded_text": recovered_decoded_text,
        "recovered_text_ok": recovered_text_ok,

        "huffman_ok": decoded_text == text,
        "hamming_ok": recovered_bits == encoded_bits,
    }
