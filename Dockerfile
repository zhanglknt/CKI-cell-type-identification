# Dockerfile for the CKI package (v0.4.4)
# ----------------------------------------------------------------------------
# Builds a minimal container with the CKI package installed, so that the
# analyses in the manuscript can be reproduced in a controlled environment.
#
# Build:    docker build -t cki:0.4.4 .
# Verify:   docker run --rm cki:0.4.4
#
# The base image tracks the Python version used for the reported analyses
# (3.14.4). The container image provides the package and its dependencies;
# input datasets are downloaded separately per ENV_SETUP.md / the
# Reproducibility Guide (not bundled to keep the image small).
FROM python:3.14-slim

WORKDIR /app

# Install the CKI package from the repository root
COPY pyproject.toml README.md LICENSE ./
COPY cki/ ./cki/
RUN pip install --no-cache-dir .

# Sanity check: the package imports and ships the HRT Atlas reference
RUN python -c "import cki; print('CKI', cki.__version__)"

CMD ["python", "-c", "import cki; from cki.species import load_reference_hk_genes; print('CKI', cki.__version__, 'ready; HRT Atlas HK genes:', len(load_reference_hk_genes('human')))"]
