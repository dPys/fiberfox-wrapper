#!/bin/bash
ln -s /ismrm/FilesForSimulation/param.ffp_VOLUME1.nrrd /out/
ln -s /ismrm/FilesForSimulation/TemplateDWI.dwi /out/
ln -s /ismrm/FilesForSimulation/SimulationMask.nrrd /out/
ln -s /ismrm/FilesForSimulation/Fibers.fib /out/
ln -s /ismrm/FilesForSimulation/param.ffp_VOLUME4.nrrd /out/
ln -s /ismrm/FilesForSimulation/Readme.txt /out/
ln -s /ismrm/FilesForSimulation/param.ffp_VOLUME3.nrrd /out/
ln -s /ismrm/FilesForSimulation/param.ffp_FMAP.nrrd /out/
ln -s /ismrm/FilesForSimulation/param.ffp_MASK.nrrd /out/
ln -s /ismrm/FilesForSimulation/param.ffp_VOLUME2.nrrd /out/

exec /fiberfox/MITK-Diffusion-2017.07-linux64/MitkFiberfox.sh "$@"
