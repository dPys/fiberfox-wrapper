# Fiberfox in a container

This code uses a Docker or Singularity image to simulate diffusion weighted MRI.

The container has all the data and software needed to simulate images based on the
realistic streamline set used in the [ISMRM 2015 challenge](http://tractometer.org/ismrm_2015_challenge/).
You can produce simulated dMRI using just the bvals and bvecs (in FSL format) and add additional
noise.

## Making images

To get the Docker image, run

```bash
  $ docker pull pennbbl/fiberfox:latest
```

To build a Singularity image:

```bash
  $ singularity build ~/fiberfox.simg docker://pennbbl/fiberfox:latest
```

## Running simulations

Download and unpack this repository and change into this directory. From python

```python
from simulate_scheme import simulate

simulate("gradients/hcp_multishell.bvec", "gradients/hcp_multishell.bval",
         output_dir="~/", singularity_image="~/fiberfox.simg")
```

If you're using Docker instead of Singularity, set `singularity_image=""`. After these arguments,
you can add anything that goes into the Fiberfox `ffp` file format. Here are the currently
available options (documentation [here](http://docs.mitk.org/nightly/org_mitk_views_fiberfoxview.html))

```python
# Acquisition parameters
acquisitiontype=0 # 0=EPI
coilsensitivityprofile=0
numberofcoils=1
reversephase="false" # Only does something if combined with doAddDistortions

# Pulse sequence
partialfourier=1
trep=4000
signalScale=100
tEcho=108
tLine=1
tInhom=50

# Streamline-based fiber parameters
axonRadius=0
diffusiondirectionmode=0
fiberseparationthreshold=30
doSimulateRelaxation="true"
doDisablePartialVolume="false"

# k space
simulatekspace="true"
kspaceLineOffset=0.1
addringing="false"

# Motion
doAddMotion="false"
randomMotion="false"
motionvolumes=(6, 12, 24)
# These determine the range of possible motion
translation0=2
translation1=0
translation2=0
rotation0=0
rotation1=0
rotation2=4

# Noise
addnoise="false"
noisetype="gaussian"
noisevariance=251

# ghosts/aliasing
addghosts="false"
addaliasing="false"
aliasingfactor=0

# Signal spikes
addspikes="false"
spikesnum=0
spikesscale=1

# Eddy currents
addeddycurrents="false"
eddyStrength=0
eddyTau=70

# B0 distortion
doAddDistortions="false"

# image
outputvolumefractions="false"
artifactmodelstring="_COMPLEX-GAUSSIAN-251"
```
