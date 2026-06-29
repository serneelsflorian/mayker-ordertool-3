import { API_BASE_URL } from '../config/constants';
import type { ApiError } from './types';

export class ApiRequestError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: unknown[];

  constructor(status: number, code: string, message: string, details: unknown[] = []) {
    super(message);
    this.name = 'ApiRequestError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export class NetworkError extends Error {
  constructor(message = 'Network request failed') {
    super(message);
    this.name = 'NetworkError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    if (response.status === 204) {
      return undefined as unknown as T;
    }
    return response.json() as Promise<T>;
  }

  let errorBody: ApiError | undefined;
  try {
    errorBody = (await response.json()) as ApiError;
  } catch {
    throw new ApiRequestError(response.status, 'unknown_error', response.statusText);
  }

  const { code, message, details } = errorBody?.error ?? {
    code: 'unknown_error',
    message: response.statusText,
    details: [],
  };

  throw new ApiRequestError(response.status, code, message, details);
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers ?? {}),
      },
      ...options,
    });
    return handleResponse<T>(response);
  } catch (err) {
    if (err instanceof ApiRequestError) {
      throw err;
    }
    throw new NetworkError(
      err instanceof Error ? err.message : 'Unknown network error',
    );
  }
}
