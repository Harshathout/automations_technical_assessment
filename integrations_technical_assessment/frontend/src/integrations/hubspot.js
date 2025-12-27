import { Button, Stack } from "@mui/material";

export const HubSpotIntegration = ({
  user,
  org,
  integrationParams,
  setIntegrationParams,
}) => {

  // STEP 1: OAuth Redirect (ONLY way)
  const connectHubSpot = () => {
  window.location.href =
    `http://localhost:8000/integrations/hubspot/authorize?user_id=${user}&org_id=${org}`;
  };
  // STEP 2: Fetch stored credentials from backend
  const fetchCredentials = async () => {
    const fd = new FormData();
    fd.append("user_id", user);
    fd.append("org_id", org);

    const res = await fetch(
      "http://localhost:8000/integrations/hubspot/credentials",
      { method: "POST", body: fd }
    );

    const credentials = await res.json();

    setIntegrationParams({
      type: "HubSpot", // ✅ EXACT MATCH
      credentials,
    });
  };

  return (
    <Stack spacing={2}>
      <Button variant="contained" onClick={connectHubSpot}>
        Connect HubSpot
      </Button>

      <Button variant="outlined" onClick={fetchCredentials}>
        Load HubSpot Data
      </Button>
    </Stack>
  );
};
