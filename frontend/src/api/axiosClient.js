import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const axiosClient = axios.create({ baseURL: BASE_URL, timeout: 60000 })

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error:", error.response?.data ?? error.message ?? error);
    return Promise.reject(error);
  }
);

export default axiosClient;
