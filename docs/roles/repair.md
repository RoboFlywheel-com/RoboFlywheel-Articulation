# Repair Agent

Input: failed checks, sampled configuration, affected parts/joints, measurements
and localized functions from the Revision Module. Decide whether the error lies
in the blueprint's construction rule or its code implementation. Route rule errors
to the Architect and rebuild the generator; change only code for implementation
errors. Preserve failed configurations and rerun them together with passing cases.
Use the same state directory across repairs. Do not remove domain choices, weaken
tests or change overlap allowances simply to hide a failing configuration.

Output: corrected blueprint/generator and strict release reports with no failures
and passing coverage of every declared choice.
