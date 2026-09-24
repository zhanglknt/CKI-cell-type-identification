# Dockerfile for the CKI package (v0.5.2)
# ----------------------------------------------------------------------------
# Builds a minimal container with the CKI package installed, so that the
# analyses in the manuscript can be reproduced in a controlled environment.
#
# Build:    docker build -t cki:0.5.2 .
# Verify:   docker run --rm cki:0.5.2
#
# The base image tracks the Python version used for the reported analyses
# (3.14.4). The container image provides the package and its dependencies;
# input datasets are downloaded separately per ENV_SETUP.md / the
# Reproducibility Guide (not bundled to keep the image small).
FROM python:3.14-slim

WORKDIR /app

# Install pinned dependencies from the lock file, then the CKI package
COPY requirements-lock.txt pyproject.toml README.md LICENSE ./
COPY cki/ ./cki/
RUN pip install --no-cache-dir -r requirements-lock.txt \
    && pip install --no-cache-dir --no-deps .

# Sanity check: the package imports and ships the HRT Atlas reference
RUN python -c "import cki; print('CKI', cki.__version__)"

CMD ["python", "-c", "import cki; from cki.species import load_reference_hk_genes; print('CKI', cki.__version__, 'ready; HRT Atlas HK genes:', len(load_reference_hk_genes('human')))"]
