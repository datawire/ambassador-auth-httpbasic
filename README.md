# Ambassador Module - HTTP Basic Authentication

Generic reusable Ambassador Authentication Module that supports HTTP Basic Authentication and a simple username to password database.

# Using With Ambassador

To use this authentication module with Ambassador you need to configure Ambassador to be aware of it. The easiest way to do that is to attach it to the annotations on the Kubernetes service that acts as the entrypoint to Ambassador, for example:

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
      kind: Module
      name: authentication
      config:
        auth_service: "ambassador-auth:80"
        path_prefix: "/extauth"
        allowed_headers: []
        
spec:
  type: LoadBalancer
  ports:
    - name: ambassador
      port: 80
      targetPort: 80
  selector:
    service: ambassador
```

# License

Licensed under Apache 2.0. Please read [LICENSE](LICENSE) for details.

