// @ts-nocheck
import {
  Box, Card, CardContent, Typography, Switch, Avatar, Chip,
  List, ListItem, ListItemText, ListItemSecondaryAction, Button,
} from '@mui/material';
import { DarkMode, LightMode, Logout } from '@mui/icons-material';
import { useAuthStore, useThemeStore } from '../context/store';
import { authService } from '../services/auth';
import { useNavigate } from 'react-router-dom';

const Settings: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const { mode, toggleTheme } = useThemeStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await authService.logout();
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600 }}>
      <Typography  variant="h5" sx={{ fontWeight: 700 }}  gutterBottom>Settings</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Manage your profile and application preferences
      </Typography>

      <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>Profile</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 2 }}>
            <Avatar sx={{ width: 56, height: 56, bgcolor: 'primary.main', fontSize: '1.5rem' }}>
              {user?.name?.charAt(0) || 'U'}
            </Avatar>
            <Box>
              <Typography  variant="h6" sx={{ fontWeight: 600 }} >{user?.name}</Typography>
              <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
              <Chip label={user?.role?.replace('_', ' ')} size="small" sx={{ mt: 0.5, textTransform: 'capitalize' }} />
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>Appearance</Typography>
          <List>
            <ListItem sx={{ px: 0 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {mode === 'dark' ? <DarkMode /> : <LightMode />}
                <ListItemText primary="Dark Mode" secondary={mode === 'dark' ? 'Enabled' : 'Disabled'} />
              </Box>
              <ListItemSecondaryAction>
                <Switch checked={mode === 'dark'} onChange={toggleTheme} />
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </CardContent>
      </Card>

      <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>Account</Typography>
          <Button
            variant="outlined"
            color="error"
            startIcon={<Logout />}
            onClick={handleLogout}
            sx={{ mt: 1, borderRadius: 2, textTransform: 'none' }}
          >
            Sign Out
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Settings;
