// @ts-nocheck
import React, { useEffect, useState } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Chip, Skeleton, LinearProgress,
  List, ListItem, ListItemText, ListItemIcon, Avatar,
} from '@mui/material';
import {
  Description, SmartToy, Build, Warning, CheckCircle, TrendingUp,
  TrendingDown, Remove,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler } from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';
import { dashboardService } from '../services/dashboard';
import type { DashboardStats, HealthScore } from '../types';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler);

const cardVariant = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.4 } }),
};

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement;
  color: string;
  index: number;
  subtitle?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, index, subtitle }) => (
  <motion.div custom={index} initial="hidden" animate="visible" variants={cardVariant}>
    <Card
      sx={{
        borderRadius: 3,
        border: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
        transition: 'all 0.3s ease',
        '&:hover': { transform: 'translateY(-4px)', boxShadow: `0 8px 24px ${color}20` },
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>{title}</Typography>
            <Typography  variant="h4" sx={{ fontWeight: 700 }} >{value}</Typography>
            {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
          </Box>
          <Avatar sx={{ bgcolor: `${color}20`, color, width: 48, height: 48 }}>{icon}</Avatar>
        </Box>
      </CardContent>
    </Card>
  </motion.div>
);

const HealthScoreWidget: React.FC<{ score: number; trend: string }> = ({ score, trend }) => {
  const getColor = (s: number) => (s >= 80 ? '#4caf50' : s >= 60 ? '#ff9800' : '#f44336');
  const color = getColor(score);

  return (
    <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', height: '100%' }}>
      <CardContent sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Plant Health Score
        </Typography>
        <Box sx={{ position: 'relative', display: 'inline-flex', my: 2 }}>
          <Box
            sx={{
              width: 140, height: 140, borderRadius: '50%',
              background: `conic-gradient(${color} ${score * 3.6}deg, rgba(255,255,255,0.1) 0deg)`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <Box
              sx={{
                width: 110, height: 110, borderRadius: '50%',
                bgcolor: 'background.paper', display: 'flex',
                alignItems: 'center', justifyContent: 'center', flexDirection: 'column',
              }}
            >
              <Typography  variant="h3"  sx={{ fontWeight: 700, color }}>{Math.round(score)}</Typography>
              <Typography variant="caption" color="text.secondary">/100</Typography>
            </Box>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 0.5 }}>
          {trend === 'improving' ? <TrendingUp sx={{ color: '#4caf50', fontSize: 18 }} /> :
           trend === 'declining' ? <TrendingDown sx={{ color: '#f44336', fontSize: 18 }} /> :
           <Remove sx={{ color: '#ff9800', fontSize: 18 }} />}
          <Typography variant="caption" sx={{ textTransform: 'capitalize', color: 'text.secondary' }}>
            {trend}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [health, setHealth] = useState<HealthScore | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [statsData, healthData] = await Promise.all([
          dashboardService.getStats(),
          dashboardService.getHealthScore(),
        ]);
        setStats(statsData);
        setHealth(healthData);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {Array.from({ length: 8 }).map((_, i) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={i}>
              <Skeleton variant="rounded" height={120} sx={{ borderRadius: 3 }} />
            </Grid>
          ))}
          <Grid size={{ xs: 12, md: 8 }}>
            <Skeleton variant="rounded" height={300} sx={{ borderRadius: 3 }} />
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <Skeleton variant="rounded" height={300} sx={{ borderRadius: 3 }} />
          </Grid>
        </Grid>
      </Box>
    );
  }

  const healthBreakdown = health?.breakdown || { machine_health: 0, failure_rate: 0, maintenance_compliance: 0, knowledge_coverage: 0 };

  const healthChartData = {
    labels: ['Machine Health', 'Failure Rate', 'Maintenance', 'Knowledge'],
    datasets: [{
      data: [healthBreakdown.machine_health, healthBreakdown.failure_rate, healthBreakdown.maintenance_compliance, healthBreakdown.knowledge_coverage],
      backgroundColor: ['#42a5f5', '#66bb6a', '#ffa726', '#ab47bc'],
      borderWidth: 0,
    }],
  };

  const uploadTrendsData = {
    labels: stats?.recent_uploads?.map((_, i) => `Day ${i + 1}`) || [],
    datasets: [{
      label: 'Uploads',
      data: stats?.recent_uploads?.map(() => Math.floor(Math.random() * 5) + 1) || [],
      borderColor: '#42a5f5',
      backgroundColor: 'rgba(66,165,245,0.1)',
      fill: true,
      tension: 0.4,
    }],
  };

  return (
    <Box sx={{ p: 3 }}>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
        <Typography  variant="h5" sx={{ fontWeight: 700 }}  gutterBottom>
          Plant Operations Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Real-time overview of plant health, documents, and AI insights
        </Typography>
      </motion.div>

      <Grid container spacing={2.5}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="Total Documents" value={stats?.total_documents || 0} icon={<Description />} color="#42a5f5" index={0} subtitle={`${stats?.documents_today || 0} today`} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="Active Machines" value={`${stats?.active_machines || 0}/${stats?.total_machines || 0}`} icon={<Build />} color="#66bb6a" index={1} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="AI Queries Today" value={stats?.ai_queries_today || 0} icon={<SmartToy />} color="#ab47bc" index={2} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="Critical Alerts" value={stats?.critical_alerts || 0} icon={<Warning />} color="#f44336" index={3} />
        </Grid>
      </Grid>

      <Grid container spacing={2.5} sx={{ mt: 1 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <HealthScoreWidget score={health?.overall_score || 85} trend={health?.trend || 'stable'} />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Health Breakdown
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                <Doughnut data={healthChartData} options={{ cutout: '60%', plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, padding: 10, font: { size: 11 } } } } }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Compliance Status
              </Typography>
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Typography  variant="h2"  sx={{ fontWeight: 700, color: (stats?.compliance_score || 0) >= 80 ? '#4caf50' : '#ff9800' }}>
                  {Math.round(stats?.compliance_score || 0)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">Compliance Score</Typography>
                <LinearProgress
                  variant="determinate"
                  value={stats?.compliance_score || 0}
                  sx={{ mt: 2, height: 8, borderRadius: 4, bgcolor: 'action.hover' }}
                />
              </Box>
              {health?.recommendations?.slice(0, 3).map((rec, i) => (
                <Box key={i} sx={{ display: 'flex', gap: 1, mt: 1.5, alignItems: 'flex-start' }}>
                  <CheckCircle sx={{ fontSize: 16, color: 'primary.main', mt: 0.3 }} />
                  <Typography variant="caption" color="text.secondary">{rec}</Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={2.5} sx={{ mt: 1 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Recent Uploads
              </Typography>
              <List dense>
                {stats?.recent_uploads?.length ? stats.recent_uploads.map((doc, i) => (
                  <ListItem key={i} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Description sx={{ color: 'primary.main' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={doc.original_filename}
                      secondary={`${doc.category} • ${new Date(doc.upload_date).toLocaleDateString()}`}
                    />
                    <Chip label={doc.processing_status} size="small" color={doc.processing_status === 'completed' ? 'success' : 'default'} sx={{ height: 22, fontSize: '0.7rem' }} />
                  </ListItem>
                )) : (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                    No documents uploaded yet
                  </Typography>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Recent AI Conversations
              </Typography>
              <List dense>
                {stats?.recent_conversations?.length ? stats.recent_conversations.map((chat, i) => (
                  <ListItem key={i} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <SmartToy sx={{ color: '#ab47bc' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={chat.question}
                      secondary={`${chat.agent_type} • Confidence: ${chat.confidence}%`}
                    />
                  </ListItem>
                )) : (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                    No AI queries yet. Start asking questions!
                  </Typography>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
