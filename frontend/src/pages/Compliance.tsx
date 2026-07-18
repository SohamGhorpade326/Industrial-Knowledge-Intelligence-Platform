// @ts-nocheck
import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, TextField, Button, Grid,
  Chip, List, ListItem, ListItemIcon, ListItemText, LinearProgress,
  Accordion, AccordionSummary, AccordionDetails,
} from '@mui/material';
import { Security, CheckCircle, Warning, ExpandMore, Search, Gavel } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { chatService } from '../services/chat';
import type { ChatMessage } from '../types';
import ReactMarkdown from 'react-markdown';

const complianceAreas = [
  { title: 'Electrical Safety', status: 'compliant', score: 95 },
  { title: 'Fire Safety', status: 'compliant', score: 90 },
  { title: 'Chemical Handling', status: 'review_needed', score: 75 },
  { title: 'PPE Compliance', status: 'compliant', score: 88 },
  { title: 'Machine Guarding', status: 'compliant', score: 92 },
  { title: 'Emergency Procedures', status: 'review_needed', score: 78 },
];

const Compliance: React.FC = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<ChatMessage | null>(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const result = await chatService.complianceQuery(query);
      setResponse(result);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography  variant="h5" sx={{ fontWeight: 700 }}  gutterBottom>Compliance Assistant</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Safety compliance tracking, regulatory guidance, and AI-generated checklists
      </Typography>

      <Grid container spacing={2.5}>
        {complianceAreas.map((area, i) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={area.title}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography  variant="subtitle2" sx={{ fontWeight: 600 }} >{area.title}</Typography>
                    {area.status === 'compliant'
                      ? <CheckCircle sx={{ color: '#4caf50', fontSize: 20 }} />
                      : <Warning sx={{ color: '#ffa726', fontSize: 20 }} />
                    }
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">Compliance Score</Typography>
                    <Typography  variant="caption" sx={{ fontWeight: 600 }} >{area.score}%</Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={area.score}
                    sx={{
                      height: 6, borderRadius: 3, bgcolor: 'action.hover',
                      '& .MuiLinearProgress-bar': { bgcolor: area.score >= 85 ? '#4caf50' : '#ffa726' },
                    }}
                  />
                  <Chip
                    label={area.status === 'compliant' ? 'Compliant' : 'Review Needed'}
                    size="small"
                    color={area.status === 'compliant' ? 'success' : 'warning'}
                    sx={{ mt: 1.5, fontSize: '0.7rem' }}
                  />
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Card sx={{ mt: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
        <CardContent sx={{ p: 3 }}>
          <Typography  variant="subtitle1" sx={{ fontWeight: 600 }}  gutterBottom>
            <Gavel sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
            AI Compliance Assistant
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              fullWidth size="small"
              placeholder="Ask about safety procedures, compliance requirements, SOPs..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
            />
            <Button variant="contained" onClick={handleQuery} disabled={loading} sx={{ borderRadius: 2, textTransform: 'none' }}>
              {loading ? 'Searching...' : 'Ask'}
            </Button>
          </Box>

          <Box sx={{ display: 'flex', gap: 0.5, mb: 2, flexWrap: 'wrap' }}>
            {['Show electrical safety SOP', 'PPE requirements for welding', 'Fire safety checklist'].map((q) => (
              <Chip key={q} label={q} size="small" onClick={() => setQuery(q)} sx={{ cursor: 'pointer', fontSize: '0.7rem' }} />
            ))}
          </Box>

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          {response && (
            <Box sx={{ p: 2, bgcolor: 'action.hover', borderRadius: 2 }}>
              <ReactMarkdown>{response.answer}</ReactMarkdown>
              {response.confidence > 0 && (
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  <Chip label={`Confidence: ${response.confidence}%`} size="small" />
                  <Chip label={`Severity: ${response.severity}`} size="small" />
                </Box>
              )}
              {response.sources?.length > 0 && (
                <Accordion sx={{ mt: 1, bgcolor: 'transparent', boxShadow: 'none' }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="caption">{response.sources.length} source(s)</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    {response.sources.map((src, j) => (
                      <Typography key={j} variant="caption" display="block">
                        📄 {src.document} {src.page && `(Page ${src.page})`}
                      </Typography>
                    ))}
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Compliance;
