from platform import release
import caps2tacs
from pyoptsparse import SLSQP, Optimization
import sys

# all the capsManager package modules/classes are also available 
# in caps2tacs since caps2tacs package imports the whole capsManager package

# pyoptsparse documentation: https://mdolab-pyoptsparse.readthedocs-hosted.com/en/latest/

problem = caps2tacs.CapsStruct.default(csmFile="generic_missile.csm")
tacs_aim = problem.tacsAim
egads_aim = problem.egadsAim

aluminum = caps2tacs.Isotropic.aluminum()
tacs_aim.add_material(material=aluminum)

constraint = caps2tacs.ZeroConstraint(name="bottom", caps_constraint="root")
tacs_aim.add_constraint(constraint=constraint)

for group in ["MissileOML"]:
    thick_DV = caps2tacs.ThicknessVariable(name=group, caps_group=group, value=0.1, material=aluminum)
    tacs_aim.add_variable(variable=thick_DV)

load = caps2tacs.GridForce(name="load1", caps_load="fuselage", direction=[0,0,-1.0], magnitude=1.0E2)    
tacs_aim.add_load(load=load)

tacs_aim.setup_aim()
egads_aim.set_mesh(edge_pt_min=30, edge_pt_max=40, global_mesh_size=0.01)

#print([dv.name for dv in tacs_aim.shape_design_variables])

# make a pytacs function
pytacs_function = caps2tacs.MassStress()

# start a caps tacs main problem
caps_tacs = caps2tacs.CapsTacs(name="optimal_missile", tacs_aim=tacs_aim, egads_aim=egads_aim, pytacs_function=pytacs_function, view_plots=True)

def initial_stress(relative:bool=True):
    if relative:
        return caps_tacs.function(function_name="ks_vmfailure")
    else:
        return 1.0

names = ["mass", "stress"]

def objfunc(xdict):
    funcs = {}
    fail = False
    try:
        funcs["mass"] = caps_tacs.function("mass", xdict)
        funcs["stress"] = caps_tacs.function("ks_vmfailure", xdict)
    except:
        fail = True
        for name in names:
            funcs[name] = None

    print(funcs)
    #sys.exit()

    return funcs, fail

def objsens(xdict, funcs):
    grads = {}
    fail = False
    try:
        grads["mass"] = caps_tacs.gradient("mass", xdict)
        grads["stress"] = caps_tacs.gradient("ks_vmfailure", xdict)
    except:
        for name in names:
            grads[name] = None
        fail = True

    print(grads)

    return grads, fail

opt_problem = Optimization(name="purdue_p_structure", objFun=objfunc)
opt_problem.addObj(name="mass", scale=0.001)
opt_problem.addCon(name="stress", upper=initial_stress(relative=False), scale=1.0)

for thickDV in tacs_aim.thickness_design_variables:
    value = thickDV.value
    opt_problem.addVar(name=thickDV.name, lower=0.0001, upper=0.50, value=value, scale=100.0)

for shape_var in tacs_aim.shape_design_variables:
    value = shape_var.value
    opt_problem.addVar(name=shape_var.name, value=value, lower=0.5*value, upper=2.0*value, scale=100.0)

slsqp_method = SLSQP(options={
    "IPRINT" : -1,
    "MAXIT" : 10
})

solution = slsqp_method(opt_problem, sens=objsens)

# rst begin check
# Check Solution
print(solution)



