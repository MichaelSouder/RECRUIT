Air-gapped deployment — required container images
==================================================

You need ALL of the following .tar files on the offline machine:

  Infrastructure (Docker Hub originals):
    postgres-15.tar       -> image: postgres:15
    redis-7-alpine.tar    -> image: redis:7-alpine

  RECRUIT application (built from this repo):
    recruit-backend.tar   -> image: ghcr.io/michaelsouder/recruit-backend:latest
    recruit-frontend.tar  -> image: ghcr.io/michaelsouder/recruit-frontend:latest

GitHub Container Registry only stores the app images; Postgres and Redis are
included only in the offline export (this bundle / CI artifacts).

Full procedure: read AIRGAP_DEPLOY.md in this folder (copy of docs/AIRGAP_DEPLOY.md).
Load images: ./load-container-images.sh .   (script is copied here by export)
Or from repo: ./scripts/load-container-images.sh path/to/folder-with-all-four-tars
