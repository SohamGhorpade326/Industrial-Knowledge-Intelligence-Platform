// @ts-nocheck
import React from 'react';
import {
  AppBar, Toolbar, Typography, IconButton, InputBase, Box, Avatar,
  Badge, Tooltip,
} from '@mui/material';
import {
  Search, Notifications, DarkMode, LightMode, Menu as MenuIcon,
  Warning,
} from '@mui/icons-material';
import { useAuthStore, useThemeStore } from '../../context/store';

interface TopBarProps {
  onMenuToggle: () => void;
}

const TopBar: React.FC<TopBarProps> = ({ onMenuToggle }) => {
  const user = useAuthStore((s) => s.user);
  const { mode, toggleTheme } = useThemeStore();

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
        zIndex: (theme) => theme.zIndex.drawer - 1,
      }}
    >
      <Toolbar sx={{ gap: 2 }}>
        <IconButton onClick={onMenuToggle} sx={{ display: { md: 'none' } }}>
          <MenuIcon />
        </IconButton>

        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            bgcolor: 'action.hover',
            borderRadius: 2,
            px: 2,
            py: 0.5,
            flex: 1,
            maxWidth: 480,
          }}
        >
          <Search sx={{ color: 'text.secondary', mr: 1 }} />
          <InputBase
            placeholder="Search documents, machines, SOPs..."
            sx={{ flex: 1, fontSize: '0.875rem' }}
            fullWidth
          />
        </Box>

        <Box sx={{ flex: 1 }} />

        <Tooltip title="Emergency Mode">
          <IconButton sx={{ color: 'error.main' }}>
            <Warning />
          </IconButton>
        </Tooltip>

        <Tooltip title={`Switch to ${mode === 'dark' ? 'light' : 'dark'} mode`}>
          <IconButton onClick={toggleTheme}>
            {mode === 'dark' ? <LightMode /> : <DarkMode />}
          </IconButton>
        </Tooltip>

        <Tooltip title="Notifications">
          <IconButton>
            <Badge badgeContent={3} color="error">
              <Notifications />
            </Badge>
          </IconButton>
        </Tooltip>

        <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main', fontSize: '0.875rem', cursor: 'pointer' }}>
          {user?.name?.charAt(0) || 'U'}
        </Avatar>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
