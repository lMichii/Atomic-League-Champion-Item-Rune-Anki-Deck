# Author-model evaluation: Karma

Candidate: gpt-6-luna. Independent model checker: gpt-6.1-sol. Status: evaluated.

No review records, production configuration or approved content were changed.

```json
{
  "attempts_without_usage": 0,
  "available_new_attempt_usage": {
    "gpt-6-luna": {
      "cache_write_input_tokens": 0,
      "cached_input_tokens": 0,
      "input_tokens": 43425,
      "output_tokens": 4756,
      "reasoning_output_tokens": 269
    },
    "gpt-6.1-sol": {
      "cache_write_input_tokens": 0,
      "cached_input_tokens": 0,
      "input_tokens": 25105,
      "output_tokens": 2143,
      "reasoning_output_tokens": 150
    }
  },
  "candidate_model": "gpt-6-luna",
  "candidate_suitable_for_controlled_trial": false,
  "cards": 8,
  "champion": "Karma",
  "editorial_imports": 0,
  "elapsed_seconds": 73.88,
  "failed_checks": [
    {
      "all_answer_claims_covered": true,
      "beginner_friendly": true,
      "card_id": "champ:karma:overview:L1",
      "core_coverage": [
        {
          "answer_quote": "Karma is a mage and support who pokes enemies with magic damage and helps allies with shields and movement speed.",
          "covered": false,
          "mechanic_id": "karma_overview_role",
          "reason": "Explains her roles, poke, shielding and movement speed, but omits the frozen core's slows."
        },
        {
          "answer_quote": "Mantra empowers her next basic ability, changing its effect, while damaging abilities help bring Mantra back.",
          "covered": true,
          "mechanic_id": "karma_overview_empowerment",
          "reason": "Explains empowerment and cooldown recovery."
        }
      ],
      "counterplay_grounded": true,
      "english": true,
      "facts_supported": true,
      "issues": [
        "Add slowing enemies to the overview to cover its complete frozen role mechanic."
      ],
      "priority_reasonable": true
    },
    {
      "all_answer_claims_covered": true,
      "beginner_friendly": true,
      "card_id": "champ:karma:ability_variant:w:renewal:mantra:recognize:L2",
      "core_coverage": [
        {
          "answer_quote": "Renewal empowers Focused Resolve with a longer root and heals Karma when cast.",
          "covered": true,
          "mechanic_id": "karma_renewal_root",
          "reason": "Explicitly explains the longer root."
        },
        {
          "answer_quote": "Renewal empowers Focused Resolve with a longer root and heals Karma when cast. It heals her again if the tether lasts its full duration or the target dies while tethered.",
          "covered": false,
          "mechanic_id": "karma_renewal_heal",
          "reason": "Explains both healing triggers but omits that healing is based on missing health."
        }
      ],
      "counterplay_grounded": true,
      "english": true,
      "facts_supported": true,
      "issues": [
        "Specify that Renewal heals based on Karma's missing health; this explains its low-health reversal purpose.",
        "The counterplay correctly limits its prevention claim to the completion-triggered heal."
      ],
      "priority_reasonable": true
    }
  ],
  "human_approved": false,
  "kit_complete": false,
  "limitation": "Controlled source-packet comparison; model cross-check is fallible and is not human factual QA.",
  "missing_core_ids": [
    "karma_overview_role",
    "karma_renewal_heal"
  ],
  "new_model_attempts": 3,
  "omitted_topics": [
    "Renewal's missing-health-based healing, an important frozen core mechanic and explanation of its low-health purpose.",
    "Slows in the frozen overview role mechanic; slowing effects are covered on the individual Q cards."
  ],
  "production_configuration_changed": false,
  "receipts": {
    "candidate": {
      "attempts": 2,
      "configured_model": "gpt-6-luna",
      "execution_attempts": 2,
      "metadata": {
        "ephemeral": true,
        "image_inputs": 0,
        "resolved_model": "gpt-6-luna",
        "runtime_version": "codex-cli 0.164.0-alpha.11.1",
        "tool_items": 0,
        "usage": [
          {
            "cache_write_input_tokens": 0,
            "cached_input_tokens": 0,
            "input_tokens": 21718,
            "output_tokens": 2294,
            "reasoning_output_tokens": 96
          }
        ]
      },
      "output_sha256": "594c5dafb3d6406bbcfe5aa19f3a29bf302e39976f7da928050734f3a9030c4c",
      "prior_errors": [
        "Fact must quote actual answer"
      ],
      "provider": "codex",
      "request_sha256": "9f01475587c3a0bf65802081624b12c64bf7854a0ea9c838118bd8f798a3b283"
    },
    "verifier": {
      "attempts": 1,
      "configured_model": "gpt-6.1-sol",
      "execution_attempts": 1,
      "metadata": {
        "ephemeral": true,
        "image_inputs": 0,
        "resolved_model": "gpt-6.1-sol",
        "runtime_version": "codex-cli 0.164.0-alpha.11.1",
        "tool_items": 0,
        "usage": [
          {
            "cache_write_input_tokens": 0,
            "cached_input_tokens": 0,
            "input_tokens": 25105,
            "output_tokens": 2143,
            "reasoning_output_tokens": 150
          }
        ]
      },
      "output_sha256": "9fc625bfa0e8aa68b50fff141fd2b27a39a0def43fc09821d8686f618009504d",
      "prior_errors": [],
      "provider": "codex",
      "request_sha256": "9e9e57dce0c11a78d4a80e36219fcbee0942f02b51172659f9885bb2728edf2e"
    }
  },
  "schema_and_citations_passed": true,
  "schema_version": 1,
  "semantic_failed_checks": 2,
  "source_archive": "data/drafts/karma/bb319fa856301728ae26",
  "source_packet_sha256": "f19d60ffe939a23d3284cd4ffe3a797dd429fd4574822ab76572566ed98abcf2",
  "status": "evaluated",
  "verifier_model": "gpt-6.1-sol"
}
```
