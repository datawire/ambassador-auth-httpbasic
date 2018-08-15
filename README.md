# Ambassador Module - HTTP Basic Authentication

[![Build Status](https://travis-ci.org/datawire/ambassador-auth-httpbasic.svg?branch=master)](https://travis-ci.org/datawire/ambassador-auth-httpbasic)

Reusable Ambassador Authentication Module that supports HTTP Basic Authentication and a username and password database.

# Quick Start

**NOTE**: The quick start sets up a user database with a single user `admin` and password `admin`. Later on the `README` shows how to add and remove users from the database so you can customize for your own uses.

1. [Install Ambassador if you have not already!](https://www.getambassador.io/user-guide/getting-started)

2. Add the the Authentication service to your Ambassador.
    
   Given (the original Ambassador service from [Getting Started](https://www.getambassador.io/user-guide/getting-started):
   
   ```yaml
   ---
   apiVersion: v1
   kind: Service
   metadata:
     labels:
       service: ambassador
     name: ambassador
     annotations:
       getambassador.io/config: |
         ---
         apiVersion: ambassador/v0
         kind:  Mapping
         name:  httpbin_mapping
         prefix: /httpbin/
         service: httpbin.org:80
         host_rewrite: httpbin.org
   spec:
     type: LoadBalancer
     ports:
       - name: ambassador
         port: 80
         targetPort: 80
     selector:
       service: ambassador
   ```
   
   Edit so afterwards it becomes:
   
   ```yaml
   ---
   apiVersion: v1
   kind: Service
   metadata:
     labels:
       service: ambassador
     name: ambassador
     annotations:
       getambassador.io/config: |
         ---
         apiVersion: ambassador/v0
         kind: AuthService
         name: authentication
         auth_service: "ambassador-auth:80"
         path_prefix: "/extauth"
         allowed_headers: []
         ---
         apiVersion: ambassador/v0
         kind:  Mapping
         name:  httpbin_mapping
         prefix: /httpbin/
         service: httpbin.org:80
         host_rewrite: httpbin.org
   spec:
     type: LoadBalancer
     ports:
       - name: ambassador
         port: 80
         targetPort: 80
     selector:
       service: ambassador
   ```

3. Install the Ambassador HTTP Basic Authentication module from this repository

    ```bash
    kubectl apply -f https://raw.githubusercontent.com/datawire/ambassador-auth-httpbasic/master/manifests/ambassador-auth-httpbasic.yaml
    ```

4. Get the value of Ambassador's External IP (shown as `__EXTERNAL_IP_VALUE__` below)

    ```bash
    kubectl get svc ambassador -o wide
 
    NAME         TYPE           CLUSTER-IP      EXTERNAL-IP             PORT(S)        AGE       SELECTOR
    ambassador   LoadBalancer   100.67.255.49   __EXTERNAL_IP_VALUE__   80:30818/TCP   3h        service=ambassador
    ```
    
5. Attempt to reach one of your services without authentication:

    ```bash
    curl -v http://__EXTERNAL_IP_VALUE__/qotm/
 
    > GET /qotm/ HTTP/1.1
    > Host: __EXTERNAL_IP_VALUE__
    > User-Agent: curl/7.55.1
    > Accept: */*

    < HTTP/1.1 401 Unauthorized
    < server: envoy
    < date: Tue, 20 Mar 2018 17:07:56 GMT
    * Authentication problem. Ignoring this.
    < www-authenticate: Basic realm="Authentication Required"
    < content-type: text/html; charset=utf-8
    < content-length: 0
    < x-envoy-upstream-service-time: 305

    ```
    
6. Attempt to reach one of your services with authentication:

    ```bash
    curl -v -u admin:admin http://__EXTERNAL_IP_VALUE__/qotm/
 
    > GET /qotm/ HTTP/1.1
    > Host: __EXTERNAL_IP_VALUE__
    > Authorization: Basic YWRtaW46YWRtaW4=
    > User-Agent: curl/7.55.1
    > Accept: */*
     
    < HTTP/1.1 200 OK
    < content-type: application/json
    < content-length: 172
    < server: envoy
    < date: Tue, 20 Mar 2018 17:08:40 GMT
    < x-envoy-upstream-service-time: 98
 
    {
      "hostname": "qotm-58d5cb7699-hrp7p", 
      "ok": true, 
      "quote": "A late night does not make any sense.", 
      "time": "2018-03-20T17:08:40.556710", 
      "version": "1.1"
    }
    ```

# Users Database

The file format for the users database is:

- A single UTF-8 encoded YAML document
- Each key in the YAML document is a plaintext username.
- Each value for a key is a YAML object with a single field named `hashed_password`.
- The value of `hashed_password` is a [bcrypt](https://en.wikipedia.org/wiki/Bcrypt) encrypted Base64 representation of a SHA256 hashed password in hexadecimal representation. The complexity of this step is to support long passwords since bcrypt does not work for longer than 72 bytes of data.

An example is shown below:

```yaml
admin:
  hashed_password: "$2b$12$2uSUm0tOHR.6.otAic0zZuHNLjH2TJ5fymD3GwDgEGJx6Mfqbcn/u"

user1:
  hashed_password: "$2b$12$BfyGWJEVpybci4ze7tpKuuWxlJ/aS1sFqQwuuxMC/X0ey9YkHxnr."
```

# Manipulating the Users Database

1. You need to install a bcrypt tool or library. The Python implementation is recommended and can be installed with `pip`.

    ```bash
    pip install bcrypt
    ```

## Add User

1. Prepare the password for bcrypt. In the below example we prepare the password `hunter2` for use.

    ```bash
    export PREPARED_PASSWORD=$(printf "hunter2" | shasum -a 256 | head -c 64 | openssl base64 -A)
    ```
    
2. Encrypt the prepared password using bcrypt:

    ```bash
    printf "$PREPARED_PASSWORD" | python -c 'import bcrypt, sys; print(bcrypt.hashpw(sys.stdin.read().encode(), bcrypt.gensalt()).decode())'
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
      name: ambassador-auth-httpbasic
    type: Opaque
    data:
      users.yaml: ${BASE64_ENCODED_USERS_DATA}
    ```
    
3. Update the secret:

    ```bash
    kubectl apply -f path/to/secret.yaml
    ```
    
4. Propagation of the change to all Pods running the authentication module takes about 30 seconds to a minute.

# License

Licensed under Apache 2.0. Please read [LICENSE](LICENSE) for details.

