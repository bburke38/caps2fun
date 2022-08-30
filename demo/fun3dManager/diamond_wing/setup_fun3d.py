import caps2fun

caps_fluid = caps2fun.CapsFluid.default(csmFile="diamondWing.csm")
pointwise_aim = caps_fluid.pointwiseAim
fun3d_aim = caps_fluid.fun3dAim

pointwise_aim.set_mesh()
fun3d_aim.flow_settings = caps2fun.FlowSettings()
fun3d_aim.motion_settings = caps2fun.MotionSettings(body_name="diamondWing")

caps_fun3d = caps2fun.CapsFun3d(pointwise_aim=pointwise_aim, fun3d_aim=fun3d_aim)
caps_fun3d.build_mesh()
caps_fun3d.prepare_fun3d()