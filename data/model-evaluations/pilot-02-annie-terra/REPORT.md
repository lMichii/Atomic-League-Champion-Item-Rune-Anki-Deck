# Author-model evaluation: Annie

Candidate: gpt-6.1-terra. Independent model checker: gpt-6.1-sol. Status: failed.

No review records, production configuration or approved content were changed.

```json
{
  "attempts_without_usage": 1,
  "available_new_attempt_usage": {
    "gpt-6.1-sol": {
      "cache_write_input_tokens": 0,
      "cached_input_tokens": 12672,
      "input_tokens": 27551,
      "output_tokens": 7721,
      "reasoning_output_tokens": 167
    },
    "gpt-6.1-terra": {
      "cache_write_input_tokens": 0,
      "cached_input_tokens": 0,
      "input_tokens": 25747,
      "output_tokens": 2829,
      "reasoning_output_tokens": 0
    }
  },
  "candidate_model": "gpt-6.1-terra",
  "candidate_suitable_for_controlled_trial": false,
  "champion": "Annie",
  "editorial_imports": 0,
  "elapsed_seconds": 413.77,
  "error": "AI verify failed after 2 attempts this execution; inspect D:\\Billo Programme\\League Anki\\.cache\\model-evaluation\\6f2c63e03da3ccef47b9\\ai\\31ae32f3e959db4f0e25389e08f55c65c0f32717a58a71905a1ebc70975a7487",
  "error_type": "ModelError",
  "human_approved": false,
  "limitation": "Controlled source-packet comparison; model cross-check is fallible and is not human factual QA.",
  "new_model_attempts": 3,
  "production_configuration_changed": false,
  "receipts": {
    "candidate": {
      "attempts": 1,
      "configured_model": "gpt-6.1-terra",
      "execution_attempts": 1,
      "metadata": {
        "ephemeral": true,
        "image_inputs": 4,
        "resolved_model": "gpt-6.1-terra",
        "runtime_version": "codex-cli 0.164.0-alpha.11.1",
        "tool_items": 0,
        "usage": [
          {
            "cache_write_input_tokens": 0,
            "cached_input_tokens": 0,
            "input_tokens": 25747,
            "output_tokens": 2829,
            "reasoning_output_tokens": 0
          }
        ]
      },
      "output_sha256": "d214854cdf47c592f6daa5351359423f7682a82c6f1d081e6564a5ab937d2149",
      "prior_errors": [],
      "provider": "codex",
      "request_sha256": "bbf4882fe80372b63e304d83c2c816c479cc0461505efe4a45b72e3af75bd917"
    }
  },
  "schema_version": 1,
  "source_archive": "data/drafts/annie/b371d44901a61a8e14df",
  "source_packet_sha256": "7fcf72c087888c175ee177b301b063f92e6dd4107cba423af7e9592e99ba12fa",
  "status": "failed",
  "verifier_model": "gpt-6.1-sol"
}
```
