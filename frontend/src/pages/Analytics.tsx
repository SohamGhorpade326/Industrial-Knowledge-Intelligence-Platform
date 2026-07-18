// @ts-nocheck
import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography, Grid, Skeleton } from '@mui/material';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler } from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import { dashboardService } from '../services/dashboard';
import type { AnalyticsData } from '../types';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler);

const chartColors = ['#42a5f5', '#66bb6a', '#ffa726', '#ef5350', '#ab47bc', '#26c6da', '#78909c', '#8d6e63', '#d4e157'];

const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardService.getAnalytics()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {Array.from({ length: 6 }).map((_, i) => (
            <Grid size={{ xs: 12, md: 6 }} key={i}>
              <Skeleton variant="rounded" height={300} sx={{ borderRadius: 3 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  const catLabels = Object.keys(data?.documents_by_category || {});
  const catValues = Object.values(data?.documents_by_category || {});

  const docCategoryData = {
    labels: catLabels.map((l) => l.replace('_', ' ')),
    datasets: [{ data: catValues, backgroundColor: chartColors.slice(0, catLabels.length), borderWidth: 0 }],
  };

  const uploadData = {
    labels: (data?.upload_trends || []).slice(-14).map((t) => t.date.slice(5)),
    datasets: [{
      label: 'Uploads',
      data: (data?.upload_trends || []).slice(-14).map((t) => t.count),
      borderColor: '#42a5f5',
      backgroundColor: 'rgba(66,165,245,0.1)',
      fill: true,
      tension: 0.4,
    }],
  };

  const machineData = {
    labels: (data?.machine_health || []).map((m) => m.name),
    datasets: [{
      label: 'Health Score',
      data: (data?.machine_health || []).map((m) => m.health_score),
      backgroundColor: (data?.machine_health || []).map((m) =>
        m.health_score >= 80 ? '#4caf50' : m.health_score >= 60 ? '#ffa726' : '#ef5350'
      ),
      borderRadius: 6,
    }],
  };

  const failureData = {
    labels: (data?.failure_trends || []).map((f) => f.severity),
    datasets: [{
      data: (data?.failure_trends || []).map((f) => f.count),
      backgroundColor: ['#4caf50', '#ffa726', '#ef5350', '#d32f2f'],
      borderWidth: 0,
    }],
  };

  const kpis = [
    { label: 'Documents Processed', value: Object.values(data?.documents_by_category || {}).reduce((a: number, b: any) => a + (b as number), 0) },
    { label: 'Total AI Queries', value: data?.ai_usage?.total_queries || 0 },
    { label: 'Avg Downtime (hrs)', value: data?.maintenance_stats?.avg_downtime_hours || 0 },
    { label: 'Total Maintenance Cost', value: `₹${(data?.maintenance_stats?.total_cost || 0).toLocaleString()}` },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography  variant="h5" sx={{ fontWeight: 700 }}  gutterBottom>Analytics & Insights</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Comprehensive plant analytics, AI usage, and maintenance intelligence
      </Typography>

      <Grid container spacing={2}>
        {kpis.map((kpi, i) => (
          <Grid size={{ xs: 6, md: 3 }} key={kpi.label}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', textAlign: 'center' }}>
                <CardContent sx={{ py: 2.5 }}>
                  <Typography  variant="h4" sx={{ fontWeight: 700 }}  color="primary">{kpi.value}</Typography>
                  <Typography variant="caption" color="text.secondary">{kpi.label}</Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={2.5} sx={{ mt: 1 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>Documents by Category</Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', maxHeight: 260 }}>
                <Doughnut data={docCategoryData} options={{ cutout: '55%', plugins: { legend: { position: 'right', labels: { boxWidth: 12, padding: 8, font: { size: 11 } } } } }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>Upload Trends (14 days)</Typography>
              <Line data={uploadData} options={{ responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>Machine Health Distribution</Typography>
              <Bar data={machineData} options={{ responsive: true, plugins: { legend: { display: false } }, scales: { y: { max: 100, beginAtZero: true } } }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>Failure Trends by Severity</Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', maxHeight: 260 }}>
                <Doughnut data={failureData} options={{ cutout: '55%', plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, padding: 10, font: { size: 11 } } } } }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
