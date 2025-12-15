# Information Theory Web App

This project implements an information-theory processing pipeline (Huffman + Hamming with channel errors and correction) with a modern frontend and serverless backend suitable for Vercel deployments.

## Local development
1. Install the Vercel CLI if you do not have it yet:
   ```bash
   npm install -g vercel
   ```
2. From the project root, run the local dev server (uses the Python runtime for `/api/process`):
   ```bash
   vercel dev
   ```
3. Open the printed localhost URL in your browser, upload a text file, choose the error interval, and run the pipeline.

## Endpoint contract
- **POST** `/api/process`
- Request JSON body: `{ "text": "...", "error_interval": <int>=50 }`
- Successful JSON response includes:
  - `summary` (lengths, pad bits, compression ratio)
  - `quality_metrics` (huffman_ok, hamming_ok, recovered_text_ok, corrupted_decode_ok)
  - `top_probabilities`
  - Stage previews (`encoded_bits_preview`, `hamming_bits_preview`, `corrupted_bits_preview`, `recovered_bits_preview`, `decoded_text_preview`, `corrupted_decoded_preview`, `recovered_decoded_preview`)
  - Full outputs for downloads (`encoded_bits`, `hamming_bits`, `corrupted_bits`, `recovered_bits`, `corrupted_decoded_text`, `recovered_decoded_text`, `codes`, `probabilities`, `error_interval`)

Example curl:
```bash
curl -X POST http://localhost:3000/api/process \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "error_interval": 7}'
```
Expect a JSON response with the keys described above, including populated previews and the corrected decoded text.

## Deployment
Deploy with the Vercel CLI or Vercel dashboard. No additional build steps are required; the Python runtime picks up `api/process.py` automatically.
