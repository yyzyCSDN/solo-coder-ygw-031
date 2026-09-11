from __future__ import annotations
from typing import Any

class BridgeRuntime:
    """Bridge workflows retain docking, motion, equipment and maintenance decisions."""
    def __init__(self,service:Any)->None:self.service=service
    def docking_job(self,request_id:str,bridge:str,aircraft:str,profile_version:int)->dict:return self.service.baseline.create_job("docking",request_id,[bridge,aircraft],profile_version=profile_version,phase="approach")
    def latest_pose(self,readings:list[dict])->dict:return {r["name"]:r["value"] for r in readings if r.get("quality","good")!="bad"}
    def motion_allowed(self,axis:str,target:float,envelope:dict)->bool:
        low,high=envelope[axis];return float(low)<=float(target)<=float(high)
    def disconnect_job(self,request_id:str,assets:list[str])->dict:return self.service.baseline.create_job("equipment_disconnect",request_id,assets,order=list(assets),confirmed=[])
    def retract_job(self,request_id:str,bridge:str,emergency:bool=False)->dict:return self.service.baseline.create_job("emergency_retract",request_id,[bridge],phase="requested",emergency=bool(emergency),final_state=None)
    def level_job(self,request_id:str,bridge:str,profile_version:int)->dict:return self.service.baseline.create_job("auto_level",request_id,[bridge],profile_version=int(profile_version),phase="tracking")
    def recover_recorded_state(self,recorded:str)->str:return recorded
    def publish_aircraft_profile(self,version:int,profile:dict)->dict:return self.service.baseline.publish_config("aircraft_profile",version,profile,active=True)
    def contact_monitor(self,request_id:str,bridge:str,force_kn:float)->dict:
        verdict="over" if force_kn>3 else "ok";self.service.baseline.record_signal(bridge,"contact_pressure",force_kn,quality="warning" if verdict=="over" else "good",source="contact-sensor")
        return self.service.baseline.create_job("contact_monitor",request_id,[bridge],verdict=verdict,threshold_kn=3.0)
    def door_alignment(self,request_id:str,door:str,distance_cm:float)->dict:return self.service.baseline.create_job("door_alignment",request_id,[door],decision="aligned" if distance_cm<=5 else "searching",basis="distance-only")
    def brake_monitor(self,request_id:str,brake:str,commanded:bool,reported:bool)->dict:
        state="mismatch" if commanded!=reported else "applied" if commanded else "released";self.service.baseline.record_signal(brake,"braking_state",1 if reported else 0,quality="bad" if state=="mismatch" else "good",source="brake-feedback")
        return self.service.baseline.create_job("brake_monitor",request_id,[brake],state=state)
    def self_test_job(self,request_id:str,bridge:str,checks:list[dict])->dict:
        failed=[r["name"] for r in checks if not r.get("ok")];return self.service.baseline.create_job("bridge_self_test",request_id,[bridge],failed=failed,count=len(failed),grading="count-only")
    def slot_plan(self,request_id:str,bridges:list[str],flights:list[str])->dict:
        assignments={flight:bridges[i%len(bridges)] for i,flight in enumerate(flights)};return self.service.baseline.create_job("slot_plan",request_id,bridges,assignments=assignments,basis="arrival-order")
    def calibration_job(self,request_id:str,sensor:str,zero:float,reference:float)->dict:
        offset=round(float(reference)-float(zero),4);return self.service.baseline.create_job("calibration",request_id,[sensor],offset=offset,basis="one-point")
    def retract_plan(self,request_id:str,bridge:str)->dict:return self.service.baseline.create_job("retract_plan",request_id,[bridge],waypoints=["extend-back","lower-hold","home"],policy="fixed-path")
