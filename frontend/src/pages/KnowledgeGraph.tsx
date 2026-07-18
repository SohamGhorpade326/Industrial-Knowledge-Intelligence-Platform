// @ts-nocheck
import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Box, Card, CardContent, Typography, TextField, Chip, Select, MenuItem, FormControl, InputLabel, Skeleton } from '@mui/material';
import { motion } from 'framer-motion';
import { graphService } from '../services/graph';
import type { GraphData } from '../types';

const NODE_COLORS: Record<string, string> = {
  Machine: '#42a5f5', Document: '#66bb6a', Engineer: '#ffa726',
  Failure: '#ef5350', SOP: '#ab47bc', Vendor: '#26c6da',
  SparePart: '#78909c', Inspection: '#8d6e63', MaintenanceTask: '#d4e157',
};

const KnowledgeGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [filterType, setFilterType] = useState('');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    graphService.getGraph()
      .then(setGraphData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!graphData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const rect = canvas.parentElement?.getBoundingClientRect();
    canvas.width = rect?.width || 800;
    canvas.height = 500;

    const nodes = graphData.nodes
      .filter((n) => !filterType || n.type === filterType)
      .map((node, i) => ({
        ...node,
        x: 100 + (i % 6) * 120 + Math.random() * 40,
        y: 80 + Math.floor(i / 6) * 100 + Math.random() * 40,
        radius: 24,
      }));

    const nodeMap = new Map(nodes.map((n) => [n.id, n]));

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    graphData.edges.forEach((edge) => {
      const source = nodeMap.get(edge.source);
      const target = nodeMap.get(edge.target);
      if (source && target) {
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.strokeStyle = 'rgba(255,255,255,0.15)';
        ctx.lineWidth = 1;
        ctx.stroke();

        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        ctx.fillStyle = 'rgba(255,255,255,0.3)';
        ctx.font = '9px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(edge.relationship, midX, midY - 4);
      }
    });

    nodes.forEach((node) => {
      const color = NODE_COLORS[node.type] || '#78909c';

      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius + 4, 0, Math.PI * 2);
      ctx.fillStyle = `${color}20`;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();

      ctx.fillStyle = 'white';
      ctx.font = 'bold 10px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const label = node.label.length > 10 ? node.label.slice(0, 9) + '…' : node.label;
      ctx.fillText(label, node.x, node.y);

      ctx.fillStyle = 'rgba(255,255,255,0.5)';
      ctx.font = '8px Inter, sans-serif';
      ctx.fillText(node.type, node.x, node.y + node.radius + 12);
    });

    const handleClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const clicked = nodes.find((n) => Math.hypot(n.x - x, n.y - y) <= n.radius);
      setSelectedNode(clicked || null);
    };

    canvas.addEventListener('click', handleClick);
    return () => canvas.removeEventListener('click', handleClick);
  }, [graphData, filterType]);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="rounded" height={500} sx={{ borderRadius: 3 }} />
      </Box>
    );
  }

  const nodeTypes = [...new Set(graphData?.nodes.map((n) => n.type) || [])];

  return (
    <Box sx={{ p: 3 }}>
      <Typography  variant="h5" sx={{ fontWeight: 700 }}  gutterBottom>Knowledge Graph</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Interactive visualization of equipment, documents, and relationships
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Filter by Type</InputLabel>
          <Select value={filterType} onChange={(e) => setFilterType(e.target.value)} label="Filter by Type">
            <MenuItem value="">All</MenuItem>
            {nodeTypes.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
          </Select>
        </FormControl>
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', alignItems: 'center' }}>
          {Object.entries(NODE_COLORS).map(([type, color]) => (
            <Chip key={type} label={type} size="small" sx={{ bgcolor: `${color}30`, color, fontSize: '0.7rem' }} />
          ))}
        </Box>
      </Box>

      <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', overflow: 'hidden' }}>
        <Box sx={{ position: 'relative' }}>
          <canvas ref={canvasRef} style={{ width: '100%', display: 'block', cursor: 'pointer' }} />
        </Box>
      </Card>

      {selectedNode && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <Card sx={{ mt: 2, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography  variant="subtitle1" sx={{ fontWeight: 600 }} >
                {selectedNode.label}
                <Chip label={selectedNode.type} size="small" sx={{ ml: 1, bgcolor: `${NODE_COLORS[selectedNode.type]}30`, color: NODE_COLORS[selectedNode.type] }} />
              </Typography>
              <Box sx={{ mt: 1 }}>
                {Object.entries(selectedNode.properties || {}).map(([key, value]) => (
                  <Typography key={key} variant="body2" color="text.secondary">
                    <strong>{key}:</strong> {String(value)}
                  </Typography>
                ))}
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </Box>
  );
};

export default KnowledgeGraph;
