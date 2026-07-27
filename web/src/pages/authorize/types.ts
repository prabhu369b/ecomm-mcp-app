export interface AuthorizationResult {
  action: 'login' | 'consent';
  request_id: string | null;
  client_name: string | null;
  scopes: string[];
  state: string;
  login_url: string | null;
}

export interface ConsentApprovalResult {
  redirect_uri: string;
}
