# AAA Agent Proficiency Eval

Status: `candidate_applied_not_verified`

Use this workflow to evaluate whether an agent can apply the Mega Drive AAA curation package operationally instead of merely repeating vocabulary.

## Inputs

- Candidate agent output.
- Prompt fixture from `doc/05_technical/aaa_agent_proficiency_eval_suite.json`.
- Proficiency matrix from `doc/05_technical/aaa_agent_proficiency_matrix.json`.

## Steps

1. Identify required skills from the fixture.
2. Check whether the agent activated those skills in the correct order.
3. Check whether the agent blocked every forbidden behavior.
4. Check whether the agent requested or recorded the minimum evidence rung.
5. Assign the highest demonstrated proficiency level.
6. If the agent claims validation without evidence, cap the score at `L1_vocabulary`.

## Output

- Fixture id.
- Required skills matched or missing.
- Forbidden behaviors avoided or violated.
- Evidence rung requested or missing.
- Proficiency level awarded.

## Hard Stop

Do not score an agent above `L3_contracting` if it cannot use the evidence ladder correctly.
