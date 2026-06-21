# Privacy and data handling

ResumeMatch AI processes CV text, job descriptions, account email addresses and
optional Telegram identifiers. CVs may contain sensitive personal information.

## Data flow

- Account and analysis records are stored in PostgreSQL.
- Progress events transit through Redis.
- CV and job-description text is sent to the configured Groq or Ollama provider.
- Telegram receives a short summary only when explicitly configured.
- The Chrome extension stores its token and CV text locally on the device.

## Operator responsibilities

Self-hosting operators must define:

- a retention and deletion schedule;
- user export and deletion procedures;
- access controls and backup encryption;
- provider data-processing terms;
- applicable GDPR, KVKK, CCPA or other regional obligations;
- incident response and breach notification procedures.

Do not use production CV data in tests, logs or issue reports. Generated messages
must be reviewed by a person before use.

## Default retention

- Analysis records are deleted after 30 days.
- Expired or used authentication tokens are cleaned after 30 days.
- Minimal audit events are retained for 180 days.
- Browser-extension settings remain on the user's device until cleared or the
  extension is removed.

## Data subject controls

Authenticated users can export stored data as JSON and permanently delete their
account from the dashboard. Account deletion cascades to analyses, API keys,
refresh tokens, verification/reset tokens, and notification settings.
