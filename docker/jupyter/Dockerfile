FROM quay.io/jupyter/minimal-notebook:python-3.13

USER root

# Force uv install location
ENV HOME=/root
ENV PATH="/root/.local/bin:${PATH}"

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Create uv venv
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Install Python deps
RUN uv pip install omop-alchemy psycopg2-binary pip omop-graph
RUN /opt/venv/bin/python -m pip install ipykernel && \
    /opt/venv/bin/python -m ipykernel install \
        --name uv-venv \
        --display-name "Python (uv venv)"
# Switch back to notebook user
USER jovyan
ENV HOME=/home/jovyan
COPY ./.env /home/jovyan/work/.env
WORKDIR /home/jovyan/work