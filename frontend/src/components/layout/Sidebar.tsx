// @ts-nocheck
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box, Drawer, List, ListItemButton, ListItemIcon, ListItemText,
  Typography, Divider, Avatar, Chip, IconButton, useMediaQuery,
} from '@mui/material';
import {
  Dashboard, Description, SmartToy, AccountTree, Build,
  Security, BarChart, Settings, ChevronLeft, ChevronRight,
  Factory,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../context/store';

const DRAWER_WIDTH = 260;
const COLLAPSED_WIDTH = 72;

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactElement;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/app', icon: <Dashboard /> },
  { label: 'Documents', path: '/app/upload', icon: <Description /> },
  { label: 'AI Assistant', path: '/app/chat', icon: <SmartToy /> },
  { label: 'Knowledge Graph', path: '/app/knowledge-graph', icon: <AccountTree /> },
  { label: 'Maintenance', path: '/app/maintenance', icon: <Build /> },
  { label: 'Compliance', path: '/app/compliance', icon: <Security /> },
  { label: 'Analytics', path: '/app/analytics', icon: <BarChart /> },
  { label: 'Settings', path: '/app/settings', icon: <Settings /> },
];

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ open, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const isMobile = useMediaQuery('(max-width:768px)');

  const drawerWidth = open ? DRAWER_WIDTH : COLLAPSED_WIDTH;

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'permanent'}
      open={isMobile ? open : true}
      onClose={onToggle}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        transition: 'width 0.3s ease',
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          borderRight: '1px solid',
          borderColor: 'divider',
          bgcolor: 'background.paper',
          transition: 'width 0.3s ease',
          overflowX: 'hidden',
        },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5, minHeight: 64 }}>
        <Factory sx={{ color: 'primary.main', fontSize: 32 }} />
        {open && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
            <Typography  variant="subtitle1"  noWrap sx={{ fontWeight: 700, color: 'primary.main' }}>
              IKP
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.65rem' }} noWrap>
              Knowledge Intelligence
            </Typography>
          </motion.div>
        )}
      </Box>

      <Divider />

      <List sx={{ px: 1, py: 1, flex: 1 }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItemButton
              key={item.path}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                minHeight: 44,
                justifyContent: open ? 'initial' : 'center',
                px: open ? 2 : 1.5,
                bgcolor: isActive ? 'primary.main' : 'transparent',
                color: isActive ? 'primary.contrastText' : 'text.secondary',
                '&:hover': {
                  bgcolor: isActive ? 'primary.dark' : 'action.hover',
                },
                transition: 'all 0.2s ease',
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: open ? 36 : 'unset',
                  color: isActive ? 'primary.contrastText' : 'text.secondary',
                  justifyContent: 'center',
                }}
              >
                {item.icon}
              </ListItemIcon>
              {open && <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: '0.875rem', fontWeight: isActive ? 600 : 400 }} />}
            </ListItemButton>
          );
        })}
      </List>

      <Divider />

      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: '0.875rem' }}>
          {user?.name?.charAt(0) || 'U'}
        </Avatar>
        {open && (
          <Box sx={{ overflow: 'hidden' }}>
            <Typography  variant="body2" sx={{ fontWeight: 600 }}  noWrap>{user?.name || 'User'}</Typography>
            <Chip label={user?.role?.replace('_', ' ') || 'viewer'} size="small" sx={{ height: 20, fontSize: '0.65rem', textTransform: 'capitalize' }} />
          </Box>
        )}
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'center', p: 1 }}>
        <IconButton onClick={onToggle} size="small">
          {open ? <ChevronLeft /> : <ChevronRight />}
        </IconButton>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
