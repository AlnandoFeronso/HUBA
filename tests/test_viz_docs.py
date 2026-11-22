"""Checks that tools/viz/README.md follows the docs template and matches the code."""
import os
import re
import unittest

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(SRC_ROOT, "tools", "viz", "README.md")
CLI = os.path.join(SRC_ROOT, "tools", "viz", "cli.py")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def headings_outside_code(text):
    """Return the heading lines that are not inside a fenced code block."""
    found, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("#"):
            found.append(line)
    return found


class ReadmeTests(unittest.TestCase):
    def setUp(self):
        self.text = read(README)
        self.lower = self.text.lower()

    def test_follows_the_docs_template(self):
        self.assertTrue(self.text.startswith('<p align="center"><strong>HUBA</strong>'))
        self.assertIn("Licensed under the Apache License 2.0", self.text.rstrip().splitlines()[-1])
        headings = headings_outside_code(self.text)
        self.assertEqual(len([h for h in headings if h.startswith("# ")]), 1)
        for section in ("## Purpose", "## Details", "## References"):
            self.assertIn(section, headings)
        for field in ("Status", "Date", "Author"):
            self.assertIn(f"| {field}", self.text)

    def test_states_the_input_contract(self):
        for needle in (".npy", "(frames, rows, cols)", "(frames, n)"):
            self.assertIn(needle, self.text)
        self.assertRegex(self.text, r"\+1/-1|-1/\+1")
        self.assertRegex(self.text, r"1/0|0/1")
        self.assertIn("frame 0", self.lower)

    def test_shows_how_the_emulator_side_writes_the_file(self):
        self.assertIn("np.save(", self.text)

    def test_documents_run_commands_and_keys(self):
        self.assertIn("python3 -m tools.viz", self.text)
        for needle in (".gif", ".mp4", "space"):
            self.assertIn(needle, self.lower)
        self.assertRegex(self.text, r"\bq\b")

    def test_lists_dependencies(self):
        for needle in ("numpy", "matplotlib", "pillow", "ffmpeg"):
            self.assertIn(needle, self.lower)

    def test_points_to_the_colour_constants(self):
        self.assertIn("frames.py", self.text)

    def test_every_option_in_the_readme_exists_in_the_cli(self):
        cli = read(CLI)
        for flag in set(re.findall(r"--[a-z][a-z-]*", self.text)):
            with self.subTest(flag=flag):
                self.assertIn(flag, cli)

    def test_every_cli_option_is_documented(self):
        for flag in re.findall(r'"(--[a-z][a-z-]*)"', read(CLI)):
            with self.subTest(flag=flag):
                self.assertIn(flag, self.text)


if __name__ == "__main__":
    unittest.main()
