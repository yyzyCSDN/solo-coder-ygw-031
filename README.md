# BoardingBridgeControl Python

这是一个可运行的机场登机桥控制服务，当前提供以下能力：

- 领域资产：bridge、aircraft、cabin_door、power_unit、air_conditioner、stair、motion_axis、sensor
- 测点历史：height、angle、distance、wind_speed、contact_pressure、wheel_chock、obstruction，包含质量、来源、校准版本和观测时间
- 可审计动作：extend、retract、align、level、stop_motion、connect_power、disconnect_power、maintenance_lock，相同幂等键不会重复登记
- 基础流程：docking、auto_level、dual_bridge、emergency_retract、equipment_disconnect，支持请求去重和状态推进
- 版本配置：aircraft_profile、motion_envelope、interlock_policy、maintenance_lock，保留历史版本和当前激活标记

当前版本侧重桥体资产、姿态测点、动作审计和基础靠接流程，高级协调与复杂故障恢复尚未覆盖。

```powershell
python -m boardingbridge --demo
python -m unittest discover -s tests -v
```
