FROM continuumio/miniconda3

WORKDIR /src/earthkit-maps

COPY environment.yml /src/earthkit-maps/

RUN conda install -c conda-forge gcc python=3.10 \
    && conda env update -n base -f environment.yml

COPY . /src/earthkit-maps

RUN pip install --no-deps -e .
