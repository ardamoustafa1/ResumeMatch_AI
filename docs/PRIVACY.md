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
