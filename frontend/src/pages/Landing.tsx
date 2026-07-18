import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Container, Grid, useTheme, Divider } from '@mui/material';
import { motion } from 'framer-motion';
import {
  Speed,
  Security,
  AccountTree,
  ArrowForward,
  AutoGraph,
  FactCheck,
  Business
} from '@mui/icons-material';

const Landing: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', overflowX: 'hidden' }}>
      
      {/* 1. Enterprise Navbar */}
      <Box sx={{ 
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50, 
        backdropFilter: 'blur(10px)', backgroundColor: 'rgba(15, 23, 42, 0.8)',
        borderBottom: '1px solid rgba(255,255,255,0.05)' 
      }}>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: 1400, mx: 'auto' }}>
          <Typography variant="h5" sx={{ fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: 1 }}>
            <AccountTree fontSize="large" sx={{ color: 'primary.main' }} /> IKP Enterprise
          </Typography>
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center' }}>
            <Typography variant="button" sx={{ color: '#aaa', display: { xs: 'none', md: 'block' }, cursor: 'pointer', '&:hover': { color: '#fff' } }}>Platform</Typography>
            <Typography variant="button" sx={{ color: '#aaa', display: { xs: 'none', md: 'block' }, cursor: 'pointer', '&:hover': { color: '#fff' } }}>Solutions</Typography>
            <Typography variant="button" sx={{ color: '#aaa', display: { xs: 'none', md: 'block' }, cursor: 'pointer', '&:hover': { color: '#fff' } }}>Resources</Typography>
            <Divider orientation="vertical" flexItem sx={{ borderColor: 'rgba(255,255,255,0.1)' }} />
            <Button variant="text" sx={{ color: '#fff' }} onClick={() => navigate('/login')}>Sign In</Button>
            <Button variant="contained" color="primary" onClick={() => navigate('/login')} sx={{ borderRadius: 1, px: 3, fontWeight: 700 }}>
              Request Demo
            </Button>
          </Box>
        </Box>
      </Box>

      {/* 2. Hero Section */}
      <Container maxWidth="xl" sx={{ pt: { xs: 15, md: 20 }, pb: 10 }}>
        <Grid container spacing={8} sx={{ alignItems: 'center' }}>
          <Grid size={{ xs: 12, md: 6 }}>
            <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
              <Typography variant="overline" sx={{ color: 'primary.main', fontWeight: 800, letterSpacing: 2 }}>
                THE FUTURE OF INDUSTRIAL INTELLIGENCE
              </Typography>
              <Typography variant="h1" sx={{ fontWeight: 900, lineHeight: 1.1, mb: 3, mt: 2, fontSize: { xs: '3rem', md: '4.5rem' } }}>
                Unify Your <br/>
                <Box component="span" sx={{ color: 'primary.main' }}>Factory Data.</Box>
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ mb: 5, fontWeight: 400, maxWidth: 600, lineHeight: 1.6 }}>
                Transform disconnected manuals, SOPs, and maintenance records into a centralized, queryable AI Knowledge Graph. Diagnose failures instantly and reduce downtime by 40%.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  size="large"
                  endIcon={<ArrowForward />}
                  onClick={() => navigate('/login')}
                  sx={{ borderRadius: 1, px: 4, py: 2, fontSize: '1.1rem', fontWeight: 700 }}
                >
                  Start Enterprise Trial
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  sx={{ borderRadius: 1, px: 4, py: 2, fontSize: '1.1rem', fontWeight: 700, color: 'text.primary', borderColor: 'divider' }}
                >
                  Contact Sales
                </Button>
              </Box>
            </motion.div>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 1, delay: 0.2 }}>
              <Box
                sx={{
                  position: 'relative',
                  width: '100%',
                  height: 500,
                  bgcolor: '#0f172a',
                  borderRadius: 4,
                  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
                  overflow: 'hidden',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundImage: 'url(/ai-brain.png)',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                }}
              >
                <Box sx={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, #0f172a, transparent)' }} />
                <Typography variant="h4" sx={{ fontWeight: 700, zIndex: 1, color: '#fff', position: 'absolute', bottom: 40, left: 40, textShadow: '0 4px 20px rgba(0,0,0,0.8)' }}>
                  Industrial Knowledge Core
                </Typography>
              </Box>
            </motion.div>
          </Grid>
        </Grid>
      </Container>

      {/* 3. Trusted By Ticker */}
      <Box sx={{ borderTop: '1px solid', borderBottom: '1px solid', borderColor: 'divider', py: 4, bgcolor: 'background.paper' }}>
        <Container maxWidth="xl">
          <Typography variant="body2" color="text.secondary" align="center" sx={{ fontWeight: 600, mb: 3, letterSpacing: 1, textTransform: 'uppercase' }}>
            Trusted by Industry Leaders Worldwide
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: { xs: 4, md: 10 }, flexWrap: 'wrap', opacity: 0.6, filter: 'grayscale(100%)' }}>
            <Business sx={{ fontSize: 40 }} />
            <AutoGraph sx={{ fontSize: 40 }} />
            <AccountTree sx={{ fontSize: 40 }} />
            <Speed sx={{ fontSize: 40 }} />
            <FactCheck sx={{ fontSize: 40 }} />
            <Security sx={{ fontSize: 40 }} />
          </Box>
        </Container>
      </Box>

      {/* 4. Deep Dive Features */}
      <Box sx={{ bgcolor: theme.palette.mode === 'dark' ? '#0b1120' : '#f8fafc', py: 15 }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 10 }}>
            <Typography variant="h2" sx={{ fontWeight: 800, mb: 3 }}>
              Enterprise-Grade Capabilities
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto', fontWeight: 400 }}>
              Purpose-built for massive industrial operations. Connect your data silos into a single source of truth.
            </Typography>
          </Box>

          <Grid container spacing={4}>
            {[
              { title: 'Neo4j Knowledge Graph', desc: 'Automatically maps relationships between machines, components, maintenance logs, and operators for deep operational insights.', icon: <AccountTree fontSize="large" color="primary" /> },
              { title: 'Generative AI RAG', desc: 'Ask complex engineering questions and get precise, confident answers cited directly from your manuals and SOPs.', icon: <Speed fontSize="large" color="secondary" /> },
              { title: 'Compliance & Safety', desc: 'Monitor safety violations, audit trails, and ensure all operational procedures meet strict global regulatory standards.', icon: <Security fontSize="large" color="error" /> },
              { title: 'Automated Ingestion', desc: 'Instantly parse and embed complex industrial PDFs, schematics, and CSV maintenance logs into vector storage.', icon: <AccountTree fontSize="large" color="info" /> },
              { title: 'Failure Diagnosis', desc: 'Utilize historical maintenance logs and LLM reasoning to rapidly diagnose the root cause of unexpected machine downtimes.', icon: <Speed fontSize="large" color="warning" /> },
              { title: 'Enterprise SSO Ready', desc: 'Seamlessly integrate into your corporate network with role-based access control and secure authentication.', icon: <Security fontSize="large" color="success" /> },
            ].map((feature, idx) => (
              <Grid size={{ xs: 12, md: 4 }} key={idx}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <Box sx={{ p: 4, bgcolor: 'background.default', borderRadius: 2, height: '100%', border: '1px solid', borderColor: 'divider' }}>
                    <Box sx={{ mb: 2, display: 'inline-block', p: 1.5, bgcolor: 'background.paper', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
                      {feature.icon}
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>{feature.title}</Typography>
                    <Typography color="text.secondary" sx={{ lineHeight: 1.6 }}>{feature.desc}</Typography>
                  </Box>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* 5. CTA Section */}
      <Box sx={{ py: 15, bgcolor: 'primary.dark', color: '#fff', textAlign: 'center' }}>
        <Container maxWidth="md">
          <Typography variant="h2" sx={{ fontWeight: 800, mb: 3 }}>
            Ready to Transform Your Operations?
          </Typography>
          <Typography variant="h6" sx={{ mb: 5, fontWeight: 400, opacity: 0.9 }}>
            Join the leading manufacturers who trust IKP to minimize downtime and maximize intelligence.
          </Typography>
          <Button variant="contained" size="large" onClick={() => navigate('/login')} sx={{ bgcolor: '#fff', color: 'primary.dark', fontWeight: 800, px: 5, py: 2, borderRadius: 1, fontSize: '1.2rem', '&:hover': { bgcolor: '#f1f5f9' } }}>
            Deploy IKP Today
          </Button>
        </Container>
      </Box>

      {/* 6. Footer */}
      <Box sx={{ bgcolor: '#020617', color: '#94a3b8', py: 6, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
        <Container maxWidth="xl" sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <Typography variant="body2">© 2026 Industrial Knowledge Platform. All rights reserved.</Typography>
          <Box sx={{ display: 'flex', gap: 3 }}>
            <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { color: '#fff' } }}>Privacy Policy</Typography>
            <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { color: '#fff' } }}>Terms of Service</Typography>
            <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { color: '#fff' } }}>Security</Typography>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default Landing;
