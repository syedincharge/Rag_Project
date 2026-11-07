# Payments Service Runbook

Owner: Payments Platform team. On-call channel: #payments-oncall.

## Overview

The payments service processes customer orders, refunds and restaurant payouts. It runs as a stateless service behind a load balancer, with 6 replicas per region. It talks to several payment gateways and banks, a PostgreSQL primary with read replicas, a Redis cache and Kafka for payment events.

## Architecture and dependencies

| Component | Purpose | Failure impact |
|---|---|---|
| Payments API | Creates and confirms payments | Customers cannot pay |
| Gateway adapters | Connect to banks, UPI and card networks | Payment methods fail individually |
| Refund worker | Processes refunds from a queue | Refunds stay pending |
| Payout worker | Settles restaurant payouts weekly | Payouts are delayed |
| Webhook receiver | Gets payment status from gateways | Orders stay in pending state |

## Health checks

- Dashboard: `Payments / Overview` in the monitoring tool.
- Healthy means: error rate under 1%, p95 latency under 800 ms, and a payment success rate above 97%.
- Alerts page the on-call engineer when the success rate stays below 95% for 5 minutes.

## Restarting the payments service

Restart only after checking the health dashboard and confirming the problem is not a bank or gateway outage.

1. Post in #payments-oncall: "Restarting payments in <region>, reason: <reason>".
2. Run a rolling restart: `kubectl rollout restart deployment/payments -n payments-prod`.
3. Watch the rollout: `kubectl rollout status deployment/payments -n payments-prod`.
4. Confirm the success rate returns above 97% within 10 minutes.
5. Post the outcome in the channel and note it in the incident ticket.

Never restart all regions at once. Restart one region, verify, then continue. Never restart from the cloud console; always use the rollout command so traffic drains safely.

## Deploying and rolling back

Deploy through the pipeline during the weekday window. To roll back, run `kubectl rollout undo deployment/payments -n payments-prod` and confirm the version with `kubectl rollout history`. Database migrations must be backward compatible for one release so that a rollback is always safe.

## Common incidents

### A single bank is failing

If success drops for one bank only, check the gateway status page, then switch routing for that bank to the backup gateway from the Routing Console. Post an update in #payments-oncall every 30 minutes until recovery.

### Duplicate charges reported

Check that idempotency keys are being sent. Search the payment events for the same order id. Refund the duplicate through the refund tool and raise a Sev 2 ticket if more than 20 customers are affected.

### Webhooks not arriving

Orders stay pending when gateway webhooks stop. Check the webhook receiver logs for signature errors, confirm the gateway can reach the endpoint, and replay missed events using `python scripts/replay_webhooks.py --since 1h`.

### Database connection pool exhausted

Symptoms are rising latency followed by timeouts. Check the connection count on the primary, look for long-running queries, and scale replicas only after confirming the reads are the cause. Do not raise the pool size without checking the database limits.

## Refund queue stuck

If refunds stay in `PENDING` for more than 30 minutes:

1. Check the refund worker logs for `gateway_timeout`.
2. Re-queue with `python scripts/requeue_refunds.py --older-than 30m`.
3. If more than 500 refunds are affected, page the on-call engineer.

## Restaurant payouts

Payouts run every Tuesday for the previous Monday to Sunday week. If the payout job fails, do not run it twice. Check the job status, fix the cause and resume from the last successful batch using the resume flag, so that no restaurant is paid twice.

## Reconciliation

Finance reconciles gateway settlement files against internal records every day. Mismatches above ₹10,000 in total raise an alert to #payments-recon. The on-call engineer supports Finance by exporting the payment events for the affected window.

## Escalation

| Severity | Example | Who to page |
|---|---|---|
| Sev 1 | Payments down in any region | On-call engineer, then Engineering Manager |
| Sev 2 | Success rate between 90% and 97% | On-call engineer |
| Sev 3 | Single bank failing | Post in #payments-oncall |

## After an incident

Write a blameless post-incident review within 3 working days for every Sev 1 and Sev 2. Include a timeline, the root cause, what went well, what did not, and action items with owners and dates. Review the actions in the weekly platform meeting.
