# AI-Onboarding-Assistant-7-Day-Success-Plan-

<div align="center">

# Zylos AI Onboarding Assistant
### Personalized 7-Day Success Plan Automation for n8n

Turn new signups into successful users with an onboarding flow that asks the right questions, generates a realistic 7-day plan, tracks progress, and checks in automatically.

<br/>

<img src="https://dummyimage.com/1200x420/0b1220/ffffff&text=Zylos+Onboarding+Assistant" alt="Zylos Onboarding Assistant banner" width="100%" />

<br/><br/>

![Built with n8n](https://img.shields.io/badge/Built%20with-n8n-ff6d00?style=flat-square)
![Automation](https://img.shields.io/badge/Type-Automation-7c3aed?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production%20Ready-10b981?style=flat-square)

</div>

---

## What it does

When a user signs up, this workflow:

- Ingests onboarding data through a webhook
- Generates a tailored 7-day plan using OpenAI
- Logs the plan to Google Sheets (or swap to Airtable)
- Emails the plan to the user
- Waits 3 days
- Sends a short check-in message

Optional upgrades you can add later:
- Update Days 4 to 7 based on the user’s reply
- Route internal alerts to Slack
- Pull real product data (Stripe, Shopify, GA4, HubSpot) to make plans data-driven

---

## Quick demo

### Flow diagram

```text
Webhook (New User) 
  -> Normalize Payload 
    -> OpenAI (Generate Plan JSON)
      -> Parse JSON
        -> Google Sheets (Log)
          -> Email (Send Plan)
            -> Wait (3 days)
              -> Email (Day 3 Check-in)
