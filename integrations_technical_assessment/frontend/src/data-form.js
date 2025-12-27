import { useState } from 'react';
import {
  Box,
  TextField,
  Button,
} from '@mui/material';
import axios from 'axios';

const endpointMapping = {
  'Notion': 'notion/load',
  'Airtable': 'airtable/load',
  'HubSpot': 'hubspot/get_hubspot_items',
};

export const DataForm = ({ integrationType, credentials }) => {
  const [loadedData, setLoadedData] = useState(null);

  const endpoint = endpointMapping[integrationType];

  const handleLoad = async () => {
    if (!credentials) {
      alert('Please connect to the integration first.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('credentials', JSON.stringify(credentials));

      const res = await axios.post(
        `http://localhost:8000/integrations/${endpoint}`,
        formData
      );

      setLoadedData(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to load data");
    }
  };

  return (
    <Box display="flex" flexDirection="column">
      <TextField
        label="Loaded Data"
        multiline
        minRows={6}
        value={loadedData ? JSON.stringify(loadedData, null, 2) : ''}
        sx={{ mt: 2 }}
        InputLabelProps={{ shrink: true }}
        disabled
      />

      <Button onClick={handleLoad} sx={{ mt: 2 }} variant="contained">
        Load Data
      </Button>

      <Button onClick={() => setLoadedData(null)} sx={{ mt: 1 }}>
        Clear Data
      </Button>
    </Box>
  );
};
