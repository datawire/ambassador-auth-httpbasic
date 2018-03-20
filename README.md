# Ambassador Module - HTTP Basic Authentication

[![Build Status](https://travis-ci.org/datawire/ambassador-auth-httpbasic.svg?branch=master)](https://travis-ci.org/datawire/ambassador-auth-httpbasic)

Reusable Ambassador Authentication Module that supports HTTP Basic Authentication and a username and password database.

# Users Database

The file format for the users database is:

- A single UTF-8 encoded YAML document
- Each key in the YAML document is a plaintext username.
- Each value for a key is a YAML object with a single field named `hashed_password`.
- The value of `hashed_password` is a [bcrypt](https://en.wikipedia.org/wiki/Bcrypt) encrypted Base64 representation of a SHA256 hashed password. The complexity of this step is to support long passwords since bcrypt does not work for longer than 72 bytes of data.

An example is shown below:

```yaml
admin:
  hashed_password: "$2b$12$2uSUm0tOHR.6.otAic0zZuHNLjH2TJ5fymD3GwDgEGJx6Mfqbcn/u"

user1:
  hashed_password: "$2b$12$BfyGWJEVpybci4ze7tpKuuWxlJ/aS1sFqQwuuxMC/X0ey9YkHxnr."
```

# Editing the Users Database

1. You need to install a bcrypt tool or library. I recommend the Python implementation which can be installed with `pip`.

    ```bash
    pip install bcrypt
    ```

## Add User

1. Prepare the password for bcrypt. In the below example we prepare the password `hunter2`.

    ```bash
    export PREPARED_PASSWORD=$(echo "hunter2" | sha256sum | head -c 64 | openssl base64 -A)
    ```
    
2. Encrypt the prepared password using bcrypt:

    ```bash
    echo "$PREPARED_PASSWORD" | python -c 'import bcrypt, sys; print(bcrypt.hashpw(sys.stdin.read().encode(), bcrypt.gensalt()).decode())'
    ```

3. Add a new entry to your users database.

    Given:
    
    ```yaml
    user1:
      hashed_password: "$2b$12$BfyGWJEVpybci4ze7tpKuuWxlJ/aS1sFqQwuuxMC/X0ey9YkHxnr."
    ```
    
    Becomes:
    
    ```yaml
    user1:
      hashed_password: "$2b$12$BfyGWJEVpybci4ze7tpKuuWxlJ/aS1sFqQwuuxMC/X0ey9YkHxnr."

    user2:
      hashed_password: "$2b$12$hcPac9pcaV5caK/TU.Oi8.8Y2eosUX6zCBEdPZSDhvl7HQ1IqbnDC"   
    ```

## Remove User

1. Find the entry for a given username in the YAML document and delete it.

## Update Kubernetes Secret

1. Kubernetes secrets contain a base64 data blob that contain the secret's payload. The YAML document needs to be base64 encoded.

    ```bash
    cat path/to/users.yaml | openssl base64 -A
    ```

2. Update the secret payload:

    ```yaml
    ---
    apiVersion: v1
    kind: Secret
    metadata:
      name: ambassador-auth-httpbasic-users
    type: Opaque
    data:
      users.yaml: ${BASE64_ENCODED_USERS_DATA}
    ```
    
3. Update the secret:

    ```bash
    kubectl apply -f path/to/secret.yaml
    ```
    
4. Propagation of the change to all Pods running the authentication module takes about 30 seconds to a minute.

# Using With Ambassador

1. Install the Authentication module. A reference install is available in the [`manifests/`](manifests/) directory. It is recommended that you download the manifest into your source repository since you need to manage the Kubernetes secret in order to control who can access your services.

2. Add one or more users to the users database. Securely managing the users database file is outside scope of this doc. 

3. Configure Ambassador to use the authentication module. The easiest way to do that is to add configuration data to your Ambassador entrypoint service.

    **NOTE** - The below snippet should work with default Ambassador install. If you're using a custom install (e.g different namespace, different service name etc) then you should customize as necessary.

    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      labels:
        service: ambassador
      name: ambassador
    annotations:
      getambassador.io/config: |
        apiVersion: ambassador/v0
        kind: AuthService
        name: authentication
        config:
          auth_service: "ambassador-auth:80"
          path_prefix: "/extauth"
          allowed_headers: []
    spec:
      type: NodePort
      ports:
        - name: ambassador
          port: 80
          targetPort: 80
      selector:
        service: ambassador
    ```

# License

Licensed under Apache 2.0. Please read [LICENSE](LICENSE) for details.

