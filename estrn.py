"""Calculate equivalent strain for each frame NE field output

Carl Osterwisch, November 2021
"""

from __future__ import print_function

def estrn(NE):
    """Calculate Solidworks equivanent strain based on NE

    NE is nominal or engineering strain output from Abaqus
    
    Formulas documented in:
    https://help.solidworks.com/2017/english/solidworks/cworks/c_Strain_Components_2.htm
    """

    from abaqus import power

    EPSX = NE.getScalarField(componentLabel='NE11')
    EPSY = NE.getScalarField(componentLabel='NE22')
    if 'NE33' in NE.componentLabels: # check for full 3D results
        EPSZ = NE.getScalarField(componentLabel='NE33')
    else:
        EPSZ = 0*EPSX

    GMXY = NE.getScalarField(componentLabel='NE12')
    if 'NE13' in NE.componentLabels: # check for full 3D results
        GMXZ = NE.getScalarField(componentLabel='NE13')
        GMYZ = NE.getScalarField(componentLabel='NE23')
    else:
        GMXZ = 0*GMXY
        GMYZ = GMXZ

    Estar = (EPSX + EPSY + EPSZ)/3
    E1 = 0.5*(
            power(EPSX - Estar, 2) +
            power(EPSY - Estar, 2) +
            power(EPSZ - Estar, 2)
            )
    E2 = (power(GMXY, 2) + power(GMXZ, 2) + power(GMYZ, 2))/4

    return 2*power((E1 + E2)/3, 0.5)


def vis_plugin():
    """ Store ESTRN for each step and frame in current odb """

    from abaqus import session, milestone

    vp = session.viewports[session.currentViewportName] # current viewport
    odbDisplay = vp.odbDisplay
    odb = session.odbs[odbDisplay.name] # odb in current viewport
    sodb = session.ScratchOdb(odb) # temporary scratch odb

    for n, step in enumerate(odb.steps.values()): # loop over all steps
        sname = 'Scratch ' + step.name
        if sname in sodb.steps:
            sstep = sodb.steps[sname]
        else:
            sstep = sodb.Step( # make a scratch step
                    name = sname,
                    description = step.description,
                    domain = step.domain,
                    timePeriod = step.timePeriod,
                    )

        for frame in step.frames: # loop over all frames
            if not 'NE' in frame.fieldOutputs:
                print('Step "{}" is missing "NE" field output'.format(step.name))
                break
            if frame.frameId < len(sstep.frames):
                sframe = sstep.frames[frame.frameId]
            else:
                sframe = sstep.Frame( # make a scratch frame
                        incrementNumber = frame.incrementNumber,
                        frameValue = frame.frameValue,
                        description = frame.description,
                        )
            if 'U' in frame.fieldOutputs and not 'U' in sframe.fieldOutputs:
                # copy displacement for convenience
                sframe.FieldOutput(frame.fieldOutputs['U'])
            if not 'ESTRN' in sframe.fieldOutputs:
                sframe.FieldOutput(
                        name = 'ESTRN',
                        description = 'Solidworks equivalent strain',
                        field = estrn(frame.fieldOutputs['NE']),
                        )
        milestone(
                message = 'Calculating equivalent strain',
                object = 'steps',
                done = n + 1,
                total = len(odb.steps),
                )


if '__main__' == __name__:
    vis_plugin()
