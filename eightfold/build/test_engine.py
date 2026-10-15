# -*- coding: utf-8 -*-
"""
Unit checks the build guide asks for before the tiering node is wired (section 7), plus the
talent-leader gate and the why-now fallback. Run: python3 build/test_engine.py

Fixtures are synthetic ("Fixture Co") so a test never asserts anything about a real company's
CRM state.
"""
import json, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiering, leaders, why_now

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = {"vertical": "Healthcare", "employees": 40000, "open_reqs": 1200,
        "hcm": ["Workday"], "country": "United States", "as_of": "2026-10-15"}


class Tiering(unittest.TestCase):
    def test_matched_tier1(self):
        r = tiering.evaluate(FULL)
        self.assertEqual(r["fit_tier"], "Tier 1")
        self.assertEqual(r["fit_score"], 100)
        self.assertEqual(r["missing_required_fields"], "")

    def test_excluded(self):
        r = tiering.evaluate({**FULL, "disqualifier": "competitor"})
        self.assertEqual(r["fit_tier"], "Excluded")

    def test_missing_hcm_is_review_not_negative(self):
        r = tiering.evaluate({**FULL, "hcm": None})
        self.assertEqual(r["fit_tier"], "Review")
        self.assertEqual(r["check_hcm"], "unknown")          # not "no"
        self.assertEqual(r["missing_required_fields"], "hcm")
        self.assertEqual(r["fit_score"], 80)                # known fit
        self.assertEqual(r["fit_best_case"], 100)           # if HCM verifies

    def test_unsupported_hcm_is_a_real_no(self):
        r = tiering.evaluate({**FULL, "hcm": ["Homegrown ATS"]})
        self.assertEqual(r["check_hcm"], "no")
        self.assertEqual(r["fit_score"], 80)                # 100 - hcm(20)
        self.assertEqual(r["fit_tier"], "Tier 1")           # a known 'no' is scored, not sent to Review

    def test_two_known_misses_drop_to_tier3(self):
        r = tiering.evaluate({**FULL, "hcm": ["Homegrown ATS"], "open_reqs": 40})
        self.assertEqual((r["fit_score"], r["fit_tier"]), (55, "Tier 3"))

    def test_intent_and_engagement_never_enter_fit(self):
        a = tiering.evaluate(FULL)
        b = tiering.evaluate({**FULL, "intent_score": 99, "engagement_score": 99})
        self.assertEqual(a["fit_score"], b["fit_score"])
        self.assertEqual(b["intent_score"], 99)

    def test_rerun_is_reproducible(self):
        self.assertEqual(tiering.evaluate(FULL), tiering.evaluate(dict(FULL)))

    def test_shared_domain_parent_and_division_stay_separate(self):
        divs = json.load(open(os.path.join(BASE, "data", "divisions.json"), encoding="utf-8"))
        hca = [d for d in divs if d["entity_domain"] == "hcahealthcare.com" and d["include_in_cohort"] == "yes"]
        self.assertEqual({d["entity_name"] for d in hca},
                         {"HCA Healthcare", "HCA Healthcare Physician Services"})
        # Each is scored on its own facts; a small division does not inherit the parent's band.
        parent = tiering.evaluate({**FULL, "employees": 155698})
        division = tiering.evaluate({**FULL, "employees": 2733})
        self.assertEqual(parent["check_headcount"], "yes")
        self.assertEqual(division["check_headcount"], "no")

    def test_stale_pages_are_suppressed(self):
        divs = json.load(open(os.path.join(BASE, "data", "divisions.json"), encoding="utf-8"))
        bad = [d for d in divs if d["role"] in ("legacy-inactive", "stale stub", "wrong-company match",
                                               "non-employee network")]
        self.assertTrue(bad)
        self.assertTrue(all(d["include_in_cohort"] == "no" for d in bad))


def person(title, location="United States", start="2026-06"):
    return {"title": title, "location": location, "start": start}


class LeaderGate(unittest.TestCase):
    def q(self, *a, **k):
        return leaders.classify(person(*a, **k))

    def test_chro_qualifies(self):
        r = self.q("Executive Vice President, Chief Human Resources Officer")
        self.assertEqual((r["persona_group"], r["level"], r["qualified"]), ("economic_buyer", "exec", "yes"))

    def test_assistant_to_chro_does_not(self):
        r = self.q("Executive Assistant to the CHRO")
        self.assertEqual(r["qualified"], "no")
        self.assertEqual(r["level"], "support")

    def test_hrbp_to_chro_is_influencer(self):
        r = self.q("AVP, HR Business Partner to the CHRO & Programs Lead")
        self.assertEqual(r["persona_group"], "hr_business_partner")
        self.assertEqual(r["qualified"], "no")

    def test_cpo_analyst_does_not(self):
        self.assertEqual(self.q("CPO Group Analyst")["qualified"], "no")

    def test_marketing_match_is_off_persona(self):
        self.assertEqual(self.q("Associate Vice President, Business Solutions Marketing")["persona_group"], "off_persona")

    def test_non_us_head_of_ta_does_not(self):
        r = self.q("Head of Talent Acquisition", location="Hyderabad, Telangana, India")
        self.assertIn("outside POC geography", r["disqualify_reasons"])

    def test_enterprise_exec_abroad_is_kept(self):
        r = self.q("Chief Talent Officer", location="Greece")
        self.assertEqual(r["qualified"], "yes")
        self.assertEqual(r["us_based"], "no (enterprise exec kept)")

    def test_regional_exec_abroad_is_not(self):
        r = self.q("Senior Vice President - Head of Talent Acquisition Operations (International)", location="Singapore")
        self.assertEqual(r["qualified"], "no")

    def test_regional_title_does_not(self):
        self.assertIn("regional scope", self.q("Head of Talent Acquisition UK and Europe")["disqualify_reasons"])

    def test_talent_intelligence_qualifies(self):
        self.assertEqual(self.q("Head of Talent Intelligence", location="Tampa, Florida, United States")["qualified"], "yes")

    def test_banded_svp_manager_flagged(self):
        r = self.q("Senior Vice President - Senior Talent Acquisition Manager")
        self.assertEqual(r["title_banded"], "yes")

    def test_outside_window(self):
        self.assertIn("outside 18-month window", self.q("Chief People Officer", start="2024-11")["disqualify_reasons"])


class WhyNow(unittest.TestCase):
    def test_no_signal_wording(self):
        rows = json.load(open(os.path.join(BASE, "data", "why_now_public.json"), encoding="utf-8"))
        fit_led = [r for r in rows if r["motion"] == "fit-led"]
        self.assertTrue(fit_led)
        self.assertTrue(all(r["why_now"] == why_now.NO_SIGNAL for r in fit_led))
        self.assertTrue(all(r["create_task_now"] == "no" for r in fit_led))


if __name__ == "__main__":
    unittest.main(verbosity=1)
