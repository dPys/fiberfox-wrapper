#!/bin/bash
cp /ismrm/FilesForSimulation/param.ffp_VOLUME1.nrrd /out/
cp /ismrm/FilesForSimulation/TemplateDWI.dwi /out/
cp /ismrm/FilesForSimulation/SimulationMask.nrrd /out/
cp /ismrm/FilesForSimulation/Fibers.fib /out/
cp /ismrm/FilesForSimulation/param.ffp_VOLUME4.nrrd /out/
cp /ismrm/FilesForSimulation/Readme.txt /out/
cp /ismrm/FilesForSimulation/param.ffp_VOLUME3.nrrd /out/
cp /ismrm/FilesForSimulation/param.ffp_FMAP.nrrd /out/
cp /ismrm/FilesForSimulation/param.ffp_MASK.nrrd /out/
cp /ismrm/FilesForSimulation/param.ffp_VOLUME2.nrrd /out/

exec /fiberfox/MITK-Diffusion-2018.09.99-linux64/MitkFiberfox.sh "$@"
