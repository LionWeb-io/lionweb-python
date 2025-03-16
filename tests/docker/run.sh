cd packages/server
echo "== MODEL REPOSITORY SETUP =="
node dist/server.js --setup --config my-server-local-config.json
echo "== MODEL REPOSITORY RUN =="
node dist/server.js --run --config my-server-local-config.json
