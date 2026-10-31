export interface User {
  id: string;
  email: string;
  role: "owner" | "accountant" | "cashier";
  preferredLanguage: "ar" | "en";
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}
