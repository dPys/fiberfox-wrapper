import os
import numpy as np
import tempfile
import shutil
import glob
import itertools
#import time
import json
import asyncio
import subprocess
from joblib import Parallel, delayed
from pathlib import Path
from nipype.utils.filemanip import copyfile, fname_presuffix

default_args = dict(
    acquisitiontype=0,
    coilsensitivityprofile=0,
    numberofcoils=1,
    partialfourier=1,
    trep=4000,
    signalScale=100,
    tEcho=108,
    tLine=1,
    tInhom=50,
    tinv=0, #new
    echoTrainLength=8, #new
    simulatekspace="true",
    axonRadius=0,
    diffusiondirectionmode=0,
    fiberseparationthreshold=30,
    doSimulateRelaxation="true",
    doDisablePartialVolume="false",

    # artifacts
    kspaceLineOffset=0.1,
    addringing="false",
    drift=0.06, #new
    zeroringing=0, #new
    doAddDrift=0, #new

    addnoise="false",
    noisetype="gaussian",
    noisevariance=0, # 0 or 251

    addghosts="false",

    addaliasing="false",
    aliasingfactor=0,

    addspikes="false",
    spikesnum=0,
    spikesscale=1,

    eddyTau=70,

    doAddDistortions="false",

    # image
    outputvolumefractions="false",
    showadvanced="true",
    signalmodelstring="StickTensorBallBall",

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

class FiberFoxSimulation(object):
    def __init__(self, bvals, bvecs, dirpath, voxel_size, doAddMotion, randomMotion, motion_volumes, addeddycurrents, reversephase, default_fov, motion_bounds, eddyStrength, artifactmodelstring, b2q, **kwargs):
        self.__dict__.update(kwargs)
        self.bvals = bvals
        self.bvecs = bvecs
        self.dirpath = dirpath
        self.voxel_size = voxel_size
        self.doAddMotion = doAddMotion
        self.randomMotion = randomMotion
        self.motionvolumes = motion_volumes
        self.addeddycurrents = addeddycurrents
        self.reversephase = reversephase
        self.default_fov = default_fov
        self.eddyStrength = eddyStrength
        self.b2q = b2q
        self.artifactmodelstring = artifactmodelstring
        self.output_ffp = os.path.join(self.dirpath, "param.ffp")
        self.rotation0, self.rotation1, self.rotation2, self.translation0, self.translation1, self.translation2 = motion_bounds

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
    <tinv>{tinv}</tinv>
    <echoTrainLength>{echoTrainLength}</echoTrainLength>
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
      <drift>{drift}</drift>
      <zeroringing>{zeroringing}</zeroringing>
      <doAddDrift>{doAddDrift}</doAddDrift>
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
           tinv=self.tinv,
           echoTrainLength=self.echoTrainLength,
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
           drift=self.drift, #new
           zeroringing=self.zeroringing, #new
           doAddDrift=self.doAddDrift, #new
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
        xvoxels, yvoxels, zvoxels = (self.default_fov / self.voxel_size).astype(np.int32)
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
        with open(self.output_ffp, "w+") as f:
            f.write(self.ffp_string())
        f.close()

        if os.path.isfile(self.output_ffp) is False:
            raise FileNotFoundError(f"\n\nFailed to find {self.output_ffp}...")
            return 1
        else:
            #print(f"Parameters file: {self.output_ffp}\n\n{self.ffp_string()}")
            print(f"Parameters file: {self.output_ffp}")
            #time.sleep(2)


    def run_simulation(self, run_method, fiber_tmp):
        self.write_ffp()

        if run_method == "Docker":
            cmd = ["bash", f"docker run",
                  f"-v",
                  f"{self.dirpath}:/out",
                  f"pennbbl/fiberfox:latest",
                  f"-i",
                  f"/ismrm/FilesForSimulation/Fibers.fib",
                  f"-p",
                  f"/out/param.ffp",
                  f"--verbose",
                  f"-o",
                  f"/outs"]
        elif run_method.endswith(".simg"):
            cmd = ["bash", f"singularity run",
                  f"-B",
                  f"{self.dirpath}:/out",
                  f"{run_method}",
                  f"-i",
                  f"/ismrm/FilesForSimulation/Fibers.fib",
                  f"-p",
                  f"/out/param.ffp",
                  f"--verbose",
                  f"-o",
                  f"/out"]
        else:
            cmd = ["bash", run_method,
                  f"-i",
                  fiber_tmp,
                  f"-p",
                  f"{self.output_ffp}",
                  f"--verbose",
                  f"-o",
                  f"{self.dirpath}"]

        #print(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        if (p_status == 0):
            return output
        else:
            raise subprocess.ProcessException(cmd, p_status, err)
        # p = subprocess.Popen(cmd)
        # p.terminate()


def simulate(bvecs_file, bvals_file, output_dir, run_method, sim_templates_dir,
             voxel_size, head_motion, random_motion, eddy, reverse_phase,
             motion_level, motion_percent_vols, eddy_level, b2q=True, **kwargs):
    default_args.update(kwargs)

    try:
        bvals_arr = np.loadtxt(bvals_file)
    except:
        return print(f"{bvals_file} not found!")

    num_vols = len(np.arange(len(bvals_arr), dtype=np.int32))
    num_noise_vols = np.ceil(motion_percent_vols*num_vols).astype('int32')

    combo=""

    detailed_data = {}

    if head_motion is True:
        doAddMotion = "true"
        motion_volumes = tuple(np.random.randint(0, num_vols, (1, num_noise_vols)).tolist()[0])

        detailed_data['motion_vols'] = motion_volumes

        if random_motion is True:
            randomMotion = "true"
            combo = combo + '_HM_TYPE-random'
        else:
            randomMotion = "false"
            combo = combo + '_HM_TYPE-linear'

        combo = combo + '-LEVEL-' + motion_level
        combo = combo + f"-EXTENT-{np.round(100*motion_percent_vols, 2)}%"

        if motion_level == "severe":
            rotation0 = 8
            rotation1 = 8
            rotation2 = 8
            translation0 = 8
            translation1 = 8
            translation2 = 8
        elif motion_level == "moderate":
            rotation0 = 5
            rotation1 = 5
            rotation2 = 5
            translation0 = 5
            translation1 = 5
            translation2 = 5
        elif motion_level == "mild":
            rotation0 = 2
            rotation1 = 2
            rotation2 = 2
            translation0 = 2
            translation1 = 2
            translation2 = 2
    else:
        motion_volumes = (0)
        doAddMotion = "false"
        randomMotion = "false"
        rotation0 = 0
        rotation1 = 0
        rotation2 = 0
        translation0 = 0
        translation1 = 0
        translation2 = 0

    motion_bounds = [rotation0, rotation1, rotation2, translation0, translation1, translation2]

    if eddy is True:
        addeddycurrents="true"
        combo = combo + '_EDDY'
        if eddy_level=="severe": # Uncompensated eddy-current gradient amplitudes are typically < 1% of the pulsed-gradient amplitude, whose maximum ranges from 40 − 80 mT/m. If we measure this in mT/m at the beginning of the k-space readout, and assume that a spatially linear eddy current profile in the direction of the respective diffusion-weighting gradient is used, then this value should be <0.1
            eddyStrength = 0.01
        elif eddy_level=="moderate":
            eddyStrength = 0.005
        else:
            eddyStrength = 0.001
        combo = combo + '-LEVEL-' + eddy_level
    else:
        eddyStrength = 0
        addeddycurrents = "false"

    if reverse_phase is True:
        reversephase="true"
        combo = combo + '_REVPHASE'
    else:
        reversephase="false"

    default_fov = np.array([90, 108, 90]) * voxel_size

    dirpath = tempfile.mkdtemp()
    req_fils = glob.glob(f"{sim_templates_dir}/*")

    fiber_tmp = f"/var/tmp/Fibers_{os.path.basename(dirpath)}.fib"

    print("Copying template files...")
    for f_ in req_fils:
        if 'Fibers.fib' in f_:
            copyfile(
            f_,
            fiber_tmp,
            copy=True,
            use_hardlink=False)
        else:
            f_tmp_path = fname_presuffix(
                f_, suffix="_tmp", newpath=dirpath
            )
            copyfile(
            f_,
            f_tmp_path,
            copy=True,
            use_hardlink=False)

    #print(glob.glob(f"{dirpath}/*"))
    #return

    seq_name = os.path.basename(bvecs_file).split('.')[0]
    #artifactmodelstring = f"fbfx_SEQ-{seq_name}_VOX-{voxel_size}mm_FOV-{default_fov[0]}x{default_fov[1]}x{default_fov[2]}{combo}"
    artifactmodelstring = f"fbfx_SEQ-{seq_name}{combo}"
    out_basename = f"{output_dir}/{artifactmodelstring}"

    try:
        simulator = FiberFoxSimulation(bvals_arr,
                                       np.loadtxt(bvecs_file).T,
                                       dirpath,
                                       voxel_size=voxel_size,
                                       doAddMotion=doAddMotion,
                                       randomMotion=randomMotion,
                                       motion_volumes=motion_volumes,
                                       addeddycurrents=addeddycurrents,
                                       reversephase=reversephase,
                                       default_fov=default_fov,
                                       motion_bounds=motion_bounds,
                                       eddyStrength=eddyStrength,
                                       artifactmodelstring=artifactmodelstring,
                                       b2q=b2q,
                                       **default_args)
        simulator.run_simulation(run_method=run_method, fiber_tmp=fiber_tmp)

        shutil.copy(f"{dirpath}/fiberfox.nii.gz", f"{out_basename}.nii.gz")
        shutil.copy(f"{dirpath}/fiberfox_Phase.nii.gz", f"{out_basename}_phase.nii.gz")
        shutil.copy(f"{dirpath}/fiberfox_kSpace.nii.gz", f"{out_basename}_kspace.nii.gz")
        shutil.copy(f"{dirpath}/fiberfox_Coil-1-real.nii.gz", f"{out_basename}_Coil-1-real.nii.gz")
        shutil.copy(f"{dirpath}/fiberfox_Coil-1-imag.nii.gz", f"{out_basename}_Coil-1-imag.nii.gz")
        shutil.copy(f"{dirpath}/fiberfox.bvecs", f"{out_basename}.bvecs")
        shutil.copy(f"{dirpath}/fiberfox.bvals", f"{out_basename}.bvals")

        with open(f"{out_basename}_info.json", 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, ensure_ascii=False, indent=4)

    except:
        return print(f"FiberFoxSimulation failed for {seq_name}...")
    shutil.rmtree(dirpath)
    os.remove(fiber_tmp)


def simulator(grad_pref, output_dir, gradients_dir, sim_templates_dir, run_method, comb):
    [head_motion, random_motion, eddy, reverse_phase, motion_level, motion_percent_vols, eddy_level] = comb

    print("\n\n", grad_pref, comb, "\n\n")

    simulate(f"{gradients_dir}/{grad_pref}.bvec", f"{gradients_dir}/{grad_pref}.bval",
             output_dir=output_dir, run_method=run_method, sim_templates_dir=sim_templates_dir,
             voxel_size=2, head_motion=head_motion, random_motion=random_motion, eddy=eddy, reverse_phase=reverse_phase, motion_level=motion_level, motion_percent_vols=motion_percent_vols, eddy_level=eddy_level)
    return

if __name__ == '__main__':
    choices = [[True, False], [True, False], [True, False], [False], ["severe", "mild"], [0.25, 0.75], ["severe", "mild"]]
    combs = list(itertools.product(*choices))

    gradients_dir = f"/home/dpys/Applications/fiberfox-wrapper/gradients"
    sim_templates_dir = "/home/dpys/Applications/FilesForSimulation"
    output_dir = "/mnt/dpys/data/fiberfox_sims"

    grad_prefixes = [j for j in set([os.path.basename(i).split('.bvec')[0] for i in glob.glob(f"{gradients_dir}/*")]) if 'bval' not in j]

    #grad_prefixes = ['hcp_multishell', 'SingleShell']
    grad_prefixes = ['SingleShell']

    #run_method = "/home/dpys/Applications/fiberfox-wrapper/fiberfox.simg"
    run_method = "/home/dpys/Applications/MITK-Diffusion-2018.09.99-linux-x86_64/MitkFiberfox.sh" # options are "Docker", "PATH/TO/*.simg", "PATH/TO/MitkFiberfox.sh"

    for grad_pref in grad_prefixes:
        with Parallel(n_jobs=32, prefer="threads") as parallel:
            outs = parallel(delayed(simulator)(grad_pref, output_dir, gradients_dir, sim_templates_dir, run_method, comb) for comb in combs)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

#ps -ef | grep 'MitkFiberfox' | grep -v grep | awk '{print $2}' | xargs -r kill -9
#ps -ef | grep 'fiberfox' | grep -v grep | awk '{print $2}' | xargs -r kill -9

