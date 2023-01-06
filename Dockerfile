FROM continuumio/miniconda3

WORKDIR /src/magpye

COPY environment.yml /src/magpye/

RUN conda install -c conda-forge gcc python=3.10 \
    && conda env update -n base -f environment.yml

COPY . /src/magpye

RUN pip install --no-deps -e .
