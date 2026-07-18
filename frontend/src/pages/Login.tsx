import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, TextField, Button, Paper, InputAdornment,
  IconButton, Divider, Grid,
} from '@mui/material';
import { Visibility, VisibilityOff, Email, Lock, Login as LoginIcon, AccountTree } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuthStore } from '../context/store';
import toast from 'react-hot-toast';
import api from '../services/api';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const login = useAuthStore((s: any) => s.login);
  const [email, setEmail] = useState('admin@ikp.com');
  const [password, setPassword] = useState('admin123');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e?: React.FormEvent) => {
    e?.preventDefault();
    setLoading(true);
    try {
      const response = await api.post('/api/auth/login', { email, password });
      login(response.data.user, response.data.access_token);
      toast.success('Authentication successful');
      navigate('/app');
    } catch (error) {
      toast.error('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const handleSSO = (provider: string) => {
    toast(`Redirecting to ${provider} SSO...`, { icon: '🔄' });
    handleLogin();
  };

  return (
    <Grid container sx={{ minHeight: '100vh' }}>
      {/* Left side - Branding (Hidden on mobile) */}
      <Grid size={{ xs: 12, md: 6 }} sx={{ 
        display: { xs: 'none', md: 'flex' },
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
        color: '#fff',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <Box sx={{ position: 'absolute', top: -100, left: -100, width: 400, height: 400, borderRadius: '50%', background: 'rgba(255,255,255,0.05)' }} />
        <Box sx={{ position: 'absolute', bottom: -50, right: -50, width: 300, height: 300, borderRadius: '50%', background: 'rgba(255,255,255,0.05)' }} />
        
        <motion.div initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
            <AccountTree sx={{ fontSize: 60 }} />
            <Typography variant="h2" sx={{ fontWeight: 800 }}>IKP</Typography>
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 300, opacity: 0.9, maxWidth: 400, lineHeight: 1.5 }}>
            Enterprise Knowledge Intelligence for the modern industrial workforce.
          </Typography>
        </motion.div>
      </Grid>

      {/* Right side - Login Form */}
      <Grid size={{ xs: 12, md: 6 }} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'background.default' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ width: '100%', maxWidth: 450 }}>
          <Paper elevation={0} sx={{ p: 5, bgcolor: 'transparent' }}>
            <Box sx={{ mb: 5, textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 800, mb: 1, color: 'text.primary' }}>Welcome Back</Typography>
              <Typography variant="body1" color="text.secondary">Sign in to your enterprise account</Typography>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 4 }}>
              <Button variant="outlined" size="large" onClick={() => handleSSO('Microsoft')} sx={{ borderRadius: 2, py: 1.5, color: 'text.primary', borderColor: 'divider' }}>
                <img src="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg" alt="MS" width="20" style={{ marginRight: 12 }} />
                Sign in with Microsoft
              </Button>
              <Button variant="outlined" size="large" onClick={() => handleSSO('Google')} sx={{ borderRadius: 2, py: 1.5, color: 'text.primary', borderColor: 'divider' }}>
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" alt="G" width="20" style={{ marginRight: 12 }} />
                Sign in with Google
              </Button>
            </Box>

            <Divider sx={{ mb: 4 }}>
              <Typography variant="caption" color="text.secondary" sx={{ px: 1 }}>OR USE EMAIL</Typography>
            </Divider>

            <form onSubmit={handleLogin}>
              <TextField
                fullWidth
                label="Corporate Email"
                variant="outlined"
                margin="normal"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                // @ts-ignore
                InputProps={{
                  startAdornment: <InputAdornment position="start"><Email color="action" /></InputAdornment>,
                  sx: { borderRadius: 2 }
                }}
              />
              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                variant="outlined"
                margin="normal"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                // @ts-ignore
                InputProps={{
                  startAdornment: <InputAdornment position="start"><Lock color="action" /></InputAdornment>,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                  sx: { borderRadius: 2 }
                }}
              />
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1, mb: 4 }}>
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer', fontWeight: 600 }}>
                  Forgot Password?
                </Typography>
              </Box>

              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                startIcon={<LoginIcon />}
                sx={{ py: 1.5, borderRadius: 2, fontSize: '1.1rem', fontWeight: 700 }}
              >
                {loading ? 'Authenticating...' : 'Sign In'}
              </Button>
            </form>
          </Paper>
        </motion.div>
      </Grid>
    </Grid>
  );
};

export default Login;
