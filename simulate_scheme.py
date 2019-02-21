#!/usr/bin/env python
import os
import numpy as np
default_args = dict(
    acquisitiontype=0,
    coilsensitivityprofile=0,
    numberofcoils=1,
    reversephase="false",
    partialfourier=1,
    trep=4000,
    signalScale=100,
    tEcho=108,
    tLine=1,
    tInhom=50,
    simulatekspace="true",
    axonRadius=0,
    diffusiondirectionmode=0,
    fiberseparationthreshold=30,
    doSimulateRelaxation="true",
    doDisablePartialVolume="false",

    # artifacts
    kspaceLineOffset=0.1,
    addringing="false",

    doAddMotion="false",
    randomMotion="false",
    motionvolumes=(6, 12, 24),
    translation0=2,
    translation1=0,
    translation2=0,
    rotation0=0,
    rotation1=0,
    rotation2=4,

    addnoise="false",
    noisetype="gaussian",
    noisevariance=251,
    addghosts="false",

    addaliasing="false",
    aliasingfactor=0,

    addspikes="false",
    spikesnum=0,
    spikesscale=1,

    addeddycurrents="false",
    eddyStrength=0,
    eddyTau=70,

    doAddDistortions="false",

    # image
    outputvolumefractions="false",
    showadvanced="true",
    signalmodelstring="StickTensorBallBall",
    artifactmodelstring="_COMPLEX-GAUSSIAN-251",

    compartments = [
        {"type": "fiber",
         "model": "stick",
         "d": 0.0012,
         "t2": 110,
         "t1": 0,
         "ID": 1
        },
        {"type": "fiber",
         "model": "tensor",
         "d1": 0.0012,
         "d2": 0.0003,
         "d3": 0.0003,
         "t2": 110,
         "t1": 0,
         "ID": 2
        },
        {"type": "non-fiber",
         "model": "ball",
         "d": 0.001,
         "t2": 80,
         "t1": 0,
         "ID": 3
        },
        {"type": "non-fiber",
         "model": "ball",
         "d": 0.002,
         "t2": 2500,
         "t1": 0,
         "ID": 4
        }
    ]

)

default_fov = np.array([90, 108, 90]) * 2

