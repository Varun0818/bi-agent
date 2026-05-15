import axiosClient from "./axiosClient";

export function sendQuery(userQuery, sessionId) {
  return axiosClient
    .post("/chat/query", {
      user_query: userQuery,
      session_id: sessionId ?? null,
    })
    .then((res) => res.data);
}

export function getSessions() {
  return axiosClient.get("/sessions/").then((res) => res.data);
}

export function createSession(name) {
  return axiosClient
    .post("/sessions/", { session_name: name })
    .then((res) => res.data);
}

export function getHistory(sessionId, limit = 20) {
  return axiosClient
    .get("/history/", {
      params: { session_id: sessionId, limit },
    })
    .then((res) => res.data);
}

export function getTrace(queryId) {
  return axiosClient.get(`/traces/${queryId}`).then((res) => res.data);
}

export function getSchema() {
  return axiosClient.get("/schema/").then((res) => res.data);
}

export const getSessionMessages = async (sessionId) => {
  const response = await axiosClient.get(`/sessions/${sessionId}/messages`);
  return response.data;
};

export const renameSession = async (sessionId, name) => {
  const response = await axiosClient.patch(`/sessions/${sessionId}`, {
    session_name: name,
  });
  return response.data;
};

export const deleteSession = async (sessionId) => {
  const response = await axiosClient.delete(`/sessions/${sessionId}`);
  return response.data;
};

export const clearAllSessions = async () => {
  const response = await axiosClient.delete("/sessions/clear-all");
  return response.data;
};

export const cleanupGarbageSessions = async () => {
  const response = await axiosClient.post("/sessions/cleanup-garbage");
  return response.data;
};
