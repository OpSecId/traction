export const TABLE_OPT = {
  ROWS_DEFAULT: 10,
  ROWS_OPTIONS: [10, 25, 50],
};

export const API_PATH = {
  // The tenant UI backend
  CONFIG: '/config',
  EMAIL_CONFIRMATION: '/email/reservationConfirmation',
  EMAIL_STATUS: '/email/reservationStatus',

  // Acapy and plugins (and Traction for now)
  INNKEEPER_TOKEN: '/innkeeper/token',
  INNKEEPER_TENANTS: '/innkeeper/tenants/',
  INNKEEPER_TENANT: (id: string) => `/innkeeper/tenants/${id}`,
  INNKEEPER_RESERVATIONS: '/innkeeper/reservations/',
  INNKEEPER_RESERVATIONS_APPROVE: (id: string) =>
    `/innkeeper/reservations/${id}/approve`,
  INNKEEPER_RESERVATIONS_DENY: (id: string) =>
    `/innkeeper/reservations/${id}/deny`,

  OIDC_INNKEEPER_LOGIN: '/api/innkeeperLogin',

  TENANT_TOKEN: '/tenant/token',

  CONNECTIONS: '/connections',
  CONNECTION: (id: string) => `/connections/${id}`,
  CONNECTIONS_CREATE_INVITATION: '/connections/create-invitation',
  // CONTACTS_RECEIVE_INVITATION: '/tenant/v1/contacts/receive-invitation',
  CONNECTIONS_INVITATION: (id: string) => `/connections/${id}/invitation`,

  HOLDER_CREDENTIALS: '/tenant/v1/holder/credentials/',
  HOLDER_CREDENTIALS_ACCEPT_OFFER: (id: string) =>
    `/tenant/v1/holder/credentials/${id}/accept-offer`,
  HOLDER_CREDENTIALS_REJECT_OFFER: (id: string) =>
    `/tenant/v1/holder/credentials/${id}/reject-offer`,
  HOLDER_CREDENTIAL: (id: string) => `/tenant/v1/holder/credentials/${id}`,
  HOLDER_PRESENTATIONS: '/tenant/v1/holder/presentations/',
  HOLDER_PRESENTATION: (id: string) => `/tenant/v1/holder/presentations/${id}`,

  ISSUER_CREDENTIALS: '/tenant/v1/issuer/credentials/',
  ISSUER_CREDENTIAL: (id: string) => `/tenant/v1/issuer/credentials/${id}`,
  ISSUER_CREDENTIAL_REVOKE: (id: string) =>
    `/tenant/v1/issuer/credentials/${id}/revoke-credential`,

  VERIFIER_PRESENTATIONS: '/tenant/v1/verifier/presentations/',
  VERIFIER_PRESENTATION: (id: string) =>
    `/tenant/v1/verifier/presentations/${id}`,
  VERIFIER_PRESENTATION_ADHOC_REQUEST:
    '/tenant/v1/verifier/presentations/adhoc-request',
  VERIFIER_PRESENTATION_TEMPLATES:
    '/tenant/v1/verifier/presentation_templates/',

  GOVERNANCE_SCHEMA_TEMPLATES: '/tenant/v1/governance/schema_templates/',
  GOVERNANCE_SCHEMA_TEMPLATES_IMPORT:
    '/tenant/v1/governance/schema_templates/import',
  GOVERNANCE_SCHEMA_TEMPLATE: (id: string) =>
    `/tenant/v1/governance/schema_templates/${id}`,
  GOVERNANCE_CREDENTIAL_TEMPLATES:
    '/tenant/v1/governance/credential_templates/',
  GOVERNANCE_CREDENTIAL_TEMPLATE: (id: string) =>
    `/tenant/v1/governance/credential_templates/${id}`,

  BASICMESSAGES: '/basicmessages',
  BASICMESSAGES_SEND: (connId: string) => `/connections/${connId}/send-message`,

  TENANT_SELF: '/tenant',
  TENANT_ENDORSER_CONNECTION: '/tenant/endorser-connection',
  TENANT_ENDORSER_INFO: '/tenant/endorser-info',
  TENANT_REGISTER_PUBLIC_DID: '/tenant/register-public-did',

  MULTITENANCY_RESERVATIONS: '/multitenancy/reservations',
  MULTITENANCY_RESERVATION: (resId: string) =>
    `/multitenancy/reservations/${resId}`,
  MULTITENANCY_RESERVATION_CHECK_IN: (resId: string) =>
    `/multitenancy/reservations/${resId}/check-in`,
  MULTITENANCY_TENANT_TOKEN: (tenantId: string) =>
    `/multitenancy/tenant/${tenantId}/token`,
  MULTITENANCY_WALLET_TOKEN: (tenantId: string) =>
    `/multitenancy/wallet/${tenantId}/token`,

  WALLET_DID_PUBLIC: '/wallet/did/public',
};

export const CONNECTION_STATUSES = {
  INVITATION: 'invitation',
  ACTIVE: 'active',
  RESPONSE: 'response',
};

export const RESERVATION_STATUSES = {
  APPROVED: 'approved',
  CHECKED_IN: 'checked_in',
  DENIED: 'denied',
  REQUESTED: 'requested',
  // Not an API status, but the state on the FE when just checked-in
  // so they can one-time see the wallet key
  SHOW_WALLET: 'show_wallet',
};
