# SPEC-002 Candidate Matching Engine

## 1. Purpose
Define a deterministic, configurable candidate-to-job matching engine for Blackcrest RecruitOS Version 2. The engine evaluates one applicant against one job order and returns a transparent match decision with explainable scoring components. This specification is architecture-only and does not introduce implementation code.

## 2. Business Goals
- Improve recruiter speed-to-shortlist with consistent, repeatable match scoring.
- Reduce subjective variance in candidate screening by standardizing scoring factors.
- Increase submission quality by aligning applicants to job order requirements.
- Preserve recruiter trust through clear factor-level explanations.
- Support multi-tenant business rules by organization and client-specific profile tuning.

## 3. Architecture Overview
The Candidate Matching Engine is a domain service layer component in Version 2 that operates after applicant intake and resume intelligence extraction.

High-level flow:
1. Applicant profile data is already structured by intake and resume intelligence.
2. Job order requirements are normalized from Job Order domain fields and optional hiring preferences.
3. Matching engine applies a selected deterministic scoring profile.
4. Engine produces MatchResult with factor scores, total score, confidence, recommendation, and explanation.
5. Downstream workflows consume MatchResult for recruiter queues and reporting.

Design principles:
- Deterministic: same inputs and profile produce same outputs.
- Configurable: factor weights and thresholds are profile-driven.
- Explainable: each score contribution is traceable.
- Tenant-aware: profile selection can vary by organization/client/job family.

## 4. Inputs
### Required Inputs
- Applicant context:
  - applicant_id
  - organization_id
  - client_id
  - job_order_id
- Applicant structured attributes:
  - contact/location fields
  - skills
  - employers and titles
  - years_experience
  - certifications/licenses
  - delivery/management indicators
  - cdl and military indicators
- Job order context:
  - job_order_id
  - organization_id
  - client_id
- Job order requirements:
  - title and role family
  - required/preferred skills
  - minimum years experience
  - required licenses/certifications
  - location/work modality constraints
  - delivery, management, CDL preferences/requirements
- Scoring profile key:
  - organization default, client override, or explicit profile id

### Optional Inputs
- Recruiter override flags (for simulation mode only; not persisted unless approved).
- Temporal context (for tie-break logic and stale profile checks).

## 5. Outputs
The engine returns one deterministic MatchResult payload containing:
- Identity and linkage fields:
  - match_id (or computed correlation id)
  - applicant_id
  - job_order_id
  - organization_id
  - client_id
  - profile_id/profile_name
- Scoring outputs:
  - total_score (0-100)
  - normalized_factor_scores
  - weighted_factor_scores
  - factor_breakdown list
- Decision outputs:
  - recommendation (Strong Match, Match, Borderline, Do Not Recommend)
  - confidence (0.00-1.00)
- Explanation outputs:
  - recruiter_summary (short deterministic narrative)
  - strengths list
  - gaps list
  - gating_failures list
- Diagnostics:
  - rule_version
  - computed_at
  - deterministic_hash (input + profile fingerprint)

## 6. Candidate Matching Workflow
1. Validate context ownership boundaries:
   - Applicant, job order, client, and organization must be consistent.
2. Resolve active scoring profile:
   - explicit profile -> client profile -> organization default -> platform default.
3. Normalize data:
   - case normalization, token normalization, synonym expansion, de-duplication.
4. Evaluate gating rules:
   - hard requirements (for example required license/CDL) checked first.
5. Compute factor-level raw scores:
   - each factor produces a bounded score and evidence.
6. Apply weights and aggregate total score:
   - weighted deterministic calculation with fixed rounding policy.
7. Apply recommendation thresholds:
   - map total score + gating outcomes to recommendation band.
8. Compute confidence:
   - based on evidence completeness and score stability characteristics.
9. Generate explanation:
   - deterministic template-based summary, strengths, and gaps.
10. Emit MatchResult:
   - include profile metadata and traceability fields.

## 7. Scoring Architecture
Scoring is a weighted-factor deterministic system.

Formula:
- Let factors be f_i with raw score r_i in [0,1] and weight w_i where sum(w_i)=1.
- Weighted total T is:
  - T = 100 * sum(r_i * w_i)
- Apply fixed rounding:
  - round half up to 2 decimals.

Architecture rules:
- No stochastic or model-generated score components.
- Factor functions are pure for identical normalized inputs.
- Missing data handling is explicit per factor (neutral, penalized, or excluded).
- Gating failures can cap or override recommendation independent of T.

## 8. Configurable Scoring Profiles
A ScoringProfile defines:
- profile_id, name, scope (platform/org/client/job_family)
- factor weights
- factor-specific parameters (for example required skill minimums)
- threshold bands for recommendations
- confidence parameters
- version and effective date

Profile hierarchy:
1. Explicit profile passed by workflow.
2. Client-level default profile.
3. Organization-level default profile.
4. Platform baseline profile.

Governance:
- Profiles are versioned and immutable after activation.
- Changes require new version issuance.
- MatchResult stores profile version used for replayability.

