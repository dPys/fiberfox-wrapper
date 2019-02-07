#!/usr/bin/env python
import os
import numpy as np
default_args = dict(
    acquisitiontype=0,
    coilsensitivityprofile=0,
    numberofcoils=1,
    reversephase="false",
    partialfourier=1,
    noisevariance=251,
    trep=4000,
    signalscale=100,
    tEcho=108,
    tline=1,
    tinhom=50,
    simulatekspace="true",
    axonradius=0,
    diffusiondirectionmode=0,
    fiberseparationthreshold=30,
    dosimulaterelaxation="true",
    dodisablepartialvolume="false",

    # artifacts
    spikesnum=0,
    spikesscale=1,
    kspacelineoffset=0.1,
    eddystrength=0,
    eddyTau=70,
    aliasingfactor=0,
    addringing="false",
    doaddmotion="false",
    randommotion="false",
    #motionvolumes=(6, 12, 24),
    addnoise="false",
    addghosts="false",
    addaliasing="false",
    addspikes="false",
    addeddycurrents="false",
    doadddistortions="false",

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
    def __init__(self, bvals, bvecs, output_dir, voxel_size = 2, b2q=False, **kwargs):
        self.__dict__.update(kwargs)
        self.bvals = bvals
        self.bvecs = bvecs
        self.output_dir = output_dir
        self.voxel_size = voxel_size
        self.b2q = b2q
        self.output_ffp = os.path.join(self.output_dir, "param.ffp")

    def ffp_string(self):
        ffp = """\
        <?xml version="1.0" encoding="utf-8"?>
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
    <acquisitiontype>0</acquisitiontype>
    <coilsensitivityprofile>0</coilsensitivityprofile>
    <numberofcoils>1</numberofcoils>
    <reversephase>false</reversephase>
    <partialfourier>1</partialfourier>
    <noisevariance>251</noisevariance>
    <trep>4000</trep>
    <signalScale>100</signalScale>
    <tEcho>{tEcho}</tEcho>
    <tLine>1</tLine>
    <tInhom>50</tInhom>
    <bvalue>{bvalue}</bvalue>
    <simulatekspace>true</simulatekspace>
    <axonRadius>0</axonRadius>
    <diffusiondirectionmode>0</diffusiondirectionmode>
    <fiberseparationthreshold>30</fiberseparationthreshold>
    <doSimulateRelaxation>true</doSimulateRelaxation>
    <doDisablePartialVolume>false</doDisablePartialVolume>
    <artifacts>
      <spikesnum>10</spikesnum>
      <spikesscale>1</spikesscale>
      <kspaceLineOffset>0.1</kspaceLineOffset>
      <eddyStrength>0</eddyStrength>
      <eddyTau>{eddyTau}</eddyTau>
      <aliasingfactor>1</aliasingfactor>
      <addringing>false</addringing>
      <addnoise>false</addnoise>
      <addghosts>false</addghosts>
      <addaliasing>false</addaliasing>
      <addspikes>false</addspikes>
      <addeddycurrents>false</addeddycurrents>
      <doAddDistortions>false</doAddDistortions>
    </artifacts>
    <outputvolumefractions>{outputvolumefractions}</outputvolumefractions>
    <showadvanced>true</showadvanced>
    <signalmodelstring>StickTensorBallBall</signalmodelstring>
    <artifactmodelstring>{artifactmodelstring}</artifactmodelstring>
    <outpath/>
{compartments}
  </image>
""".format(basic=self._format_image_basic(),
           gradients=self._format_image_gradients(),
           compartments=self._format_image_compartments(),
           artifactmodelstring=self.artifactmodelstring,
           outputvolumefractions=self.outputvolumefractions,
           eddyTau=self.eddyTau,
           bvalue=self.bvals.max(),
           tEcho=self.tEcho
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


    def run_simulation(self):
        self.write_ffp()

        cmd = "docker run " \
              "-v {output_dir}:/out " \
              "-v {ffp_file}:/ismrm/FilesForSimulation/param.ffp " \
              "pennbbl/fiberfox:latest " \
              "-i /ismrm/FilesForSimulation/Fibers.fib " \
              "-p /ismrm/FilesForSimulation/param.ffp " \
              "--verbose " \
              "-o /out ".format(output_dir=self.output_dir,
                                ffp_file=self.output_ffp)
        print(cmd)
        os.system(cmd)





def simulate(bvecs_file, bvals_file, output_dir, b2q=True, voxel_size=2, **kwargs):
    default_args.update(kwargs)
    simulator = FiberFoxSimulation(np.loadtxt(bvals_file),
                                   np.loadtxt(bvecs_file).T,
                                   output_dir,
                                   voxel_size=voxel_size,
                                   b2q=b2q,
                                   **default_args)
    simulator.run_simulation()
