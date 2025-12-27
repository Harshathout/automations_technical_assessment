import { useState } from 'react';
import {
  Box,
  Autocomplete,
  TextField,
} from '@mui/material';

import { AirtableIntegration } from './integrations/airtable';
import { NotionIntegration } from './integrations/notion';
import { HubSpotIntegration } from './integrations/hubspot';
import { DataForm } from './data-form';

/**
 * Mapping integration name → component
 * This controls the dropdown AND rendering
 */
const integrationMapping = {
  'HubSpot': HubSpotIntegration,
  'Notion': NotionIntegration,
  'Airtable': AirtableIntegration,
};

export const IntegrationForm = () => {
  const [integrationParams, setIntegrationParams] = useState({});
  const [user, setUser] = useState('TestUser');
  const [org, setOrg] = useState('TestOrg');
  const [currType, setCurrType] = useState(null);

  const CurrIntegration = currType ? integrationMapping[currType] : null;

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      flexDirection="column"
      sx={{ width: '100%' }}
    >
      {/* User & Org Inputs */}
      <Box display="flex" flexDirection="column">
        <TextField
          label="User"
          value={user}
          onChange={(e) => setUser(e.target.value)}
          sx={{ mt: 2 }}
        />

        <TextField
          label="Organization"
          value={org}
          onChange={(e) => setOrg(e.target.value)}
          sx={{ mt: 2 }}
        />

        {/* Integration Type Dropdown */}
        <Autocomplete
          id="integration-type"
          options={Object.keys(integrationMapping)}
          sx={{ width: 300, mt: 2 }}
          renderInput={(params) => (
            <TextField {...params} label="Integration Type" />
          )}
          onChange={(e, value) => {
            setCurrType(value);
            setIntegrationParams({});
          }}
        />
      </Box>

      {/* Selected Integration UI */}
      {CurrIntegration && (
        <Box sx={{ mt: 2 }}>
          <CurrIntegration
            user={user}
            org={org}
            integrationParams={integrationParams}
            setIntegrationParams={setIntegrationParams}
          />
        </Box>
      )}

      {/* Data Form */}
      {integrationParams?.credentials && (
        <Box sx={{ mt: 2 }}>
          <DataForm
            integrationType={integrationParams?.type}
            credentials={integrationParams?.credentials}
          />
        </Box>
      )}
    </Box>
  );
};
