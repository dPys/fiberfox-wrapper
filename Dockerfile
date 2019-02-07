FROM ubuntu:xenial-20190122

COPY neurodebian.gpg /root/.neurodebian.gpg

# Prepare environment
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    curl \
                    bzip2 \
                    ca-certificates \
                    xvfb \
                    cython3 \
                    build-essential \
                    autoconf \
                    libtool \
                    wget \
                    zip \
                    unzip \
                    pkg-config && \
    curl -sSL http://neuro.debian.net/lists/xenial.us-ca.full >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key add /root/.neurodebian.gpg && \
    (apt-key adv --refresh-keys --keyserver hkp://ha.pool.sks-keyservers.net 0xA5D32F012649A5A9 || true) && \
    apt-get update

# Download fiberfox
RUN mkdir /fiberfox \
    && cd /fiberfox \
    && wget -nv https://www.nitrc.org/frs/downloadlink.php/10130 \
    && tar xvfz 10130 \
    && rm 10130

# Download the test data
RUN mkdir /ismrm \
    && cd /ismrm \
    && wget -nv 'http://tractometer.org/downloads/downloads/ismrm_challenge_2015/ISMRM_2015_Tracto_challenge_ground_truth_dwi_v2.zip' \
    && unzip ISMRM_2015_Tracto_challenge_ground_truth_dwi_v2.zip \
    && rm ISMRM_2015_Tracto_challenge_ground_truth_dwi_v2.zip \
    && wget -nv 'http://tractometer.org/downloads/downloads/ismrm_challenge_2015/FilesForSimulation_v1.zip' \
    && unzip FilesForSimulation_v1.zip \
    && rm FilesForSimulation_v1.zip

RUN apt-get install -y \
      libx11-xcb-dev \
      libfontconfig1-dev \
      libxi-dev \
      libdbus-1-3 \
      libjpeg8 \
      mesa-utils \
      libnss3 \
      libffi-dev \
      libglib2.0-dev \
      libxcomposite-dev \
      libtiff5-dev \
      libgtk2.0-dev \
      libgtk2.0 \
      libtiff5 \
      libxtst6 \
      libxtst-dev \
      gnome-core


ENV LD_LIBRARY_PATH="/fiberfox/MITK-Diffusion-2017.07-linux64/bin":"/fiberfox/MITK-Diffusion-2017.07-linux64/bin/plugins":$LD_LIBRARY_PATH \
    QT_QPA_PLATFORM_PLUGIN_PATH=/fiberfox/MITK-Diffusion-2017.07-linux64/bin

COPY run_fiberfox.sh /usr/local/bin/docker-entrypoint.sh
RUN ln -s /usr/local/bin/docker-entrypoint.sh / \
    && mkdir /out

ENTRYPOINT ["docker-entrypoint.sh"]
