import unittest

from resume_utils import analyze_resume, extract_skills


class TestResumeUtils(unittest.TestCase):

    def test_extract_skills_case_insensitive(self):
        skills = extract_skills("Experienced PYTHON developer with SQL and Flask.")
        self.assertIn("python", skills)
        self.assertIn("sql", skills)
        self.assertIn("flask", skills)

    def test_match_score_is_bounded(self):
        result = analyze_resume(
            "Python developer with SQL and Flask experience.",
            "Looking for Python, SQL and Flask skills.",
            ["Python", "SQL", "Flask"],
        )
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)

    def test_missing_skill_is_reported(self):
        result = analyze_resume(
            "Python developer with SQL experience.",
            "Looking for Python, SQL and Flask skills.",
            ["Python", "SQL", "Flask"],
        )
        self.assertIn("flask", result["missing"])
        self.assertIn("python", result["matched"])

    def test_empty_resume_does_not_crash(self):
        result = analyze_resume(
            "",
            "Looking for Python developer with SQL skills.",
            ["Python", "SQL"],
        )
        self.assertEqual(result["text_score"], 0.0)
        self.assertEqual(result["skill_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
