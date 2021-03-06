# YODA to YAML conversion script for BELLE_2017_I1512299.
# G. Watt (27 FEB 2017), using YODA file provided by H. Schulz.

import yoda
import yaml

# define some metadata
variables = ["w", r"\cos\theta_\nu", r"\cos\theta_\ell", r"\chi"]
comment = r"Unfolded differential decay rates of four kinematic variables fully describing the $\bar B^0 \to D^{*\,+} \, \ell^- \, \bar \nu_\ell$ decay in the $B$-meson rest frame are presented.  Numbers taken from a YODA file provided by Holger Schulz, in turn prepared from a ROOT file provided by Florian Bernlochner (Belle)."
keywords = []
keywords.append({"name": "reactions", "values": ["BBAR0 --> D*(2010)+ LEPTON- NUBAR"]})
keywords.append({"name": "observables", "values": ["WIDTH"]})
keywords.append({"name": "phrases", "values": ["Decay", "Charm Production"]})
reaction = r"$\bar{B}^0\to D^{*+}\ell^-\bar{\nu}_\ell$"

# metadata for whole submission
submission = [{"comment": comment}]

# read YODA file as a list of objects
objects = yoda.read("BELLE_2017_I1512299.yoda", asdict=False)

# loop over YODA objects, writing one YAML data table for each one
for iobj, object in enumerate(objects):

    # define variable names depending on dimension of YODA object
    if object.dim < 3:
        ind_name = r"${}$".format(variables[iobj])
        dep_name = r"$\Delta\Gamma/\Delta {}$".format(variables[iobj])
        dep_units = r"$10^{-15}$ GeV"
        dep_scale = 1e-15 # scale rates to match numbers in Table 3 of paper
        description = r"The unfolded differential rate as a function of ${}$.".format(variables[iobj])
    else:
        ind_name = "Bin"
        dep_name = "Correlation"
        dep_units = ""
        dep_scale = 1
        description = r"The correlation matrix of the unfolded differential rates.  The full error covariance can be obtained by combining the quoted error in the other tables with these values.  The ordering of the correlations is {$w$, $\cos\theta_\nu$, $\cos\theta_\ell$, $\chi$}, where each variable has 10 bins."

    # metadata for individual table
    submission.append({"name": "Table {}".format(iobj+1), "description": description, "keywords": keywords, "data_file": "{}.yaml".format(object.name)})

    # define independent and dependent variables depending on dimension of YODA object
    independent_variables = []
    dependent_variables = []
    for i in range(1, object.dim):
        independent_variables.append({"header": {"name": ind_name}, "values": []})
    dependent_variables.append({"header": {"name": dep_name, "units": dep_units}, "qualifiers": [{"name": "RE", "value": reaction}], "values": []})

    # loop over data points and add to independent and dependent variables
    for p in object.points:

        # independent variables
        for i in range(1, object.dim):
            low = "{}".format(p.val(i) - p.errMinus(i))
            high = "{}".format(p.val(i) + p.errMinus(i))
            if object.dim == 3: # for correlation matrix, number bins from 1 with no bin width
                independent_variables[i-1]["values"].append({"value": int(p.val(i) + 1)})
            elif not p.errPlus(i) and not p.errMinus(i): # no bin width
                independent_variables[i-1]["values"].append({"value": float(p.val(i))})
            elif p.errPlus(i) == p.errMinus(i): # focus is midpoint of bin
                independent_variables[i-1]["values"].append({"low": float(low), "high": float(high)})
            else: # focus is not midpoint of bin
                independent_variables[i-1]["values"].append({"value": float(p.val(i)), "low": float(low), "high": float(high)})

        # dependent variables
        value = '{}'.format(p.val(object.dim)/dep_scale)
        plus = '{}'.format(p.errPlus(object.dim)/dep_scale)
        minus = '{}'.format(-p.errMinus(object.dim)/dep_scale)
        if not p.errPlus(object.dim) and not p.errMinus(object.dim): # no errors
            dependent_variables[0]["values"].append({"value": float(value)})
        elif p.errPlus(object.dim) == p.errMinus(object.dim): # one symmetric error (no label)
            dependent_variables[0]["values"].append({"value": float(value), "errors": [{"symerror": float(plus)}]})
        else: # one asymmetric error (no label)
            dependent_variables[0]["values"].append({"value": float(value), "errors": [{"asymerror": {"plus": float(plus), "minus": float(minus)}}]})

    # dump YAML documents for data tables
    print "Path={}".format(object.path)
    data_document = {"independent_variables": independent_variables, "dependent_variables": dependent_variables}
    data_stream = file("{}.yaml".format(object.name), "w")
    yaml.dump(data_document, data_stream)
    print "Written {} object to {}.yaml\n".format(object.type, object.name)

# dump YAML documents for metadata
submission_stream = file("submission.yaml", "w")
yaml.dump_all(submission, submission_stream)
print "Written metadata to submission.yaml"
