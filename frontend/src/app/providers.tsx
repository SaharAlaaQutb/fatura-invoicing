import { createContext, useContext, useState, ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

interface AuthContextValue {
  user: AuthUser | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

interface AuthUser {
  id: string;
  email: string;
  role: string;
  preferredLanguage: string;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface LocaleContextValue {
  locale: string;
  setLocale: (locale: string) => void;
  dir: "ltr" | "rtl";
}

const LocaleContext = createContext<LocaleContextValue | undefined>(undefined);

interface ToastContextValue {
  toast: (message: string, type?: "success" | "error" | "info") => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [locale, setLocaleState] = useState<"ar" | "en">("en");
  const dir = locale === "ar" ? "rtl" : "ltr";

  const login = async (_email: string, _password: string) => {
    setUser({
      id: "1",
      email: _email,
      role: "owner",
      preferredLanguage: locale,
    });
  };

  const logout = () => {
    setUser(null);
  };

  const setLocale = (next: string) => {
    setLocaleState(next as "ar" | "en");
  };

  const toast = (message: string, type: "success" | "error" | "info" = "info") => {
    // eslint-disable-next-line no-console
    (console as unknown as Record<string, (...args: unknown[]) => void>)[type](message);
  };

  const isAuthenticated = !!user;

  return (
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={{ user, login, logout, isAuthenticated }}>
        <LocaleContext.Provider value={{ locale, setLocale, dir }}>
          <ToastContext.Provider value={{ toast }}>
            <div dir={dir} lang={locale}>
              {children}
            </div>
          </ToastContext.Provider>
        </LocaleContext.Provider>
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within Providers");
  return ctx;
};

export const useLocale = () => {
  const ctx = useContext(LocaleContext);
  if (!ctx) throw new Error("useLocale must be used within Providers");
  return ctx;
};

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within Providers");
  return ctx;
};

export default Providers;
