singularity exec --nv --fakeroot --bind ~/.ssh:/home/$USER/.ssh \
 --overlay /scratch/cx2219/codebase/myenv/overlay-50G-10M-dev.ext3:rw \
  /scratch/cx2219/codebase/myenv/cuda12.1.1-cudnn8.9.0-devel-ubuntu22.04.2.sif \
  /bin/bash \
