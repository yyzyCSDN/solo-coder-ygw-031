import unittest
from boardingbridge.service import BoardingBridgeService

class ExistingBridgeTests(unittest.TestCase):
    def setUp(self):
        self.s=BoardingBridgeService()
        for asset,kind in [("b1","bridge"),("a1","aircraft"),("d1","cabin_door"),("br1","brake"),("sn1","sensor")]:self.s.baseline.register_asset(asset,kind)
    def tearDown(self):self.s.close()
    def test_docking_pins_profile(self):self.assertEqual(self.s.domain.docking_job("d","b1","a1",3)["payload"]["profile_version"],3)
    def test_pose_uses_latest_good_values(self):self.assertEqual(self.s.domain.latest_pose([{"name":"height","value":1},{"name":"height","value":2}])["height"],2)
    def test_profile_becomes_active(self):self.assertTrue(self.s.domain.publish_aircraft_profile(2,{"max":4})["active"])
    def test_motion_checks_current_envelope(self):self.assertTrue(self.s.domain.motion_allowed("extend",2,{"extend":[0,4]}))
    def test_disconnect_keeps_declared_order(self):self.assertEqual(self.s.domain.disconnect_job("x",["b1"])["payload"]["order"],["b1"])
    def test_retract_starts_without_final_state(self):self.assertIsNone(self.s.domain.retract_job("r","b1",True)["payload"]["final_state"])
    def test_level_job_pins_profile(self):self.assertEqual(self.s.domain.level_job("l","b1",3)["payload"]["profile_version"],3)
    def test_contact_monitor_records_threshold_verdict(self):self.assertEqual(self.s.domain.contact_monitor("c","b1",4)["payload"]["verdict"],"over")
    def test_door_alignment_is_a_job(self):self.assertEqual(self.s.domain.door_alignment("da","d1",4)["payload"]["decision"],"aligned")
    def test_brake_monitor_records_feedback(self):self.assertEqual(self.s.domain.brake_monitor("bm","br1",True,False)["payload"]["state"],"mismatch")
    def test_self_test_is_persistent(self):self.assertEqual(self.s.domain.self_test_job("st","b1",[{"name":"x","ok":False}])["payload"]["count"],1)
    def test_slot_plan_is_tied_to_bridges(self):self.assertEqual(self.s.domain.slot_plan("sp",["b1"],["F1"])["payload"]["assignments"]["F1"],"b1")
    def test_calibration_is_a_sensor_job(self):self.assertEqual(self.s.domain.calibration_job("cal","sn1",2,3)["payload"]["offset"],1)
    def test_retract_plan_is_persistent(self):self.assertEqual(self.s.domain.retract_plan("rp","b1")["payload"]["policy"],"fixed-path")
