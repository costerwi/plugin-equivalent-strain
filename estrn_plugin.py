"""Calculate Solidworks equivanent strain based on NE field output of odb in current display.

ESTRN field output results are stored in temporary scratch steps for contour plot.
"""

__VERSION__ = '1.0.1'

from abaqusGui import getAFXApp

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

toolset.registerKernelMenuButton(
        moduleName='estrn',
        functionName='vis_plugin()',
        buttonText='Solidworks Equivalent Strain',
        author='Carl Osterwisch',
        description=__doc__,
        version=__VERSION__,
        helpUrl='https://github.com/costerwi/plugin-equivalent-strain',
        applicableModules=['Visualization'],
    )