class FiberFoxSimulation(object):
    def __init__(self, bvals, bvecs, output_dir, voxel_size = 2, b2q=False, 
                 **kwargs):
        self.__dict__.update(kwargs)
        self.bvals = bvals
        self.bvecs = bvecs
        self.output_dir = output_dir
        self.voxel_size = voxel_size
        self.b2q = b2q
        self.output_ffp = os.path.join(self.output_dir, "param.ffp")
        self.motion_percent = self.motion_percent / 100
        # Randomly choose volumes 
        self.motionvolumes = np.arange(len(self.bvals), dtype=np.int)
            

    def ffp_string(self):
        ffp = """<?xml version="1.0" encoding="utf-8"?>
<fiberfox>
{fibers}
{image}
</fiberfox>
""".format(fibers=self._format_fibers(), image=self._format_image())
        return ffp

    def _format_fibers(self):

        return """\
  <fibers>
    <distribution>0</distribution>
    <variance>0.1</variance>
    <density>100</density>
    <spline>
      <sampling>1</sampling>
      <tension>0</tension>
      <continuity>0</continuity>
      <bias>0</bias>
    </spline>
    <rotation>
      <x>0</x>
      <y>0</y>
      <z>0</z>
    </rotation>
    <translation>
      <x>0</x>
      <y>0</y>
      <z>0</z>
    </translation>
    <scale>
      <x>1</x>
      <y>1</y>
      <z>1</z>
    </scale>
    <realtime>false</realtime>
    <showadvanced>true</showadvanced>
    <constantradius>false</constantradius>
    <includeFiducials>true</includeFiducials>
  </fibers>
  """

    def _format_image(self):
        image_str = """\
  <image>
{basic}
{gradients}
    <acquisitiontype>{acquisitiontype}</acquisitiontype>
    <coilsensitivityprofile>{coilsensitivityprofile}</coilsensitivityprofile>
    <numberofcoils>{numberofcoils}</numberofcoils>
    <reversephase>{reversephase}</reversephase>
    <partialfourier>{partialfourier}</partialfourier>
    <noisevariance>{noisevariance}</noisevariance>
    <trep>{trep}</trep>
    <signalScale>{signalScale}</signalScale>
    <tEcho>{tEcho}</tEcho>
    <tLine>{tLine}</tLine>
    <tInhom>{tInhom}</tInhom>
    <bvalue>{bvalue}</bvalue>
    <simulatekspace>{simulatekspace}</simulatekspace>
    <axonRadius>{axonRadius}</axonRadius>
    <diffusiondirectionmode>{diffusiondirectionmode}</diffusiondirectionmode>
    <fiberseparationthreshold>{fiberseparationthreshold}</fiberseparationthreshold>
    <doSimulateRelaxation>{doSimulateRelaxation}</doSimulateRelaxation>
    <doDisablePartialVolume>{doDisablePartialVolume}</doDisablePartialVolume>
    <artifacts>
      <spikesnum>0</spikesnum>
      <spikesscale>1</spikesscale>
      <kspaceLineOffset>{kspaceLineOffset}</kspaceLineOffset>
      <eddyStrength>{eddyStrength}</eddyStrength>
      <eddyTau>{eddyTau}</eddyTau>
      <aliasingfactor>{aliasingfactor}</aliasingfactor>
      <addringing>{addringing}</addringing>
      <doAddMotion>{doAddMotion}</doAddMotion>
      <randomMotion>{randomMotion}</randomMotion>
      <translation0>{translation0}</translation0>
      <translation1>{translation1}</translation1>
      <translation2>{translation2}</translation2>
      <rotation0>{rotation0}</rotation0>
      <rotation1>{rotation1}</rotation1>
      <rotation2>{rotation2}</rotation2>
      <motionvolumes>{motionvolumes}</motionvolumes>
      <addnoise>{addnoise}</addnoise>
      <addghosts>{addghosts}</addghosts>
      <addaliasing>{addaliasing}</addaliasing>
      <addspikes>{addspikes}</addspikes>
      <addeddycurrents>{addeddycurrents}</addeddycurrents>
      <doAddDistortions>{doAddDistortions}</doAddDistortions>
      <noisevariance>{noisevariance}</noisevariance>
      <noisetype>{noisetype}</noisetype>
    </artifacts>
    <outputvolumefractions>{outputvolumefractions}</outputvolumefractions>
    <showadvanced>true</showadvanced>
    <signalmodelstring>StickTensorBallBall</signalmodelstring>
    <artifactmodelstring>{artifactmodelstring}</artifactmodelstring>
    <outpath>/out/</outpath>
{compartments}
  </image>
""".format(basic=self._format_image_basic(),
           gradients=self._format_image_gradients(),
           compartments=self._format_image_compartments(),
           artifactmodelstring=self.artifactmodelstring,
           outputvolumefractions=self.outputvolumefractions,
           eddyTau=self.eddyTau,
           bvalue=self.bvals.max(),
           tEcho=self.tEcho,
           addghosts=self.addghosts,
           addaliasing=self.addaliasing,
           addspikes=self.addspikes,
           noisetype=self.noisetype,
           noiasevariance=self.noisevariance,
           addeddycurrents=self.addeddycurrents,
           motionvolumes=" ".join(map(str, self.motionvolumes)),
           doAddDistortions=self.doAddDistortions,
           addnoise=self.addnoise,
           doAddMotion=self.doAddMotion,
           randomMotion=self.randomMotion,
           rotation0=self.rotation0,
           rotation1=self.rotation1,
           rotation2=self.rotation2,
           translation0=self.translation0,
           translation1=self.translation1,
           translation2=self.translation2,
           addringing=self.addringing,
           aliasingfactor=self.aliasingfactor,
           eddyStrength=self.eddyStrength,
           acquisitiontype=self.acquisitiontype,
           coilsensitivityprofile=self.coilsensitivityprofile,
           numberofcoils=self.numberofcoils,
           reversephase=self.reversephase,
           partialfourier=self.partialfourier,
           noisevariance=self.noisevariance,
           trep=self.trep,
           signalScale=self.signalScale,
           tLine=self.tLine,
           tInhom=self.tInhom,
           simulatekspace=self.simulatekspace,
           axonRadius=self.axonRadius,
           diffusiondirectionmode=self.diffusiondirectionmode,
           fiberseparationthreshold=self.fiberseparationthreshold,
           doSimulateRelaxation=self.doSimulateRelaxation,
           doDisablePartialVolume=self.doDisablePartialVolume,
           kspaceLineOffset=self.kspaceLineOffset
           )
        return image_str

    def _format_image_basic(self):
        xvoxels, yvoxels, zvoxels = (default_fov / self.voxel_size).astype(np.int)
        basic_str = """\
    <basic>
      <size>
        <x>{xvoxels}</x>
        <y>{yvoxels}</y>
        <z>{zvoxels}</z>
      </size>
      <spacing>
        <x>{voxel_size}</x>
        <y>{voxel_size}</y>
        <z>{voxel_size}</z>
      </spacing>
      <origin>
        <x>0</x>
        <y>0</y>
        <z>0</z>
      </origin>
      <direction>
        <1>1</1>
        <2>0</2>
        <3>0</3>
        <4>0</4>
        <5>1</5>
        <6>0</6>
        <7>0</7>
        <8>0</8>
        <9>1</9>
      </direction>
      <numgradients>{numgradients}</numgradients>
    </basic>""".format(numgradients=max(self.bvecs.shape),
                       voxel_size=self.voxel_size,
                       xvoxels=xvoxels,
                       yvoxels=yvoxels,
                       zvoxels=zvoxels)
        return basic_str

    def _format_image_gradients(self):
        dir_str = """
      <{dirnum}>
        <x>{x}</x>
        <y>{y}</y>
        <z>{z}</z>
      </{dirnum}>\n"""

        # adjust bvals
        bvals = np.sqrt(self.bvals) if self.b2q else self.bvals
        bvals = bvals/bvals.max()
        scaled_vectors = bvals[:, None] * self.bvecs

        direction_elements = []
        for dirnum, scaled_vector in enumerate(scaled_vectors):
          x, y, z = scaled_vector
          direction_elements.append(dir_str.format(x=x, y=y, z=z, dirnum=dirnum))

        gradient_str = """\
    <gradients>
{dirs}
    </gradients>
""".format(dirs="".join(direction_elements))
        return gradient_str

    def _format_image_compartments(self):
        return """    <compartments>
      <0>
        <type>fiber</type>
        <model>stick</model>
        <d>0.0012</d>
        <t2>110</t2>
        <t1>0</t1>
        <ID>1</ID>
      </0>
      <1>
        <type>fiber</type>
        <model>tensor</model>
        <d1>0.0012</d1>
        <d2>0.0003</d2>
        <d3>0.0003</d3>
        <t2>110</t2>
        <t1>0</t1>
        <ID>2</ID>
      </1>
      <2>
        <type>non-fiber</type>
        <model>ball</model>
        <d>0.001</d>
        <t2>80</t2>
        <t1>0</t1>
        <ID>3</ID>
      </2>
      <3>
        <type>non-fiber</type>
        <model>ball</model>
        <d>0.002</d>
        <t2>2500</t2>
        <t1>0</t1>
        <ID>4</ID>
      </3>
    </compartments>"""

    def write_ffp(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        with open(self.output_ffp, "w") as f:
            f.write(self.ffp_string())

    def run_simulation(self, singularity_image=""):
        self.write_ffp()

        if not singularity_image:
            cmd = "docker run " \
                  "-v {output_dir}:/out " \
                  "pennbbl/fiberfox:latest " \
                  "-i /ismrm/FilesForSimulation/Fibers.fib " \
                  "-p /out/param.ffp " \
                  "--verbose " \
                  "-o /out ".format(output_dir=self.output_dir,
                                    ffp_file=self.output_ffp)
        else:
            cmd = "singularity run " \
                  "-B {output_dir}:/out " \
                  "{image} " \
                  "-i /ismrm/FilesForSimulation/Fibers.fib " \
                  "-p /out/param.ffp " \
                  "--verbose " \
                  "-o /out ".format(image=singularity_image,
                                    output_dir=self.output_dir,
                                    ffp_file=self.output_ffp)
        print(cmd)
        os.system(cmd)


def simulate(bvecs_file, bvals_file, output_dir, singularity_image="", b2q=True,
             voxel_size=2, **kwargs):
    default_args.update(kwargs)
    simulator = FiberFoxSimulation(np.loadtxt(bvals_file),
                                   np.loadtxt(bvecs_file).T,
                                   output_dir,
                                   voxel_size=voxel_size,
                                   b2q=b2q,
                                   **default_args)
    simulator.run_simulation(singularity_image=singularity_image)
