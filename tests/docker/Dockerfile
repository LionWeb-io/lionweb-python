FROM node
ARG lionwebRepositoryCommitId=74d2c6ea6f719f27e6274182d5ab92c9b53cb3c6
RUN mkdir lionweb-repository
WORKDIR lionweb-repository
RUN git init
RUN git remote add origin https://github.com/LionWeb-io/lionweb-repository.git
# Note that this line includes a fetch operation mentioning a specific commit id, so that if this change this step
# will be invalidated and a cached step would not be used (as it would be the case if we first cloned and then
# checked out a commit id)
RUN git fetch --depth 1 origin ${lionwebRepositoryCommitId}
RUN git checkout FETCH_HEAD
ADD my-server-local-config.json packages/server
ADD wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it
COPY run.sh run.sh
RUN chmod +x run.sh
RUN npm install
RUN npm run build
ENV PGHOST=postgres
CMD ["wait-for-it", "pgdb_for_lwpython_tests:5432", "--", "sh", "run.sh"]
