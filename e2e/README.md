# End to End ("e2e") Tests

Simple end to end test suite.

# Setup

Run `./setup.sh` to do the following things:

1. Setup a Kubernetes cluster
2. Install Ambassador
3. Install the `auth-httpbasic` Ambassador authentication module.
4. Install a service behind the module that should be protected.

# Running

Run `./e2e-test.sh` to run the tests.

# Cleanup

Run `./teardown.sh` to cleanup all the things performed by `setup.sh`
