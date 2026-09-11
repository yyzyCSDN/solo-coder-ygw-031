import tempfile
import unittest
from boardingbridge import BoardingBridgeService

class ExpandedTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.service=BoardingBridgeService(self.temp.name+"/data.db")
    def tearDown(self):
        self.service.close(); self.temp.cleanup()
    def test_create_search_and_persist(self):
        item=self.service.create("primary",priority=90,tags=["test"])
        self.assertEqual(self.service.get(item.id).name,"primary")
        self.assertEqual(len(self.service.search("PRIMARY")),1)
        self.assertTrue(self.service.operations.consistency()["ok"])
    def test_domain_control_and_safety(self):
        item=self.service.create("equipment",priority=80)
        reading=self.service.controller.ingest("signal",91,"unit")
        self.assertEqual(reading.quality,"good")
        self.assertEqual(self.service.controller.safety_check(91)["level"],"critical")
        result=self.service.controller.command(item.id,"start","tester")
        self.assertIn("result_state",result)
    def test_plan_simulation_and_exports(self):
        for i in range(4): self.service.create("job-"+str(i),priority=40+i)
        self.assertEqual(len(self.service.build_plan()["slots"]),4)
        self.assertEqual(self.service.simulate(3)["created"],3)
        self.assertIn("id,name,state",self.service.export("csv"))
if __name__=="__main__": unittest.main()

