// @ts-nocheck
import React, { useEffect, useState } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Chip, List, ListItem, ListItemText,
  Select, MenuItem, FormControl, InputLabel, TextField, Skeleton, Avatar,
  LinearProgress, Divider,
} from '@mui/material';
import { Build, Warning, CheckCircle, Schedule, Engineering } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { maintenanceService } from '../services/maintenance';
import { chatService } from '../services/chat';
import type { Machine, MaintenanceLog, ChatMessage } from '../types';

const severityColor: Record<string, string> = {
  low: '#4caf50', medium: '#ffa726', high: '#ef5350', critical: '#d32f2f',
};

const statusIcon: Record<string, React.ReactElement> = {
  operational: <CheckCircle sx={{ color: '#4caf50' }} />,
  maintenance: <Build sx={{ color: '#ffa726' }} />,
  failed: <Warning sx={{ color: '#ef5350' }} />,
  idle: <Schedule sx={{ color: '#78909c' }} />,
};

const Maintenance: React.FC = () => {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);
  const [logs, setLogs] = useState<MaintenanceLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [aiResponse, setAiResponse] = useState<ChatMessage | null>(null);
  const [querying, setQuerying] = useState(false);

  useEffect(() => {
    maintenanceService.getMachines()
      .then((data) => { setMachines(data.machines); if (data.machines.length > 0) setSelectedMachine(data.machines[0]); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedMachine) {
      maintenanceService.getLogs(selectedMachine.id).then((data) => setLogs(data.logs)).catch(console.error);
    }
  }, [selectedMachine]);

  const handleQuery = async () => {
    if (!query.trim()) return;
    setQuerying(true);
    try {
      const response = await chatService.maintenanceQuery(query, selectedMachine?.id);
      setAiResponse(response);
    } catch (err) {
      console.error(err);
    } finally {
      setQuerying(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {Array.from({ length: 6 }).map((_, i) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={i}>
              <Skeleton variant="rounded" height={160} sx={{ borderRadius: 3 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography  variant="h5" sx={{ fontWeight: 700 }}  gutterBottom>Maintenance Intelligence</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Monitor machines, track failures, and get AI-powered maintenance recommendations
      </Typography>

      <Grid container spacing={2.5}>
        {machines.map((machine) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={machine.id}>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Card
                onClick={() => setSelectedMachine(machine)}
                sx={{
                  borderRadius: 3,
                  border: '2px solid',
                  borderColor: selectedMachine?.id === machine.id ? 'primary.main' : 'divider',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': { borderColor: 'primary.main' },
                }}
              >
                <CardContent sx={{ p: 2.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography  variant="subtitle1" sx={{ fontWeight: 600 }} >{machine.name}</Typography>
                    {statusIcon[machine.status] || statusIcon.idle}
                  </Box>
                  <Typography variant="body2" color="text.secondary">{machine.machine_type} • {machine.manufacturer}</Typography>
                  <Typography variant="caption" color="text.secondary">{machine.location}</Typography>
                  <Box sx={{ mt: 1.5 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption">Health Score</Typography>
                      <Typography  variant="caption" sx={{ fontWeight: 600 }} >{machine.health_score}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={machine.health_score}
                      sx={{ height: 6, borderRadius: 3, bgcolor: 'action.hover',
                        '& .MuiLinearProgress-bar': { bgcolor: machine.health_score >= 80 ? '#4caf50' : machine.health_score >= 60 ? '#ffa726' : '#ef5350' },
                      }}
                    />
                  </Box>
                  <Chip label={machine.status} size="small" sx={{ mt: 1, textTransform: 'capitalize', fontSize: '0.7rem' }} />
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {selectedMachine && (
        <>
          <Card sx={{ mt: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography  variant="subtitle1" sx={{ fontWeight: 600 }}  gutterBottom>
                Maintenance History — {selectedMachine.name}
              </Typography>
              {logs.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>No maintenance records found</Typography>
              ) : (
                <List>
                  {logs.map((log) => (
                    <React.Fragment key={log.id}>
                      <ListItem sx={{ px: 0 }}>
                        <Box sx={{ width: 4, height: 40, bgcolor: severityColor[log.severity] || '#78909c', borderRadius: 2, mr: 2 }} />
                        <ListItemText
                          primary={log.issue}
                          secondary={
                            <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                              <Chip label={log.severity} size="small" sx={{ bgcolor: `${severityColor[log.severity]}20`, color: severityColor[log.severity], fontSize: '0.65rem', height: 20 }} />
                              <Chip label={log.issue_type} size="small" sx={{ fontSize: '0.65rem', height: 20 }} />
                              <Typography variant="caption" color="text.secondary">
                                {new Date(log.date).toLocaleDateString()} • {log.engineer} • {log.downtime_hours}h downtime
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>

          <Card sx={{ mt: 2, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography  variant="subtitle1" sx={{ fontWeight: 600 }}  gutterBottom>
                AI Maintenance Assistant
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth size="small"
                  placeholder={`Ask about ${selectedMachine.name}...`}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                />
              </Box>
              {querying && <LinearProgress sx={{ mb: 2 }} />}
              {aiResponse && (
                <Box sx={{ p: 2, bgcolor: 'action.hover', borderRadius: 2 }}>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{aiResponse.answer}</Typography>
                  {aiResponse.confidence > 0 && (
                    <Chip label={`Confidence: ${aiResponse.confidence}%`} size="small" sx={{ mt: 1 }} />
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
};

export default Maintenance;
