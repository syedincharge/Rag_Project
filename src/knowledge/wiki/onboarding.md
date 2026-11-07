# Engineering Onboarding

Welcome to Zomato Engineering. This page covers your first weeks. Ask in #new-joiners if anything is unclear.

## Day one

- Collect your laptop and access card from the IT desk.
- Meet your onboarding buddy. They will walk you through the team's codebase and rituals.
- Complete the mandatory security awareness course in the Learning Portal within your first 3 days.
- Join the team Slack channels listed in your welcome email.

## Accounts and access

You will receive these accounts on day one: company email, Slack, GitHub, Jira, Confluence and the internal Zomato Admin dashboard. Production access is **not** granted automatically. Request it through the Access Portal after you finish the security course; your manager must approve it, and access is reviewed every quarter.

### VPN setup

Install the company VPN client from the IT portal, then sign in with your work email and the authenticator app. Connect to the VPN before opening any internal tool from outside the office. If the VPN disconnects repeatedly, restart the client and check that your laptop clock is correct. If it still fails, switch the VPN protocol to TCP in the client settings. For anything else, contact itdesk@zomato.example.

### Two-factor authentication

Two-factor authentication is mandatory for email, GitHub and the Admin dashboard. Use the authenticator app, not SMS. Store your recovery codes in the company password manager. If you change your phone, ask IT to reset your authenticator before you wipe the old device.

### Password manager

All shared credentials live in the company password manager. Never paste secrets into Slack, tickets or code. Rotate any secret you suspect was exposed and tell #security-help right away.

## Your development environment

1. Install the standard toolchain with the setup script in the `dev-setup` repository.
2. Clone your team's repositories using SSH keys registered on GitHub.
3. Run the service locally using the team README and the shared `docker compose` file.
4. Use the staging environment for integration testing. Never test against production data.

### Local services

Most backend services run on Java or Go with PostgreSQL and Redis. Messaging uses Kafka. A local `docker compose up` starts the dependencies you need, and seed data scripts load test restaurants and menus.

## How we ship code

### Branching and pull requests

Create a feature branch from `main`, keep pull requests small (under 400 changed lines where possible) and link the Jira ticket in the title. Every pull request needs at least one approval from a teammate who owns the area, and all checks must pass.

### Code review norms

Review within one working day. Comment on the code, not the person, and prefer questions to commands. Use "nit:" for optional style suggestions. The author resolves comments and merges after approval.

### Deployments

Deployments run through the CI/CD pipeline. Merges to `main` deploy to staging automatically. Production deploys happen in a weekday window between 11:00 and 17:00, with a rollback plan written in the ticket. There is a deployment freeze on festival sale days and the last week of each quarter, announced in #eng-announcements.

## On-call

After your first month you join the on-call rotation as a shadow, then as primary after 3 months. On-call engineers carry the pager for one week, acknowledge alerts within 10 minutes and follow the runbooks. You get a compensatory off for weekend incidents, as described in the handbook.

## Your first week

1. Set up your local development environment from the team README.
2. Pick up a starter ticket labelled `good-first-issue` and open your first pull request.
3. Shadow one on-call shift so you understand how incidents are handled.
4. Schedule 1:1 introductions with your manager, buddy and product partner.

## First 30, 60 and 90 days

| Period | Goal |
|---|---|
| 30 days | Ship your first change to production and understand the service architecture |
| 60 days | Own a small feature end to end and join the review rotation |
| 90 days | Take part in on-call and present a short tech talk to the team |

## Communication norms

Use Slack for quick questions and Confluence for anything that should live longer than a week. Put decisions in writing. Keep meetings to 30 minutes by default, share an agenda in advance and end with clear action owners.

## Learning resources

Your learning budget of ₹40,000 per year covers courses and books. The internal Learning Portal has security training, system design talks and recordings of past tech talks.

## Who to ask

| Topic | Where |
|---|---|
| Laptop and access problems | #it-help or itdesk@zomato.example |
| Leave and payroll | peopleops@zomato.example |
| Security questions | #security-help or security@zomato.example |
| Team questions | Your onboarding buddy |
