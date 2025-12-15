import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, Tuple

# Ensure the project root is on the import path so codec can be imported on Vercel
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from codec import run_full_pipeline


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _preview(text: str, limit: int) -> str:
    return text[:limit] if text else ""


def _validate_request(data: Dict[str, Any]) -> Tuple[str, int]:
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")

    text = data.get("text", "")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("'text' must be a non-empty string")

    try:
        interval = int(data.get("error_interval", 50))
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("'error_interval' must be an integer") from exc

    if interval < 1:
        raise ValueError("'error_interval' must be >= 1")

    return text, interval


def _build_response(text: str, interval: int, results: Dict[str, Any]) -> Dict[str, Any]:
    encoded_bits = results.get("encoded_bits", "")
    hamming_bits = results.get("hamming_bits", "")
    corrupted_bits = results.get("corrupted_bits", "")
    recovered_bits = results.get("recovered_bits", "")

    encoded_length = len(encoded_bits)
    hamming_length = len(hamming_bits)
    compression_ratio = (
        f"{(len(text) / encoded_length):.2f}:1" if encoded_length else "N/A"
    )

    top_probs = sorted(results.get("probabilities", {}).items(), key=lambda kv: -kv[1])[:10]

    return {
        "success": True,
        "summary": {
            "original_length": len(text),
            "encoded_length": encoded_length,
            "hamming_length": hamming_length,
            "pad_bits": results.get("pad_bits", 0),
            "compression_ratio": compression_ratio,
        },
        "quality_metrics": {
            "huffman_ok": results.get("huffman_ok", False),
            "hamming_ok": results.get("hamming_ok", False),
            "corrupted_decode_ok": results.get("corrupted_decode_ok", False),
            "recovered_text_ok": results.get("recovered_text_ok", False),
        },
        "top_probabilities": top_probs,
        "encoded_bits_preview": _preview(encoded_bits, 200),
        "hamming_bits_preview": _preview(hamming_bits, 200),
        "corrupted_bits_preview": _preview(corrupted_bits, 200),
        "recovered_bits_preview": _preview(recovered_bits, 200),
        "original_text_preview": _preview(text, 300),
        "decoded_text_preview": _preview(results.get("decoded_text", ""), 300),
        "corrupted_decoded_preview": _preview(results.get("corrupted_decoded_text", ""), 300),
        "recovered_decoded_preview": _preview(results.get("recovered_decoded_text", ""), 300),
        # Full outputs to support downloads on the client
        "encoded_bits": encoded_bits,
        "hamming_bits": hamming_bits,
        "corrupted_bits": corrupted_bits,
        "recovered_bits": recovered_bits,
        "corrupted_decoded_text": results.get("corrupted_decoded_text", ""),
        "recovered_decoded_text": results.get("recovered_decoded_text", ""),
        "codes": results.get("codes", {}),
        "probabilities": results.get("probabilities", {}),
        "error_interval": interval,
    }


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:  # pragma: no cover - HTTP negotiation
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length) if content_length else b""
            try:
                data = json.loads(raw_body.decode("utf-8")) if raw_body else {}
            except json.JSONDecodeError as exc:
                _json_response(self, 400, {"error": f"Invalid JSON: {exc}"})
                return

            try:
                text, interval = _validate_request(data)
            except ValueError as exc:
                _json_response(self, 400, {"error": str(exc)})
                return

            pipeline_results = run_full_pipeline(text, error_interval=interval)
            response_body = _build_response(text, interval, pipeline_results)
            _json_response(self, 200, response_body)
        except Exception as exc:  # pragma: no cover - runtime guard
            _json_response(self, 500, {"error": f"Processing failed: {exc}"})

    def log_message(self, format: str, *args: Any) -> None:  # pragma: no cover - silence logs
        return
