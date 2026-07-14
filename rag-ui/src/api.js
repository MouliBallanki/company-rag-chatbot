const API_BASE_URL = "http://localhost:8000/api";
 
export const uploadFiles = async (fileList) => {
  const formData = new FormData();
  // Append all selected files to the form data object
  for (let i = 0; i < fileList.length; i++) {
    formData.append("files", fileList[i]);
  }
 
  const response = await fetch(`${API_BASE_URL}/admin/upload`, {
    method: "POST",
    body: formData, // Browser automatically sets Content-Type to multipart/form-data
  });
 
  if (!response.ok) throw new Error("Failed to upload files");
  return response.json();
};

export const sendChatQuery = async (userQuery) => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: userQuery }),
  });
 
  if (!response.ok) throw new Error("Failed to fetch response from agent");
  return response.json(); // Returns { query, answer_context, sources }
};