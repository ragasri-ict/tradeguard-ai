const API_URL = "https://tradeguard-ai-e3jb.onrender.com";

export async function getCompanies() {
  const response = await fetch(
    `${API_URL}/companies`
  );

  if (!response.ok) {
    throw new Error("Unable to load companies.");
  }

  return response.json();
}


export async function getHealth() {
  const response = await fetch(
    `${API_URL}/health`
  );

  if (!response.ok) {
    throw new Error("Backend is not available.");
  }

  return response.json();
}


export async function analyzeAttribution(
  symbol,
  date
) {
  const response = await fetch(
    `${API_URL}/attribution/${encodeURIComponent(symbol)}/${date}`
  );

  const result = await response.json();

  if (!response.ok || result.error) {
    throw new Error(
      result.error ||
      "Unable to analyze event."
    );
  }

  return result;
}
