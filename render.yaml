services:
  - type: web
    name: scrap-googl-chrome-sele-test
    env: python
    buildCommand: ./render-build.sh
    startCommand: gunicorn app:app --bind=0.0.0.0:$PORT
    autoDeploy: true