## 9. MatchResult Model
Conceptual model (documentation-level only):
- Core fields:
  - match_id
  - applicant_id
  - job_order_id
  - organization_id
  - client_id
  - profile_id
  - profile_version
  - total_score
  - recommendation
  - confidence
- Breakdown fields:
  - factor_breakdown (list of factor_name, raw_score, weight, weighted_score, evidence)
  - strengths
  - gaps
  - gating_failures
- Audit fields:
  - deterministic_hash
  - computed_at
  - rule_version
  - explanation_text

## 10. Scoring Factors
Baseline factors (configurable enablement and weights):
- Skills Match:
  - overlap of required and preferred skills.
- Experience Match:
  - years_experience compared to minimum and target ranges.
- Title Relevance:
  - historical titles aligned to job title family.
- Industry/Employer Relevance:
  - prior employers mapped to target domain preferences.
- Certification Match:
  - required and preferred certifications.
- License Match:
  - required and preferred licenses; includes CDL checks.
- Location Fit:
  - city/state proximity and modality constraints.
- Delivery Domain Fit:
  - delivery-related signals for logistics roles.
- Management Fit:
  - management indicators for supervisory roles.
- Military Preference Bonus (optional policy-controlled):
  - additive bounded bonus when enabled by profile.

Each factor must define:
- Input dependencies
- Raw score function
- Missing data policy
- Evidence payload for explanations

## 11. Recommendation Logic
Recommendation bands are profile-driven and deterministic.

Example baseline bands:
- Strong Match: T >= 85 and no gating failures
- Match: 70 <= T < 85 and no critical gating failures
- Borderline: 55 <= T < 70 or minor gating concerns
- Do Not Recommend: T < 55 or critical gating failure

Override rules:
- Critical gating failure (for example required CDL absent) forces Do Not Recommend regardless of T.
- Recruiter can manually override decision downstream, but engine output remains immutable for audit trace.

## 12. Confidence Calculation
Confidence C is deterministic and separate from total score.

Inputs to confidence:
- Evidence completeness ratio (how many required factor inputs are present).
- Signal consistency (agreement across related factors).
- Threshold distance (margin from recommendation boundaries).

Example conceptual formula:
- C = clamp(0, 1, a*completeness + b*consistency + c*margin)
- a, b, c are profile parameters with a+b+c=1.

Rules:
- Missing critical data lowers confidence.
- Borderline scores near threshold reduce confidence.
- High score with sparse data does not yield high confidence.

## 13. Recruiter Explanation Generation
Explanation output is deterministic template generation using factor evidence.

Required explanation components:
- One summary sentence with recommendation and top reasons.
- Strength bullets from highest positive weighted factors.
- Gap bullets from lowest factors or gating failures.
- Action suggestions (for example missing certification follow-up).

Constraints:
- No generative AI text for this story.
- No probabilistic phrasing outside confidence value.
- Reproducible wording for identical outputs and locale.

## 14. Future AI Integration
Future AI phases may augment but not replace deterministic core:
- Skill synonym expansion with model-assisted ontology updates.
- Enhanced title-to-role-family mapping suggestions.
- Natural-language explanation polish layer.
- Human-in-the-loop recommendation commentary.

Guardrails for future AI:
- Deterministic core score remains source of truth.
- AI outputs must be advisory unless explicitly approved by policy.
- Full traceability between deterministic score and AI augmentation.

## 15. Database Impact
This story is specification-only; no schema changes are introduced now.

Planned persistence impact for later implementation:
- Optional table for match results history.
- Optional table for scoring profiles and versions.
- Optional table for factor-level evidence snapshots.

Data retention and audit:
- Store profile version, rule version, and deterministic hash.
- Preserve immutable historical results for compliance and replay.

## 16. Service Responsibilities
Candidate Matching Engine service responsibilities:
- Validate cross-entity ownership boundaries.
- Resolve and load scoring profile.
- Normalize applicant/job data consistently.
- Execute deterministic factor scoring.
- Apply recommendation and confidence rules.
- Produce explainable MatchResult payload.

Out of scope for this story:
- Applicant scoring model training.
- AI summary generation.
- UI workflow redesign.
- External API dependencies.

## 17. Acceptance Criteria
- Engine behavior is fully deterministic for identical input/profile.
- Scores are transparent with factor-level evidence.
- Recommendation thresholds are profile-configurable.
- Confidence is produced with explicit deterministic logic.
- Recruiter explanation is template-based and reproducible.
- Multi-tenant profile resolution hierarchy is defined and enforceable.
- No external AI/API dependency required for baseline matching.
- Backward compatibility preserved with existing Version 2 modules.

## 18. Future Enhancements
- Profile simulation mode for what-if analysis before profile activation.
- Role-family scoring presets (for example warehouse, driving, supervisory).
- Localization for explanation templates.
- Calibrated threshold tuning toolkit using historical outcomes.
- Bias/fairness diagnostics for factor and threshold reviews.
- Event hooks for downstream automation (alerts, auto-shortlist queues).
- Hybrid deterministic + advisory AI insights with strict governance.
