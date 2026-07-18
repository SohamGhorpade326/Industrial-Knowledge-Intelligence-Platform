// @ts-nocheck
import React, { useState, useRef, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, TextField, IconButton, Chip,
  Drawer, List, ListItemButton, ListItemText, Divider, Paper,
  CircularProgress, Accordion, AccordionSummary, AccordionDetails,
  Button,
} from '@mui/material';
import {
  Send, SmartToy, Person, ContentCopy, ExpandMore,
  Description, History, Add, Refresh,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { chatService } from '../services/chat';
import type { ChatMessage } from '../types';
import toast from 'react-hot-toast';

const agentTypes = [
  { value: 'knowledge', label: 'Knowledge', color: '#42a5f5' },
  { value: 'maintenance', label: 'Maintenance', color: '#66bb6a' },
  { value: 'compliance', label: 'Compliance', color: '#ffa726' },
  { value: 'rootcause', label: 'Root Cause', color: '#ef5350' },
];

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = sessionStorage.getItem('ikp_chat_messages');
    return saved ? JSON.parse(saved) : [];
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [agentType, setAgentType] = useState('knowledge');
  const [historyOpen, setHistoryOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

  useEffect(() => {
    scrollToBottom();
    sessionStorage.setItem('ikp_chat_messages', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    chatService.getHistory(undefined, 20).then(setChatHistory).catch(console.error);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput('');
    const userMessage: ChatMessage = { question, answer: '', agent_type: agentType, confidence: 0, risk_level: '', severity: '', recommended_action: '', sources: [], suggested_questions: [], isUser: true };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await chatService.sendMessage(question, agentType);
      setMessages((prev) => [...prev, { ...response, isUser: false }]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        question: '', answer: err.response?.data?.detail || 'Failed to get response. Please try again.',
        agent_type: agentType, confidence: 0, risk_level: 'error', severity: '', recommended_action: '',
        sources: [], suggested_questions: [], isUser: false,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestedQuestion = (q: string) => {
    setInput(q);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  return (
    <Box sx={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
      <Drawer
        variant="temporary"
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        sx={{ '& .MuiDrawer-paper': { width: 300 } }}
      >
        <Box sx={{ p: 2 }}>
          <Typography  variant="subtitle1" sx={{ fontWeight: 600 }} >Chat History</Typography>
        </Box>
        <Divider />
        <List>
          {chatHistory.map((item, i) => (
            <ListItemButton key={i} onClick={() => {
              setMessages((prev) => [...prev,
                { ...item, isUser: true, answer: '' },
                { ...item, isUser: false },
              ]);
              setHistoryOpen(false);
            }}>
              <ListItemText
                primary={item.question}
                secondary={`${item.agent_type} • ${item.confidence}%`}
                primaryTypographyProps={{ fontSize: '0.8rem', noWrap: true }}
                secondaryTypographyProps={{ fontSize: '0.7rem' }}
              />
            </ListItemButton>
          ))}
        </List>
      </Drawer>

      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
          <IconButton onClick={() => setHistoryOpen(true)}><History /></IconButton>
          <Typography  variant="h6"  sx={{ fontWeight: 600, flex: 1 }}>AI Knowledge Assistant</Typography>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            {agentTypes.map((agent) => (
              <Chip
                key={agent.value}
                label={agent.label}
                onClick={() => setAgentType(agent.value)}
                sx={{
                  bgcolor: agentType === agent.value ? agent.color : 'transparent',
                  color: agentType === agent.value ? 'white' : 'text.secondary',
                  border: '1px solid',
                  borderColor: agentType === agent.value ? agent.color : 'divider',
                  fontWeight: agentType === agent.value ? 600 : 400,
                  cursor: 'pointer',
                  fontSize: '0.75rem',
                }}
              />
            ))}
          </Box>
        </Box>

        <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
          {messages.length === 0 && (
            <Box sx={{ textAlign: 'center', mt: 8 }}>
              <SmartToy sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
              <Typography variant="h5" gutterBottom>Ask me anything about your plant</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                I can help with SOPs, maintenance, compliance, and more
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
                {['What is the startup procedure for the CNC Machine?', 'Show electrical safety SOP', 'Why did Compressor A fail last month?'].map((q) => (
                  <Chip key={q} label={q} onClick={() => handleSuggestedQuestion(q)}
                    sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }} />
                ))}
              </Box>
            </Box>
          )}

          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Box sx={{ display: 'flex', gap: 2, mb: 3, justifyContent: msg.isUser ? 'flex-end' : 'flex-start' }}>
                  {!msg.isUser && (
                    <Box sx={{
                      width: 36, height: 36, borderRadius: '50%',
                      bgcolor: 'primary.main', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      flexShrink: 0,
                    }}>
                      <SmartToy sx={{ fontSize: 20, color: 'white' }} />
                    </Box>
                  )}
                  <Paper sx={{
                    p: 2, maxWidth: '70%', borderRadius: 3,
                    bgcolor: msg.isUser ? 'primary.main' : 'background.paper',
                    color: msg.isUser ? 'primary.contrastText' : 'text.primary',
                    border: msg.isUser ? 'none' : '1px solid',
                    borderColor: 'divider',
                  }}>
                    {msg.isUser ? (
                      <Typography variant="body2">{msg.question}</Typography>
                    ) : (
                      <>
                        <ReactMarkdown>{msg.answer}</ReactMarkdown>

                        {msg.confidence > 0 && (
                          <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            <Chip label={`Confidence: ${msg.confidence}%`} size="small" color={msg.confidence >= 70 ? 'success' : 'warning'} sx={{ fontSize: '0.7rem' }} />
                            {msg.risk_level && <Chip label={`Risk: ${msg.risk_level}`} size="small" sx={{ fontSize: '0.7rem' }} />}
                          </Box>
                        )}

                        {msg.sources?.length > 0 && (
                          <Accordion sx={{ mt: 1, bgcolor: 'transparent', boxShadow: 'none', '&:before': { display: 'none' } }}>
                            <AccordionSummary expandIcon={<ExpandMore />} sx={{ p: 0, minHeight: 36 }}>
                              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <Description sx={{ fontSize: 14 }} /> {msg.sources.length} source(s)
                              </Typography>
                            </AccordionSummary>
                            <AccordionDetails sx={{ p: 0 }}>
                              {msg.sources.map((src, j) => (
                                <Box key={j} sx={{ p: 1, mb: 0.5, bgcolor: 'action.hover', borderRadius: 1 }}>
                                  <Typography  variant="caption" sx={{ fontWeight: 600 }} >{src.document}</Typography>
                                  {src.page && <Typography variant="caption" color="text.secondary"> • Page {src.page}</Typography>}
                                  <Typography variant="caption" display="block" color="text.secondary">{src.chunk_text}</Typography>
                                </Box>
                              ))}
                            </AccordionDetails>
                          </Accordion>
                        )}

                        <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                          <IconButton size="small" onClick={() => copyToClipboard(msg.answer)}><ContentCopy sx={{ fontSize: 16 }} /></IconButton>
                        </Box>

                        {msg.suggested_questions?.length > 0 && (
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="caption" color="text.secondary" gutterBottom>Follow-up:</Typography>
                            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                              {msg.suggested_questions.map((q, j) => (
                                <Chip key={j} label={q} size="small" onClick={() => handleSuggestedQuestion(q)}
                                  sx={{ cursor: 'pointer', fontSize: '0.7rem', '&:hover': { bgcolor: 'action.hover' } }} />
                              ))}
                            </Box>
                          </Box>
                        )}
                      </>
                    )}
                  </Paper>
                  {msg.isUser && (
                    <Box sx={{
                      width: 36, height: 36, borderRadius: '50%',
                      bgcolor: 'secondary.main', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      flexShrink: 0,
                    }}>
                      <Person sx={{ fontSize: 20, color: 'white' }} />
                    </Box>
                  )}
                </Box>
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <Box sx={{ width: 36, height: 36, borderRadius: '50%', bgcolor: 'primary.main', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <SmartToy sx={{ fontSize: 20, color: 'white' }} />
              </Box>
              <Paper sx={{ p: 2, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2" color="text.secondary">Thinking...</Typography>
                </Box>
              </Paper>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder="Ask about SOPs, maintenance, compliance..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': { borderRadius: 3 },
              }}
            />
            <IconButton
              onClick={handleSend}
              disabled={!input.trim() || loading}
              sx={{
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': { bgcolor: 'primary.dark' },
                '&:disabled': { bgcolor: 'action.disabledBackground' },
                borderRadius: 2,
                width: 44,
                height: 44,
              }}
            >
              <Send />
            </IconButton>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default Chat;
