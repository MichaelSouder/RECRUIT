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
Load + start (requires python3, stdlib only -- no pip install needed):
  ./airgap-cli update-containers .
Or, to also bring up Postgres/Redis on a completely fresh host:
  copy recruit-airgap.env.example to recruit-airgap.env, edit, then:
  ./airgap-cli stack-up .
Or from repo: ./scripts/airgap-cli update-containers /path/to/bundle
