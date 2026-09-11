import unittest
from boardingbridge.rules import DomainRules
class DomainRuleTests(unittest.TestCase):
    def test_axis(self): self.assertEqual(DomainRules.axis("extend"),"extend")
    def test_profile_version(self):
        with self.assertRaises(ValueError): DomainRules.profile_version(0)
