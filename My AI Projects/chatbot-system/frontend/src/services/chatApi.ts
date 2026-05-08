const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const chatApi = {
  baseUrl: API_BASE_URL,

  async sendMessage(): Promise<void> {
    // TODO: Implement backend chat API call.
    return Promise.resolve()
  },
}
