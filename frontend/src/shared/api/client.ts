import type { AxiosInstance, AxiosResponse } from "axios";
import axios from "axios";

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  request_id?: string;
}

export class ApiClientError extends Error {
  constructor(public error: ApiError, public status: number) {
    super(error.message || "API error");
    this.name = "ApiClientError";
  }
}

export interface ApiClientConfig {
  baseURL: string;
  getToken?: () => string | null;
}

export class ApiClient {
  private client: AxiosInstance;

  constructor(config: ApiClientConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.client.interceptors.request.use((req) => {
      const token = config.getToken?.();
      if (token) {
        req.headers.Authorization = `Bearer ${token}`;
      }
      return req;
    });

    this.client.interceptors.response.use(
      (res: AxiosResponse) => res,
      (err) => {
        if (err.response) {
          const error: ApiError =
            err.response.data?.error ?? {
              code: "api.error",
              message: err.response.statusText || "API error",
              request_id: err.response.headers["x-request-id"],
            };
          throw new ApiClientError(error, err.response.status);
        }
        throw err;
      }
    );
  }

  async get<T>(path: string, params?: Record<string, unknown>): Promise<T> {
    const res = await this.client.get<T>(path, { params });
    return res.data;
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    const res = await this.client.post<T>(path, body);
    return res.data;
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    const res = await this.client.patch<T>(path, body);
    return res.data;
  }

  async delete(path: string): Promise<void> {
    await this.client.delete(path);
  }
}
