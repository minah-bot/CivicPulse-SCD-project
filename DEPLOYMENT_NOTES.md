# CivicPulse: Kubernetes Deployment and Autoscaling Notes

A summary of how we got CivicPulse running on a local Kubernetes cluster and set up the autoscaling test.

## The problem

After deploying to a local cluster, the backend pods stayed at `0/1` and never became ready. Once they were up, submitting a request in the browser returned a 500 error.

## 1. Backend would not start

The logs showed `Connection refused` to `127.0.0.1:5432` and `localhost:6379`. Those are the fallback defaults in the code, so the pods were not receiving the right settings. The backend deployment had no `envFrom`, so the ConfigMap never reached the container. Adding `envFrom: configMapRef: civicpulse-config` fixed the Redis connection.

## 2. Database connection

The app reads a single `DATABASE_URL`, but the cluster only provided separate `POSTGRES_*` values, so it still fell back to localhost. An earlier attempt to patch the secret also failed, because the deployment never loaded that secret and a placeholder password had been pasted in literally.

The fix was an `env` block in the deployment that pulls `POSTGRES_PASSWORD` from `civicpulse-secrets` and builds `DATABASE_URL` pointing at the `postgres` service. After `kubectl apply -k k8s/overlays/dev/`, both backend pods came up `1/1` and passed the `/ready` check.

## 3. The 500 error

The backend logs showed `KeyError: 'GROQ_API_KEY'`. The app was running, but the request handler needed an API key that was missing from the pod. The fix was to store the key in `civicpulse-secrets` and expose it to the container with a `secretKeyRef` entry in the deployment.

## Lessons learned

- Repeated `rollout restart` commands pile up stuck ReplicaSets. Fix the manifest and apply once.
- `head -1` on the pod list can grab an old terminating pod. Use explicit pod names when checking logs.
- Secrets and ConfigMaps only matter if the deployment actually references them.

## 4. Autoscaling setup

The HPA (min 2, max 6 replicas, 65% CPU target) showed `<unknown>` for CPU, and `kubectl top` reported "Metrics API not available". The cause was that metrics-server was not installed. We installed it and added `--kubelet-insecure-tls`, since local cluster certificates are not trusted by default. `kubectl top pods` then showed real numbers (about 6m CPU per backend pod at idle).

## 5. Chart tooling

- `log_hpa.sh` records time, CPU %, and replica counts every 5 seconds into `hpa_log.csv`.
- `plot.py` turns that data into a replicas-vs-load chart with the 65% target line.
- On Ubuntu, the libraries were installed with `apt` (`python3-pandas python3-matplotlib`) to avoid the pip restriction.

The first two charts were flat because metrics-server was missing and the logger wrote 0 when it got no reading.

## Load test procedure

1. Confirm `kubectl get hpa backend-hpa -n civicpulse` shows a real percentage.
2. Start `./log_hpa.sh` and wait about a minute at idle.
3. Start the load-generator pods and watch replicas scale up.
4. Delete the load pods and wait about 5 minutes for scale-down.
5. Stop the logger and run `python3 plot.py` to produce `hpa_chart.png`.

## Evidence

- `hpa_chart.png`: replicas vs load chart
- `hpa_log.csv`: raw data behind the chart
